#!/usr/bin/env python3
"""
Etsy Trend Detection Agent - Main Entry Point

Automated trend detection system for Etsy sellers to identify trending product niches.
"""

import asyncio
import click
import logging
from datetime import datetime, timedelta
from pathlib import Path
import sys
import os

# Add project root to path
sys.path.append(str(Path(__file__).parent))

from data_ingestion.collector_manager import DataCollectorManager
from analysis.trend_analyzer import TrendAnalyzer
from reporting.report_generator import ReportGenerator
from utils.config import Config
from utils.database import Database
from utils.helpers import setup_logging, create_directories

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

@click.group()
@click.option('--config', default='config.yaml', help='Configuration file path')
@click.pass_context
def cli(ctx, config):
    """Etsy Trend Detection Agent - Identify trending product niches for your Etsy store."""
    ctx.ensure_object(dict)
    ctx.obj['config'] = Config(config)
    
    # Create necessary directories
    create_directories()

@cli.command()
@click.option('--mode', type=click.Choice(['daily', 'weekly']), default='daily', 
              help='Collection mode')
@click.option('--sources', default='all', 
              help='Comma-separated list of data sources (all, google, reddit, pinterest, etc.)')
@click.pass_context
def collect(ctx, mode, sources):
    """Collect trend data from various sources."""
    config = ctx.obj['config']
    
    logger.info(f"Starting data collection in {mode} mode")
    
    # Parse sources
    if sources == 'all':
        sources_to_collect = ['google_trends', 'reddit', 'pinterest', 'twitter', 'amazon', 'etsy']
    else:
        sources_to_collect = [s.strip() for s in sources.split(',')]
    
    async def run_collection():
        collector = DataCollectorManager(config)
        await collector.collect_all_data(sources_to_collect, mode)
    
    asyncio.run(run_collection())
    logger.info("Data collection completed")

@cli.command()
@click.option('--mode', type=click.Choice(['daily', 'weekly']), default='daily',
              help='Analysis mode')
@click.option('--output', default='data/processed/',
              help='Output directory for analysis results')
@click.pass_context
def analyze(ctx, mode, output):
    """Analyze collected data and identify trending opportunities."""
    config = ctx.obj['config']
    
    logger.info(f"Starting trend analysis in {mode} mode")
    
    async def run_analysis():
        analyzer = TrendAnalyzer(config)
        results = await analyzer.analyze_trends(mode)
        
        # Save results
        output_path = Path(output)
        output_path.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_file = output_path / f"trend_analysis_{mode}_{timestamp}.json"
        
        import json
        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        logger.info(f"Analysis results saved to {results_file}")
    
    asyncio.run(run_analysis())

@cli.command()
@click.option('--mode', type=click.Choice(['daily', 'weekly']), default='daily',
              help='Report mode')
@click.option('--format', type=click.Choice(['html', 'pdf', 'email']), default='html',
              help='Report format')
@click.option('--output', default='data/reports/',
              help='Output directory for reports')
@click.pass_context
def report(ctx, mode, format, output):
    """Generate trend reports."""
    config = ctx.obj['config']
    
    logger.info(f"Generating {mode} report in {format} format")
    
    async def run_report():
        generator = ReportGenerator(config)
        report_path = await generator.generate_report(mode, format, output)
        
        if report_path:
            logger.info(f"Report generated: {report_path}")
        else:
            logger.error("Failed to generate report")
    
    asyncio.run(run_report())

@cli.command()
@click.option('--port', default=8501, help='Dashboard port')
@click.pass_context
def dashboard(ctx, port):
    """Start the Streamlit dashboard."""
    import subprocess
    import sys
    
    dashboard_path = Path(__file__).parent / "dashboard" / "app.py"
    
    if not dashboard_path.exists():
        logger.error("Dashboard not found. Please ensure dashboard/app.py exists.")
        return
    
    logger.info(f"Starting dashboard on port {port}")
    
    try:
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", 
            str(dashboard_path), "--server.port", str(port)
        ])
    except KeyboardInterrupt:
        logger.info("Dashboard stopped")

@cli.command()
@click.option('--mode', type=click.Choice(['daily', 'weekly']), default='daily',
              help='Full pipeline mode')
@click.option('--sources', default='all', 
              help='Comma-separated list of data sources')
@click.option('--report-format', type=click.Choice(['html', 'pdf', 'email']), default='html',
              help='Report format')
@click.pass_context
def run(ctx, mode, sources, report_format):
    """Run the complete pipeline: collect -> analyze -> report."""
    config = ctx.obj['config']
    
    logger.info(f"Running complete pipeline in {mode} mode")
    
    async def run_pipeline():
        # Step 1: Collect data
        logger.info("Step 1: Collecting data...")
        collector = DataCollectorManager(config)
        
        if sources == 'all':
            sources_to_collect = ['google_trends', 'reddit', 'pinterest', 'twitter', 'amazon', 'etsy']
        else:
            sources_to_collect = [s.strip() for s in sources.split(',')]
        
        await collector.collect_all_data(sources_to_collect, mode)
        
        # Step 2: Analyze trends
        logger.info("Step 2: Analyzing trends...")
        analyzer = TrendAnalyzer(config)
        analysis_results = await analyzer.analyze_trends(mode)
        
        # Step 3: Generate report
        logger.info("Step 3: Generating report...")
        generator = ReportGenerator(config)
        report_path = await generator.generate_report(mode, report_format)
        
        if report_path:
            logger.info(f"Pipeline completed successfully! Report: {report_path}")
        else:
            logger.error("Pipeline completed with errors")
    
    asyncio.run(run_pipeline())

@cli.command()
@click.pass_context
def status(ctx):
    """Show system status and recent data."""
    config = ctx.obj['config']
    
    logger.info("Checking system status...")
    
    # Check data directories
    data_dirs = ['data/raw', 'data/processed', 'data/reports']
    for dir_path in data_dirs:
        path = Path(dir_path)
        if path.exists():
            files = list(path.glob('*'))
            logger.info(f"{dir_path}: {len(files)} files")
        else:
            logger.warning(f"{dir_path}: Directory not found")
    
    # Check database
    try:
        db = Database(config)
        recent_data = db.get_recent_data()
        logger.info(f"Database: {len(recent_data)} recent records")
    except Exception as e:
        logger.error(f"Database error: {e}")
    
    # Check configuration
    logger.info(f"Configuration loaded: {config.config_file}")
    logger.info(f"Data sources enabled: {config.get('data_sources', [])}")

@cli.command()
@click.option('--days', default=7, help='Number of days to clean')
@click.pass_context
def cleanup(ctx, days):
    """Clean up old data files."""
    config = ctx.obj['config']
    
    logger.info(f"Cleaning up data older than {days} days...")
    
    cutoff_date = datetime.now() - timedelta(days=days)
    
    data_dirs = ['data/raw', 'data/processed', 'data/reports']
    cleaned_files = 0
    
    for dir_path in data_dirs:
        path = Path(dir_path)
        if path.exists():
            for file_path in path.glob('*'):
                if file_path.is_file():
                    file_time = datetime.fromtimestamp(file_path.stat().st_mtime)
                    if file_time < cutoff_date:
                        file_path.unlink()
                        cleaned_files += 1
                        logger.info(f"Deleted: {file_path}")
    
    logger.info(f"Cleanup completed. Deleted {cleaned_files} files.")

if __name__ == '__main__':
    cli() 