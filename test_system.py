#!/usr/bin/env python3
"""
Test script for the Etsy Trend Detection system.

This script tests all major components to ensure they work correctly.
"""

import asyncio
import logging
import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent))

from utils.config import Config
from utils.helpers import setup_logging, create_directories
from data_ingestion.collector_manager import DataCollectorManager
from analysis.trend_analyzer import TrendAnalyzer
from analysis.category_classifier import CategoryClassifier
from analysis.scoring_engine import ScoringEngine

def test_config():
    """Test configuration loading."""
    print("Testing configuration...")
    
    try:
        config = Config()
        print("✅ Configuration loaded successfully")
        
        # Test basic config methods
        sources = config.get_data_sources()
        categories = config.get_categories()
        weights = config.get_scoring_weights()
        
        print(f"  - Data sources: {sources}")
        print(f"  - Categories: {list(categories.keys())}")
        print(f"  - Scoring weights: {weights}")
        
        return True
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return False

def test_collectors():
    """Test data collectors."""
    print("\nTesting data collectors...")
    
    try:
        config = Config()
        collector = DataCollectorManager(config)
        
        # Test collector status
        status = collector.get_collector_status()
        print("✅ Collector manager initialized")
        
        for source, info in status.items():
            status_text = "✅" if info['enabled'] else "❌"
            print(f"  {status_text} {source}: {'Enabled' if info['enabled'] else 'Disabled'}")
        
        return True
    except Exception as e:
        print(f"❌ Collector test failed: {e}")
        return False

async def test_data_collection():
    """Test data collection."""
    print("\nTesting data collection...")
    
    try:
        config = Config()
        collector = DataCollectorManager(config)
        
        # Test with enabled sources
        sources = config.get_data_sources()
        if not sources:
            print("⚠️ No enabled data sources found")
            return True
        
        print(f"Collecting from: {', '.join(sources)}")
        
        # Run collection
        collected_data = await collector.collect_all_data(sources[:2], 'daily')  # Test with first 2 sources
        
        if collected_data:
            total_items = collected_data.get('metadata', {}).get('total_items', 0)
            print(f"✅ Data collection successful! Collected {total_items} items")
            
            # Show breakdown
            for source, items in collected_data.items():
                if source != 'metadata' and isinstance(items, list):
                    print(f"  - {source}: {len(items)} items")
            
            return True
        else:
            print("❌ Data collection failed")
            return False
            
    except Exception as e:
        print(f"❌ Data collection test failed: {e}")
        return False

def test_analysis():
    """Test analysis components."""
    print("\nTesting analysis components...")
    
    try:
        config = Config()
        
        # Test category classifier
        classifier = CategoryClassifier(config)
        test_keywords = ['jewelry', 'necklace', 'home decor', 'candle', 'random']
        
        print("Testing category classifier...")
        for keyword in test_keywords:
            category = classifier.classify_keyword(keyword)
            print(f"  - '{keyword}' -> {category or 'No category'}")
        
        # Test scoring engine
        scoring_engine = ScoringEngine(config)
        test_data = [
            {'title': 'handmade jewelry', 'source': 'google_trends', 'collected_at': '2024-01-01T10:00:00'},
            {'title': 'personalized necklace', 'source': 'reddit', 'collected_at': '2024-01-01T11:00:00'}
        ]
        
        print("Testing scoring engine...")
        score = scoring_engine.calculate_score('jewelry', 5, test_data)
        print(f"  - Score for 'jewelry': {score:.3f}")
        
        # Test trend analyzer
        analyzer = TrendAnalyzer(config)
        print("✅ Analysis components initialized")
        
        return True
    except Exception as e:
        print(f"❌ Analysis test failed: {e}")
        return False

async def test_full_pipeline():
    """Test the full pipeline."""
    print("\nTesting full pipeline...")
    
    try:
        config = Config()
        collector = DataCollectorManager(config)
        analyzer = TrendAnalyzer(config)
        
        # Step 1: Collect data
        print("Step 1: Collecting data...")
        sources = config.get_data_sources()[:2]  # Use first 2 sources for testing
        collected_data = await collector.collect_all_data(sources, 'daily')
        
        if not collected_data:
            print("⚠️ No data collected, skipping analysis")
            return True
        
        # Step 2: Analyze trends
        print("Step 2: Analyzing trends...")
        analysis_results = await analyzer.analyze_trends('daily')
        
        if analysis_results:
            print("✅ Full pipeline test successful!")
            
            # Show results summary
            summary = analysis_results.get('summary', {})
            print(f"  - Trends analyzed: {summary.get('total_trends_analyzed', 0)}")
            print(f"  - Opportunities found: {summary.get('high_potential_opportunities', 0)}")
            
            return True
        else:
            print("❌ Analysis step failed")
            return False
            
    except Exception as e:
        print(f"❌ Full pipeline test failed: {e}")
        return False

def test_utilities():
    """Test utility functions."""
    print("\nTesting utilities...")
    
    try:
        from utils.helpers import clean_text, extract_keywords, calculate_similarity
        
        # Test text cleaning
        test_text = "  Handmade   jewelry  with  personalized  design!  "
        cleaned = clean_text(test_text)
        print(f"✅ Text cleaning: '{test_text}' -> '{cleaned}'")
        
        # Test keyword extraction
        keywords = extract_keywords(test_text)
        print(f"✅ Keyword extraction: {keywords}")
        
        # Test similarity
        text1 = "handmade jewelry personalized"
        text2 = "jewelry handmade custom"
        similarity = calculate_similarity(text1, text2)
        print(f"✅ Similarity calculation: {similarity:.3f}")
        
        return True
    except Exception as e:
        print(f"❌ Utilities test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("🧪 Etsy Trend Detection System - Test Suite")
    print("=" * 50)
    
    # Setup
    setup_logging()
    create_directories()
    
    # Run tests
    tests = [
        ("Configuration", test_config),
        ("Data Collectors", test_collectors),
        ("Analysis Components", test_analysis),
        ("Utilities", test_utilities),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results.append((test_name, False))
    
    # Async tests
    async def run_async_tests():
        async_tests = [
            ("Data Collection", test_data_collection),
            ("Full Pipeline", test_full_pipeline),
        ]
        
        for test_name, test_func in async_tests:
            try:
                result = await test_func()
                results.append((test_name, result))
            except Exception as e:
                print(f"❌ {test_name} test crashed: {e}")
                results.append((test_name, False))
    
    asyncio.run(run_async_tests())
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Results Summary:")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! System is ready to use.")
    else:
        print("⚠️ Some tests failed. Check the output above for details.")
    
    print("\nNext steps:")
    print("1. Run 'python example.py' to see the system in action")
    print("2. Run 'python main.py collect' to collect real data")
    print("3. Run 'streamlit run dashboard/app.py' to view the dashboard")

if __name__ == "__main__":
    main() 