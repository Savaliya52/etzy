#!/usr/bin/env python3
"""
Etsy Trend Detection System - Main Application

Comprehensive trend detection system that identifies emerging trends
across multiple platforms and provides business intelligence for Etsy sellers.
"""

import argparse
import asyncio
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional
import json

# Import system modules
from data_ingestion.collector_manager import CollectorManager
from analysis.emerging_trend_detector import EmergingTrendDetector
from analysis.trend_analyzer import TrendAnalyzer
from analysis.scoring_engine import ScoringEngine
from storage.history_manager import HistoryManager
from reporting.report_generator import ReportGenerator
from utils.config import Config
from utils.helpers import setup_logging, create_directories

class TrendDetectionSystem:
    """Main system class that orchestrates all components."""
    
    def __init__(self, config_path: str = "config.json"):
        """
        Initialize the trend detection system.
        
        Args:
            config_path: Path to configuration file
        """
        self.config = Config(config_path)
        self.history_manager = HistoryManager()
        self.emerging_detector = EmergingTrendDetector()
        self.trend_analyzer = TrendAnalyzer()
        self.scoring_engine = ScoringEngine()
        self.report_generator = ReportGenerator()
        self.collector_manager = CollectorManager(self.config)
        
        # Setup logging
        setup_logging()
        self.logger = logging.getLogger(__name__)
        
        # Create necessary directories
        create_directories()
        
    async def collect_data(self, sources: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """
        Collect data from all configured sources.
        
        Args:
            sources: List of specific sources to collect from (None for all)
            
        Returns:
            List of collected trend data
        """
        self.logger.info("Starting data collection...")
        
        try:
            # Collect data from all sources
            collected_data = await self.collector_manager.collect_all_data(sources)
            
            # Store in history
            today = datetime.now().strftime('%Y-%m-%d')
            self.history_manager.store_daily_trends(collected_data, today)
            
            self.logger.info(f"Collected {len(collected_data)} data points from {len(collected_data)} sources")
            return collected_data
            
        except Exception as e:
            self.logger.error(f"Error during data collection: {e}")
            return []
            
    def analyze_trends(self, trends_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze trends and detect emerging patterns.
        
        Args:
            trends_data: Raw trends data
            
        Returns:
            Dictionary containing analysis results
        """
        self.logger.info("Starting trend analysis...")
        
        try:
            # Get historical data for comparison
            end_date = datetime.now().strftime('%Y-%m-%d')
            start_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
            historical_data = self.history_manager.get_trends_by_date_range(start_date, end_date)
            
            # Detect emerging trends
            emerging_trends = self.emerging_detector.detect_emerging_trends(
                trends_data, historical_data
            )
            
            # Calculate multi-source confidence
            trends_with_confidence = self.emerging_detector.calculate_multi_source_confidence(
                trends_data
            )
            
            # Detect cross-platform trends
            cross_platform_trends = self.emerging_detector.detect_cross_platform_trends(
                trends_with_confidence
            )
            
            # Filter high-quality trends
            high_quality_trends = self.emerging_detector.filter_high_quality_trends(
                emerging_trends
            )
            
            # Generate business suggestions
            product_suggestions = self.emerging_detector.suggest_etsy_products(
                high_quality_trends
            )
            
            analysis_results = {
                'total_trends': len(trends_data),
                'emerging_trends': emerging_trends,
                'cross_platform_trends': cross_platform_trends,
                'high_quality_trends': high_quality_trends,
                'product_suggestions': product_suggestions,
                'analysis_date': datetime.now().isoformat()
            }
            
            self.logger.info(f"Analysis complete: {len(emerging_trends)} emerging trends detected")
            return analysis_results
            
        except Exception as e:
            self.logger.error(f"Error during trend analysis: {e}")
            return {}
            
    def generate_reports(self, analysis_results: Dict[str, Any]) -> Dict[str, str]:
        """
        Generate comprehensive reports.
        
        Args:
            analysis_results: Results from trend analysis
            
        Returns:
            Dictionary with paths to generated reports
        """
        self.logger.info("Generating reports...")
        
        try:
            # Generate daily report
            daily_reports = self.report_generator.generate_daily_report(
                analysis_results.get('total_trends', []),
                analysis_results.get('emerging_trends', []),
                analysis_results.get('cross_platform_trends', [])
            )
            
            # Generate weekly report if enough data
            weekly_reports = {}
            end_date = datetime.now().strftime('%Y-%m-%d')
            start_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
            weekly_data = self.history_manager.get_trends_by_date_range(start_date, end_date)
            
            if weekly_data:
                weekly_reports = self.report_generator.generate_weekly_report(
                    weekly_data, (start_date, end_date)
                )
                
            all_reports = {**daily_reports, **weekly_reports}
            
            self.logger.info(f"Generated {len(all_reports)} reports")
            return all_reports
            
        except Exception as e:
            self.logger.error(f"Error generating reports: {e}")
            return {}
            
    def cleanup_old_data(self):
        """Clean up old data based on retention policy."""
        self.logger.info("Cleaning up old data...")
        self.history_manager.cleanup_old_data()
        
    def get_system_stats(self) -> Dict[str, Any]:
        """Get system statistics."""
        db_stats = self.history_manager.get_database_stats()
        
        # Get recent trends
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
        recent_trends = self.history_manager.get_trends_by_date_range(start_date, end_date)
        
        # Get emerging trends
        emerging_trends = self.history_manager.get_emerging_trends()
        
        # Get multi-source trends
        multi_source_trends = self.history_manager.get_multi_source_trends()
        
        stats = {
            'database': db_stats,
            'recent_trends': len(recent_trends),
            'emerging_trends': len(emerging_trends),
            'multi_source_trends': len(multi_source_trends),
            'last_updated': datetime.now().isoformat()
        }
        
        return stats
        
    async def run_full_cycle(self) -> Dict[str, Any]:
        """
        Run a complete data collection and analysis cycle.
        
        Returns:
            Dictionary with cycle results
        """
        self.logger.info("Starting full trend detection cycle...")
        
        # Step 1: Collect data
        collected_data = await self.collect_data()
        
        if not collected_data:
            self.logger.warning("No data collected, skipping analysis")
            return {}
            
        # Step 2: Analyze trends
        analysis_results = self.analyze_trends(collected_data)
        
        if not analysis_results:
            self.logger.warning("No analysis results generated")
            return {}
            
        # Step 3: Generate reports
        reports = self.generate_reports(analysis_results)
        
        # Step 4: Cleanup old data
        self.cleanup_old_data()
        
        # Step 5: Get system stats
        stats = self.get_system_stats()
        
        cycle_results = {
            'collected_data_count': len(collected_data),
            'emerging_trends_count': len(analysis_results.get('emerging_trends', [])),
            'reports_generated': len(reports),
            'system_stats': stats,
            'cycle_completed_at': datetime.now().isoformat()
        }
        
        self.logger.info(f"Full cycle completed: {cycle_results}")
        return cycle_results
        
    async def run_demo(self):
        """Run a demo with sample data."""
        self.logger.info("Running demo mode...")
        
        # Create sample data
        sample_data = [
            {
                'keyword': 'personalized jewelry',
                'platform': 'google_trends',
                'category': 'jewelry',
                'popularity_score': 85,
                'timestamp': datetime.now().isoformat()
            },
            {
                'keyword': 'handmade candles',
                'platform': 'pinterest',
                'category': 'home_decor',
                'popularity_score': 72,
                'timestamp': datetime.now().isoformat()
            },
            {
                'keyword': 'custom wall art',
                'platform': 'reddit',
                'category': 'home_decor',
                'popularity_score': 68,
                'timestamp': datetime.now().isoformat()
            }
        ]
        
        # Analyze sample data
        analysis_results = self.analyze_trends(sample_data)
        
        # Generate reports
        reports = self.generate_reports(analysis_results)
        
        self.logger.info(f"Demo completed: {len(analysis_results.get('emerging_trends', []))} emerging trends detected")
        return analysis_results, reports

def main():
    """Main entry point for the application."""
    parser = argparse.ArgumentParser(description="Etsy Trend Detection System")
    parser.add_argument("command", choices=[
        "collect", "analyze", "report", "demo", "stats", "full-cycle", "dashboard"
    ], help="Command to execute")
    
    parser.add_argument("--sources", nargs="+", help="Specific data sources to use")
    parser.add_argument("--config", default="config.json", help="Configuration file path")
    parser.add_argument("--output", help="Output directory for reports")
    parser.add_argument("--demo", action="store_true", help="Run in demo mode")
    
    args = parser.parse_args()
    
    # Initialize system
    system = TrendDetectionSystem(args.config)
    
    try:
        if args.command == "collect":
            # Collect data only
            asyncio.run(system.collect_data(args.sources))
            print("✅ Data collection completed")
            
        elif args.command == "analyze":
            # Analyze existing data
            end_date = datetime.now().strftime('%Y-%m-%d')
            trends_data = system.history_manager.get_trends_by_date(end_date)
            if trends_data:
                results = system.analyze_trends(trends_data)
                print(f"✅ Analysis completed: {len(results.get('emerging_trends', []))} emerging trends")
            else:
                print("⚠️ No data found for today. Run 'collect' first.")
                
        elif args.command == "report":
            # Generate reports from existing data
            end_date = datetime.now().strftime('%Y-%m-%d')
            trends_data = system.history_manager.get_trends_by_date(end_date)
            if trends_data:
                analysis_results = system.analyze_trends(trends_data)
                reports = system.generate_reports(analysis_results)
                print(f"✅ Reports generated: {list(reports.keys())}")
            else:
                print("⚠️ No data found for today. Run 'collect' first.")
                
        elif args.command == "demo":
            # Run demo
            analysis_results, reports = asyncio.run(system.run_demo())
            print(f"✅ Demo completed: {len(analysis_results.get('emerging_trends', []))} emerging trends")
            
        elif args.command == "stats":
            # Show system statistics
            stats = system.get_system_stats()
            print("📊 System Statistics:")
            print(f"  Total trends in database: {stats['database']['total_trends']}")
            print(f"  Recent trends (7 days): {stats['recent_trends']}")
            print(f"  Emerging trends: {stats['emerging_trends']}")
            print(f"  Multi-source trends: {stats['multi_source_trends']}")
            print(f"  Database size: {stats['database']['database_size']} bytes")
            
        elif args.command == "full-cycle":
            # Run complete cycle
            results = asyncio.run(system.run_full_cycle())
            print(f"✅ Full cycle completed:")
            print(f"  Collected: {results['collected_data_count']} data points")
            print(f"  Emerging trends: {results['emerging_trends_count']}")
            print(f"  Reports generated: {results['reports_generated']}")
            
        elif args.command == "dashboard":
            # Launch Streamlit dashboard
            import subprocess
            import sys
            
            dashboard_path = Path("dashboard/streamlit_app.py")
            if dashboard_path.exists():
                print("🚀 Launching Streamlit dashboard...")
                subprocess.run([sys.executable, "-m", "streamlit", "run", str(dashboard_path)])
            else:
                print("❌ Dashboard file not found")
                
    except KeyboardInterrupt:
        print("\n⚠️ Operation cancelled by user")
    except Exception as e:
        print(f"❌ Error: {e}")
        system.logger.error(f"Application error: {e}")

if __name__ == "__main__":
    main() 