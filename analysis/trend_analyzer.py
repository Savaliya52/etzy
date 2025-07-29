"""
Trend Analyzer

Analyzes collected data to identify trending products and opportunities.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import pandas as pd
import numpy as np
from collections import Counter

from utils.config import Config
from utils.database import Database
from .category_classifier import CategoryClassifier
from .scoring_engine import ScoringEngine

logger = logging.getLogger(__name__)

class TrendAnalyzer:
    """Analyzes trends from collected data and identifies opportunities."""
    
    def __init__(self, config: Config):
        self.config = config
        self.db = Database(config)
        self.category_classifier = CategoryClassifier(config)
        self.scoring_engine = ScoringEngine(config)
    
    async def analyze_trends(self, mode: str = 'daily') -> Dict[str, Any]:
        """
        Analyze trends from collected data.
        
        Args:
            mode: 'daily' or 'weekly'
        
        Returns:
            Dictionary containing trend analysis results
        """
        logger.info(f"Starting trend analysis in {mode} mode")
        
        try:
            # Get recent data from database
            hours_back = 24 if mode == 'daily' else 168  # 1 day vs 1 week
            recent_data = await self.db.get_recent_data(hours_back)
            
            if not recent_data:
                logger.warning("No recent data found for analysis")
                return self._get_empty_analysis()
            
            # Extract keywords and phrases
            keywords = self._extract_keywords(recent_data)
            
            # Classify trends by category
            categorized_trends = self._categorize_trends(keywords)
            
            # Score trends
            scored_trends = self._score_trends(keywords, recent_data)
            
            # Identify opportunities
            opportunities = self._identify_opportunities(scored_trends, recent_data)
            
            # Generate analysis results
            analysis_results = {
                'mode': mode,
                'analysis_timestamp': datetime.now().isoformat(),
                'data_sources_analyzed': self._get_data_sources(recent_data),
                'total_items_analyzed': len(recent_data),
                'trending_keywords': scored_trends[:20],
                'categorized_trends': categorized_trends,
                'opportunities': opportunities,
                'summary': self._generate_summary(scored_trends, opportunities)
            }
            
            logger.info(f"Trend analysis completed. Found {len(scored_trends)} trending keywords")
            return analysis_results
            
        except Exception as e:
            logger.error(f"Error analyzing trends: {e}")
            return self._get_empty_analysis()
    
    def _extract_keywords(self, data: List[Dict[str, Any]]) -> List[str]:
        """Extract keywords from collected data."""
        keywords = []
        
        for item in data:
            # Extract from title
            if 'title' in item:
                keywords.extend(self._tokenize_text(item['title']))
            
            # Extract from description
            if 'description' in item:
                keywords.extend(self._tokenize_text(item['description']))
            
            # Extract from text content
            if 'text' in item:
                keywords.extend(self._tokenize_text(item['text']))
            
            # Extract from search terms
            if 'search_term' in item:
                keywords.extend(self._tokenize_text(item['search_term']))
        
        return keywords
    
    def _tokenize_text(self, text: str) -> List[str]:
        """Tokenize text into keywords."""
        if not text:
            return []
        
        # Convert to lowercase and split
        words = text.lower().split()
        
        # Filter out common stop words and short words
        stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
            'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could',
            'should', 'may', 'might', 'can', 'this', 'that', 'these', 'those',
            'i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her',
            'us', 'them', 'my', 'your', 'his', 'her', 'its', 'our', 'their'
        }
        
        # Filter words
        filtered_words = []
        for word in words:
            # Remove punctuation and clean
            clean_word = ''.join(c for c in word if c.isalnum())
            if (len(clean_word) > 2 and 
                clean_word not in stop_words and 
                not clean_word.isdigit()):
                filtered_words.append(clean_word)
        
        return filtered_words
    
    def _categorize_trends(self, keywords: List[str]) -> Dict[str, List[str]]:
        """Categorize trends by product category."""
        categories = self.config.get_categories()
        categorized = {category: [] for category in categories.keys()}
        
        # Count keyword frequency
        keyword_counts = Counter(keywords)
        
        # Categorize keywords
        for keyword, count in keyword_counts.most_common(100):
            category = self.category_classifier.classify_keyword(keyword)
            if category:
                categorized[category].append(keyword)
        
        return categorized
    
    def _score_trends(self, keywords: List[str], data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Score trends using the scoring engine."""
        keyword_counts = Counter(keywords)
        
        scored_trends = []
        for keyword, count in keyword_counts.most_common(50):
            score = self.scoring_engine.calculate_score(keyword, count, data)
            
            trend_data = {
                'keyword': keyword,
                'frequency': count,
                'score': score,
                'category': self.category_classifier.classify_keyword(keyword),
                'sources': self._get_keyword_sources(keyword, data)
            }
            scored_trends.append(trend_data)
        
        # Sort by score
        scored_trends.sort(key=lambda x: x['score'], reverse=True)
        
        return scored_trends
    
    def _identify_opportunities(self, scored_trends: List[Dict[str, Any]], data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Identify business opportunities from trends."""
        opportunities = []
        
        for trend in scored_trends[:20]:  # Top 20 trends
            if trend['score'] > self.config.get('analysis.min_score', 0.1):
                opportunity = {
                    'keyword': trend['keyword'],
                    'category': trend['category'],
                    'score': trend['score'],
                    'frequency': trend['frequency'],
                    'sources': trend['sources'],
                    'suggested_tags': self._generate_suggested_tags(trend['keyword']),
                    'market_potential': self._assess_market_potential(trend, data),
                    'competition_level': self._assess_competition(trend, data)
                }
                opportunities.append(opportunity)
        
        return opportunities
    
    def _get_keyword_sources(self, keyword: str, data: List[Dict[str, Any]]) -> List[str]:
        """Get sources where a keyword appears."""
        sources = set()
        
        for item in data:
            text = ''
            if 'title' in item:
                text += item['title'] + ' '
            if 'description' in item:
                text += item['description'] + ' '
            if 'text' in item:
                text += item['text'] + ' '
            
            if keyword.lower() in text.lower():
                sources.add(item.get('source', 'unknown'))
        
        return list(sources)
    
    def _generate_suggested_tags(self, keyword: str) -> List[str]:
        """Generate suggested Etsy tags for a keyword."""
        # This is a simplified implementation
        # In practice, you'd use NLP or AI to generate better tags
        base_tags = [keyword]
        
        # Add related tags based on keyword
        if 'jewelry' in keyword or 'necklace' in keyword:
            base_tags.extend(['handmade', 'personalized', 'gift'])
        elif 'home' in keyword or 'decor' in keyword:
            base_tags.extend(['handmade', 'unique', 'artisan'])
        elif 'gift' in keyword:
            base_tags.extend(['personalized', 'custom', 'unique'])
        
        return base_tags[:5]  # Return top 5 tags
    
    def _assess_market_potential(self, trend: Dict[str, Any], data: List[Dict[str, Any]]) -> str:
        """Assess market potential for a trend."""
        score = trend['score']
        frequency = trend['frequency']
        
        if score > 0.8 and frequency > 50:
            return 'High'
        elif score > 0.5 and frequency > 20:
            return 'Medium'
        else:
            return 'Low'
    
    def _assess_competition(self, trend: Dict[str, Any], data: List[Dict[str, Any]]) -> str:
        """Assess competition level for a trend."""
        # This is a simplified implementation
        # In practice, you'd analyze actual competition data
        frequency = trend['frequency']
        
        if frequency > 100:
            return 'High'
        elif frequency > 50:
            return 'Medium'
        else:
            return 'Low'
    
    def _get_data_sources(self, data: List[Dict[str, Any]]) -> List[str]:
        """Get list of data sources from the data."""
        sources = set()
        for item in data:
            if 'source' in item:
                sources.add(item['source'])
        return list(sources)
    
    def _generate_summary(self, scored_trends: List[Dict[str, Any]], opportunities: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate analysis summary."""
        return {
            'total_trends_analyzed': len(scored_trends),
            'high_potential_opportunities': len([o for o in opportunities if o['market_potential'] == 'High']),
            'top_categories': self._get_top_categories(scored_trends),
            'trending_sources': self._get_trending_sources(scored_trends)
        }
    
    def _get_top_categories(self, scored_trends: List[Dict[str, Any]]) -> List[str]:
        """Get top trending categories."""
        category_scores = {}
        for trend in scored_trends:
            category = trend.get('category')
            if category:
                category_scores[category] = category_scores.get(category, 0) + trend['score']
        
        sorted_categories = sorted(category_scores.items(), key=lambda x: x[1], reverse=True)
        return [category for category, score in sorted_categories[:5]]
    
    def _get_trending_sources(self, scored_trends: List[Dict[str, Any]]) -> List[str]:
        """Get top trending data sources."""
        source_scores = {}
        for trend in scored_trends:
            for source in trend.get('sources', []):
                source_scores[source] = source_scores.get(source, 0) + trend['score']
        
        sorted_sources = sorted(source_scores.items(), key=lambda x: x[1], reverse=True)
        return [source for source, score in sorted_sources[:5]]
    
    def _get_empty_analysis(self) -> Dict[str, Any]:
        """Return empty analysis structure."""
        return {
            'mode': 'daily',
            'analysis_timestamp': datetime.now().isoformat(),
            'data_sources_analyzed': [],
            'total_items_analyzed': 0,
            'trending_keywords': [],
            'categorized_trends': {},
            'opportunities': [],
            'summary': {
                'total_trends_analyzed': 0,
                'high_potential_opportunities': 0,
                'top_categories': [],
                'trending_sources': []
            }
        } 