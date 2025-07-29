#!/usr/bin/env python3
"""
Emerging Trend Detector Module

Detects emerging trends by analyzing growth patterns and delta changes
across multiple time periods and data sources.
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional, Any
import logging
from collections import defaultdict

logger = logging.getLogger(__name__)

class EmergingTrendDetector:
    """Detects emerging trends using delta analysis and multi-source validation."""
    
    def __init__(self, 
                 min_emerging_score: float = 0.75,
                 min_growth_rate: float = 0.2,
                 min_sources: int = 2,
                 lookback_days: int = 7):
        """
        Initialize the emerging trend detector.
        
        Args:
            min_emerging_score: Minimum score to consider a trend emerging
            min_growth_rate: Minimum growth rate threshold
            min_sources: Minimum number of sources required for validation
            lookback_days: Number of days to look back for trend analysis
        """
        self.min_emerging_score = min_emerging_score
        self.min_growth_rate = min_growth_rate
        self.min_sources = min_sources
        self.lookback_days = lookback_days
        
    def calculate_emerging_score(self, 
                               current_popularity: float,
                               previous_popularity: float,
                               days_between: int = 1) -> float:
        """
        Calculate emerging score using the specified formula.
        
        Formula: emerging_score = (current - previous) / (previous + 1) * log(current + 1)
        
        Args:
            current_popularity: Current popularity score
            previous_popularity: Previous popularity score
            days_between: Number of days between measurements
            
        Returns:
            Emerging score (0-1 scale)
        """
        if previous_popularity <= 0:
            # Handle new trends
            if current_popularity > 0:
                return min(0.8, current_popularity / 100)  # Cap at 0.8 for new trends
            else:
                return 0.0
                
        # Calculate growth rate
        growth_rate = (current_popularity - previous_popularity) / (previous_popularity + 1)
        
        # Apply logarithmic scaling
        log_factor = np.log(current_popularity + 1)
        
        # Calculate emerging score
        emerging_score = growth_rate * log_factor
        
        # Normalize to 0-1 range and apply minimum threshold
        emerging_score = max(0, min(1, emerging_score))
        
        return emerging_score
        
    def detect_emerging_trends(self, 
                              trends_data: List[Dict[str, Any]],
                              historical_data: Optional[List[Dict[str, Any]]] = None) -> List[Dict[str, Any]]:
        """
        Detect emerging trends from current and historical data.
        
        Args:
            trends_data: Current trends data
            historical_data: Historical trends data for comparison
            
        Returns:
            List of emerging trends with scores
        """
        if not trends_data:
            return []
            
        # Group trends by keyword and platform
        current_trends = defaultdict(dict)
        for trend in trends_data:
            key = (trend['keyword'], trend['platform'])
            current_trends[key] = trend
            
        # Group historical data
        historical_trends = defaultdict(dict)
        if historical_data:
            for trend in historical_data:
                key = (trend['keyword'], trend['platform'])
                historical_trends[key] = trend
                
        emerging_trends = []
        
        for (keyword, platform), current_trend in current_trends.items():
            # Find corresponding historical data
            historical_trend = historical_trends.get((keyword, platform))
            
            if historical_trend:
                # Calculate emerging score
                emerging_score = self.calculate_emerging_score(
                    current_trend.get('popularity_score', 0),
                    historical_trend.get('popularity_score', 0)
                )
                
                # Check if trend is emerging
                if emerging_score >= self.min_emerging_score:
                    current_trend['emerging_score'] = emerging_score
                    current_trend['growth_rate'] = (
                        current_trend.get('popularity_score', 0) - 
                        historical_trend.get('popularity_score', 0)
                    ) / max(historical_trend.get('popularity_score', 1), 1)
                    
                    emerging_trends.append(current_trend)
            else:
                # New trend - check if it appears in multiple sources
                if self._is_new_trend_emerging(keyword, current_trends):
                    current_trend['emerging_score'] = 0.7  # Default score for new trends
                    current_trend['growth_rate'] = float('inf')  # Infinite growth for new trends
                    emerging_trends.append(current_trend)
                    
        # Sort by emerging score
        emerging_trends.sort(key=lambda x: x.get('emerging_score', 0), reverse=True)
        
        return emerging_trends
        
    def _is_new_trend_emerging(self, keyword: str, current_trends: Dict) -> bool:
        """
        Check if a new trend is emerging across multiple sources.
        
        Args:
            keyword: Trend keyword
            current_trends: Current trends data
            
        Returns:
            True if trend appears in multiple sources
        """
        sources = set()
        for (k, platform) in current_trends.keys():
            if k == keyword:
                sources.add(platform)
                
        return len(sources) >= self.min_sources
        
    def calculate_multi_source_confidence(self, 
                                       trends_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Calculate confidence scores based on multi-source appearance.
        
        Args:
            trends_data: List of trend dictionaries
            
        Returns:
            List of trends with updated confidence scores
        """
        # Group by keyword
        keyword_sources = defaultdict(set)
        keyword_trends = defaultdict(list)
        
        for trend in trends_data:
            keyword = trend['keyword']
            platform = trend['platform']
            keyword_sources[keyword].add(platform)
            keyword_trends[keyword].append(trend)
            
        # Calculate confidence scores
        for keyword, trends in keyword_trends.items():
            source_count = len(keyword_sources[keyword])
            
            # Base confidence on number of sources
            base_confidence = min(1.0, source_count / 4.0)  # Max 4 sources
            
            # Boost confidence for high emerging scores
            max_emerging = max(t.get('emerging_score', 0) for t in trends)
            emerging_boost = max_emerging * 0.3
            
            # Boost confidence for high popularity
            max_popularity = max(t.get('popularity_score', 0) for t in trends)
            popularity_boost = min(0.2, max_popularity / 100)
            
            final_confidence = min(1.0, base_confidence + emerging_boost + popularity_boost)
            
            # Update all trends for this keyword
            for trend in trends:
                trend['confidence_score'] = final_confidence
                trend['source_count'] = source_count
                trend['sources'] = list(keyword_sources[keyword])
                
        return trends_data
        
    def detect_cross_platform_trends(self, 
                                   trends_data: List[Dict[str, Any]],
                                   min_sources: int = 2) -> List[Dict[str, Any]]:
        """
        Detect trends that appear across multiple platforms.
        
        Args:
            trends_data: List of trend dictionaries
            min_sources: Minimum number of sources required
            
        Returns:
            List of cross-platform trends
        """
        # Group by keyword
        keyword_data = defaultdict(list)
        for trend in trends_data:
            keyword_data[trend['keyword']].append(trend)
            
        cross_platform_trends = []
        
        for keyword, trends in keyword_data.items():
            if len(trends) >= min_sources:
                # Calculate aggregate metrics
                avg_popularity = np.mean([t.get('popularity_score', 0) for t in trends])
                avg_emerging = np.mean([t.get('emerging_score', 0) for t in trends])
                max_emerging = max([t.get('emerging_score', 0) for t in trends])
                
                # Create aggregated trend
                aggregated_trend = {
                    'keyword': keyword,
                    'platforms': [t['platform'] for t in trends],
                    'source_count': len(trends),
                    'avg_popularity': avg_popularity,
                    'avg_emerging': avg_emerging,
                    'max_emerging': max_emerging,
                    'confidence_score': min(1.0, len(trends) / 4.0 + max_emerging * 0.3),
                    'trends': trends
                }
                
                cross_platform_trends.append(aggregated_trend)
                
        # Sort by confidence and emerging score
        cross_platform_trends.sort(
            key=lambda x: (x['confidence_score'], x['max_emerging']), 
            reverse=True
        )
        
        return cross_platform_trends
        
    def filter_high_quality_trends(self, 
                                  trends_data: List[Dict[str, Any]],
                                  min_emerging_score: float = None,
                                  min_confidence: float = 0.6) -> List[Dict[str, Any]]:
        """
        Filter trends based on quality thresholds.
        
        Args:
            trends_data: List of trend dictionaries
            min_emerging_score: Minimum emerging score (uses instance default if None)
            min_confidence: Minimum confidence score
            
        Returns:
            List of high-quality trends
        """
        if min_emerging_score is None:
            min_emerging_score = self.min_emerging_score
            
        filtered_trends = []
        
        for trend in trends_data:
            emerging_score = trend.get('emerging_score', 0)
            confidence_score = trend.get('confidence_score', 0)
            
            if emerging_score >= min_emerging_score and confidence_score >= min_confidence:
                filtered_trends.append(trend)
                
        return filtered_trends
        
    def generate_trend_report(self, 
                            emerging_trends: List[Dict[str, Any]],
                            cross_platform_trends: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate a comprehensive trend report.
        
        Args:
            emerging_trends: List of emerging trends
            cross_platform_trends: List of cross-platform trends
            
        Returns:
            Dictionary containing trend report
        """
        report = {
            'generated_at': datetime.now().isoformat(),
            'summary': {
                'total_emerging_trends': len(emerging_trends),
                'cross_platform_trends': len(cross_platform_trends),
                'high_confidence_trends': len([t for t in emerging_trends if t.get('confidence_score', 0) > 0.8]),
                'avg_emerging_score': np.mean([t.get('emerging_score', 0) for t in emerging_trends]) if emerging_trends else 0
            },
            'top_emerging_trends': emerging_trends[:10],
            'cross_platform_trends': cross_platform_trends[:10],
            'platform_breakdown': self._get_platform_breakdown(emerging_trends),
            'category_breakdown': self._get_category_breakdown(emerging_trends)
        }
        
        return report
        
    def _get_platform_breakdown(self, trends: List[Dict[str, Any]]) -> Dict[str, int]:
        """Get breakdown of trends by platform."""
        platform_counts = defaultdict(int)
        for trend in trends:
            platform_counts[trend.get('platform', 'unknown')] += 1
        return dict(platform_counts)
        
    def _get_category_breakdown(self, trends: List[Dict[str, Any]]) -> Dict[str, int]:
        """Get breakdown of trends by category."""
        category_counts = defaultdict(int)
        for trend in trends:
            category = trend.get('category', 'uncategorized')
            category_counts[category] += 1
        return dict(category_counts)
        
    def suggest_etsy_products(self, 
                             emerging_trends: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Generate Etsy product suggestions based on emerging trends.
        
        Args:
            emerging_trends: List of emerging trends
            
        Returns:
            List of product suggestions
        """
        suggestions = []
        
        for trend in emerging_trends[:20]:  # Top 20 trends
            keyword = trend['keyword']
            category = trend.get('category', 'general')
            emerging_score = trend.get('emerging_score', 0)
            confidence_score = trend.get('confidence_score', 0)
            
            # Generate product title
            title = f"Personalized {keyword.title()} - Handmade Custom Design"
            
            # Generate tags
            tags = [
                keyword.lower(),
                'handmade',
                'personalized',
                'custom',
                category.lower(),
                'etsy',
                'trending'
            ]
            
            # Add category-specific tags
            if category == 'jewelry':
                tags.extend(['necklace', 'bracelet', 'ring', 'earrings'])
            elif category == 'home_decor':
                tags.extend(['wall art', 'home decor', 'interior design'])
            elif category == 'gifts':
                tags.extend(['gift', 'present', 'special occasion'])
                
            suggestion = {
                'keyword': keyword,
                'emerging_score': emerging_score,
                'confidence_score': confidence_score,
                'category': category,
                'suggested_title': title,
                'suggested_tags': tags[:10],  # Limit to 10 tags
                'market_potential': self._assess_market_potential(emerging_score, confidence_score)
            }
            
            suggestions.append(suggestion)
            
        return suggestions
        
    def _assess_market_potential(self, emerging_score: float, confidence_score: float) -> str:
        """Assess market potential based on scores."""
        combined_score = (emerging_score + confidence_score) / 2
        
        if combined_score > 0.8:
            return "High"
        elif combined_score > 0.6:
            return "Medium"
        else:
            return "Low" 