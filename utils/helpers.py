"""
Helper utilities for the Etsy Trend Detection system.
"""

import logging
import os
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Any
import json

def setup_logging():
    """Setup logging configuration."""
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_dir / "trend_detector.log"),
            logging.StreamHandler()
        ]
    )

def create_directories():
    """Create necessary directories."""
    directories = [
        "data/raw",
        "data/processed", 
        "data/reports",
        "logs",
        "dashboard/components"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)

def save_json_data(data: Dict[str, Any], filename: str, directory: str = "data/raw"):
    """Save data to JSON file."""
    try:
        filepath = Path(directory) / filename
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2, default=str)
        
        return filepath
    except Exception as e:
        logging.error(f"Error saving JSON data: {e}")
        return None

def load_json_data(filepath: str) -> Dict[str, Any]:
    """Load data from JSON file."""
    try:
        with open(filepath, 'r') as f:
            return json.load(f)
    except Exception as e:
        logging.error(f"Error loading JSON data: {e}")
        return {}

def format_timestamp(timestamp: str) -> str:
    """Format timestamp for display."""
    try:
        dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    except:
        return timestamp

def clean_text(text: str) -> str:
    """Clean and normalize text."""
    if not text:
        return ""
    
    # Remove extra whitespace
    text = " ".join(text.split())
    
    # Remove special characters (keep alphanumeric and spaces)
    import re
    text = re.sub(r'[^\w\s]', '', text)
    
    return text.strip()

def extract_keywords(text: str, min_length: int = 3) -> List[str]:
    """Extract keywords from text."""
    if not text:
        return []
    
    # Clean text
    text = clean_text(text.lower())
    
    # Split into words
    words = text.split()
    
    # Filter words
    stop_words = {
        'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
        'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
        'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could',
        'should', 'may', 'might', 'can', 'this', 'that', 'these', 'those',
        'i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her',
        'us', 'them', 'my', 'your', 'his', 'her', 'its', 'our', 'their'
    }
    
    keywords = []
    for word in words:
        if (len(word) >= min_length and 
            word not in stop_words and 
            not word.isdigit()):
            keywords.append(word)
    
    return keywords

def calculate_similarity(text1: str, text2: str) -> float:
    """Calculate similarity between two texts."""
    if not text1 or not text2:
        return 0.0
    
    # Simple Jaccard similarity
    words1 = set(extract_keywords(text1))
    words2 = set(extract_keywords(text2))
    
    if not words1 and not words2:
        return 0.0
    
    intersection = len(words1.intersection(words2))
    union = len(words1.union(words2))
    
    return intersection / union if union > 0 else 0.0

def get_file_size_mb(filepath: str) -> float:
    """Get file size in MB."""
    try:
        size_bytes = os.path.getsize(filepath)
        return size_bytes / (1024 * 1024)
    except:
        return 0.0

def format_file_size(size_mb: float) -> str:
    """Format file size for display."""
    if size_mb < 1:
        return f"{size_mb * 1024:.1f} KB"
    elif size_mb < 1024:
        return f"{size_mb:.1f} MB"
    else:
        return f"{size_mb / 1024:.1f} GB"

def validate_email(email: str) -> bool:
    """Validate email address format."""
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def sanitize_filename(filename: str) -> str:
    """Sanitize filename for safe file operations."""
    import re
    # Remove or replace unsafe characters
    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
    # Remove leading/trailing spaces and dots
    filename = filename.strip(' .')
    # Limit length
    if len(filename) > 255:
        filename = filename[:255]
    return filename

def get_system_info() -> Dict[str, Any]:
    """Get system information."""
    import platform
    import psutil
    
    return {
        'platform': platform.system(),
        'platform_version': platform.version(),
        'python_version': platform.python_version(),
        'cpu_count': psutil.cpu_count(),
        'memory_total': psutil.virtual_memory().total,
        'disk_usage': psutil.disk_usage('/').percent
    }

def check_disk_space(path: str = ".") -> Dict[str, Any]:
    """Check available disk space."""
    import psutil
    
    try:
        usage = psutil.disk_usage(path)
        return {
            'total': usage.total,
            'used': usage.used,
            'free': usage.free,
            'percent': usage.percent
        }
    except Exception as e:
        logging.error(f"Error checking disk space: {e}")
        return {}

def backup_data(source_dir: str, backup_dir: str):
    """Create backup of data directory."""
    import shutil
    from datetime import datetime
    
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = Path(backup_dir) / f"backup_{timestamp}"
        
        if Path(source_dir).exists():
            shutil.copytree(source_dir, backup_path)
            logging.info(f"Backup created: {backup_path}")
            return str(backup_path)
        else:
            logging.warning(f"Source directory does not exist: {source_dir}")
            return None
    except Exception as e:
        logging.error(f"Error creating backup: {e}")
        return None

def cleanup_old_files(directory: str, days: int = 7):
    """Clean up old files in directory."""
    try:
        cutoff_time = datetime.now() - timedelta(days=days)
        directory_path = Path(directory)
        
        if not directory_path.exists():
            return
        
        deleted_count = 0
        for file_path in directory_path.rglob("*"):
            if file_path.is_file():
                try:
                    if datetime.fromtimestamp(file_path.stat().st_mtime) < cutoff_time:
                        file_path.unlink()
                        deleted_count += 1
                except Exception as e:
                    logging.warning(f"Could not delete {file_path}: {e}")
        
        logging.info(f"Cleaned up {deleted_count} old files from {directory}")
        
    except Exception as e:
        logging.error(f"Error cleaning up old files: {e}")

def send_notification(message: str, notification_type: str = "info"):
    """Send notification (placeholder for future implementation)."""
    # This could be expanded to send emails, Slack messages, etc.
    logging.info(f"[{notification_type.upper()}] {message}")
    
    # Example: Send to console with color
    colors = {
        'info': '\033[94m',    # Blue
        'success': '\033[92m',  # Green
        'warning': '\033[93m',  # Yellow
        'error': '\033[91m',    # Red
    }
    
    color = colors.get(notification_type, '')
    reset = '\033[0m'
    
    print(f"{color}{message}{reset}") 