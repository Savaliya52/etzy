"""
Etsy Trend Detection Dashboard

Streamlit dashboard for visualizing trends and analysis results.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json
from pathlib import Path
import sys

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from utils.config import Config
from analysis.trend_analyzer import TrendAnalyzer
from data_ingestion.collector_manager import DataCollectorManager

# Page configuration
st.set_page_config(
    page_title="Etsy Trend Detector",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize config
@st.cache_resource
def get_config():
    return Config()

config = get_config()

# Initialize components
@st.cache_resource
def get_analyzer():
    return TrendAnalyzer(config)

@st.cache_resource
def get_collector():
    return DataCollectorManager(config)

analyzer = get_analyzer()
collector = get_collector()

def main():
    """Main dashboard function."""
    
    # Sidebar
    st.sidebar.title("🎯 Etsy Trend Detector")
    st.sidebar.markdown("---")
    
    # Navigation
    page = st.sidebar.selectbox(
        "Navigation",
        ["📊 Dashboard", "🔍 Trend Analysis", "📈 Data Collection", "⚙️ Settings"]
    )
    
    if page == "📊 Dashboard":
        show_dashboard()
    elif page == "🔍 Trend Analysis":
        show_trend_analysis()
    elif page == "📈 Data Collection":
        show_data_collection()
    elif page == "⚙️ Settings":
        show_settings()

def show_dashboard():
    """Show main dashboard."""
    st.title("📊 Etsy Trend Detection Dashboard")
    st.markdown("Monitor trending products and opportunities for your Etsy store.")
    
    # Get recent analysis
    try:
        analysis_data = load_recent_analysis()
        
        if analysis_data:
            # Key metrics
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric(
                    "Trends Analyzed",
                    analysis_data.get('summary', {}).get('total_trends_analyzed', 0)
                )
            
            with col2:
                st.metric(
                    "High Potential",
                    analysis_data.get('summary', {}).get('high_potential_opportunities', 0)
                )
            
            with col3:
                st.metric(
                    "Data Sources",
                    len(analysis_data.get('data_sources_analyzed', []))
                )
            
            with col4:
                st.metric(
                    "Items Analyzed",
                    analysis_data.get('total_items_analyzed', 0)
                )
            
            # Top trends
            st.subheader("🔥 Top Trending Keywords")
            trending_keywords = analysis_data.get('trending_keywords', [])
            
            if trending_keywords:
                df_trends = pd.DataFrame(trending_keywords[:10])
                
                # Create trend chart
                fig = px.bar(
                    df_trends,
                    x='keyword',
                    y='score',
                    title="Top 10 Trending Keywords",
                    labels={'keyword': 'Keyword', 'score': 'Trend Score'}
                )
                fig.update_layout(xaxis_tickangle=-45)
                st.plotly_chart(fig, use_container_width=True)
                
                # Trend table
                st.dataframe(
                    df_trends[['keyword', 'score', 'frequency', 'category']].head(10),
                    use_container_width=True
                )
            
            # Category breakdown
            st.subheader("📂 Category Breakdown")
            categorized_trends = analysis_data.get('categorized_trends', {})
            
            if categorized_trends:
                category_data = []
                for category, keywords in categorized_trends.items():
                    if keywords:
                        category_data.append({
                            'Category': category.replace('_', ' ').title(),
                            'Keywords': len(keywords),
                            'Top Keywords': ', '.join(keywords[:3])
                        })
                
                df_categories = pd.DataFrame(category_data)
                
                # Category chart
                fig = px.pie(
                    df_categories,
                    values='Keywords',
                    names='Category',
                    title="Trends by Category"
                )
                st.plotly_chart(fig, use_container_width=True)
                
                # Category table
                st.dataframe(df_categories, use_container_width=True)
            
            # Opportunities
            st.subheader("💡 Business Opportunities")
            opportunities = analysis_data.get('opportunities', [])
            
            if opportunities:
                df_opps = pd.DataFrame(opportunities[:10])
                
                # Opportunity chart
                fig = px.scatter(
                    df_opps,
                    x='score',
                    y='frequency',
                    size='score',
                    color='category',
                    hover_data=['keyword', 'market_potential', 'competition_level'],
                    title="Business Opportunities"
                )
                st.plotly_chart(fig, use_container_width=True)
                
                # Opportunity table
                opps_display = df_opps[['keyword', 'score', 'category', 'market_potential', 'competition_level']].head(10)
                st.dataframe(opps_display, use_container_width=True)
        
        else:
            st.warning("No recent analysis data found. Run data collection and analysis first.")
    
    except Exception as e:
        st.error(f"Error loading dashboard data: {e}")

def show_trend_analysis():
    """Show trend analysis page."""
    st.title("🔍 Trend Analysis")
    
    # Analysis controls
    col1, col2 = st.columns(2)
    
    with col1:
        analysis_mode = st.selectbox("Analysis Mode", ["daily", "weekly"])
    
    with col2:
        if st.button("🔄 Run Analysis"):
            with st.spinner("Running trend analysis..."):
                try:
                    analysis_results = asyncio.run(analyzer.analyze_trends(analysis_mode))
                    save_analysis_results(analysis_results)
                    st.success("Analysis completed!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error running analysis: {e}")
    
    # Load and display analysis results
    analysis_data = load_recent_analysis()
    
    if analysis_data:
        st.subheader("📊 Analysis Results")
        
        # Detailed trend analysis
        trending_keywords = analysis_data.get('trending_keywords', [])
        
        if trending_keywords:
            # Filter controls
            col1, col2 = st.columns(2)
            
            with col1:
                min_score = st.slider("Minimum Score", 0.0, 1.0, 0.1, 0.1)
            
            with col2:
                selected_category = st.selectbox(
                    "Category Filter",
                    ["All"] + list(set(trend.get('category') for trend in trending_keywords if trend.get('category')))
                )
            
            # Filter data
            filtered_trends = []
            for trend in trending_keywords:
                if trend['score'] >= min_score:
                    if selected_category == "All" or trend.get('category') == selected_category:
                        filtered_trends.append(trend)
            
            if filtered_trends:
                df_filtered = pd.DataFrame(filtered_trends)
                
                # Trend visualization
                fig = px.scatter(
                    df_filtered,
                    x='frequency',
                    y='score',
                    size='score',
                    color='category',
                    hover_data=['keyword', 'sources'],
                    title="Trend Analysis Scatter Plot"
                )
                st.plotly_chart(fig, use_container_width=True)
                
                # Detailed table
                st.dataframe(df_filtered, use_container_width=True)
            else:
                st.info("No trends match the selected filters.")
    
    else:
        st.info("No analysis data available. Run analysis first.")

def show_data_collection():
    """Show data collection page."""
    st.title("📈 Data Collection")
    
    # Collection controls
    col1, col2, col3 = st.columns(3)
    
    with col1:
        collection_mode = st.selectbox("Collection Mode", ["daily", "weekly"])
    
    with col2:
        sources = st.multiselect(
            "Data Sources",
            ["google_trends", "reddit", "pinterest", "twitter", "amazon", "etsy"],
            default=["google_trends", "reddit", "pinterest"]
        )
    
    with col3:
        if st.button("📥 Collect Data"):
            with st.spinner("Collecting data..."):
                try:
                    collected_data = asyncio.run(collector.collect_all_data(sources, collection_mode))
                    st.success(f"Data collection completed! Collected {collected_data.get('metadata', {}).get('total_items', 0)} items.")
                except Exception as e:
                    st.error(f"Error collecting data: {e}")
    
    # Data source status
    st.subheader("📊 Data Source Status")
    
    status = collector.get_collector_status()
    
    for source, info in status.items():
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.write(f"**{source.replace('_', ' ').title()}**")
        
        with col2:
            if info['enabled']:
                st.success("✅ Enabled")
            else:
                st.error("❌ Disabled")
        
        with col3:
            if info['available']:
                st.success("✅ Available")
            else:
                st.warning("⚠️ Not Available")
    
    # Recent data summary
    st.subheader("📋 Recent Data Summary")
    
    try:
        recent_data = asyncio.run(collector.get_recent_data(24))
        
        if recent_data:
            # Data source breakdown
            source_counts = {}
            for item in recent_data:
                source = item.get('source', 'unknown')
                source_counts[source] = source_counts.get(source, 0) + 1
            
            if source_counts:
                df_sources = pd.DataFrame([
                    {'Source': source, 'Count': count}
                    for source, count in source_counts.items()
                ])
                
                fig = px.pie(
                    df_sources,
                    values='Count',
                    names='Source',
                    title="Data by Source (Last 24 Hours)"
                )
                st.plotly_chart(fig, use_container_width=True)
        
        else:
            st.info("No recent data available.")
    
    except Exception as e:
        st.error(f"Error loading recent data: {e}")

def show_settings():
    """Show settings page."""
    st.title("⚙️ Settings")
    
    st.subheader("Configuration")
    
    # Display current config
    st.json(config.config)
    
    # Data source configuration
    st.subheader("Data Sources")
    
    for source, source_config in config.config.get('data_sources', {}).items():
        with st.expander(f"{source.replace('_', ' ').title()}"):
            enabled = st.checkbox("Enabled", source_config.get('enabled', False), key=f"enabled_{source}")
            config.set(f'data_sources.{source}.enabled', enabled)
    
    # Save configuration
    if st.button("💾 Save Configuration"):
        config.save()
        st.success("Configuration saved!")

def load_recent_analysis():
    """Load recent analysis results."""
    try:
        # Look for recent analysis files
        analysis_files = list(Path("data/processed").glob("trend_analysis_*.json"))
        
        if analysis_files:
            # Get most recent file
            latest_file = max(analysis_files, key=lambda x: x.stat().st_mtime)
            
            with open(latest_file, 'r') as f:
                return json.load(f)
        
        return None
    
    except Exception as e:
        st.error(f"Error loading analysis data: {e}")
        return None

def save_analysis_results(results):
    """Save analysis results to file."""
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"data/processed/trend_analysis_{results['mode']}_{timestamp}.json"
        
        filepath = Path(filename)
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        with open(filepath, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        st.success(f"Analysis results saved to {filename}")
    
    except Exception as e:
        st.error(f"Error saving analysis results: {e}")

if __name__ == "__main__":
    main() 