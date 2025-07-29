"""
Simple Configuration Module

A simplified configuration system that doesn't require external dependencies.
"""

import os
import json
from pathlib import Path
from typing import Dict, Any, List

class SimpleConfig:
    """Simple configuration manager without external dependencies."""
    
    def __init__(self, config_file: str = 'config.json'):
        self.config_file = config_file
        self.config = self._load_config()
        self._load_env_vars()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from JSON file."""
        config_path = Path(self.config_file)
        
        if not config_path.exists():
            # Create default configuration
            self._create_default_config(config_path)
        
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading config: {e}")
            return self._get_default_config()
    
    def _create_default_config(self, config_path: Path):
        """Create default configuration file."""
        default_config = self._get_default_config()
        
        config_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(config_path, 'w') as f:
            json.dump(default_config, f, indent=2)
        
        print(f"Created default configuration file: {config_path}")
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration."""
        return {
            'data_sources': {
                'google_trends': {
                    'enabled': True,
                    'max_results': 100,
                    'timeframe': 'today 3-m',
                    'geo': 'US'
                },
                'reddit': {
                    'enabled': True,
                    'subreddits': [
                        'Etsy', 'EtsySellers', 'gifts', 'jewelry', 
                        'homeimprovement', 'weddingplanning', 'crafts'
                    ],
                    'max_posts': 50,
                    'time_filter': 'week'
                },
                'pinterest': {
                    'enabled': True,
                    'max_pins': 100,
                    'search_terms': [
                        'etsy jewelry', 'etsy home decor', 'etsy gifts',
                        'handmade', 'personalized gifts', 'vintage'
                    ]
                },
                'twitter': {
                    'enabled': False,
                    'max_tweets': 100,
                    'search_terms': [
                        'etsy', 'handmade', 'personalized gifts'
                    ]
                },
                'amazon': {
                    'enabled': True,
                    'categories': [
                        'Home & Kitchen', 'Jewelry', 'Arts & Crafts',
                        'Beauty & Personal Care', 'Toys & Games'
                    ],
                    'max_products': 50
                },
                'etsy': {
                    'enabled': True,
                    'max_suggestions': 100,
                    'categories': [
                        'jewelry', 'home-decor', 'clothing', 'art',
                        'crafts', 'wedding', 'vintage', 'toys'
                    ]
                }
            },
            'analysis': {
                'categories': {
                    'home_decor': ['home decor', 'wall art', 'candle', 'mug', 'pillow'],
                    'jewelry': ['necklace', 'ring', 'bracelet', 'earrings', 'jewelry'],
                    'gifts': ['gift', 'personalized', 'custom', 'unique'],
                    'pets': ['pet', 'dog', 'cat', 'animal'],
                    'wellness': ['soap', 'candle', 'beauty', 'skincare'],
                    'digital': ['digital', 'printable', 'download'],
                    'vintage': ['vintage', 'retro', 'antique'],
                    'crafts': ['craft', 'diy', 'handmade']
                },
                'scoring': {
                    'frequency_weight': 0.3,
                    'recency_weight': 0.3,
                    'growth_weight': 0.2,
                    'cross_platform_weight': 0.2
                },
                'min_score': 0.1,
                'max_trends': 20
            },
            'reporting': {
                'daily': {
                    'enabled': True,
                    'top_trends': 5,
                    'email_enabled': False
                },
                'weekly': {
                    'enabled': True,
                    'top_trends': 10,
                    'email_enabled': False,
                    'include_charts': True
                }
            },
            'database': {
                'type': 'sqlite',
                'path': 'data/trends.db'
            },
            'logging': {
                'level': 'INFO',
                'file': 'logs/trend_detector.log'
            }
        }
    
    def _load_env_vars(self):
        """Load environment variables."""
        # Override config with environment variables
        env_mappings = {
            'REDDIT_CLIENT_ID': ('data_sources.reddit.client_id', str),
            'REDDIT_CLIENT_SECRET': ('data_sources.reddit.client_secret', str),
            'TWITTER_BEARER_TOKEN': ('data_sources.twitter.bearer_token', str),
            'OPENAI_API_KEY': ('ai.openai_api_key', str)
        }
        
        for env_var, (config_path, var_type) in env_mappings.items():
            env_value = os.getenv(env_var)
            if env_value:
                self._set_nested_value(config_path, var_type(env_value))
    
    def _set_nested_value(self, path: str, value: Any):
        """Set a nested configuration value."""
        keys = path.split('.')
        current = self.config
        
        for key in keys[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]
        
        current[keys[-1]] = value
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value using dot notation."""
        keys = key.split('.')
        current = self.config
        
        for k in keys:
            if isinstance(current, dict) and k in current:
                current = current[k]
            else:
                return default
        
        return current
    
    def set(self, key: str, value: Any):
        """Set configuration value using dot notation."""
        self._set_nested_value(key, value)
    
    def get_data_sources(self) -> List[str]:
        """Get list of enabled data sources."""
        sources = []
        for source, config in self.config.get('data_sources', {}).items():
            if config.get('enabled', False):
                sources.append(source)
        return sources
    
    def get_categories(self) -> Dict[str, List[str]]:
        """Get category keywords."""
        return self.config.get('analysis.categories', {})
    
    def get_scoring_weights(self) -> Dict[str, float]:
        """Get scoring weights."""
        return self.config.get('analysis.scoring', {})
    
    def is_source_enabled(self, source: str) -> bool:
        """Check if a data source is enabled."""
        return self.config.get(f'data_sources.{source}.enabled', False)
    
    def get_source_config(self, source: str) -> Dict[str, Any]:
        """Get configuration for a specific data source."""
        return self.config.get(f'data_sources.{source}', {})
    
    def save(self):
        """Save configuration to file."""
        config_path = Path(self.config_file)
        config_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(config_path, 'w') as f:
            json.dump(self.config, f, indent=2)
    
    def validate(self) -> bool:
        """Validate configuration."""
        required_keys = [
            'data_sources',
            'analysis',
            'reporting',
            'database'
        ]
        
        for key in required_keys:
            if key not in self.config:
                print(f"Missing required configuration key: {key}")
                return False
        
        return True 