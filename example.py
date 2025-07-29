#!/usr/bin/env python3
"""
Example usage of the Etsy Trend Detection system.

This script demonstrates how to use the system to collect data,
analyze trends, and generate reports.
"""

import asyncio
import logging
from datetime import datetime
from pathlib import Path

# Add project root to path
import sys
sys.path.append(str(Path(__file__).parent))

from utils.config import Config
from utils.helpers import setup_logging, create_directories
from data_ingestion.collector_manager import DataCollectorManager
from analysis.trend_analyzer import TrendAnalyzer

def main():
    """Main example function."""
    print("🎯 Etsy Trend Detection System - Example Usage")
    print("=" * 50)
    
    # Setup
    setup_logging()
    create_directories()
    
    # Initialize components
    config = Config()
    collector = DataCollectorManager(config)
    analyzer = TrendAnalyzer(config)
    
    print("\n📊 System Status:")
    print(f"Configuration loaded: {config.config_file}")
    print(f"Enabled data sources: {config.get_data_sources()}")
    
    # Example 1: Collect data
    print("\n📥 Example 1: Data Collection")
    print("-" * 30)
    
    async def collect_example():
        print("Collecting data from enabled sources...")
        
        sources = config.get_data_sources()
        if not sources:
            print("No enabled data sources found. Check configuration.")
            return
        
        print(f"Collecting from: {', '.join(sources)}")
        
        collected_data = await collector.collect_all_data(sources, 'daily')
        
        if collected_data:
            total_items = collected_data.get('metadata', {}).get('total_items', 0)
            print(f"✅ Data collection completed! Collected {total_items} items.")
            
            # Show breakdown by source
            for source, items in collected_data.items():
                if source != 'metadata' and isinstance(items, list):
                    print(f"  - {source}: {len(items)} items")
        else:
            print("❌ Data collection failed.")
    
    asyncio.run(collect_example())
    
    # Example 2: Analyze trends
    print("\n🔍 Example 2: Trend Analysis")
    print("-" * 30)
    
    async def analyze_example():
        print("Analyzing trends from collected data...")
        
        analysis_results = await analyzer.analyze_trends('daily')
        
        if analysis_results:
            print("✅ Analysis completed!")
            
            # Show summary
            summary = analysis_results.get('summary', {})
            print(f"  - Total trends analyzed: {summary.get('total_trends_analyzed', 0)}")
            print(f"  - High potential opportunities: {summary.get('high_potential_opportunities', 0)}")
            print(f"  - Top categories: {', '.join(summary.get('top_categories', []))}")
            
            # Show top trends
            trending_keywords = analysis_results.get('trending_keywords', [])
            if trending_keywords:
                print("\n🔥 Top 5 Trending Keywords:")
                for i, trend in enumerate(trending_keywords[:5], 1):
                    print(f"  {i}. {trend['keyword']} (Score: {trend['score']:.3f})")
            
            # Show opportunities
            opportunities = analysis_results.get('opportunities', [])
            if opportunities:
                print("\n💡 Top Business Opportunities:")
                for i, opp in enumerate(opportunities[:3], 1):
                    print(f"  {i}. {opp['keyword']} - {opp['market_potential']} potential")
        else:
            print("❌ Analysis failed.")
    
    asyncio.run(analyze_example())
    
    # Example 3: Database operations
    print("\n🗄️ Example 3: Database Operations")
    print("-" * 30)
    
    async def database_example():
        db = collector.db
        
        # Get database stats
        stats = db.get_database_stats()
        if stats:
            print("📊 Database Statistics:")
            print(f"  - Total records: {stats.get('total_records', 0)}")
            print(f"  - Recent records (24h): {stats.get('recent_records_24h', 0)}")
            
            source_counts = stats.get('source_counts', {})
            if source_counts:
                print("  - Records by source:")
                for source, count in source_counts.items():
                    print(f"    * {source}: {count}")
        
        # Get trending keywords
        trending_keywords = await db.get_trending_keywords(hours=24, limit=5)
        if trending_keywords:
            print("\n🔥 Trending Keywords (Last 24h):")
            for i, keyword_data in enumerate(trending_keywords, 1):
                print(f"  {i}. {keyword_data['keyword']} (Frequency: {keyword_data['frequency']})")
    
    asyncio.run(database_example())
    
    # Example 4: Configuration
    print("\n⚙️ Example 4: Configuration")
    print("-" * 30)
    
    print("Current configuration:")
    print(f"  - Data sources: {config.get_data_sources()}")
    print(f"  - Categories: {list(config.get_categories().keys())}")
    print(f"  - Scoring weights: {config.get_scoring_weights()}")
    
    # Example 5: System information
    print("\n💻 Example 5: System Information")
    print("-" * 30)
    
    from utils.helpers import get_system_info, check_disk_space
    
    system_info = get_system_info()
    print("System Information:")
    print(f"  - Platform: {system_info.get('platform', 'Unknown')}")
    print(f"  - Python version: {system_info.get('python_version', 'Unknown')}")
    print(f"  - CPU cores: {system_info.get('cpu_count', 'Unknown')}")
    
    disk_info = check_disk_space()
    if disk_info:
        print(f"  - Disk usage: {disk_info.get('percent', 0):.1f}%")
    
    print("\n✅ Example completed successfully!")
    print("\nNext steps:")
    print("1. Run 'python main.py collect' to collect data")
    print("2. Run 'python main.py analyze' to analyze trends")
    print("3. Run 'streamlit run dashboard/app.py' to view dashboard")
    print("4. Check the README.md for more detailed instructions")

if __name__ == "__main__":
    main() 