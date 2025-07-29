"""
Category Classifier

Classifies trends and keywords into product categories.
"""

import logging
from typing import Dict, List, Optional
from utils.config import Config

logger = logging.getLogger(__name__)

class CategoryClassifier:
    """Classifies keywords and trends into product categories."""
    
    def __init__(self, config: Config):
        self.config = config
        self.categories = self.config.get_categories()
    
    def classify_keyword(self, keyword: str) -> Optional[str]:
        """
        Classify a keyword into a product category.
        
        Args:
            keyword: The keyword to classify
        
        Returns:
            Category name or None if no match
        """
        keyword_lower = keyword.lower()
        
        for category, keywords in self.categories.items():
            for category_keyword in keywords:
                if category_keyword.lower() in keyword_lower:
                    return category
        
        return None
    
    def get_category_keywords(self, category: str) -> List[str]:
        """Get keywords for a specific category."""
        return self.categories.get(category, [])
    
    def get_all_categories(self) -> List[str]:
        """Get all available categories."""
        return list(self.categories.keys())
    
    def classify_text(self, text: str) -> Dict[str, float]:
        """
        Classify text into multiple categories with confidence scores.
        
        Args:
            text: Text to classify
        
        Returns:
            Dictionary mapping categories to confidence scores
        """
        text_lower = text.lower()
        category_scores = {}
        
        for category, keywords in self.categories.items():
            score = 0
            for keyword in keywords:
                if keyword.lower() in text_lower:
                    score += 1
            
            if score > 0:
                category_scores[category] = score / len(keywords)
        
        return category_scores 