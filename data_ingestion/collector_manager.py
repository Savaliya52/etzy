"""
Data Collector Manager - Coordinates data collection from multiple sources.
"""

import asyncio
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path
import json

from .google_trends_collector import GoogleTrendsCollector
from .reddit_collector import RedditCollector
from .pinterest_collector import PinterestCollector
from .twitter_collector import TwitterCollector
from .amazon_collector import AmazonCollector
from .etsy_collector import EtsyCollector
from utils.config import Config
from utils.database import Database

logger = logging.getLogger(__name__)

class DataCollectorManager:
    """Manages data collection from multiple sources."""
    
    def __init__(self, config: Config):
        self.config = config
        self.db = Database(config)
        
        # Initialize collectors
        self.collectors = {
            'google_trends': GoogleTrendsCollector(config),
            'reddit': RedditCollector(config),
            'pinterest': PinterestCollector(config),
            'twitter': TwitterCollector(config),
            'amazon': AmazonCollector(config),
            'etsy': EtsyCollector(config)
        }
    
    async def collect_all_data(self, sources: List[str], mode: str = 'daily') -> Dict[str, Any]:
        """
        Collect data from all specified sources.
        
        Args:
            sources: List of source names to collect from
            mode: 'daily' or 'weekly'
        
        Returns:
            Dictionary containing collected data from all sources
        """
        logger.info(f"Starting data collection for sources: {sources}")
        
        # Filter enabled sources
        enabled_sources = [s for s in sources if self.config.is_source_enabled(s)]
        
        if not enabled_sources:
            logger.warning("No enabled data sources found")
            return {}
        
        # Collect data from each source
        collection_tasks = []
        for source in enabled_sources:
            if source in self.collectors:
                task = self._collect_from_source(source, mode)
                collection_tasks.append(task)
        
        # Run all collection tasks concurrently
        results = await asyncio.gather(*collection_tasks, return_exceptions=True)
        
        # Process results
        collected_data = {}
        for i, source in enumerate(enabled_sources):
            result = results[i]
            if isinstance(result, Exception):
                logger.error(f"Error collecting from {source}: {result}")
                collected_data[source] = []
            else:
                collected_data[source] = result
                logger.info(f"Collected {len(result)} items from {source}")
        
        # Add metadata
        collected_data['metadata'] = {
            'collection_time': datetime.now().isoformat(),
            'mode': mode,
            'sources': enabled_sources,
            'total_items': sum(len(data) for data in collected_data.values() if isinstance(data, list))
        }
        
        # Save to database
        await self._save_to_database(collected_data)
        
        # Save raw data to file
        self._save_raw_data(collected_data, mode)
        
        logger.info(f"Data collection completed. Total items: {collected_data['metadata']['total_items']}")
        
        return collected_data
    
    async def _collect_from_source(self, source: str, mode: str) -> List[Dict[str, Any]]:
        """Collect data from a specific source."""
        try:
            collector = self.collectors[source]
            source_config = self.config.get_source_config(source)
            
            logger.info(f"Collecting data from {source}")
            
            if hasattr(collector, 'collect_data'):
                data = await collector.collect_data(mode, source_config)
            else:
                logger.warning(f"Collector {source} does not have collect_data method")
                data = []
            
            return data
            
        except Exception as e:
            logger.error(f"Error collecting from {source}: {e}")
            return []
    
    async def _save_to_database(self, data: Dict[str, Any]):
        """Save collected data to database."""
        try:
            for source, items in data.items():
                if source == 'metadata':
                    continue
                
                if isinstance(items, list):
                    for item in items:
                        item['source'] = source
                        item['collected_at'] = datetime.now().isoformat()
                        await self.db.insert_trend_data(item)
            
            logger.info("Data saved to database")
            
        except Exception as e:
            logger.error(f"Error saving to database: {e}")
    
    def _save_raw_data(self, data: Dict[str, Any], mode: str):
        """Save raw data to file."""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"data/raw/collected_data_{mode}_{timestamp}.json"
            
            filepath = Path(filename)
            filepath.parent.mkdir(parents=True, exist_ok=True)
            
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2, default=str)
            
            logger.info(f"Raw data saved to {filepath}")
            
        except Exception as e:
            logger.error(f"Error saving raw data: {e}")
    
    async def get_recent_data(self, hours: int = 24) -> Dict[str, Any]:
        """Get recent data from database."""
        try:
            recent_data = await self.db.get_recent_data(hours)
            return recent_data
        except Exception as e:
            logger.error(f"Error getting recent data: {e}")
            return {}
    
    async def cleanup_old_data(self, days: int = 7):
        """Clean up old data from database."""
        try:
            await self.db.cleanup_old_data(days)
            logger.info(f"Cleaned up data older than {days} days")
        except Exception as e:
            logger.error(f"Error cleaning up old data: {e}")
    
    def get_collector_status(self) -> Dict[str, bool]:
        """Get status of all collectors."""
        status = {}
        for source, collector in self.collectors.items():
            status[source] = {
                'enabled': self.config.is_source_enabled(source),
                'available': hasattr(collector, 'collect_data')
            }
        return status 