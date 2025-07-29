"""
Scoring Engine

Calculates trend scores based on frequency, recency, growth, and cross-platform presence.
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any
from utils.config import Config

logger = logging.getLogger(__name__)

class ScoringEngine:
    """Calculates trend scores using multiple factors."""
    
    def __init__(self, config: Config):
        self.config = config
        self.weights = self.config.get_scoring_weights()
    
    def calculate_score(self, keyword: str, frequency: int, data: List[Dict[str, Any]]) -> float:
        """
        Calculate a comprehensive score for a trend keyword.
        
        Args:
            keyword: The keyword to score
            frequency: Frequency count of the keyword
            data: Raw data for additional analysis
        
        Returns:
            Score between 0 and 1
        """
        try:
            # Calculate individual scores
            frequency_score = self._calculate_frequency_score(frequency)
            recency_score = self._calculate_recency_score(keyword, data)
            growth_score = self._calculate_growth_score(keyword, data)
            cross_platform_score = self._calculate_cross_platform_score(keyword, data)
            
            # Apply weights
            final_score = (
                frequency_score * self.weights.get('frequency_weight', 0.3) +
                recency_score * self.weights.get('recency_weight', 0.3) +
                growth_score * self.weights.get('growth_weight', 0.2) +
                cross_platform_score * self.weights.get('cross_platform_weight', 0.2)
            )
            
            return min(final_score, 1.0)  # Cap at 1.0
            
        except Exception as e:
            logger.error(f"Error calculating score for '{keyword}': {e}")
            return 0.0
    
    def _calculate_frequency_score(self, frequency: int) -> float:
        """Calculate frequency score (0-1)."""
        # Normalize frequency to 0-1 scale
        # Higher frequency = higher score
        if frequency <= 0:
            return 0.0
        elif frequency >= 100:
            return 1.0
        else:
            return frequency / 100.0
    
    def _calculate_recency_score(self, keyword: str, data: List[Dict[str, Any]]) -> float:
        """Calculate recency score based on how recent mentions are."""
        keyword_lower = keyword.lower()
        recent_mentions = 0
        total_mentions = 0
        
        for item in data:
            text = ''
            if 'title' in item:
                text += item['title'] + ' '
            if 'description' in item:
                text += item['description'] + ' '
            if 'text' in item:
                text += item['text'] + ' '
            
            if keyword_lower in text.lower():
                total_mentions += 1
                
                # Check if mention is recent (within last 24 hours)
                collected_at = item.get('collected_at')
                if collected_at:
                    try:
                        mention_time = datetime.fromisoformat(collected_at.replace('Z', '+00:00'))
                        if datetime.now(mention_time.tzinfo) - mention_time < timedelta(hours=24):
                            recent_mentions += 1
                    except:
                        pass
        
        if total_mentions == 0:
            return 0.0
        
        return recent_mentions / total_mentions
    
    def _calculate_growth_score(self, keyword: str, data: List[Dict[str, Any]]) -> float:
        """Calculate growth score based on trend direction."""
        # This is a simplified implementation
        # In practice, you'd compare current period vs previous period
        keyword_lower = keyword.lower()
        
        # Count mentions by time period
        recent_mentions = 0
        older_mentions = 0
        
        for item in data:
            text = ''
            if 'title' in item:
                text += item['title'] + ' '
            if 'description' in item:
                text += item['description'] + ' '
            if 'text' in item:
                text += item['text'] + ' '
            
            if keyword_lower in text.lower():
                collected_at = item.get('collected_at')
                if collected_at:
                    try:
                        mention_time = datetime.fromisoformat(collected_at.replace('Z', '+00:00'))
                        now = datetime.now(mention_time.tzinfo)
                        
                        if now - mention_time < timedelta(hours=12):
                            recent_mentions += 1
                        elif now - mention_time < timedelta(hours=24):
                            older_mentions += 1
                    except:
                        pass
        
        if older_mentions == 0:
            return 0.5  # Neutral score if no older data
        
        growth_rate = (recent_mentions - older_mentions) / max(older_mentions, 1)
        
        # Normalize to 0-1 scale
        if growth_rate >= 1.0:
            return 1.0
        elif growth_rate <= -0.5:
            return 0.0
        else:
            return (growth_rate + 0.5) / 1.5
    
    def _calculate_cross_platform_score(self, keyword: str, data: List[Dict[str, Any]]) -> float:
        """Calculate cross-platform score based on presence across multiple sources."""
        keyword_lower = keyword.lower()
        platforms = set()
        
        for item in data:
            text = ''
            if 'title' in item:
                text += item['title'] + ' '
            if 'description' in item:
                text += item['description'] + ' '
            if 'text' in item:
                text += item['text'] + ' '
            
            if keyword_lower in text.lower():
                source = item.get('source', 'unknown')
                platforms.add(source)
        
        # Score based on number of platforms
        # More platforms = higher score
        max_platforms = 6  # google_trends, reddit, pinterest, twitter, amazon, etsy
        return min(len(platforms) / max_platforms, 1.0)
    
    def get_score_breakdown(self, keyword: str, frequency: int, data: List[Dict[str, Any]]) -> Dict[str, float]:
        """Get detailed score breakdown for a keyword."""
        return {
            'frequency_score': self._calculate_frequency_score(frequency),
            'recency_score': self._calculate_recency_score(keyword, data),
            'growth_score': self._calculate_growth_score(keyword, data),
            'cross_platform_score': self._calculate_cross_platform_score(keyword, data),
            'final_score': self.calculate_score(keyword, frequency, data)
        } 