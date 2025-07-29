"""
Database utility for storing and retrieving trend data.
"""

import sqlite3
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from pathlib import Path
import json

from utils.config import Config

logger = logging.getLogger(__name__)

class Database:
    """SQLite database for storing trend data."""
    
    def __init__(self, config: Config):
        self.config = config
        self.db_path = Path(config.get('database.path', 'data/trends.db'))
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_database()
    
    def _init_database(self):
        """Initialize database tables."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Create trends table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS trends (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        keyword TEXT NOT NULL,
                        source TEXT NOT NULL,
                        title TEXT,
                        description TEXT,
                        text_content TEXT,
                        category TEXT,
                        score REAL,
                        frequency INTEGER,
                        collected_at TEXT NOT NULL,
                        created_at TEXT DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # Create analysis_results table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS analysis_results (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        mode TEXT NOT NULL,
                        analysis_data TEXT NOT NULL,
                        created_at TEXT DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # Create indexes
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_keyword ON trends(keyword)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_source ON trends(source)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_collected_at ON trends(collected_at)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_category ON trends(category)')
                
                conn.commit()
                logger.info("Database initialized successfully")
                
        except Exception as e:
            logger.error(f"Error initializing database: {e}")
    
    async def insert_trend_data(self, data: Dict[str, Any]):
        """Insert trend data into database."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Extract keyword from various fields
                keyword = self._extract_keyword(data)
                
                cursor.execute('''
                    INSERT INTO trends (
                        keyword, source, title, description, text_content,
                        category, score, frequency, collected_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    keyword,
                    data.get('source', 'unknown'),
                    data.get('title', ''),
                    data.get('description', ''),
                    data.get('text', ''),
                    data.get('category', ''),
                    data.get('score', 0.0),
                    data.get('frequency', 1),
                    data.get('collected_at', datetime.now().isoformat())
                ))
                
                conn.commit()
                
        except Exception as e:
            logger.error(f"Error inserting trend data: {e}")
    
    def _extract_keyword(self, data: Dict[str, Any]) -> str:
        """Extract primary keyword from data."""
        # Try to extract keyword from various fields
        text_fields = ['title', 'description', 'text', 'search_term']
        
        for field in text_fields:
            if field in data and data[field]:
                # Simple keyword extraction - take first meaningful word
                words = str(data[field]).lower().split()
                for word in words:
                    if len(word) > 3 and word.isalpha():
                        return word
        
        return 'unknown'
    
    async def get_recent_data(self, hours: int = 24) -> List[Dict[str, Any]]:
        """Get recent data from database."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cutoff_time = datetime.now() - timedelta(hours=hours)
                
                cursor.execute('''
                    SELECT * FROM trends 
                    WHERE collected_at >= ?
                    ORDER BY collected_at DESC
                ''', (cutoff_time.isoformat(),))
                
                rows = cursor.fetchall()
                
                # Convert to list of dictionaries
                columns = [description[0] for description in cursor.description]
                data = []
                
                for row in rows:
                    item = dict(zip(columns, row))
                    data.append(item)
                
                return data
                
        except Exception as e:
            logger.error(f"Error getting recent data: {e}")
            return []
    
    async def get_trends_by_keyword(self, keyword: str, hours: int = 24) -> List[Dict[str, Any]]:
        """Get trends for a specific keyword."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cutoff_time = datetime.now() - timedelta(hours=hours)
                
                cursor.execute('''
                    SELECT * FROM trends 
                    WHERE keyword LIKE ? AND collected_at >= ?
                    ORDER BY collected_at DESC
                ''', (f'%{keyword}%', cutoff_time.isoformat()))
                
                rows = cursor.fetchall()
                
                columns = [description[0] for description in cursor.description]
                data = []
                
                for row in rows:
                    item = dict(zip(columns, row))
                    data.append(item)
                
                return data
                
        except Exception as e:
            logger.error(f"Error getting trends by keyword: {e}")
            return []
    
    async def get_trends_by_category(self, category: str, hours: int = 24) -> List[Dict[str, Any]]:
        """Get trends for a specific category."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cutoff_time = datetime.now() - timedelta(hours=hours)
                
                cursor.execute('''
                    SELECT * FROM trends 
                    WHERE category = ? AND collected_at >= ?
                    ORDER BY collected_at DESC
                ''', (category, cutoff_time.isoformat()))
                
                rows = cursor.fetchall()
                
                columns = [description[0] for description in cursor.description]
                data = []
                
                for row in rows:
                    item = dict(zip(columns, row))
                    data.append(item)
                
                return data
                
        except Exception as e:
            logger.error(f"Error getting trends by category: {e}")
            return []
    
    async def get_trending_keywords(self, hours: int = 24, limit: int = 20) -> List[Dict[str, Any]]:
        """Get trending keywords based on frequency."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cutoff_time = datetime.now() - timedelta(hours=hours)
                
                cursor.execute('''
                    SELECT keyword, COUNT(*) as frequency, 
                           AVG(score) as avg_score,
                           COUNT(DISTINCT source) as source_count
                    FROM trends 
                    WHERE collected_at >= ?
                    GROUP BY keyword
                    ORDER BY frequency DESC, avg_score DESC
                    LIMIT ?
                ''', (cutoff_time.isoformat(), limit))
                
                rows = cursor.fetchall()
                
                data = []
                for row in rows:
                    data.append({
                        'keyword': row[0],
                        'frequency': row[1],
                        'avg_score': row[2],
                        'source_count': row[3]
                    })
                
                return data
                
        except Exception as e:
            logger.error(f"Error getting trending keywords: {e}")
            return []
    
    async def save_analysis_results(self, mode: str, analysis_data: Dict[str, Any]):
        """Save analysis results to database."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT INTO analysis_results (mode, analysis_data)
                    VALUES (?, ?)
                ''', (mode, json.dumps(analysis_data)))
                
                conn.commit()
                
        except Exception as e:
            logger.error(f"Error saving analysis results: {e}")
    
    async def get_latest_analysis(self, mode: str = None) -> Optional[Dict[str, Any]]:
        """Get latest analysis results."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                if mode:
                    cursor.execute('''
                        SELECT analysis_data FROM analysis_results 
                        WHERE mode = ?
                        ORDER BY created_at DESC
                        LIMIT 1
                    ''', (mode,))
                else:
                    cursor.execute('''
                        SELECT analysis_data FROM analysis_results 
                        ORDER BY created_at DESC
                        LIMIT 1
                    ''')
                
                row = cursor.fetchone()
                
                if row:
                    return json.loads(row[0])
                
                return None
                
        except Exception as e:
            logger.error(f"Error getting latest analysis: {e}")
            return None
    
    async def cleanup_old_data(self, days: int = 7):
        """Clean up old data from database."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cutoff_time = datetime.now() - timedelta(days=days)
                
                cursor.execute('''
                    DELETE FROM trends 
                    WHERE collected_at < ?
                ''', (cutoff_time.isoformat(),))
                
                deleted_count = cursor.rowcount
                conn.commit()
                
                logger.info(f"Cleaned up {deleted_count} old records")
                
        except Exception as e:
            logger.error(f"Error cleaning up old data: {e}")
    
    def get_database_stats(self) -> Dict[str, Any]:
        """Get database statistics."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Total records
                cursor.execute('SELECT COUNT(*) FROM trends')
                total_records = cursor.fetchone()[0]
                
                # Records by source
                cursor.execute('''
                    SELECT source, COUNT(*) as count 
                    FROM trends 
                    GROUP BY source
                ''')
                source_counts = dict(cursor.fetchall())
                
                # Records by category
                cursor.execute('''
                    SELECT category, COUNT(*) as count 
                    FROM trends 
                    WHERE category IS NOT NULL AND category != ''
                    GROUP BY category
                ''')
                category_counts = dict(cursor.fetchall())
                
                # Recent activity
                cursor.execute('''
                    SELECT COUNT(*) FROM trends 
                    WHERE collected_at >= ?
                ''', ((datetime.now() - timedelta(hours=24)).isoformat(),))
                recent_records = cursor.fetchone()[0]
                
                return {
                    'total_records': total_records,
                    'recent_records_24h': recent_records,
                    'source_counts': source_counts,
                    'category_counts': category_counts
                }
                
        except Exception as e:
            logger.error(f"Error getting database stats: {e}")
            return {} 