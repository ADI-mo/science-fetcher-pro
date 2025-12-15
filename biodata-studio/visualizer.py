"""
מודול ויזואליזציה - גרפים אינטראקטיביים
"""

import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import numpy as np
import pandas as pd


class Visualizer:
    """יוצר ויזואליזציות אינטראקטיביות"""
    
    def __init__(self, analyzer):
        """
        Args:
            analyzer: GrowthCurveAnalyzer instance
        """
        self.analyzer = analyzer
        self.time_col, self.od_cols = analyzer._identify_columns()
    
    def plot_growth_curves(self, show_fitted=True):
        """
        מצייר את כל ה-growth curves
        
        Args:
            show_fitted: האם להציג גם את ה-fitted models
        """
        fig = go.Figure()
        
        time = self.analyzer.data[self.time_col].values
        
        for col in self.od_cols:
            od = self.analyzer.data[col].values
            
            # נתונים אמיתיים
            fig.add_trace(go.Scatter(
                x=time,
                y=od,
                mode='markers+lines',
                name=col,
                marker=dict(size=8),
                line=dict(width=2)
            ))
            
            # fitted curve
            if show_fitted and col in self.analyzer.fitted_curves:
                fitted_data = self.analyzer.fitted_curves[col]['fitted']
                fig.add_trace(go.Scatter(
                    x=time,
                    y=fitted_data,
                    mode='lines',
                    name=f'{col} (fitted)',
                    line=dict(dash='dash', width=2),
                    opacity=0.7
                ))
        
        fig.update_layout(
            title='Growth Curves Analysis',
            xaxis_title='Time (hours)',
            yaxis_title='OD600',
            hovermode='x unified',
            template='plotly_white',
            width=1000,
            height=600,
            font=dict(size=14)
        )
        
        return fig
    
    def plot_growth_rate_comparison(self):
        """השוואת growth rates בין דגימות"""
        if self.analyzer.results is None:
            raise ValueError("רוץ analyze() קודם")
        
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            x=self.analyzer.results['Sample'],
            y=self.analyzer.results['Growth_Rate (1/h)'],
            marker=dict(
                color=self.analyzer.results['Growth_Rate (1/h)'],
                colorscale='Viridis',
                showscale=True,
                colorbar=dict(title="Growth Rate")
            ),
            text=self.analyzer.results['Growth_Rate (1/h)'].round(3),
            textposition='outside'
        ))
        
        fig.update_layout(
            title='Growth Rate Comparison',
            xaxis_title='Sample',
            yaxis_title='Growth Rate (1/h)',
            template='plotly_white',
            width=900,
            height=500
        )
        
        return fig
    
    def plot_parameter_heatmap(self):
        """Heatmap של כל הפרמטרים"""
        if self.analyzer.results is None:
            raise ValueError("רוץ analyze() קודם")
        
        # נורמליזציה לכל עמודה
        numeric_cols = ['Max_OD', 'Growth_Rate (1/h)', 'Doubling_Time (h)', 'Lag_Phase (h)', 'AUC']
        data_normalized = self.analyzer.results[numeric_cols].copy()
        
        for col in numeric_cols:
            min_val = data_normalized[col].min()
            max_val = data_normalized[col].max()
            if max_val - min_val > 0:
                data_normalized[col] = (data_normalized[col] - min_val) / (max_val - min_val)
        
        fig = go.Figure(data=go.Heatmap(
            z=data_normalized.T.values,
            x=self.analyzer.results['Sample'],
            y=numeric_cols,
            colorscale='RdYlGn',
            text=self.analyzer.results[numeric_cols].T.values.round(2),
            texttemplate='%{text}',
            textfont={"size": 10},
            colorbar=dict(title="Normalized<br>Value")
        ))
        
        fig.update_layout(
            title='Growth Parameters Heatmap (Normalized)',
            xaxis_title='Sample',
            yaxis_title='Parameter',
            template='plotly_white',
            width=1000,
            height=500
        )
        
        return fig
    
    def plot_doubling_time_distribution(self):
        """התפלגות של doubling times"""
        if self.analyzer.results is None:
            raise ValueError("רוץ analyze() קודם")
        
        fig = go.Figure()
        
        fig.add_trace(go.Box(
            y=self.analyzer.results['Doubling_Time (h)'],
            x=self.analyzer.results['Sample'],
            marker=dict(color='lightseagreen'),
            boxmean='sd'
        ))
        
        fig.update_layout(
            title='Doubling Time Distribution',
            xaxis_title='Sample',
            yaxis_title='Doubling Time (hours)',
            template='plotly_white',
            width=900,
            height=500
        )
        
        return fig
    
    def plot_summary_dashboard(self):
        """Dashboard מלא עם כל הגרפים"""
        if self.analyzer.results is None:
            raise ValueError("רוץ analyze() קודם")
        
        # יצירת subplots
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Growth Curves', 'Growth Rate Comparison',
                          'Parameter Heatmap', 'Doubling Time'),
            specs=[[{"type": "scatter"}, {"type": "bar"}],
                   [{"type": "heatmap"}, {"type": "box"}]]
        )
        
        # Growth curves
        time = self.analyzer.data[self.time_col].values
        for col in self.od_cols[:5]:  # רק 5 ראשונים למען הבהירות
            od = self.analyzer.data[col].values
            fig.add_trace(
                go.Scatter(x=time, y=od, mode='lines+markers', name=col,
                          showlegend=False),
                row=1, col=1
            )
        
        # Growth rates
        fig.add_trace(
            go.Bar(x=self.analyzer.results['Sample'],
                  y=self.analyzer.results['Growth_Rate (1/h)'],
                  showlegend=False, marker_color='indianred'),
            row=1, col=2
        )
        
        # Heatmap
        numeric_cols = ['Max_OD', 'Growth_Rate (1/h)', 'AUC']
        fig.add_trace(
            go.Heatmap(z=self.analyzer.results[numeric_cols].T.values,
                      x=self.analyzer.results['Sample'],
                      y=numeric_cols,
                      colorscale='Viridis',
                      showscale=False),
            row=2, col=1
        )
        
        # Box plot
        fig.add_trace(
            go.Box(y=self.analyzer.results['Doubling_Time (h)'],
                  showlegend=False, marker_color='lightseagreen'),
            row=2, col=2
        )
        
        fig.update_layout(
            title_text="Growth Analysis Dashboard",
            height=900,
            width=1400,
            showlegend=False,
            template='plotly_white'
        )
        
        return fig
