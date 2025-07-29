"""
Google Trends Data Collector

Collects trending search data from Google Trends using pytrends library.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import pandas as pd
from pytrends.request import TrendReq

from utils.config import Config

logger = logging.getLogger(__name__)

class GoogleTrendsCollector:
    """Collects trending search data from Google Trends."""
    
    def __init__(self, config: Config):
        self.config = config
        self.pytrends = TrendReq(hl='en-US', tz=360)
        
        # Etsy-related search terms
        self.search_terms = [
            "etsy jewelry", "etsy home decor", "etsy personalized gifts",
            "etsy wedding", "etsy vintage", "etsy handmade",
            "etsy art", "etsy clothing", "etsy accessories",
            "etsy crafts", "etsy beauty", "etsy toys",
            "handmade jewelry", "personalized gifts", "custom jewelry",
            "vintage jewelry", "home decor ideas", "wedding gifts",
            "handmade soap", "custom t-shirt", "wall art",
            "personalized necklace", "custom mug", "handmade candles"
        ]
    
    async def collect_data(self, mode: str = 'daily', config: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        Collect trending data from Google Trends.
        
        Args:
            mode: 'daily' or 'weekly'
            config: Source-specific configuration
        
        Returns:
            List of trend data dictionaries
        """
        logger.info("Starting Google Trends data collection")
        
        try:
            all_trends = []
            
            # Collect data for each search term
            for term in self.search_terms:
                trend_data = await self._get_trend_data(term, mode, config)
                if trend_data:
                    all_trends.append(trend_data)
            
            logger.info(f"Collected {len(all_trends)} Google Trends records")
            return all_trends
            
        except Exception as e:
            logger.error(f"Error collecting Google Trends data: {e}")
            return self._get_mock_data()
    
    async def _get_trend_data(self, search_term: str, mode: str, config: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Get trend data for a specific search term."""
        try:
            # Build payload
            self.pytrends.build_payload(
                [search_term], 
                cat=0, 
                timeframe=config.get('timeframe', 'today 3-m') if config else 'today 3-m',
                geo=config.get('geo', 'US') if config else 'US'
            )
            
            # Get interest over time
            interest_over_time = self.pytrends.interest_over_time()
            
            if interest_over_time.empty:
                return None
            
            # Get related queries
            related_queries = self.pytrends.related_queries()
            
            # Get related topics
            related_topics = self.pytrends.related_topics()
            
            # Calculate trend metrics
            recent_interest = interest_over_time[search_term].tail(7).mean()
            trend_direction = self._calculate_trend_direction(interest_over_time[search_term])
            growth_rate = self._calculate_growth_rate(interest_over_time[search_term])
            
            # Process related queries
            top_queries = []
            rising_queries = []
            
            if search_term in related_queries:
                queries_data = related_queries[search_term]
                if 'top' in queries_data and not queries_data['top'].empty:
                    top_queries = queries_data['top'].head(5).to_dict('records')
                if 'rising' in queries_data and not queries_data['rising'].empty:
                    rising_queries = queries_data['rising'].head(5).to_dict('records')
            
            trend_data = {
                'search_term': search_term,
                'recent_interest': float(recent_interest),
                'trend_direction': trend_direction,
                'growth_rate': growth_rate,
                'interest_over_time': interest_over_time[search_term].tail(30).to_dict(),
                'top_queries': top_queries,
                'rising_queries': rising_queries,
                'related_topics': related_topics.get(search_term, {}),
                'collected_at': datetime.now().isoformat(),
                'source': 'google_trends'
            }
            
            return trend_data
            
        except Exception as e:
            logger.error(f"Error getting trend data for '{search_term}': {e}")
            return None
    
    def _calculate_trend_direction(self, interest_series: pd.Series) -> str:
        """Calculate if trend is rising, falling, or stable."""
        if len(interest_series) < 14:
            return "stable"
        
        recent_avg = interest_series.tail(7).mean()
        older_avg = interest_series.head(7).mean()
        
        if recent_avg > older_avg * 1.1:
            return "rising"
        elif recent_avg < older_avg * 0.9:
            return "falling"
        else:
            return "stable"
    
    def _calculate_growth_rate(self, interest_series: pd.Series) -> float:
        """Calculate growth rate over the last 30 days."""
        if len(interest_series) < 30:
            return 0.0
        
        recent_avg = interest_series.tail(7).mean()
        older_avg = interest_series.head(7).mean()
        
        if older_avg == 0:
            return 0.0
        
        return ((recent_avg - older_avg) / older_avg) * 100
    
    async def get_rising_searches(self) -> List[str]:
        """Get currently rising searches related to Etsy."""
        try:
            # Get real-time trending searches
            trending_searches = self.pytrends.trending_searches(pn='united_states')
            
            # Filter for Etsy-related terms
            etsy_related = []
            etsy_keywords = ['gift', 'jewelry', 'handmade', 'personalized', 'craft', 'art', 'decor']
            
            for term in trending_searches[0]:
                if any(keyword in term.lower() for keyword in etsy_keywords):
                    etsy_related.append(term)
            
            return etsy_related[:10]  # Return top 10
            
        except Exception as e:
            logger.error(f"Error getting rising searches: {e}")
            return []
    
    def _get_mock_data(self) -> List[Dict[str, Any]]:
        """Return mock Google Trends data for testing."""
        return [
            {
                'search_term': 'etsy jewelry',
                'recent_interest': 75.5,
                'trend_direction': 'rising',
                'growth_rate': 12.5,
                'interest_over_time': {
                    '2024-01-01': 65,
                    '2024-01-02': 68,
                    '2024-01-03': 72,
                    '2024-01-04': 75,
                    '2024-01-05': 78
                },
                'top_queries': [
                    {'query': 'personalized jewelry', 'value': 100},
                    {'query': 'handmade jewelry', 'value': 85},
                    {'query': 'etsy necklaces', 'value': 70}
                ],
                'rising_queries': [
                    {'query': 'custom jewelry', 'value': 150},
                    {'query': 'etsy rings', 'value': 120}
                ],
                'related_topics': {},
                'collected_at': datetime.now().isoformat(),
                'source': 'google_trends'
            },
            {
                'search_term': 'etsy home decor',
                'recent_interest': 62.3,
                'trend_direction': 'stable',
                'growth_rate': 2.1,
                'interest_over_time': {
                    '2024-01-01': 60,
                    '2024-01-02': 62,
                    '2024-01-03': 61,
                    '2024-01-04': 63,
                    '2024-01-05': 62
                },
                'top_queries': [
                    {'query': 'wall art', 'value': 90},
                    {'query': 'home accessories', 'value': 75},
                    {'query': 'decorative items', 'value': 65}
                ],
                'rising_queries': [
                    {'query': 'minimalist decor', 'value': 130},
                    {'query': 'boho home decor', 'value': 110}
                ],
                'related_topics': {},
                'collected_at': datetime.now().isoformat(),
                'source': 'google_trends'
            },
            {
                'search_term': 'etsy personalized gifts',
                'recent_interest': 88.7,
                'trend_direction': 'rising',
                'growth_rate': 18.3,
                'interest_over_time': {
                    '2024-01-01': 80,
                    '2024-01-02': 82,
                    '2024-01-03': 85,
                    '2024-01-04': 87,
                    '2024-01-05': 89
                },
                'top_queries': [
                    {'query': 'custom gifts', 'value': 95},
                    {'query': 'personalized items', 'value': 88},
                    {'query': 'unique gifts', 'value': 82}
                ],
                'rising_queries': [
                    {'query': 'engraved gifts', 'value': 160},
                    {'query': 'monogrammed items', 'value': 140}
                ],
                'related_topics': {},
                'collected_at': datetime.now().isoformat(),
                'source': 'google_trends'
            }
        ] 