#!/usr/bin/env python3
"""
Etsy Trend Detection System - Demo

A simple demo that showcases the system's capabilities without external dependencies.
"""

import json
from datetime import datetime
from pathlib import Path
from utils.simple_config import SimpleConfig

def run_demo():
    """Run the demo."""
    print("🎯 Etsy Trend Detection System - Demo")
    print("=" * 50)
    
    # Initialize configuration
    print("\n📋 Step 1: Configuration")
    print("-" * 30)
    config = SimpleConfig()
    print(f"✅ Configuration loaded from: {config.config_file}")
    print(f"📊 Enabled data sources: {config.get_data_sources()}")
    print(f"🏷️ Categories: {list(config.get_categories().keys())}")
    
    # Demo data collection
    print("\n📥 Step 2: Data Collection Simulation")
    print("-" * 30)
    
    mock_data = {
        'google_trends': [
            {
                'keyword': 'personalized jewelry',
                'score': 0.85,
                'trend_direction': 'rising',
                'recent_interest': 75,
                'growth_rate': 12.5,
                'collected_at': datetime.now().isoformat()
            },
            {
                'keyword': 'handmade candles',
                'score': 0.72,
                'trend_direction': 'stable',
                'recent_interest': 62,
                'growth_rate': 2.1,
                'collected_at': datetime.now().isoformat()
            },
            {
                'keyword': 'custom wall art',
                'score': 0.68,
                'trend_direction': 'rising',
                'recent_interest': 58,
                'growth_rate': 8.3,
                'collected_at': datetime.now().isoformat()
            }
        ],
        'reddit': [
            {
                'title': 'Just bought this amazing personalized necklace from Etsy!',
                'text': 'I found this beautiful custom name necklace on Etsy and I love it!',
                'subreddit': 'jewelry',
                'score': 45,
                'collected_at': datetime.now().isoformat()
            },
            {
                'title': 'Etsy home decor haul - everything is handmade!',
                'text': 'I went on a shopping spree on Etsy for home decor items.',
                'subreddit': 'homeimprovement',
                'score': 78,
                'collected_at': datetime.now().isoformat()
            }
        ],
        'pinterest': [
            {
                'title': 'Beautiful Handmade Jewelry from Etsy',
                'description': 'Stunning personalized name necklace found on Etsy.',
                'note': 'Love this handmade necklace! #Etsy #Handmade #Jewelry',
                'collected_at': datetime.now().isoformat()
            }
        ],
        'metadata': {
            'total_items': 6,
            'collection_time': datetime.now().isoformat(),
            'sources': ['google_trends', 'reddit', 'pinterest']
        }
    }
    
    print(f"✅ Collected {mock_data['metadata']['total_items']} items from {len(mock_data['metadata']['sources'])} sources")
    
    # Demo trend analysis
    print("\n🔍 Step 3: Trend Analysis")
    print("-" * 30)
    
    # Extract keywords from all data
    keywords = []
    for source, items in mock_data.items():
        if source != 'metadata':
            for item in items:
                # Extract from title
                if 'title' in item:
                    keywords.extend(item['title'].lower().split())
                # Extract from text
                if 'text' in item:
                    keywords.extend(item['text'].lower().split())
                # Extract from description
                if 'description' in item:
                    keywords.extend(item['description'].lower().split())
    
    # Filter and count keywords
    stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'can', 'this', 'that', 'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her', 'us', 'them', 'my', 'your', 'his', 'her', 'its', 'our', 'their'}
    
    keyword_counts = {}
    for keyword in keywords:
        clean_keyword = ''.join(c for c in keyword if c.isalnum())
        if len(clean_keyword) > 3 and clean_keyword not in stop_words:
            keyword_counts[clean_keyword] = keyword_counts.get(clean_keyword, 0) + 1
    
    # Sort by frequency
    sorted_keywords = sorted(keyword_counts.items(), key=lambda x: x[1], reverse=True)
    
    print("🔥 Top Trending Keywords:")
    for i, (keyword, count) in enumerate(sorted_keywords[:10], 1):
        print(f"  {i}. {keyword} (Frequency: {count})")
    
    # Demo category classification
    print("\n📂 Step 4: Category Classification")
    print("-" * 30)
    
    categories = config.get_categories()
    categorized_trends = {category: [] for category in categories.keys()}
    
    for keyword, count in sorted_keywords[:10]:
        for category, keywords in categories.items():
            if any(cat_keyword in keyword.lower() for cat_keyword in keywords):
                categorized_trends[category].append(keyword)
                break
    
    for category, keywords in categorized_trends.items():
        if keywords:
            print(f"  📁 {category.replace('_', ' ').title()}: {', '.join(keywords[:3])}")
    
    # Demo opportunity detection
    print("\n💡 Step 5: Business Opportunities")
    print("-" * 30)
    
    opportunities = []
    for keyword, count in sorted_keywords[:5]:
        # Simple scoring based on frequency
        score = min(count / 10.0, 1.0)  # Normalize to 0-1
        
        # Determine market potential
        if score > 0.7:
            market_potential = "High"
        elif score > 0.4:
            market_potential = "Medium"
        else:
            market_potential = "Low"
        
        # Determine competition level
        if count > 5:
            competition = "High"
        elif count > 2:
            competition = "Medium"
        else:
            competition = "Low"
        
        opportunities.append({
            'keyword': keyword,
            'score': score,
            'frequency': count,
            'market_potential': market_potential,
            'competition_level': competition,
            'suggested_tags': [keyword, 'handmade', 'personalized', 'etsy']
        })
    
    print("💼 Top Business Opportunities:")
    for i, opp in enumerate(opportunities, 1):
        print(f"  {i}. {opp['keyword']}")
        print(f"     - Score: {opp['score']:.2f}")
        print(f"     - Market Potential: {opp['market_potential']}")
        print(f"     - Competition: {opp['competition_level']}")
        print(f"     - Suggested Tags: {', '.join(opp['suggested_tags'][:3])}")
        print()
    
    # Demo report generation
    print("\n📊 Step 6: Report Generation")
    print("-" * 30)
    
    report = {
        'report_date': datetime.now().isoformat(),
        'summary': {
            'total_trends_analyzed': len(sorted_keywords),
            'high_potential_opportunities': len([o for o in opportunities if o['market_potential'] == 'High']),
            'data_sources': mock_data['metadata']['sources'],
            'total_items_collected': mock_data['metadata']['total_items']
        },
        'top_trends': sorted_keywords[:10],
        'opportunities': opportunities[:5],
        'categorized_trends': {k: v for k, v in categorized_trends.items() if v}
    }
    
    # Save report
    reports_dir = Path("data/reports")
    reports_dir.mkdir(parents=True, exist_ok=True)
    
    report_file = reports_dir / f"demo_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"✅ Report generated: {report_file}")
    print(f"📈 Summary:")
    print(f"  - Trends analyzed: {report['summary']['total_trends_analyzed']}")
    print(f"  - High potential opportunities: {report['summary']['high_potential_opportunities']}")
    print(f"  - Data sources: {len(report['summary']['data_sources'])}")
    
    # Demo dashboard data
    print("\n📈 Step 7: Dashboard Data")
    print("-" * 30)
    
    dashboard_data = {
        'trends_over_time': {
            'personalized': [65, 68, 72, 75, 78],
            'handmade': [45, 48, 52, 55, 58],
            'jewelry': [35, 38, 42, 45, 48]
        },
        'category_breakdown': {
            'jewelry': 40,
            'home_decor': 30,
            'gifts': 20,
            'other': 10
        },
        'source_analysis': {
            'google_trends': 45,
            'reddit': 30,
            'pinterest': 25
        }
    }
    
    print("📊 Dashboard Metrics:")
    print(f"  - Trending keywords tracked: {len(dashboard_data['trends_over_time'])}")
    print(f"  - Categories analyzed: {len(dashboard_data['category_breakdown'])}")
    print(f"  - Data sources: {len(dashboard_data['source_analysis'])}")
    
    # Save dashboard data
    dashboard_dir = Path("data/processed")
    dashboard_dir.mkdir(parents=True, exist_ok=True)
    
    dashboard_file = dashboard_dir / "dashboard_data.json"
    with open(dashboard_file, 'w') as f:
        json.dump(dashboard_data, f, indent=2)
    
    print(f"✅ Dashboard data saved: {dashboard_file}")
    
    # Final summary
    print("\n" + "=" * 50)
    print("🎉 Demo Completed Successfully!")
    print("=" * 50)
    
    print("\n📋 What the system can do:")
    print("✅ Collect data from multiple sources (Google Trends, Reddit, Pinterest, etc.)")
    print("✅ Analyze trends and identify patterns")
    print("✅ Classify trends into product categories")
    print("✅ Score opportunities based on multiple factors")
    print("✅ Generate business recommendations")
    print("✅ Create reports and visualizations")
    print("✅ Provide real-time dashboard insights")
    
    print("\n🚀 Next steps:")
    print("1. Install additional dependencies for full functionality")
    print("2. Set up API keys for external data sources")
    print("3. Run the full system: python main.py collect")
    print("4. Launch the dashboard: streamlit run dashboard/app.py")
    print("5. Customize categories and scoring for your niche")
    
    print("\n💡 Business Value:")
    print("• Identify trending products before they become saturated")
    print("• Find underserved niches with high potential")
    print("• Validate market demand across multiple platforms")
    print("• Optimize product listings with trending tags")
    print("• Stay ahead of competition with real-time insights")

if __name__ == "__main__":
    run_demo() 