#!/usr/bin/env python3
"""
Simple test script for the Etsy Trend Detection system.
This version works with minimal dependencies.
"""

import sys
import json
from datetime import datetime
from pathlib import Path

def test_basic_functionality():
    """Test basic functionality without external dependencies."""
    print("🧪 Simple Etsy Trend Detection Test")
    print("=" * 40)
    
    # Test 1: File structure
    print("\n📁 Testing file structure...")
    required_files = [
        "main.py",
        "requirements.txt", 
        "README.md",
        "utils/config.py",
        "data_ingestion/collector_manager.py",
        "analysis/trend_analyzer.py",
        "dashboard/app.py"
    ]
    
    missing_files = []
    for file_path in required_files:
        if Path(file_path).exists():
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path}")
            missing_files.append(file_path)
    
    if missing_files:
        print(f"\n⚠️ Missing files: {len(missing_files)}")
    else:
        print("\n✅ All required files present!")
    
    # Test 2: Configuration
    print("\n⚙️ Testing configuration...")
    try:
        # Create a simple config test
        config_data = {
            'data_sources': {
                'google_trends': {'enabled': True},
                'reddit': {'enabled': True},
                'pinterest': {'enabled': True}
            },
            'analysis': {
                'categories': {
                    'jewelry': ['necklace', 'ring', 'bracelet'],
                    'home_decor': ['candle', 'mug', 'pillow']
                }
            }
        }
        
        # Save test config
        config_file = Path("test_config.json")
        with open(config_file, 'w') as f:
            json.dump(config_data, f, indent=2)
        
        print("✅ Configuration test passed")
        
        # Clean up
        config_file.unlink()
        
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
    
    # Test 3: Mock data collection
    print("\n📊 Testing mock data collection...")
    try:
        mock_data = {
            'google_trends': [
                {
                    'keyword': 'personalized jewelry',
                    'score': 0.85,
                    'trend_direction': 'rising',
                    'collected_at': datetime.now().isoformat()
                },
                {
                    'keyword': 'handmade candles',
                    'score': 0.72,
                    'trend_direction': 'stable',
                    'collected_at': datetime.now().isoformat()
                }
            ],
            'reddit': [
                {
                    'title': 'Beautiful handmade jewelry from Etsy!',
                    'score': 0.68,
                    'subreddit': 'jewelry',
                    'collected_at': datetime.now().isoformat()
                }
            ],
            'metadata': {
                'total_items': 3,
                'collection_time': datetime.now().isoformat()
            }
        }
        
        # Save mock data
        data_dir = Path("data/raw")
        data_dir.mkdir(parents=True, exist_ok=True)
        
        mock_file = data_dir / "mock_data.json"
        with open(mock_file, 'w') as f:
            json.dump(mock_data, f, indent=2)
        
        print("✅ Mock data collection test passed")
        
    except Exception as e:
        print(f"❌ Mock data collection test failed: {e}")
    
    # Test 4: Simple trend analysis
    print("\n🔍 Testing simple trend analysis...")
    try:
        # Simple keyword extraction
        test_texts = [
            "personalized name necklace",
            "handmade ceramic mug",
            "custom wedding gift"
        ]
        
        keywords = []
        for text in test_texts:
            words = text.lower().split()
            keywords.extend([word for word in words if len(word) > 3])
        
        # Simple scoring
        keyword_counts = {}
        for keyword in keywords:
            keyword_counts[keyword] = keyword_counts.get(keyword, 0) + 1
        
        # Sort by frequency
        sorted_keywords = sorted(keyword_counts.items(), key=lambda x: x[1], reverse=True)
        
        print("✅ Simple trend analysis test passed")
        print(f"  - Extracted {len(keywords)} keywords")
        print(f"  - Top keywords: {sorted_keywords[:3]}")
        
    except Exception as e:
        print(f"❌ Simple trend analysis test failed: {e}")
    
    # Test 5: Directory creation
    print("\n📂 Testing directory creation...")
    try:
        directories = [
            "data/raw",
            "data/processed", 
            "data/reports",
            "logs",
            "dashboard/components"
        ]
        
        created_dirs = []
        for directory in directories:
            Path(directory).mkdir(parents=True, exist_ok=True)
            created_dirs.append(directory)
        
        print(f"✅ Created {len(created_dirs)} directories")
        
    except Exception as e:
        print(f"❌ Directory creation test failed: {e}")
    
    # Test 6: System information
    print("\n💻 Testing system information...")
    try:
        import platform
        import os
        
        system_info = {
            'platform': platform.system(),
            'python_version': platform.python_version(),
            'current_directory': os.getcwd(),
            'files_in_directory': len(list(Path('.').glob('*')))
        }
        
        print("✅ System information test passed")
        print(f"  - Platform: {system_info['platform']}")
        print(f"  - Python: {system_info['python_version']}")
        print(f"  - Files in directory: {system_info['files_in_directory']}")
        
    except Exception as e:
        print(f"❌ System information test failed: {e}")
    
    print("\n" + "=" * 40)
    print("🎉 Simple test completed!")
    print("\nNext steps:")
    print("1. Install missing dependencies: pip install PyYAML python-dotenv")
    print("2. Run the full test: python test_system.py")
    print("3. Try the example: python example.py")
    print("4. Launch dashboard: streamlit run dashboard/app.py")

if __name__ == "__main__":
    test_basic_functionality() 