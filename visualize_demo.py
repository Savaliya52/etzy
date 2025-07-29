#!/usr/bin/env python3
"""
Etsy Trend Detection System - Data Visualization

Generate graphs and charts from the demo data to visualize trends and insights.
"""

import json
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
import seaborn as sns
from datetime import datetime, timedelta

# Set style for better looking plots
plt.style.use('seaborn-v0_8')
sns.set_palette("husl")

def load_demo_data():
    """Load the demo data from the generated files."""
    try:
        with open('data/processed/dashboard_data.json', 'r') as f:
            dashboard_data = json.load(f)
        
        # Load the latest report
        reports_dir = Path("data/reports")
        report_files = list(reports_dir.glob("demo_report_*.json"))
        if report_files:
            latest_report = max(report_files, key=lambda x: x.stat().st_mtime)
            with open(latest_report, 'r') as f:
                report_data = json.load(f)
        else:
            report_data = {}
            
        return dashboard_data, report_data
    except FileNotFoundError:
        print("Demo data not found. Please run demo.py first.")
        return None, None

def create_trends_over_time_chart(dashboard_data):
    """Create a line chart showing trends over time."""
    trends_data = dashboard_data['trends_over_time']
    
    plt.figure(figsize=(12, 8))
    
    # Generate time periods (last 5 periods)
    periods = [f"Period {i+1}" for i in range(len(list(trends_data.values())[0]))]
    
    for keyword, values in trends_data.items():
        plt.plot(periods, values, marker='o', linewidth=2, markersize=8, label=keyword.title())
    
    plt.title('🔥 Trending Keywords Over Time', fontsize=16, fontweight='bold')
    plt.xlabel('Time Periods', fontsize=12)
    plt.ylabel('Trend Score', fontsize=12)
    plt.legend(fontsize=11)
    plt.grid(True, alpha=0.3)
    plt.xticks(rotation=45)
    
    # Add value annotations
    for keyword, values in trends_data.items():
        for i, value in enumerate(values):
            plt.annotate(f'{value}', (i, value), textcoords="offset points", 
                        xytext=(0,10), ha='center', fontsize=9)
    
    plt.tight_layout()
    plt.savefig('trends_over_time.png', dpi=300, bbox_inches='tight')
    plt.show()

def create_category_breakdown_pie(dashboard_data):
    """Create a pie chart showing category breakdown."""
    category_data = dashboard_data['category_breakdown']
    
    plt.figure(figsize=(10, 8))
    
    # Create pie chart
    colors = plt.cm.Set3(np.linspace(0, 1, len(category_data)))
    wedges, texts, autotexts = plt.pie(
        category_data.values(), 
        labels=[cat.replace('_', ' ').title() for cat in category_data.keys()],
        autopct='%1.1f%%',
        startangle=90,
        colors=colors,
        explode=[0.05] * len(category_data)
    )
    
    plt.title('📂 Category Breakdown', fontsize=16, fontweight='bold')
    
    # Enhance text appearance
    for autotext in autotexts:
        autotext.set_color('white')
        autotext.set_fontweight('bold')
    
    plt.axis('equal')
    plt.tight_layout()
    plt.savefig('category_breakdown.png', dpi=300, bbox_inches='tight')
    plt.show()

def create_source_analysis_bar(dashboard_data):
    """Create a bar chart showing data source analysis."""
    source_data = dashboard_data['source_analysis']
    
    plt.figure(figsize=(10, 6))
    
    sources = list(source_data.keys())
    values = list(source_data.values())
    colors = ['#FF6B6B', '#4ECDC4', '#45B7D1']
    
    bars = plt.bar(sources, values, color=colors, alpha=0.8, edgecolor='black', linewidth=1)
    
    plt.title('📊 Data Source Analysis', fontsize=16, fontweight='bold')
    plt.xlabel('Data Sources', fontsize=12)
    plt.ylabel('Contribution (%)', fontsize=12)
    
    # Add value labels on bars
    for bar, value in zip(bars, values):
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height + 1,
                f'{value}%', ha='center', va='bottom', fontweight='bold')
    
    plt.ylim(0, max(values) + 10)
    plt.grid(True, alpha=0.3, axis='y')
    plt.tight_layout()
    plt.savefig('source_analysis.png', dpi=300, bbox_inches='tight')
    plt.show()

def create_opportunity_radar_chart(report_data):
    """Create a radar chart for business opportunities."""
    if not report_data or 'opportunities' not in report_data:
        print("No opportunity data available for radar chart.")
        return
    
    opportunities = report_data['opportunities'][:5]  # Top 5 opportunities
    
    # Prepare data for radar chart
    categories = ['Score', 'Frequency', 'Market Potential', 'Competition Level']
    
    # Convert text values to numeric for radar chart
    def convert_to_numeric(value):
        if isinstance(value, (int, float)):
            return value
        elif value == 'High':
            return 3
        elif value == 'Medium':
            return 2
        elif value == 'Low':
            return 1
        else:
            return 0
    
    fig, ax = plt.subplots(figsize=(12, 8), subplot_kw=dict(projection='polar'))
    
    angles = np.linspace(0, 2 * np.pi, len(categories), endpoint=False).tolist()
    angles += angles[:1]  # Complete the circle
    
    colors = plt.cm.tab10(np.linspace(0, 1, len(opportunities)))
    
    for i, opp in enumerate(opportunities):
        values = [
            opp['score'] * 3,  # Scale score to 0-3 range
            min(opp['frequency'] / 2, 3),  # Scale frequency
            convert_to_numeric(opp['market_potential']),
            convert_to_numeric(opp['competition_level'])
        ]
        values += values[:1]  # Complete the circle
        
        ax.plot(angles, values, 'o-', linewidth=2, label=opp['keyword'].title(), color=colors[i])
        ax.fill(angles, values, alpha=0.25, color=colors[i])
    
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(categories)
    ax.set_ylim(0, 3)
    ax.set_title('💡 Business Opportunity Analysis', size=16, fontweight='bold', pad=20)
    ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.0))
    
    plt.tight_layout()
    plt.savefig('opportunity_radar.png', dpi=300, bbox_inches='tight')
    plt.show()

def create_keyword_heatmap(report_data):
    """Create a heatmap of keyword frequencies."""
    if not report_data or 'top_trends' not in report_data:
        print("No trend data available for heatmap.")
        return
    
    trends = report_data['top_trends'][:10]  # Top 10 trends
    
    # Create a simple frequency matrix
    keywords = [trend[0] for trend in trends]
    frequencies = [trend[1] for trend in trends]
    
    # Create a matrix for visualization
    matrix = np.array(frequencies).reshape(1, -1)
    
    plt.figure(figsize=(12, 4))
    
    sns.heatmap(matrix, 
                annot=True, 
                fmt='d',
                xticklabels=keywords,
                yticklabels=['Frequency'],
                cmap='YlOrRd',
                cbar_kws={'label': 'Frequency Count'})
    
    plt.title('🔥 Keyword Frequency Heatmap', fontsize=16, fontweight='bold')
    plt.xlabel('Keywords', fontsize=12)
    plt.ylabel('Metric', fontsize=12)
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.savefig('keyword_heatmap.png', dpi=300, bbox_inches='tight')
    plt.show()

def create_comprehensive_dashboard(dashboard_data, report_data):
    """Create a comprehensive dashboard with multiple subplots."""
    fig = plt.figure(figsize=(20, 12))
    
    # Create a 2x3 grid of subplots
    gs = fig.add_gridspec(2, 3, hspace=0.3, wspace=0.3)
    
    # 1. Trends over time (top left)
    ax1 = fig.add_subplot(gs[0, 0])
    trends_data = dashboard_data['trends_over_time']
    periods = [f"P{i+1}" for i in range(len(list(trends_data.values())[0]))]
    for keyword, values in trends_data.items():
        ax1.plot(periods, values, marker='o', linewidth=2, label=keyword.title())
    ax1.set_title('📈 Trends Over Time', fontweight='bold')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # 2. Category breakdown (top middle)
    ax2 = fig.add_subplot(gs[0, 1])
    category_data = dashboard_data['category_breakdown']
    colors = plt.cm.Set3(np.linspace(0, 1, len(category_data)))
    ax2.pie(category_data.values(), labels=[cat.replace('_', ' ').title() for cat in category_data.keys()],
            autopct='%1.1f%%', colors=colors, startangle=90)
    ax2.set_title('📂 Category Breakdown', fontweight='bold')
    
    # 3. Source analysis (top right)
    ax3 = fig.add_subplot(gs[0, 2])
    source_data = dashboard_data['source_analysis']
    bars = ax3.bar(source_data.keys(), source_data.values(), color=['#FF6B6B', '#4ECDC4', '#45B7D1'])
    ax3.set_title('📊 Data Sources', fontweight='bold')
    ax3.set_ylabel('Contribution (%)')
    for bar in bars:
        height = bar.get_height()
        ax3.text(bar.get_x() + bar.get_width()/2., height + 1,
                f'{height}%', ha='center', va='bottom')
    
    # 4. Keyword frequency (bottom left)
    ax4 = fig.add_subplot(gs[1, 0])
    if report_data and 'top_trends' in report_data:
        trends = report_data['top_trends'][:8]
        keywords = [trend[0] for trend in trends]
        frequencies = [trend[1] for trend in trends]
        bars = ax4.barh(keywords, frequencies, color='skyblue')
        ax4.set_title('🔥 Top Keywords', fontweight='bold')
        ax4.set_xlabel('Frequency')
        for bar in bars:
            width = bar.get_width()
            ax4.text(width + 0.1, bar.get_y() + bar.get_height()/2,
                    f'{width}', ha='left', va='center')
    
    # 5. Opportunity scores (bottom middle)
    ax5 = fig.add_subplot(gs[1, 1])
    if report_data and 'opportunities' in report_data:
        opps = report_data['opportunities'][:5]
        keywords = [opp['keyword'] for opp in opps]
        scores = [opp['score'] for opp in opps]
        bars = ax5.bar(keywords, scores, color='lightgreen')
        ax5.set_title('💡 Opportunity Scores', fontweight='bold')
        ax5.set_ylabel('Score')
        ax5.set_ylim(0, 1)
        for bar in bars:
            height = bar.get_height()
            ax5.text(bar.get_x() + bar.get_width()/2., height + 0.02,
                    f'{height:.2f}', ha='center', va='bottom')
    
    # 6. Summary stats (bottom right)
    ax6 = fig.add_subplot(gs[1, 2])
    ax6.axis('off')
    if report_data and 'summary' in report_data:
        summary = report_data['summary']
        stats_text = f"""
        📊 System Summary
        
        • Trends Analyzed: {summary.get('total_trends_analyzed', 'N/A')}
        • High Potential Opportunities: {summary.get('high_potential_opportunities', 'N/A')}
        • Data Sources: {len(summary.get('data_sources', []))}
        • Total Items Collected: {summary.get('total_items_collected', 'N/A')}
        
        🎯 Demo Status: ✅ Complete
        📅 Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}
        """
        ax6.text(0.1, 0.5, stats_text, transform=ax6.transAxes, fontsize=12,
                verticalalignment='center', fontfamily='monospace')
    
    plt.suptitle('🎯 Etsy Trend Detection System - Dashboard', fontsize=20, fontweight='bold')
    plt.tight_layout()
    plt.savefig('comprehensive_dashboard.png', dpi=300, bbox_inches='tight')
    plt.show()

def main():
    """Main function to generate all visualizations."""
    print("🎨 Generating Etsy Trend Detection Visualizations...")
    print("=" * 60)
    
    # Load data
    dashboard_data, report_data = load_demo_data()
    
    if dashboard_data is None:
        return
    
    # Generate individual charts
    print("📈 Creating trends over time chart...")
    create_trends_over_time_chart(dashboard_data)
    
    print("📂 Creating category breakdown pie chart...")
    create_category_breakdown_pie(dashboard_data)
    
    print("📊 Creating source analysis bar chart...")
    create_source_analysis_bar(dashboard_data)
    
    print("💡 Creating opportunity radar chart...")
    create_opportunity_radar_chart(report_data)
    
    print("🔥 Creating keyword frequency heatmap...")
    create_keyword_heatmap(report_data)
    
    print("🎯 Creating comprehensive dashboard...")
    create_comprehensive_dashboard(dashboard_data, report_data)
    
    print("\n✅ All visualizations generated successfully!")
    print("📁 Generated files:")
    print("  • trends_over_time.png")
    print("  • category_breakdown.png")
    print("  • source_analysis.png")
    print("  • opportunity_radar.png")
    print("  • keyword_heatmap.png")
    print("  • comprehensive_dashboard.png")

if __name__ == "__main__":
    main() 