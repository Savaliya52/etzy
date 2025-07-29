"""
Reddit Data Collector

Collects discussions and mentions related to Etsy products from Reddit.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import praw
import os

from utils.config import Config

logger = logging.getLogger(__name__)

class RedditCollector:
    """Collects Reddit discussions and mentions related to Etsy products."""
    
    def __init__(self, config: Config):
        self.config = config
        self.reddit = None
        self._initialize_reddit()
    
    def _initialize_reddit(self):
        """Initialize Reddit API client."""
        try:
            client_id = self.config.get('data_sources.reddit.client_id')
            client_secret = self.config.get('data_sources.reddit.client_secret')
            
            if client_id and client_secret:
                self.reddit = praw.Reddit(
                    client_id=client_id,
                    client_secret=client_secret,
                    user_agent='EtsyTrendDetector/1.0'
                )
                logger.info("Reddit API initialized successfully")
            else:
                logger.warning("Reddit API credentials not found. Using mock data.")
                self.reddit = None
                
        except Exception as e:
            logger.error(f"Error initializing Reddit API: {e}")
            self.reddit = None
    
    async def collect_data(self, mode: str = 'daily', config: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        Collect Reddit posts and comments mentioning Etsy products.
        
        Args:
            mode: 'daily' or 'weekly'
            config: Source-specific configuration
        
        Returns:
            List of Reddit post data dictionaries
        """
        logger.info("Starting Reddit data collection")
        
        if not self.reddit:
            logger.warning("Reddit API not available. Using mock data.")
            return self._get_mock_data()
        
        try:
            subreddits = config.get('subreddits', [
                'Etsy', 'EtsySellers', 'gifts', 'jewelry', 
                'homeimprovement', 'weddingplanning', 'crafts'
            ])
            
            max_posts = config.get('max_posts', 50)
            time_filter = config.get('time_filter', 'week')
            
            all_posts = []
            
            for subreddit_name in subreddits:
                posts = await self._get_subreddit_posts(subreddit_name, max_posts, time_filter)
                all_posts.extend(posts)
            
            # Filter for Etsy-related content
            etsy_posts = self._filter_etsy_content(all_posts)
            
            logger.info(f"Collected {len(etsy_posts)} Etsy-related Reddit posts")
            return etsy_posts
            
        except Exception as e:
            logger.error(f"Error collecting Reddit data: {e}")
            return self._get_mock_data()
    
    async def _get_subreddit_posts(self, subreddit_name: str, max_posts: int, time_filter: str) -> List[Dict[str, Any]]:
        """Get posts from a specific subreddit."""
        try:
            subreddit = self.reddit.subreddit(subreddit_name)
            
            # Get hot posts
            posts = []
            for post in subreddit.hot(limit=max_posts):
                post_data = {
                    'id': post.id,
                    'title': post.title,
                    'text': post.selftext,
                    'subreddit': post.subreddit.display_name,
                    'score': post.score,
                    'upvote_ratio': post.upvote_ratio,
                    'num_comments': post.num_comments,
                    'created_utc': post.created_utc,
                    'url': post.url,
                    'permalink': f"https://reddit.com{post.permalink}",
                    'author': str(post.author) if post.author else '[deleted]',
                    'collected_at': datetime.now().isoformat(),
                    'source': 'reddit'
                }
                posts.append(post_data)
            
            return posts
            
        except Exception as e:
            logger.error(f"Error getting posts from r/{subreddit_name}: {e}")
            return []
    
    def _filter_etsy_content(self, posts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Filter posts for Etsy-related content."""
        etsy_keywords = [
            'etsy', 'handmade', 'personalized', 'custom', 'gift',
            'jewelry', 'necklace', 'ring', 'bracelet', 'earrings',
            'home decor', 'wall art', 'candle', 'mug', 't-shirt',
            'wedding', 'vintage', 'craft', 'art', 'beauty',
            'handcrafted', 'unique', 'artisan', 'small business'
        ]
        
        etsy_posts = []
        
        for post in posts:
            title_lower = post.get('title', '').lower()
            text_lower = post.get('text', '').lower()
            
            # Check if post contains Etsy-related keywords
            if any(keyword in title_lower or keyword in text_lower for keyword in etsy_keywords):
                etsy_posts.append(post)
        
        return etsy_posts
    
    async def get_trending_keywords(self) -> List[str]:
        """Extract trending keywords from Reddit posts."""
        try:
            # Get recent posts from Etsy-related subreddits
            subreddits = ['Etsy', 'gifts', 'jewelry', 'crafts']
            all_keywords = {}
            
            for subreddit_name in subreddits:
                posts = await self._get_subreddit_posts(subreddit_name, 25, 'week')
                
                for post in posts:
                    text = f"{post.get('title', '')} {post.get('text', '')}"
                    words = text.lower().split()
                    
                    for word in words:
                        if len(word) > 3 and word.isalpha():
                            all_keywords[word] = all_keywords.get(word, 0) + 1
            
            # Sort by frequency and return top keywords
            sorted_keywords = sorted(all_keywords.items(), key=lambda x: x[1], reverse=True)
            return [keyword for keyword, count in sorted_keywords[:20]]
            
        except Exception as e:
            logger.error(f"Error getting trending keywords: {e}")
            return []
    
    def _get_mock_data(self) -> List[Dict[str, Any]]:
        """Return mock Reddit data for testing."""
        return [
            {
                'id': 'abc123',
                'title': 'Just bought this amazing personalized necklace from Etsy!',
                'text': 'I found this beautiful custom name necklace on Etsy and I love it! The seller was so helpful and the quality is amazing. Highly recommend checking out their shop.',
                'subreddit': 'jewelry',
                'score': 45,
                'upvote_ratio': 0.95,
                'num_comments': 12,
                'created_utc': datetime.now().timestamp(),
                'url': 'https://example.com/necklace',
                'permalink': 'https://reddit.com/r/jewelry/comments/abc123',
                'author': 'jewelry_lover',
                'collected_at': datetime.now().isoformat(),
                'source': 'reddit'
            },
            {
                'id': 'def456',
                'title': 'Etsy home decor haul - everything is handmade!',
                'text': 'I went on a shopping spree on Etsy for home decor items. Everything is handmade and unique. The wall art and candles are absolutely stunning.',
                'subreddit': 'homeimprovement',
                'score': 78,
                'upvote_ratio': 0.92,
                'num_comments': 23,
                'created_utc': datetime.now().timestamp(),
                'url': 'https://example.com/decor',
                'permalink': 'https://reddit.com/r/homeimprovement/comments/def456',
                'author': 'decor_enthusiast',
                'collected_at': datetime.now().isoformat(),
                'source': 'reddit'
            },
            {
                'id': 'ghi789',
                'title': 'Best Etsy shops for wedding gifts?',
                'text': 'Looking for recommendations for Etsy shops that sell great wedding gifts. I want something personalized and unique for the couple.',
                'subreddit': 'weddingplanning',
                'score': 156,
                'upvote_ratio': 0.88,
                'num_comments': 34,
                'created_utc': datetime.now().timestamp(),
                'url': 'https://example.com/wedding',
                'permalink': 'https://reddit.com/r/weddingplanning/comments/ghi789',
                'author': 'bride_to_be',
                'collected_at': datetime.now().isoformat(),
                'source': 'reddit'
            },
            {
                'id': 'jkl012',
                'title': 'Handmade soap from Etsy - my new favorite!',
                'text': 'I ordered some handmade soap from an Etsy seller and it\'s incredible. The scents are amazing and my skin feels so much better. Will definitely order again.',
                'subreddit': 'beauty',
                'score': 89,
                'upvote_ratio': 0.94,
                'num_comments': 18,
                'created_utc': datetime.now().timestamp(),
                'url': 'https://example.com/soap',
                'permalink': 'https://reddit.com/r/beauty/comments/jkl012',
                'author': 'skincare_lover',
                'collected_at': datetime.now().isoformat(),
                'source': 'reddit'
            },
            {
                'id': 'mno345',
                'title': 'Vintage finds on Etsy - treasure hunting success!',
                'text': 'Found some amazing vintage items on Etsy today. The seller had a great collection of retro jewelry and accessories. Love supporting small businesses!',
                'subreddit': 'vintage',
                'score': 67,
                'upvote_ratio': 0.91,
                'num_comments': 15,
                'created_utc': datetime.now().timestamp(),
                'url': 'https://example.com/vintage',
                'permalink': 'https://reddit.com/r/vintage/comments/mno345',
                'author': 'vintage_hunter',
                'collected_at': datetime.now().isoformat(),
                'source': 'reddit'
            }
        ] 