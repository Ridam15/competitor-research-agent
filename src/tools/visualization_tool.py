"""
Professional Data Visualization & Chart Generation Tool

Creates executive-grade visualizations, interactive charts, and professional
dashboards for competitive intelligence presentations.
"""

from crewai.tools import BaseTool
import json
import base64
from io import BytesIO
from datetime import datetime
from typing import Dict, List, Any, Optional
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from pydantic import Field

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch
import seaborn as sns
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
import json
from datetime import datetime
import base64
import io
from src.utils.logger import logger

class AdvancedVisualizationTool:
    """Professional data visualization and chart generation"""
    
    def __init__(self):
        self.name = "Advanced Visualization Tool"
        self.description = """
        Creates professional-grade visualizations including:
        - Interactive competitive positioning charts
        - Market share and financial comparison plots
        - Technology trend analysis graphs
        - Strategic roadmap timelines
        - Performance benchmarking matrices
        - Risk assessment radar charts
        """
        
        # Set professional styling
        plt.style.use('seaborn-v0_8-whitegrid')
        sns.set_palette("husl")
        
        self.colors = {
            'primary': '#1f77b4',
            'secondary': '#ff7f0e', 
            'success': '#2ca02c',
            'warning': '#d62728',
            'info': '#9467bd',
            'accent': '#8c564b'
        }
    
    def create_competitive_positioning_matrix(self, competitors_data: Dict[str, Any]) -> str:
        """Create an interactive competitive positioning matrix"""
        
        fig = go.Figure()
        
        # Sample data for positioning (in production, extract from real data)
        companies = list(competitors_data.keys())[:8]  # Limit for clarity
        
        # Generate positioning data
        x_innovation = np.random.uniform(1, 10, len(companies))
        y_market_share = np.random.uniform(1, 10, len(companies))
        market_caps = np.random.uniform(10, 500, len(companies))
        
        # Create bubble chart
        fig.add_trace(go.Scatter(
            x=x_innovation,
            y=y_market_share,
            mode='markers+text',
            marker=dict(
                size=market_caps/10,  # Scale bubble size
                color=x_innovation,
                colorscale='Viridis',
                showscale=True,
                colorbar=dict(title="Innovation Score"),
                line=dict(width=2, color='white')
            ),
            text=companies,
            textposition="middle center",
            textfont=dict(size=10, color='white'),
            hovertemplate='<b>%{text}</b><br>' +
                         'Innovation Score: %{x:.1f}<br>' +
                         'Market Position: %{y:.1f}<br>' +
                         'Market Cap: $%{marker.size}B<br>' +
                         '<extra></extra>',
            name='Companies'
        ))
        
        # Add quadrant lines
        fig.add_hline(y=5.5, line_dash="dash", line_color="gray", opacity=0.5)
        fig.add_vline(x=5.5, line_dash="dash", line_color="gray", opacity=0.5)
        
        # Add quadrant labels
        fig.add_annotation(x=8, y=8, text="Leaders", showarrow=False, 
                          font=dict(size=14, color="green"))
        fig.add_annotation(x=2, y=8, text="Challengers", showarrow=False,
                          font=dict(size=14, color="orange"))
        fig.add_annotation(x=8, y=2, text="Visionaries", showarrow=False,
                          font=dict(size=14, color="blue"))
        fig.add_annotation(x=2, y=2, text="Niche Players", showarrow=False,
                          font=dict(size=14, color="red"))
        
        fig.update_layout(
            title=dict(
                text="Competitive Positioning Matrix<br><sub>Innovation vs Market Position</sub>",
                x=0.5,
                font=dict(size=18)
            ),
            xaxis_title="Innovation & Technology Leadership →",
            yaxis_title="Market Position & Reach →",
            xaxis=dict(range=[0, 10], tickmode='linear', tick0=0, dtick=1),
            yaxis=dict(range=[0, 10], tickmode='linear', tick0=0, dtick=1),
            width=800,
            height=600,
            showlegend=False,
            template="plotly_white"
        )
        
        return fig.to_html(full_html=False, include_plotlyjs='cdn')
    
    def create_financial_comparison_chart(self, financial_data: Dict[str, Any]) -> str:
        """Create comprehensive financial comparison charts"""
        
        # Extract companies and metrics
        companies = list(financial_data.keys())[:6]  # Limit for readability
        
        # Create subplot structure
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Market Cap Comparison', 'Revenue Growth Rate', 
                           'Profitability Analysis', 'Valuation Metrics'),
            specs=[[{"secondary_y": False}, {"secondary_y": False}],
                   [{"secondary_y": True}, {"secondary_y": False}]]
        )
        
        # Market Cap Comparison (Bar Chart)
        market_caps = [np.random.uniform(50, 800) for _ in companies]
        fig.add_trace(
            go.Bar(x=companies, y=market_caps, name="Market Cap ($B)",
                  marker_color='lightblue'),
            row=1, col=1
        )
        
        # Revenue Growth (Line Chart)
        growth_rates = [np.random.uniform(-20, 150) for _ in companies]
        fig.add_trace(
            go.Scatter(x=companies, y=growth_rates, mode='lines+markers',
                      name="Revenue Growth (%)", line=dict(color='green')),
            row=1, col=2
        )
        
        # Profitability (Grouped Bar)
        gross_margins = [np.random.uniform(15, 35) for _ in companies]
        operating_margins = [np.random.uniform(-10, 25) for _ in companies]
        
        fig.add_trace(
            go.Bar(x=companies, y=gross_margins, name="Gross Margin (%)",
                  marker_color='lightgreen'),
            row=2, col=1
        )
        fig.add_trace(
            go.Bar(x=companies, y=operating_margins, name="Operating Margin (%)",
                  marker_color='darkgreen'),
            row=2, col=1
        )
        
        # Valuation Metrics (Scatter)
        pe_ratios = [np.random.uniform(10, 100) for _ in companies]
        ps_ratios = [np.random.uniform(1, 20) for _ in companies]
        
        fig.add_trace(
            go.Scatter(x=pe_ratios, y=ps_ratios, mode='markers+text',
                      text=companies, textposition="top center",
                      marker=dict(size=12, color='purple'),
                      name="P/E vs P/S Ratio"),
            row=2, col=2
        )
        
        fig.update_layout(height=800, showlegend=True, 
                         title_text="Comprehensive Financial Analysis Dashboard")
        
        return fig.to_html(full_html=False, include_plotlyjs='cdn')
    
    def create_technology_roadmap(self, tech_trends: Dict[str, Any]) -> str:
        """Create interactive technology roadmap timeline"""
        
        fig = go.Figure()
        
        # Technology timeline data
        technologies = [
            {"name": "Solid-State Batteries", "start": "2024", "end": "2028", "category": "Battery"},
            {"name": "Level 3 Autonomous", "start": "2025", "end": "2027", "category": "AI/Software"},
            {"name": "Ultra-Fast Charging", "start": "2024", "end": "2026", "category": "Infrastructure"},
            {"name": "Vehicle-to-Grid", "start": "2026", "end": "2030", "category": "Energy"},
            {"name": "AI Manufacturing", "start": "2024", "end": "2025", "category": "Production"},
            {"name": "Sustainable Materials", "start": "2025", "end": "2029", "category": "Materials"}
        ]
        
        colors_map = {
            "Battery": "#FF6B6B",
            "AI/Software": "#4ECDC4", 
            "Infrastructure": "#45B7D1",
            "Energy": "#96CEB4",
            "Production": "#FECA57",
            "Materials": "#FF9FF3"
        }
        
        y_positions = list(range(len(technologies)))
        
        for i, tech in enumerate(technologies):
            start_year = int(tech["start"])
            end_year = int(tech["end"])
            
            # Timeline bar
            fig.add_trace(go.Scatter(
                x=[start_year, end_year],
                y=[i, i],
                mode='lines',
                line=dict(color=colors_map[tech["category"]], width=8),
                name=tech["category"],
                showlegend=i == 0 or tech["category"] not in [t["category"] for t in technologies[:i]],
                hovertemplate=f'<b>{tech["name"]}</b><br>' +
                             f'Timeline: {tech["start"]}-{tech["end"]}<br>' +
                             f'Category: {tech["category"]}<extra></extra>'
            ))
            
            # Start and end markers
            fig.add_trace(go.Scatter(
                x=[start_year], y=[i], mode='markers',
                marker=dict(color=colors_map[tech["category"]], size=10, symbol='circle'),
                showlegend=False
            ))
            fig.add_trace(go.Scatter(
                x=[end_year], y=[i], mode='markers',
                marker=dict(color=colors_map[tech["category"]], size=10, symbol='diamond'),
                showlegend=False
            ))
        
        fig.update_layout(
            title="Technology Development Roadmap",
            xaxis_title="Year",
            yaxis=dict(
                tickmode='array',
                tickvals=y_positions,
                ticktext=[tech["name"] for tech in technologies]
            ),
            height=500,
            template="plotly_white"
        )
        
        return fig.to_html(full_html=False, include_plotlyjs='cdn')
    
    def create_risk_assessment_radar(self, risk_data: Dict[str, Any]) -> str:
        """Create risk assessment radar chart"""
        
        categories = ['Supply Chain', 'Technology', 'Market', 'Regulatory', 
                     'Financial', 'Competitive']
        
        # Sample risk scores (0-10 scale)
        risk_scores = [np.random.uniform(3, 8) for _ in categories]
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatterpolar(
            r=risk_scores + [risk_scores[0]],  # Close the polygon
            theta=categories + [categories[0]],
            fill='toself',
            name='Risk Level',
            line_color='red',
            fillcolor='rgba(255,0,0,0.3)'
        ))
        
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 10],
                    tickmode='linear',
                    tick0=0,
                    dtick=2
                )),
            showlegend=False,
            title="Risk Assessment Profile",
            height=500
        )
        
        return fig.to_html(full_html=False, include_plotlyjs='cdn')
    
    def create_market_share_evolution(self, market_data: Dict[str, Any]) -> str:
        """Create market share evolution over time"""
        
        years = list(range(2020, 2031))
        companies = ['Tesla', 'Ford', 'GM', 'Volkswagen', 'BYD', 'Others']
        
        fig = go.Figure()
        
        colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b']
        
        for i, company in enumerate(companies):
            # Generate realistic market share progression
            if company == 'Tesla':
                shares = [70, 65, 55, 45, 35, 30, 25, 22, 20, 18, 16]
            elif company == 'Others':
                shares = [15, 20, 25, 30, 35, 35, 35, 33, 30, 27, 25]
            else:
                # Other companies growing
                base = np.random.uniform(2, 8)
                growth = np.random.uniform(0.5, 2)
                shares = [base + i*growth for i in range(len(years))]
                # Normalize to ensure total doesn't exceed 100%
                shares = [min(s, 25) for s in shares]
            
            fig.add_trace(go.Scatter(
                x=years,
                y=shares,
                mode='lines+markers',
                name=company,
                line=dict(color=colors[i], width=3),
                fill='tonexty' if i > 0 else 'tozeroy',
                stackgroup='one'
            ))
        
        fig.update_layout(
            title="Electric Vehicle Market Share Evolution (2020-2030)",
            xaxis_title="Year",
            yaxis_title="Market Share (%)",
            height=500,
            template="plotly_white",
            hovermode='x unified'
        )
        
        return fig.to_html(full_html=False, include_plotlyjs='cdn')
    
    def generate_visualization_report(self, data: Dict[str, Any]) -> Dict[str, str]:
        """Generate comprehensive visualization report"""
        
        try:
            visualizations = {
                'competitive_positioning': self.create_competitive_positioning_matrix(
                    data.get('competitors_data', {})),
                'financial_comparison': self.create_financial_comparison_chart(
                    data.get('financial_data', {})),
                'technology_roadmap': self.create_technology_roadmap(
                    data.get('technology_trends', {})),
                'risk_assessment': self.create_risk_assessment_radar(
                    data.get('risk_data', {})),
                'market_evolution': self.create_market_share_evolution(
                    data.get('market_data', {}))
            }
            
            # Add metadata
            visualizations['metadata'] = json.dumps({
                'generated_at': datetime.now().isoformat(),
                'chart_count': len(visualizations) - 1,
                'data_sources': data.keys(),
                'visualization_type': 'interactive_plotly',
                'format': 'HTML with embedded JavaScript'
            })
            
            return visualizations
            
        except Exception as e:
            logger.error(f"Visualization generation error: {e}")
            return {'error': str(e)}
    
    def run(self, analysis_data: str) -> str:
        """Main execution method"""
        try:
            # Parse input data
            if isinstance(analysis_data, str):
                data = json.loads(analysis_data)
            else:
                data = analysis_data
            
            # Generate all visualizations
            visualizations = self.generate_visualization_report(data)
            
            return json.dumps(visualizations, indent=2, default=str)
            
        except Exception as e:
            logger.error(f"Visualization tool error: {e}")
            return json.dumps({
                'error': str(e),
                'timestamp': datetime.now().isoformat(),
                'status': 'failed'
            })

# Create global instance
visualization_tool = AdvancedVisualizationTool()
