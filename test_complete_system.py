#!/usr/bin/env python3
"""
Complete System Test

Tests all components of the Etsy Trend Detection System to ensure
everything works together correctly.
"""

import asyncio
import json
import sys
from pathlib import Path
from datetime import datetime, timedelta
import logging

# Add the project root to the path
sys.path.append(str(Path(__file__).parent))

def test_imports():
    """Test that all modules can be imported."""
    print("🔍 Testing module imports...")
    
    try:
        # Test core modules
        from data_ingestion.collector_manager import CollectorManager
        from analysis.emerging_trend_detector import EmergingTrendDetector
        from analysis.trend_analyzer import TrendAnalyzer
        from analysis.scoring_engine import ScoringEngine
        from storage.history_manager import HistoryManager
        from reporting.report_generator import ReportGenerator
        from utils.config import Config
        from utils.helpers import setup_logging, create_directories
        
        print("✅ All core modules imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def test_configuration():
    """Test configuration loading."""
    print("\n🔧 Testing configuration...")
    
    try:
        from utils.config import Config
        
        # Test with default config
        config = Config()
        print(f"✅ Configuration loaded: {config.config_file}")
        print(f"📊 Data sources: {config.get_data_sources()}")
        return True
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        return False

def test_history_manager():
    """Test history manager functionality."""
    print("\n💾 Testing history manager...")
    
    try:
        from storage.history_manager import HistoryManager
        
        # Initialize history manager
        history_manager = HistoryManager()
        
        # Test storing data
        test_data = [
            {
                'keyword': 'test_trend_1',
                'platform': 'google_trends',
                'category': 'jewelry',
                'popularity_score': 85.0,
                'emerging_score': 0.8,
                'confidence_score': 0.9,
                'timestamp': datetime.now().isoformat()
            },
            {
                'keyword': 'test_trend_2',
                'platform': 'reddit',
                'category': 'home_decor',
                'popularity_score': 72.0,
                'emerging_score': 0.7,
                'confidence_score': 0.8,
                'timestamp': datetime.now().isoformat()
            }
        ]
        
        today = datetime.now().strftime('%Y-%m-%d')
        history_manager.store_daily_trends(test_data, today)
        
        # Test retrieving data
        retrieved_data = history_manager.get_trends_by_date(today)
        print(f"✅ Stored and retrieved {len(retrieved_data)} trends")
        
        # Test emerging trends
        emerging_trends = history_manager.get_emerging_trends()
        print(f"✅ Found {len(emerging_trends)} emerging trends")
        
        # Test multi-source trends
        multi_source_trends = history_manager.get_multi_source_trends()
        print(f"✅ Found {len(multi_source_trends)} multi-source trends")
        
        return True
    except Exception as e:
        print(f"❌ History manager error: {e}")
        return False

def test_emerging_trend_detector():
    """Test emerging trend detection."""
    print("\n🔍 Testing emerging trend detector...")
    
    try:
        from analysis.emerging_trend_detector import EmergingTrendDetector
        
        detector = EmergingTrendDetector()
        
        # Test emerging score calculation
        score = detector.calculate_emerging_score(85.0, 65.0)
        print(f"✅ Emerging score calculation: {score:.3f}")
        
        # Test trend detection
        test_trends = [
            {
                'keyword': 'personalized jewelry',
                'platform': 'google_trends',
                'category': 'jewelry',
                'popularity_score': 85.0,
                'timestamp': datetime.now().isoformat()
            },
            {
                'keyword': 'handmade candles',
                'platform': 'pinterest',
                'category': 'home_decor',
                'popularity_score': 72.0,
                'timestamp': datetime.now().isoformat()
            }
        ]
        
        historical_data = [
            {
                'keyword': 'personalized jewelry',
                'platform': 'google_trends',
                'category': 'jewelry',
                'popularity_score': 65.0,
                'timestamp': (datetime.now() - timedelta(days=1)).isoformat()
            }
        ]
        
        emerging_trends = detector.detect_emerging_trends(test_trends, historical_data)
        print(f"✅ Detected {len(emerging_trends)} emerging trends")
        
        # Test multi-source confidence
        trends_with_confidence = detector.calculate_multi_source_confidence(test_trends)
        print(f"✅ Calculated confidence for {len(trends_with_confidence)} trends")
        
        return True
    except Exception as e:
        print(f"❌ Emerging trend detector error: {e}")
        return False

def test_report_generator():
    """Test report generation."""
    print("\n📊 Testing report generator...")
    
    try:
        from reporting.report_generator import ReportGenerator
        
        generator = ReportGenerator()
        
        # Test data
        trends_data = [
            {
                'keyword': 'personalized jewelry',
                'platform': 'google_trends',
                'category': 'jewelry',
                'popularity_score': 85.0,
                'emerging_score': 0.8,
                'confidence_score': 0.9,
                'timestamp': datetime.now().isoformat()
            }
        ]
        
        emerging_trends = [
            {
                'keyword': 'personalized jewelry',
                'platform': 'google_trends',
                'category': 'jewelry',
                'popularity_score': 85.0,
                'emerging_score': 0.8,
                'confidence_score': 0.9,
                'timestamp': datetime.now().isoformat()
            }
        ]
        
        cross_platform_trends = [
            {
                'keyword': 'personalized jewelry',
                'platforms': ['google_trends', 'pinterest'],
                'source_count': 2,
                'avg_popularity': 85.0,
                'avg_emerging': 0.8,
                'avg_confidence': 0.9
            }
        ]
        
        # Generate reports
        reports = generator.generate_daily_report(trends_data, emerging_trends, cross_platform_trends)
        print(f"✅ Generated {len(reports)} reports")
        
        for format_type, path in reports.items():
            if path and Path(path).exists():
                print(f"  📄 {format_type}: {path}")
        
        return True
    except Exception as e:
        print(f"❌ Report generator error: {e}")
        return False

def test_dashboard():
    """Test dashboard functionality."""
    print("\n🎯 Testing dashboard...")
    
    try:
        # Check if dashboard file exists
        dashboard_path = Path("dashboard/streamlit_app.py")
        if dashboard_path.exists():
            print("✅ Dashboard file exists")
            
            # Test importing dashboard
            import importlib.util
            spec = importlib.util.spec_from_file_location("streamlit_app", dashboard_path)
            dashboard_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(dashboard_module)
            
            print("✅ Dashboard module loaded successfully")
            return True
        else:
            print("❌ Dashboard file not found")
            return False
    except Exception as e:
        print(f"❌ Dashboard error: {e}")
        return False

def test_visualization():
    """Test visualization generation."""
    print("\n📈 Testing visualization...")
    
    try:
        # Test if visualization script exists and can be imported
        viz_path = Path("visualize_demo.py")
        if viz_path.exists():
            print("✅ Visualization script exists")
            
            # Test importing
            import importlib.util
            spec = importlib.util.spec_from_file_location("visualize_demo", viz_path)
            viz_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(viz_module)
            
            print("✅ Visualization module loaded successfully")
            return True
        else:
            print("❌ Visualization script not found")
            return False
    except Exception as e:
        print(f"❌ Visualization error: {e}")
        return False

def test_main_system():
    """Test main system integration."""
    print("\n🚀 Testing main system...")
    
    try:
        from main import TrendDetectionSystem
        
        # Initialize system
        system = TrendDetectionSystem()
        print("✅ System initialized successfully")
        
        # Test system stats
        stats = system.get_system_stats()
        print(f"✅ System stats retrieved: {stats['database']['total_trends']} trends in database")
        
        return True
    except Exception as e:
        print(f"❌ Main system error: {e}")
        return False

def test_demo():
    """Test demo functionality."""
    print("\n🎮 Testing demo...")
    
    try:
        # Test demo script
        demo_path = Path("demo.py")
        if demo_path.exists():
            print("✅ Demo script exists")
            
            # Test importing
            import importlib.util
            spec = importlib.util.spec_from_file_location("demo", demo_path)
            demo_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(demo_module)
            
            print("✅ Demo module loaded successfully")
            return True
        else:
            print("❌ Demo script not found")
            return False
    except Exception as e:
        print(f"❌ Demo error: {e}")
        return False

def run_complete_test():
    """Run all tests."""
    print("🧪 Starting Complete System Test")
    print("=" * 50)
    
    tests = [
        ("Module Imports", test_imports),
        ("Configuration", test_configuration),
        ("History Manager", test_history_manager),
        ("Emerging Trend Detector", test_emerging_trend_detector),
        ("Report Generator", test_report_generator),
        ("Dashboard", test_dashboard),
        ("Visualization", test_visualization),
        ("Main System", test_main_system),
        ("Demo", test_demo)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    # Print summary
    print("\n" + "=" * 50)
    print("📊 Test Results Summary")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    print(f"\n🎯 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! System is ready to use.")
        return True
    else:
        print("⚠️ Some tests failed. Please check the errors above.")
        return False

def main():
    """Main test function."""
    try:
        success = run_complete_test()
        return 0 if success else 1
    except KeyboardInterrupt:
        print("\n⚠️ Test interrupted by user")
        return 1
    except Exception as e:
        print(f"\n❌ Test failed with exception: {e}")
        return 1

if __name__ == "__main__":
    exit(main()) 