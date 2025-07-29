#!/usr/bin/env python3
"""
History Manager Module

Manages daily trend snapshots and historical data storage.
Handles data retention, retrieval, and cleanup operations.
"""

import os
import json
import sqlite3
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
import logging

logger = logging.getLogger(__name__)

class HistoryManager:
    """Manages historical trend data storage and retrieval."""
    
    def __init__(self, storage_dir: str = "data/storage", retention_days: int = 30):
        """
        Initialize the history manager.
        
        Args:
            storage_dir: Directory to store historical data
            retention_days: Number of days to retain data
        """
        self.storage_dir = Path(storage_dir)
        self.retention_days = retention_days
        self.db_path = self.storage_dir / "trends_history.db"
        
        # Create storage directory if it doesn't exist
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize database
        self._init_database()
        
    def _init_database(self):
        """Initialize SQLite database with required tables."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create trends table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS trends (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                keyword TEXT NOT NULL,
                category TEXT,
                platform TEXT NOT NULL,
                popularity_score REAL,
                emerging_score REAL DEFAULT 0,
                confidence_score REAL DEFAULT 0,
                timestamp TEXT NOT NULL,
                date TEXT NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create daily_snapshots table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS daily_snapshots (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT UNIQUE NOT NULL,
                total_trends INTEGER DEFAULT 0,
                emerging_trends INTEGER DEFAULT 0,
                high_confidence_trends INTEGER DEFAULT 0,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create indexes for better performance
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_trends_date ON trends(date)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_trends_keyword ON trends(keyword)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_trends_platform ON trends(platform)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_trends_emerging ON trends(emerging_score)')
        
        conn.commit()
        conn.close()
        
    def store_daily_trends(self, trends_data: List[Dict[str, Any]], date: str = None):
        """
        Store daily trends data.
        
        Args:
            trends_data: List of trend dictionaries
            date: Date string (YYYY-MM-DD), defaults to today
        """
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')
            
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Store trends
        for trend in trends_data:
            cursor.execute('''
                INSERT INTO trends (
                    keyword, category, platform, popularity_score, 
                    emerging_score, confidence_score, timestamp, date
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                trend.get('keyword'),
                trend.get('category'),
                trend.get('platform'),
                trend.get('popularity_score', 0),
                trend.get('emerging_score', 0),
                trend.get('confidence_score', 0),
                trend.get('timestamp'),
                date
            ))
        
        # Update daily snapshot
        cursor.execute('''
            INSERT OR REPLACE INTO daily_snapshots (
                date, total_trends, emerging_trends, high_confidence_trends
            ) VALUES (?, ?, ?, ?)
        ''', (
            date,
            len(trends_data),
            len([t for t in trends_data if t.get('emerging_score', 0) > 0.75]),
            len([t for t in trends_data if t.get('confidence_score', 0) > 0.8])
        ))
        
        conn.commit()
        conn.close()
        
        logger.info(f"Stored {len(trends_data)} trends for {date}")
        
    def get_trends_by_date(self, date: str) -> List[Dict[str, Any]]:
        """
        Retrieve trends for a specific date.
        
        Args:
            date: Date string (YYYY-MM-DD)
            
        Returns:
            List of trend dictionaries
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT keyword, category, platform, popularity_score, 
                   emerging_score, confidence_score, timestamp, date
            FROM trends 
            WHERE date = ?
            ORDER BY emerging_score DESC, popularity_score DESC
        ''', (date,))
        
        rows = cursor.fetchall()
        conn.close()
        
        trends = []
        for row in rows:
            trends.append({
                'keyword': row[0],
                'category': row[1],
                'platform': row[2],
                'popularity_score': row[3],
                'emerging_score': row[4],
                'confidence_score': row[5],
                'timestamp': row[6],
                'date': row[7]
            })
            
        return trends
        
    def get_trends_by_date_range(self, start_date: str, end_date: str) -> List[Dict[str, Any]]:
        """
        Retrieve trends for a date range.
        
        Args:
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            
        Returns:
            List of trend dictionaries
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT keyword, category, platform, popularity_score, 
                   emerging_score, confidence_score, timestamp, date
            FROM trends 
            WHERE date BETWEEN ? AND ?
            ORDER BY date DESC, emerging_score DESC
        ''', (start_date, end_date))
        
        rows = cursor.fetchall()
        conn.close()
        
        trends = []
        for row in rows:
            trends.append({
                'keyword': row[0],
                'category': row[1],
                'platform': row[2],
                'popularity_score': row[3],
                'emerging_score': row[4],
                'confidence_score': row[5],
                'timestamp': row[6],
                'date': row[7]
            })
            
        return trends
        
    def get_emerging_trends(self, days: int = 7, min_score: float = 0.75) -> List[Dict[str, Any]]:
        """
        Get emerging trends from the last N days.
        
        Args:
            days: Number of days to look back
            min_score: Minimum emerging score threshold
            
        Returns:
            List of emerging trend dictionaries
        """
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT keyword, category, platform, popularity_score, 
                   emerging_score, confidence_score, timestamp, date
            FROM trends 
            WHERE date BETWEEN ? AND ? AND emerging_score >= ?
            ORDER BY emerging_score DESC, popularity_score DESC
        ''', (start_date, end_date, min_score))
        
        rows = cursor.fetchall()
        conn.close()
        
        trends = []
        for row in rows:
            trends.append({
                'keyword': row[0],
                'category': row[1],
                'platform': row[2],
                'popularity_score': row[3],
                'emerging_score': row[4],
                'confidence_score': row[5],
                'timestamp': row[6],
                'date': row[7]
            })
            
        return trends
        
    def get_multi_source_trends(self, min_sources: int = 2, days: int = 7) -> List[Dict[str, Any]]:
        """
        Get trends that appear across multiple sources.
        
        Args:
            min_sources: Minimum number of sources required
            days: Number of days to look back
            
        Returns:
            List of multi-source trend dictionaries
        """
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get keywords that appear in multiple sources
        cursor.execute('''
            SELECT keyword, COUNT(DISTINCT platform) as source_count,
                   AVG(popularity_score) as avg_popularity,
                   AVG(emerging_score) as avg_emerging,
                   AVG(confidence_score) as avg_confidence,
                   GROUP_CONCAT(DISTINCT platform) as platforms
            FROM trends 
            WHERE date BETWEEN ? AND ?
            GROUP BY keyword
            HAVING source_count >= ?
            ORDER BY avg_emerging DESC, avg_popularity DESC
        ''', (start_date, end_date, min_sources))
        
        rows = cursor.fetchall()
        conn.close()
        
        trends = []
        for row in rows:
            trends.append({
                'keyword': row[0],
                'source_count': row[1],
                'avg_popularity': row[2],
                'avg_emerging': row[3],
                'avg_confidence': row[4],
                'platforms': row[5].split(',')
            })
            
        return trends
        
    def get_daily_summary(self, date: str = None) -> Dict[str, Any]:
        """
        Get daily summary statistics.
        
        Args:
            date: Date string (YYYY-MM-DD), defaults to today
            
        Returns:
            Dictionary with summary statistics
        """
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')
            
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get snapshot data
        cursor.execute('''
            SELECT total_trends, emerging_trends, high_confidence_trends
            FROM daily_snapshots 
            WHERE date = ?
        ''', (date,))
        
        snapshot = cursor.fetchone()
        
        # Get platform breakdown
        cursor.execute('''
            SELECT platform, COUNT(*) as count
            FROM trends 
            WHERE date = ?
            GROUP BY platform
        ''', (date,))
        
        platforms = dict(cursor.fetchall())
        
        conn.close()
        
        if snapshot:
            return {
                'date': date,
                'total_trends': snapshot[0],
                'emerging_trends': snapshot[1],
                'high_confidence_trends': snapshot[2],
                'platform_breakdown': platforms
            }
        else:
            return {
                'date': date,
                'total_trends': 0,
                'emerging_trends': 0,
                'high_confidence_trends': 0,
                'platform_breakdown': {}
            }
            
    def cleanup_old_data(self):
        """Remove data older than retention_days."""
        cutoff_date = (datetime.now() - timedelta(days=self.retention_days)).strftime('%Y-%m-%d')
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Delete old trends
        cursor.execute('DELETE FROM trends WHERE date < ?', (cutoff_date,))
        trends_deleted = cursor.rowcount
        
        # Delete old snapshots
        cursor.execute('DELETE FROM daily_snapshots WHERE date < ?', (cutoff_date,))
        snapshots_deleted = cursor.rowcount
        
        conn.commit()
        conn.close()
        
        logger.info(f"Cleaned up {trends_deleted} trends and {snapshots_deleted} snapshots older than {cutoff_date}")
        
    def export_to_csv(self, start_date: str, end_date: str, output_file: str = None):
        """
        Export trends data to CSV.
        
        Args:
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            output_file: Output file path
        """
        trends = self.get_trends_by_date_range(start_date, end_date)
        
        if not trends:
            logger.warning("No trends found for the specified date range")
            return
            
        df = pd.DataFrame(trends)
        
        if output_file is None:
            output_file = f"trends_export_{start_date}_to_{end_date}.csv"
            
        df.to_csv(output_file, index=False)
        logger.info(f"Exported {len(trends)} trends to {output_file}")
        
    def get_database_stats(self) -> Dict[str, Any]:
        """Get database statistics."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Total trends
        cursor.execute('SELECT COUNT(*) FROM trends')
        total_trends = cursor.fetchone()[0]
        
        # Total dates
        cursor.execute('SELECT COUNT(DISTINCT date) FROM trends')
        total_dates = cursor.fetchone()[0]
        
        # Date range
        cursor.execute('SELECT MIN(date), MAX(date) FROM trends')
        date_range = cursor.fetchone()
        
        # Platform breakdown
        cursor.execute('SELECT platform, COUNT(*) FROM trends GROUP BY platform')
        platforms = dict(cursor.fetchall())
        
        conn.close()
        
        return {
            'total_trends': total_trends,
            'total_dates': total_dates,
            'date_range': date_range,
            'platforms': platforms,
            'database_size': self.db_path.stat().st_size if self.db_path.exists() else 0
        } 