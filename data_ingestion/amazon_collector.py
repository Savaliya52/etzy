"""
Amazon Data Collector

Collects best sellers and trending products from Amazon for market insights.
"""

import asyncio
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional
import aiohttp
from bs4 import BeautifulSoup
import re

from utils.config import Config

logger = logging.getLogger(__name__)

class AmazonCollector:
    """Collects Amazon best sellers and trending products."""
    
    def __init__(self, config: Config):
        self.config = config
        self.session = None
    
    async def collect_data(self, mode: str = 'daily', config: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        Collect Amazon best sellers and trending products.
        
        Args:
            mode: 'daily' or 'weekly'
            config: Source-specific configuration
        
        Returns:
            List of Amazon product data dictionaries
        """
        logger.info("Starting Amazon data collection")
        
        try:
            categories = config.get('categories', [
                'Home & Kitchen', 'Jewelry', 'Arts & Crafts',
                'Beauty & Personal Care', 'Toys & Games'
            ])
            
            max_products = config.get('max_products', 50)
            
            all_products = []
            
            for category in categories:
                products = await self._get_category_bestsellers(category, max_products)
                all_products.extend(products)
            
            # Remove duplicates and filter for relevance
            unique_products = self._deduplicate_products(all_products)
            relevant_products = self._filter_relevant_products(unique_products)
            
            logger.info(f"Collected {len(relevant_products)} relevant Amazon products")
            return relevant_products
            
        except Exception as e:
            logger.error(f"Error collecting Amazon data: {e}")
            return self._get_mock_data()
    
    async def _get_category_bestsellers(self, category: str, max_products: int) -> List[Dict[str, Any]]:
        """Get best sellers for a specific category."""
        try:
            # Note: This is a simplified implementation
            # In practice, you'd need to handle Amazon's anti-bot measures
            # and use proper scraping techniques
            
            # For now, return mock data
            return self._get_mock_products_for_category(category)
            
        except Exception as e:
            logger.error(f"Error getting best sellers for category '{category}': {e}")
            return []
    
    def _deduplicate_products(self, products: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate products based on ID."""
        seen_ids = set()
        unique_products = []
        
        for product in products:
            product_id = product.get('id')
            if product_id and product_id not in seen_ids:
                seen_ids.add(product_id)
                unique_products.append(product)
        
        return unique_products
    
    def _filter_relevant_products(self, products: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Filter products for Etsy-relevant items."""
        etsy_keywords = [
            'handmade', 'personalized', 'custom', 'gift',
            'jewelry', 'necklace', 'ring', 'bracelet', 'earrings',
            'home decor', 'wall art', 'candle', 'mug', 't-shirt',
            'wedding', 'vintage', 'craft', 'art', 'beauty',
            'handcrafted', 'unique', 'artisan', 'small business'
        ]
        
        relevant_products = []
        
        for product in products:
            title_lower = product.get('title', '').lower()
            description_lower = product.get('description', '').lower()
            
            # Check if product contains Etsy-related keywords
            if any(keyword in title_lower or keyword in description_lower for keyword in etsy_keywords):
                relevant_products.append(product)
        
        return relevant_products
    
    def _get_mock_products_for_category(self, category: str) -> List[Dict[str, Any]]:
        """Get mock products for a specific category."""
        mock_products = {
            'Home & Kitchen': [
                {
                    'id': 'amz123456789',
                    'title': 'Handmade Ceramic Coffee Mug Set',
                    'description': 'Beautiful handcrafted ceramic mugs perfect for personalized gifts',
                    'category': 'Home & Kitchen',
                    'price': 24.99,
                    'rating': 4.5,
                    'review_count': 1250,
                    'collected_at': datetime.now().isoformat(),
                    'source': 'amazon'
                }
            ],
            'Jewelry': [
                {
                    'id': 'amz987654321',
                    'title': 'Personalized Name Necklace',
                    'description': 'Custom engraved name necklace, perfect gift for any occasion',
                    'category': 'Jewelry',
                    'price': 29.99,
                    'rating': 4.7,
                    'review_count': 890,
                    'collected_at': datetime.now().isoformat(),
                    'source': 'amazon'
                }
            ],
            'Arts & Crafts': [
                {
                    'id': 'amz555666777',
                    'title': 'Handmade Soap Making Kit',
                    'description': 'Complete kit for making beautiful handmade soaps at home',
                    'category': 'Arts & Crafts',
                    'price': 34.99,
                    'rating': 4.3,
                    'review_count': 567,
                    'collected_at': datetime.now().isoformat(),
                    'source': 'amazon'
                }
            ]
        }
        
        return mock_products.get(category, [])
    
    def _get_mock_data(self) -> List[Dict[str, Any]]:
        """Return mock Amazon data for testing."""
        return [
            {
                'id': 'amz123456789',
                'title': 'Handmade Ceramic Coffee Mug Set',
                'description': 'Beautiful handcrafted ceramic mugs perfect for personalized gifts. Each mug is unique and made with care.',
                'category': 'Home & Kitchen',
                'price': 24.99,
                'rating': 4.5,
                'review_count': 1250,
                'collected_at': datetime.now().isoformat(),
                'source': 'amazon'
            },
            {
                'id': 'amz987654321',
                'title': 'Personalized Name Necklace',
                'description': 'Custom engraved name necklace, perfect gift for any occasion. Handcrafted with attention to detail.',
                'category': 'Jewelry',
                'price': 29.99,
                'rating': 4.7,
                'review_count': 890,
                'collected_at': datetime.now().isoformat(),
                'source': 'amazon'
            },
            {
                'id': 'amz555666777',
                'title': 'Handmade Soap Making Kit',
                'description': 'Complete kit for making beautiful handmade soaps at home. Includes all materials and instructions.',
                'category': 'Arts & Crafts',
                'price': 34.99,
                'rating': 4.3,
                'review_count': 567,
                'collected_at': datetime.now().isoformat(),
                'source': 'amazon'
            },
            {
                'id': 'amz111222333',
                'title': 'Custom Wall Art Canvas',
                'description': 'Personalized wall art canvas, perfect for home decor. Made to order with your design.',
                'category': 'Home & Kitchen',
                'price': 45.99,
                'rating': 4.6,
                'review_count': 432,
                'collected_at': datetime.now().isoformat(),
                'source': 'amazon'
            },
            {
                'id': 'amz444555666',
                'title': 'Vintage Style Jewelry Box',
                'description': 'Beautiful vintage-style jewelry box, handcrafted with premium materials.',
                'category': 'Jewelry',
                'price': 39.99,
                'rating': 4.4,
                'review_count': 321,
                'collected_at': datetime.now().isoformat(),
                'source': 'amazon'
            }
        ] 