#!/usr/bin/env python3
"""
Report Generator Module

Generates comprehensive reports including daily and weekly trend analysis,
business recommendations, and exportable formats (HTML, PDF, CSV).
"""

import json
import csv
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
import logging
from jinja2 import Template
import matplotlib.pyplot as plt
import seaborn as sns
import io
import base64

logger = logging.getLogger(__name__)

class ReportGenerator:
    """Generates comprehensive trend reports in multiple formats."""
    
    def __init__(self, output_dir: str = "reports"):
        """
        Initialize the report generator.
        
        Args:
            output_dir: Directory to store generated reports
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Set up plotting style
        plt.style.use('seaborn-v0_8')
        sns.set_palette("husl")
        
    def generate_daily_report(self, 
                            trends_data: List[Dict[str, Any]],
                            emerging_trends: List[Dict[str, Any]],
                            cross_platform_trends: List[Dict[str, Any]],
                            date: str = None) -> Dict[str, str]:
        """
        Generate daily trend report.
        
        Args:
            trends_data: All trends data for the day
            emerging_trends: Emerging trends detected
            cross_platform_trends: Cross-platform trends
            date: Report date (YYYY-MM-DD)
            
        Returns:
            Dictionary with paths to generated reports
        """
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')
            
        # Prepare report data
        report_data = {
            'date': date,
            'total_trends': len(trends_data),
            'emerging_trends': len(emerging_trends),
            'cross_platform_trends': len(cross_platform_trends),
            'top_emerging': emerging_trends[:10],
            'top_cross_platform': cross_platform_trends[:10],
            'platform_breakdown': self._get_platform_breakdown(trends_data),
            'category_breakdown': self._get_category_breakdown(trends_data),
            'generated_at': datetime.now().isoformat()
        }
        
        # Generate different formats
        reports = {}
        
        # CSV Report
        csv_path = self._generate_csv_report(report_data, date)
        reports['csv'] = str(csv_path)
        
        # HTML Report
        html_path = self._generate_html_report(report_data, date)
        reports['html'] = str(html_path)
        
        # PDF Report
        pdf_path = self._generate_pdf_report(report_data, date)
        reports['pdf'] = str(pdf_path)
        
        logger.info(f"Generated daily report for {date}: {reports}")
        return reports
        
    def generate_weekly_report(self, 
                             weekly_data: List[Dict[str, Any]],
                             date_range: Tuple[str, str]) -> Dict[str, str]:
        """
        Generate weekly trend report.
        
        Args:
            weekly_data: Weekly aggregated data
            date_range: Tuple of (start_date, end_date)
            
        Returns:
            Dictionary with paths to generated reports
        """
        start_date, end_date = date_range
        
        # Prepare weekly report data
        report_data = {
            'start_date': start_date,
            'end_date': end_date,
            'total_trends': len(weekly_data),
            'top_trends': weekly_data[:20],
            'trend_growth': self._analyze_trend_growth(weekly_data),
            'platform_performance': self._analyze_platform_performance(weekly_data),
            'category_insights': self._analyze_category_insights(weekly_data),
            'generated_at': datetime.now().isoformat()
        }
        
        # Generate different formats
        reports = {}
        
        # CSV Report
        csv_path = self._generate_weekly_csv_report(report_data, start_date, end_date)
        reports['csv'] = str(csv_path)
        
        # HTML Report
        html_path = self._generate_weekly_html_report(report_data, start_date, end_date)
        reports['html'] = str(html_path)
        
        # PDF Report
        pdf_path = self._generate_weekly_pdf_report(report_data, start_date, end_date)
        reports['pdf'] = str(pdf_path)
        
        logger.info(f"Generated weekly report for {start_date} to {end_date}: {reports}")
        return reports
        
    def _generate_csv_report(self, report_data: Dict[str, Any], date: str) -> Path:
        """Generate CSV format report."""
        csv_path = self.output_dir / f"daily_report_{date}.csv"
        
        with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            
            # Write header
            writer.writerow(['Report Date', report_data['date']])
            writer.writerow(['Generated At', report_data['generated_at']])
            writer.writerow([])
            
            # Write summary
            writer.writerow(['Summary'])
            writer.writerow(['Total Trends', report_data['total_trends']])
            writer.writerow(['Emerging Trends', report_data['emerging_trends']])
            writer.writerow(['Cross-Platform Trends', report_data['cross_platform_trends']])
            writer.writerow([])
            
            # Write top emerging trends
            writer.writerow(['Top Emerging Trends'])
            writer.writerow(['Keyword', 'Platform', 'Emerging Score', 'Confidence Score', 'Category'])
            for trend in report_data['top_emerging']:
                writer.writerow([
                    trend.get('keyword', ''),
                    trend.get('platform', ''),
                    trend.get('emerging_score', 0),
                    trend.get('confidence_score', 0),
                    trend.get('category', '')
                ])
            writer.writerow([])
            
            # Write platform breakdown
            writer.writerow(['Platform Breakdown'])
            writer.writerow(['Platform', 'Count'])
            for platform, count in report_data['platform_breakdown'].items():
                writer.writerow([platform, count])
                
        return csv_path
        
    def _generate_html_report(self, report_data: Dict[str, Any], date: str) -> Path:
        """Generate HTML format report."""
        html_path = self.output_dir / f"daily_report_{date}.html"
        
        # Create charts
        charts = self._create_report_charts(report_data)
        
        # HTML template
        html_template = """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Daily Trend Report - {{ date }}</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; }
                .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                         color: white; padding: 20px; border-radius: 10px; }
                .summary { background: #f8f9fa; padding: 20px; margin: 20px 0; border-radius: 10px; }
                .trends-table { width: 100%; border-collapse: collapse; margin: 20px 0; }
                .trends-table th, .trends-table td { border: 1px solid #ddd; padding: 8px; text-align: left; }
                .trends-table th { background-color: #f2f2f2; }
                .chart { text-align: center; margin: 20px 0; }
                .chart img { max-width: 100%; height: auto; }
                .high-score { color: #28a745; font-weight: bold; }
                .medium-score { color: #ffc107; font-weight: bold; }
                .low-score { color: #dc3545; font-weight: bold; }
            </style>
        </head>
        <body>
            <div class="header">
                <h1>🎯 Daily Trend Report</h1>
                <p>Generated on {{ generated_at }} for {{ date }}</p>
            </div>
            
            <div class="summary">
                <h2>📊 Summary</h2>
                <p><strong>Total Trends Analyzed:</strong> {{ total_trends }}</p>
                <p><strong>Emerging Trends Detected:</strong> {{ emerging_trends }}</p>
                <p><strong>Cross-Platform Trends:</strong> {{ cross_platform_trends }}</p>
            </div>
            
            <div class="chart">
                <h2>📈 Platform Breakdown</h2>
                <img src="data:image/png;base64,{{ platform_chart }}" alt="Platform Breakdown">
            </div>
            
            <div class="chart">
                <h2>📂 Category Distribution</h2>
                <img src="data:image/png;base64,{{ category_chart }}" alt="Category Distribution">
            </div>
            
            <h2>🔥 Top Emerging Trends</h2>
            <table class="trends-table">
                <thead>
                    <tr>
                        <th>Keyword</th>
                        <th>Platform</th>
                        <th>Emerging Score</th>
                        <th>Confidence Score</th>
                        <th>Category</th>
                    </tr>
                </thead>
                <tbody>
                    {% for trend in top_emerging %}
                    <tr>
                        <td>{{ trend.keyword }}</td>
                        <td>{{ trend.platform }}</td>
                        <td class="{% if trend.emerging_score > 0.8 %}high-score{% elif trend.emerging_score > 0.6 %}medium-score{% else %}low-score{% endif %}">
                            {{ "%.3f"|format(trend.emerging_score) }}
                        </td>
                        <td>{{ "%.3f"|format(trend.confidence_score) }}</td>
                        <td>{{ trend.category }}</td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
            
            <h2>🌐 Cross-Platform Trends</h2>
            <table class="trends-table">
                <thead>
                    <tr>
                        <th>Keyword</th>
                        <th>Sources</th>
                        <th>Avg Emerging Score</th>
                        <th>Confidence Score</th>
                    </tr>
                </thead>
                <tbody>
                    {% for trend in top_cross_platform %}
                    <tr>
                        <td>{{ trend.keyword }}</td>
                        <td>{{ trend.source_count }} ({{ trend.platforms|join(', ') }})</td>
                        <td>{{ "%.3f"|format(trend.avg_emerging) }}</td>
                        <td>{{ "%.3f"|format(trend.confidence_score) }}</td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </body>
        </html>
        """
        
        template = Template(html_template)
        html_content = template.render(
            date=date,
            generated_at=report_data['generated_at'],
            total_trends=report_data['total_trends'],
            emerging_trends=report_data['emerging_trends'],
            cross_platform_trends=report_data['cross_platform_trends'],
            top_emerging=report_data['top_emerging'],
            top_cross_platform=report_data['top_cross_platform'],
            platform_chart=charts['platform'],
            category_chart=charts['category']
        )
        
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
            
        return html_path
        
    def _generate_pdf_report(self, report_data: Dict[str, Any], date: str) -> Path:
        """Generate PDF format report."""
        try:
            from fpdf import FPDF
        except ImportError:
            logger.warning("fpdf not available, skipping PDF generation")
            return None
            
        pdf_path = self.output_dir / f"daily_report_{date}.pdf"
        
        pdf = FPDF()
        pdf.add_page()
        
        # Title
        pdf.set_font('Arial', 'B', 16)
        pdf.cell(0, 10, f'Daily Trend Report - {date}', ln=True, align='C')
        pdf.ln(10)
        
        # Summary
        pdf.set_font('Arial', 'B', 12)
        pdf.cell(0, 10, 'Summary', ln=True)
        pdf.set_font('Arial', '', 10)
        pdf.cell(0, 10, f'Total Trends: {report_data["total_trends"]}', ln=True)
        pdf.cell(0, 10, f'Emerging Trends: {report_data["emerging_trends"]}', ln=True)
        pdf.cell(0, 10, f'Cross-Platform Trends: {report_data["cross_platform_trends"]}', ln=True)
        pdf.ln(10)
        
        # Top emerging trends
        pdf.set_font('Arial', 'B', 12)
        pdf.cell(0, 10, 'Top Emerging Trends', ln=True)
        pdf.set_font('Arial', '', 8)
        
        for trend in report_data['top_emerging'][:10]:
            pdf.cell(0, 8, f"{trend.get('keyword', '')} - Score: {trend.get('emerging_score', 0):.3f}", ln=True)
            
        pdf.output(str(pdf_path))
        return pdf_path
        
    def _create_report_charts(self, report_data: Dict[str, Any]) -> Dict[str, str]:
        """Create charts for the report."""
        charts = {}
        
        # Platform breakdown chart
        plt.figure(figsize=(10, 6))
        platforms = list(report_data['platform_breakdown'].keys())
        counts = list(report_data['platform_breakdown'].values())
        
        plt.bar(platforms, counts, color=['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4'])
        plt.title('Platform Breakdown')
        plt.ylabel('Number of Trends')
        plt.xticks(rotation=45)
        
        # Save to base64
        img_buffer = io.BytesIO()
        plt.savefig(img_buffer, format='png', bbox_inches='tight')
        img_buffer.seek(0)
        charts['platform'] = base64.b64encode(img_buffer.getvalue()).decode()
        plt.close()
        
        # Category breakdown chart
        plt.figure(figsize=(10, 6))
        categories = list(report_data['category_breakdown'].keys())
        cat_counts = list(report_data['category_breakdown'].values())
        
        plt.pie(cat_counts, labels=categories, autopct='%1.1f%%', startangle=90)
        plt.title('Category Distribution')
        
        # Save to base64
        img_buffer = io.BytesIO()
        plt.savefig(img_buffer, format='png', bbox_inches='tight')
        img_buffer.seek(0)
        charts['category'] = base64.b64encode(img_buffer.getvalue()).decode()
        plt.close()
        
        return charts
        
    def _get_platform_breakdown(self, trends: List[Dict[str, Any]]) -> Dict[str, int]:
        """Get breakdown of trends by platform."""
        platform_counts = {}
        for trend in trends:
            platform = trend.get('platform', 'unknown')
            platform_counts[platform] = platform_counts.get(platform, 0) + 1
        return platform_counts
        
    def _get_category_breakdown(self, trends: List[Dict[str, Any]]) -> Dict[str, int]:
        """Get breakdown of trends by category."""
        category_counts = {}
        for trend in trends:
            category = trend.get('category', 'uncategorized')
            category_counts[category] = category_counts.get(category, 0) + 1
        return category_counts
        
    def _generate_weekly_csv_report(self, report_data: Dict[str, Any], start_date: str, end_date: str) -> Path:
        """Generate weekly CSV report."""
        csv_path = self.output_dir / f"weekly_report_{start_date}_to_{end_date}.csv"
        
        with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            
            # Write header
            writer.writerow(['Weekly Report', f'{start_date} to {end_date}'])
            writer.writerow(['Generated At', report_data['generated_at']])
            writer.writerow([])
            
            # Write summary
            writer.writerow(['Weekly Summary'])
            writer.writerow(['Total Trends', report_data['total_trends']])
            writer.writerow([])
            
            # Write top trends
            writer.writerow(['Top Trends for the Week'])
            writer.writerow(['Keyword', 'Platform', 'Emerging Score', 'Confidence Score', 'Category'])
            for trend in report_data['top_trends']:
                writer.writerow([
                    trend.get('keyword', ''),
                    trend.get('platform', ''),
                    trend.get('emerging_score', 0),
                    trend.get('confidence_score', 0),
                    trend.get('category', '')
                ])
                
        return csv_path
        
    def _generate_weekly_html_report(self, report_data: Dict[str, Any], start_date: str, end_date: str) -> Path:
        """Generate weekly HTML report."""
        html_path = self.output_dir / f"weekly_report_{start_date}_to_{end_date}.html"
        
        # Similar to daily HTML but with weekly data
        html_template = """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Weekly Trend Report - {{ start_date }} to {{ end_date }}</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; }
                .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                         color: white; padding: 20px; border-radius: 10px; }
                .summary { background: #f8f9fa; padding: 20px; margin: 20px 0; border-radius: 10px; }
                .trends-table { width: 100%; border-collapse: collapse; margin: 20px 0; }
                .trends-table th, .trends-table td { border: 1px solid #ddd; padding: 8px; text-align: left; }
                .trends-table th { background-color: #f2f2f2; }
            </style>
        </head>
        <body>
            <div class="header">
                <h1>📊 Weekly Trend Report</h1>
                <p>{{ start_date }} to {{ end_date }}</p>
            </div>
            
            <div class="summary">
                <h2>📈 Weekly Summary</h2>
                <p><strong>Total Trends Analyzed:</strong> {{ total_trends }}</p>
                <p><strong>Report Period:</strong> {{ start_date }} to {{ end_date }}</p>
            </div>
            
            <h2>🔥 Top Trends for the Week</h2>
            <table class="trends-table">
                <thead>
                    <tr>
                        <th>Keyword</th>
                        <th>Platform</th>
                        <th>Emerging Score</th>
                        <th>Confidence Score</th>
                        <th>Category</th>
                    </tr>
                </thead>
                <tbody>
                    {% for trend in top_trends %}
                    <tr>
                        <td>{{ trend.keyword }}</td>
                        <td>{{ trend.platform }}</td>
                        <td>{{ "%.3f"|format(trend.emerging_score) }}</td>
                        <td>{{ "%.3f"|format(trend.confidence_score) }}</td>
                        <td>{{ trend.category }}</td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </body>
        </html>
        """
        
        template = Template(html_template)
        html_content = template.render(
            start_date=start_date,
            end_date=end_date,
            total_trends=report_data['total_trends'],
            top_trends=report_data['top_trends'],
            generated_at=report_data['generated_at']
        )
        
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
            
        return html_path
        
    def _generate_weekly_pdf_report(self, report_data: Dict[str, Any], start_date: str, end_date: str) -> Path:
        """Generate weekly PDF report."""
        try:
            from fpdf import FPDF
        except ImportError:
            logger.warning("fpdf not available, skipping PDF generation")
            return None
            
        pdf_path = self.output_dir / f"weekly_report_{start_date}_to_{end_date}.pdf"
        
        pdf = FPDF()
        pdf.add_page()
        
        # Title
        pdf.set_font('Arial', 'B', 16)
        pdf.cell(0, 10, f'Weekly Trend Report - {start_date} to {end_date}', ln=True, align='C')
        pdf.ln(10)
        
        # Summary
        pdf.set_font('Arial', 'B', 12)
        pdf.cell(0, 10, 'Weekly Summary', ln=True)
        pdf.set_font('Arial', '', 10)
        pdf.cell(0, 10, f'Total Trends: {report_data["total_trends"]}', ln=True)
        pdf.ln(10)
        
        # Top trends
        pdf.set_font('Arial', 'B', 12)
        pdf.cell(0, 10, 'Top Trends for the Week', ln=True)
        pdf.set_font('Arial', '', 8)
        
        for trend in report_data['top_trends'][:15]:
            pdf.cell(0, 8, f"{trend.get('keyword', '')} - Score: {trend.get('emerging_score', 0):.3f}", ln=True)
            
        pdf.output(str(pdf_path))
        return pdf_path
        
    def _analyze_trend_growth(self, weekly_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze trend growth patterns."""
        # Implementation for trend growth analysis
        return {
            'fastest_growing': weekly_data[:5],
            'most_consistent': weekly_data[5:10],
            'new_trends': [t for t in weekly_data if t.get('growth_rate', 0) == float('inf')]
        }
        
    def _analyze_platform_performance(self, weekly_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze platform performance."""
        platform_stats = {}
        for trend in weekly_data:
            platform = trend.get('platform', 'unknown')
            if platform not in platform_stats:
                platform_stats[platform] = {'count': 0, 'avg_score': 0, 'scores': []}
            platform_stats[platform]['count'] += 1
            platform_stats[platform]['scores'].append(trend.get('emerging_score', 0))
            
        for platform, stats in platform_stats.items():
            stats['avg_score'] = sum(stats['scores']) / len(stats['scores'])
            
        return platform_stats
        
    def _analyze_category_insights(self, weekly_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze category insights."""
        category_stats = {}
        for trend in weekly_data:
            category = trend.get('category', 'uncategorized')
            if category not in category_stats:
                category_stats[category] = {'count': 0, 'avg_score': 0, 'scores': []}
            category_stats[category]['count'] += 1
            category_stats[category]['scores'].append(trend.get('emerging_score', 0))
            
        for category, stats in category_stats.items():
            stats['avg_score'] = sum(stats['scores']) / len(stats['scores'])
            
        return category_stats 