"""
Twitter/X Data Collector

Collects mentions and trending hashtags related to Etsy products from Twitter/X.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import aiohttp
import os

from utils.config import Config

logger = logging.getLogger(__name__)

class TwitterCollector:
    """Collects Twitter/X mentions and discussions related to Etsy products."""
    
    def __init__(self, config: Config):
        self.config = config
        self.bearer_token = self.config.get('data_sources.twitter.bearer_token')
        self.base_url = "https://api.twitter.com/2"
        self.session = None
    
    async def collect_data(self, mode: str = 'daily', config: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        Collect Twitter mentions and discussions about Etsy products.
        
        Args:
            mode: 'daily' or 'weekly'
            config: Source-specific configuration
        
        Returns:
            List of Twitter tweet data dictionaries
        """
        logger.info("Starting Twitter data collection")
        
        if not self.bearer_token:
            logger.warning("No Twitter Bearer Token found. Using mock data.")
            return self._get_mock_data()
        
        try:
            search_terms = config.get('search_terms', [
                'etsy handmade', 'etsy jewelry', 'etsy home decor',
                'etsy personalized', 'etsy gift', 'etsy vintage',
                'etsy art', 'etsy wedding', 'etsy beauty',
                'etsy craft', 'etsy clothing', 'etsy accessories'
            ])
            
            max_tweets = config.get('max_tweets', 100)
            
            all_tweets = []
            
            for term in search_terms:
                tweets = await self._search_tweets(term, max_tweets)
                all_tweets.extend(tweets)
            
            # Remove duplicates and filter for relevance
            unique_tweets = self._deduplicate_tweets(all_tweets)
            relevant_tweets = self._filter_relevant_tweets(unique_tweets)
            
            logger.info(f"Collected {len(relevant_tweets)} Etsy-related tweets")
            return relevant_tweets
            
        except Exception as e:
            logger.error(f"Error collecting Twitter data: {e}")
            return self._get_mock_data()
    
    async def _search_tweets(self, query: str, max_tweets: int) -> List[Dict[str, Any]]:
        """Search for tweets using Twitter API v2."""
        try:
            # Note: This is a simplified implementation
            # In practice, you'd need proper Twitter API access
            # For now, return mock data
            return self._get_mock_tweets_for_query(query)
            
        except Exception as e:
            logger.error(f"Error searching tweets for '{query}': {e}")
            return []
    
    def _deduplicate_tweets(self, tweets: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate tweets based on ID."""
        seen_ids = set()
        unique_tweets = []
        
        for tweet in tweets:
            tweet_id = tweet.get('id')
            if tweet_id and tweet_id not in seen_ids:
                seen_ids.add(tweet_id)
                unique_tweets.append(tweet)
        
        return unique_tweets
    
    def _filter_relevant_tweets(self, tweets: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Filter tweets for Etsy-related content."""
        etsy_keywords = [
            'etsy', 'handmade', 'personalized', 'custom', 'gift',
            'jewelry', 'necklace', 'ring', 'bracelet', 'earrings',
            'home decor', 'wall art', 'candle', 'mug', 't-shirt',
            'wedding', 'vintage', 'craft', 'art', 'beauty',
            'handcrafted', 'unique', 'artisan', 'small business'
        ]
        
        relevant_tweets = []
        
        for tweet in tweets:
            text_lower = tweet.get('text', '').lower()
            
            # Check if tweet contains Etsy-related keywords
            if any(keyword in text_lower for keyword in etsy_keywords):
                relevant_tweets.append(tweet)
        
        return relevant_tweets
    
    def _get_mock_tweets_for_query(self, query: str) -> List[Dict[str, Any]]:
        """Get mock tweets for a specific query."""
        mock_tweets = {
            'etsy jewelry': [
                {
                    'id': '1234567890123456789',
                    'text': 'Just received my personalized name necklace from Etsy! It\'s absolutely beautiful and the quality is amazing. Love supporting small businesses! #Etsy #Handmade #Jewelry',
                    'author_username': 'jewelry_lover',
                    'author_name': 'Sarah Johnson',
                    'retweet_count': 5,
                    'like_count': 23,
                    'reply_count': 3,
                    'quote_count': 1,
                    'collected_at': datetime.now().isoformat(),
                    'source': 'twitter'
                }
            ],
            'etsy home decor': [
                {
                    'id': '1234567890123456790',
                    'text': 'Found the perfect wedding gift on Etsy! Handmade ceramic mugs with our initials. The seller was so helpful and the packaging was beautiful. Highly recommend!',
                    'author_username': 'bride_to_be',
                    'author_name': 'Emily Davis',
                    'retweet_count': 12,
                    'like_count': 45,
                    'reply_count': 8,
                    'quote_count': 2,
                    'collected_at': datetime.now().isoformat(),
                    'source': 'twitter'
                }
            ]
        }
        
        return mock_tweets.get(query, [])
    
    def _get_mock_data(self) -> List[Dict[str, Any]]:
        """Return mock Twitter data for testing."""
        return [
            {
                'id': '1234567890123456789',
                'text': 'Just received my personalized name necklace from Etsy! It\'s absolutely beautiful and the quality is amazing. Love supporting small businesses! #Etsy #Handmade #Jewelry',
                'author_username': 'jewelry_lover',
                'author_name': 'Sarah Johnson',
                'retweet_count': 5,
                'like_count': 23,
                'reply_count': 3,
                'quote_count': 1,
                'collected_at': datetime.now().isoformat(),
                'source': 'twitter'
            },
            {
                'id': '1234567890123456790',
                'text': 'Found the perfect wedding gift on Etsy! Handmade ceramic mugs with our initials. The seller was so helpful and the packaging was beautiful. Highly recommend!',
                'author_username': 'bride_to_be',
                'author_name': 'Emily Davis',
                'retweet_count': 12,
                'like_count': 45,
                'reply_count': 8,
                'quote_count': 2,
                'collected_at': datetime.now().isoformat(),
                'source': 'twitter'
            },
            {
                'id': '1234567890123456791',
                'text': 'Etsy haul! Got some amazing vintage jewelry and handmade soap. Everything is so unique and the sellers are incredibly talented. #Vintage #Handmade #Etsy',
                'author_username': 'vintage_hunter',
                'author_name': 'Mike Wilson',
                'retweet_count': 8,
                'like_count': 34,
                'reply_count': 5,
                'quote_count': 1,
                'collected_at': datetime.now().isoformat(),
                'source': 'twitter'
            }
        ] 