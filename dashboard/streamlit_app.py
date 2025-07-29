#!/usr/bin/env python3
"""
Streamlit Dashboard Application

Interactive dashboard for visualizing trend detection results,
including real-time data, charts, and filtering capabilities.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from datetime import datetime, timedelta
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
import sqlite3

# Page configuration
st.set_page_config(
    page_title="Etsy Trend Detection Dashboard",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #667eea;
        margin: 0.5rem 0;
    }
    .trend-card {
        background: white;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)

class TrendDashboard:
    """Main dashboard class for trend visualization."""
    
    def __init__(self):
        """Initialize the dashboard."""
        self.db_path = Path("data/storage/trends_history.db")
        self.load_data()
        
    def load_data(self):
        """Load data from database and files."""
        try:
            # Load from database if available
            if self.db_path.exists():
                self.load_from_database()
            else:
                # Load from demo data
                self.load_demo_data()
        except Exception as e:
            st.error(f"Error loading data: {e}")
            self.load_demo_data()
            
    def load_from_database(self):
        """Load data from SQLite database."""
        conn = sqlite3.connect(self.db_path)
        
        # Load recent trends
        query = """
        SELECT keyword, platform, category, popularity_score, 
               emerging_score, confidence_score, date
        FROM trends 
        WHERE date >= date('now', '-7 days')
        ORDER BY emerging_score DESC
        """
        
        self.trends_df = pd.read_sql_query(query, conn)
        
        # Load daily snapshots
        snapshot_query = """
        SELECT date, total_trends, emerging_trends, high_confidence_trends
        FROM daily_snapshots 
        WHERE date >= date('now', '-30 days')
        ORDER BY date
        """
        
        self.snapshots_df = pd.read_sql_query(snapshot_query, conn)
        conn.close()
        
    def load_demo_data(self):
        """Load demo data for testing."""
        # Create sample data
        dates = pd.date_range(start='2024-01-01', end='2024-01-07', freq='D')
        platforms = ['google_trends', 'reddit', 'pinterest', 'etsy']
        categories = ['jewelry', 'home_decor', 'gifts', 'fashion']
        
        data = []
        for date in dates:
            for platform in platforms:
                for category in categories:
                    for i in range(5):  # 5 trends per platform/category/day
                        data.append({
                            'keyword': f'sample_trend_{i}_{category}',
                            'platform': platform,
                            'category': category,
                            'popularity_score': np.random.uniform(0, 100),
                            'emerging_score': np.random.uniform(0, 1),
                            'confidence_score': np.random.uniform(0, 1),
                            'date': date.strftime('%Y-%m-%d')
                        })
                        
        self.trends_df = pd.DataFrame(data)
        
        # Create snapshots data
        snapshot_data = []
        for date in dates:
            snapshot_data.append({
                'date': date.strftime('%Y-%m-%d'),
                'total_trends': len([d for d in data if d['date'] == date.strftime('%Y-%m-%d')]),
                'emerging_trends': len([d for d in data if d['date'] == date.strftime('%Y-%m-%d') and d['emerging_score'] > 0.75]),
                'high_confidence_trends': len([d for d in data if d['date'] == date.strftime('%Y-%m-%d') and d['confidence_score'] > 0.8])
            })
            
        self.snapshots_df = pd.DataFrame(snapshot_data)
        
    def render_header(self):
        """Render the main header."""
        st.markdown("""
        <div class="main-header">
            <h1>🎯 Etsy Trend Detection Dashboard</h1>
            <p>Real-time trend analysis and business intelligence</p>
        </div>
        """, unsafe_allow_html=True)
        
    def render_metrics(self):
        """Render key metrics."""
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_trends = len(self.trends_df)
            st.metric("Total Trends", total_trends)
            
        with col2:
            emerging_trends = len(self.trends_df[self.trends_df['emerging_score'] > 0.75])
            st.metric("Emerging Trends", emerging_trends)
            
        with col3:
            high_confidence = len(self.trends_df[self.trends_df['confidence_score'] > 0.8])
            st.metric("High Confidence", high_confidence)
            
        with col4:
            avg_emerging = self.trends_df['emerging_score'].mean()
            st.metric("Avg Emerging Score", f"{avg_emerging:.3f}")
            
    def render_trending_keywords(self):
        """Render trending keywords section."""
        st.subheader("🔥 Trending Keywords")
        
        # Filter options
        col1, col2, col3 = st.columns(3)
        
        with col1:
            min_score = st.slider("Min Emerging Score", 0.0, 1.0, 0.5, 0.1)
            
        with col2:
            selected_platforms = st.multiselect(
                "Platforms",
                options=self.trends_df['platform'].unique(),
                default=self.trends_df['platform'].unique()
            )
            
        with col3:
            selected_categories = st.multiselect(
                "Categories",
                options=self.trends_df['category'].unique(),
                default=self.trends_df['category'].unique()
            )
            
        # Filter data
        filtered_df = self.trends_df[
            (self.trends_df['emerging_score'] >= min_score) &
            (self.trends_df['platform'].isin(selected_platforms)) &
            (self.trends_df['category'].isin(selected_categories))
        ].sort_values('emerging_score', ascending=False)
        
        # Display top trends
        if not filtered_df.empty:
            top_trends = filtered_df.head(20)
            
            # Create trend cards
            for _, trend in top_trends.iterrows():
                with st.container():
                    col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
                    
                    with col1:
                        st.markdown(f"**{trend['keyword']}**")
                        st.caption(f"Category: {trend['category']}")
                        
                    with col2:
                        st.metric("Emerging Score", f"{trend['emerging_score']:.3f}")
                        
                    with col3:
                        st.metric("Confidence", f"{trend['confidence_score']:.3f}")
                        
                    with col4:
                        st.metric("Platform", trend['platform'])
                        
                    st.divider()
        else:
            st.info("No trends match the current filters.")
            
    def render_source_heatmap(self):
        """Render source frequency heatmap."""
        st.subheader("📊 Source Frequency Heatmap")
        
        # Create heatmap data
        heatmap_data = self.trends_df.groupby(['platform', 'category']).size().unstack(fill_value=0)
        
        # Create heatmap
        fig = px.imshow(
            heatmap_data,
            title="Trend Distribution by Platform and Category",
            color_continuous_scale="Viridis",
            aspect="auto"
        )
        
        fig.update_layout(
            xaxis_title="Category",
            yaxis_title="Platform",
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
    def render_trend_growth(self):
        """Render trend growth over time."""
        st.subheader("📈 Trend Growth Over Time")
        
        # Prepare time series data
        if not self.snapshots_df.empty:
            fig = make_subplots(
                rows=2, cols=2,
                subplot_titles=('Total Trends', 'Emerging Trends', 'High Confidence Trends', 'Trend Growth Rate'),
                specs=[[{"secondary_y": False}, {"secondary_y": False}],
                       [{"secondary_y": False}, {"secondary_y": False}]]
            )
            
            # Total trends
            fig.add_trace(
                go.Scatter(x=self.snapshots_df['date'], y=self.snapshots_df['total_trends'],
                          mode='lines+markers', name='Total Trends'),
                row=1, col=1
            )
            
            # Emerging trends
            fig.add_trace(
                go.Scatter(x=self.snapshots_df['date'], y=self.snapshots_df['emerging_trends'],
                          mode='lines+markers', name='Emerging Trends'),
                row=1, col=2
            )
            
            # High confidence trends
            fig.add_trace(
                go.Scatter(x=self.snapshots_df['date'], y=self.snapshots_df['high_confidence_trends'],
                          mode='lines+markers', name='High Confidence'),
                row=2, col=1
            )
            
            # Growth rate
            growth_rate = self.snapshots_df['total_trends'].pct_change() * 100
            fig.add_trace(
                go.Scatter(x=self.snapshots_df['date'], y=growth_rate,
                          mode='lines+markers', name='Growth Rate (%)'),
                row=2, col=2
            )
            
            fig.update_layout(height=600, showlegend=True)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No time series data available.")
            
    def render_platform_analysis(self):
        """Render platform performance analysis."""
        st.subheader("🔍 Platform Performance Analysis")
        
        # Platform statistics
        platform_stats = self.trends_df.groupby('platform').agg({
            'emerging_score': ['mean', 'count'],
            'confidence_score': 'mean',
            'popularity_score': 'mean'
        }).round(3)
        
        platform_stats.columns = ['Avg Emerging Score', 'Trend Count', 'Avg Confidence', 'Avg Popularity']
        
        # Display platform stats
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Platform Statistics**")
            st.dataframe(platform_stats, use_container_width=True)
            
        with col2:
            # Platform performance chart
            fig = px.bar(
                x=platform_stats.index,
                y=platform_stats['Avg Emerging Score'],
                title="Average Emerging Score by Platform",
                color=platform_stats['Trend Count'],
                color_continuous_scale="Viridis"
            )
            
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
            
    def render_category_insights(self):
        """Render category insights."""
        st.subheader("📂 Category Insights")
        
        # Category statistics
        category_stats = self.trends_df.groupby('category').agg({
            'emerging_score': ['mean', 'count'],
            'confidence_score': 'mean'
        }).round(3)
        
        category_stats.columns = ['Avg Emerging Score', 'Trend Count', 'Avg Confidence']
        
        # Display category stats
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Category Statistics**")
            st.dataframe(category_stats, use_container_width=True)
            
        with col2:
            # Category performance chart
            fig = px.pie(
                values=category_stats['Trend Count'],
                names=category_stats.index,
                title="Trend Distribution by Category"
            )
            
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
            
    def render_search_and_filter(self):
        """Render search and filter functionality."""
        st.subheader("🔍 Search and Filter")
        
        # Search functionality
        search_term = st.text_input("Search keywords:", placeholder="Enter keyword to search...")
        
        if search_term:
            search_results = self.trends_df[
                self.trends_df['keyword'].str.contains(search_term, case=False, na=False)
            ]
            
            if not search_results.empty:
                st.markdown(f"**Found {len(search_results)} results for '{search_term}'**")
                st.dataframe(search_results, use_container_width=True)
            else:
                st.info(f"No results found for '{search_term}'")
                
        # Advanced filters
        with st.expander("Advanced Filters"):
            col1, col2 = st.columns(2)
            
            with col1:
                min_popularity = st.slider("Min Popularity Score", 0.0, 100.0, 0.0, 5.0)
                min_confidence = st.slider("Min Confidence Score", 0.0, 1.0, 0.0, 0.1)
                
            with col2:
                date_range = st.date_input(
                    "Date Range",
                    value=(datetime.now() - timedelta(days=7), datetime.now()),
                    max_value=datetime.now()
                )
                
            # Apply filters
            if st.button("Apply Filters"):
                filtered_df = self.trends_df[
                    (self.trends_df['popularity_score'] >= min_popularity) &
                    (self.trends_df['confidence_score'] >= min_confidence)
                ]
                
                if len(date_range) == 2:
                    start_date, end_date = date_range
                    filtered_df = filtered_df[
                        (filtered_df['date'] >= start_date.strftime('%Y-%m-%d')) &
                        (filtered_df['date'] <= end_date.strftime('%Y-%m-%d'))
                    ]
                    
                st.markdown(f"**Filtered Results: {len(filtered_df)} trends**")
                st.dataframe(filtered_df, use_container_width=True)
                
    def render_sidebar(self):
        """Render sidebar with navigation and settings."""
        st.sidebar.title("🎯 Navigation")
        
        # Navigation
        page = st.sidebar.selectbox(
            "Select Page",
            ["Overview", "Trending Keywords", "Source Analysis", "Growth Charts", "Platform Analysis", "Category Insights", "Search & Filter"]
        )
        
        # Settings
        st.sidebar.title("⚙️ Settings")
        
        # Data refresh
        if st.sidebar.button("🔄 Refresh Data"):
            self.load_data()
            st.success("Data refreshed!")
            
        # Export options
        st.sidebar.title("📊 Export")
        
        if st.sidebar.button("📥 Export to CSV"):
            csv = self.trends_df.to_csv(index=False)
            st.sidebar.download_button(
                label="Download CSV",
                data=csv,
                file_name=f"trends_export_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
            
        # System info
        st.sidebar.title("ℹ️ System Info")
        st.sidebar.info(f"Data Points: {len(self.trends_df)}")
        st.sidebar.info(f"Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        
        return page
        
    def run(self):
        """Run the dashboard."""
        self.render_header()
        
        # Render sidebar
        page = self.render_sidebar()
        
        # Render metrics
        self.render_metrics()
        
        # Render page content
        if page == "Overview":
            st.subheader("📊 Overview")
            col1, col2 = st.columns(2)
            
            with col1:
                self.render_source_heatmap()
                
            with col2:
                self.render_trend_growth()
                
        elif page == "Trending Keywords":
            self.render_trending_keywords()
            
        elif page == "Source Analysis":
            self.render_source_heatmap()
            
        elif page == "Growth Charts":
            self.render_trend_growth()
            
        elif page == "Platform Analysis":
            self.render_platform_analysis()
            
        elif page == "Category Insights":
            self.render_category_insights()
            
        elif page == "Search & Filter":
            self.render_search_and_filter()

def main():
    """Main function to run the dashboard."""
    try:
        dashboard = TrendDashboard()
        dashboard.run()
    except Exception as e:
        st.error(f"Error running dashboard: {e}")
        st.info("Please ensure all dependencies are installed and data is available.")

if __name__ == "__main__":
    main() 