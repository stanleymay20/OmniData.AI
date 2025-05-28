"""
ScrollIntel v2: The Flame Interpreter
Sacred visualization engine with flame-based styling
"""

import plotly.graph_objects as go
import plotly.express as px
from typing import Dict, Any, List, Optional, Union
import pandas as pd
import numpy as np
from datetime import datetime

class ScrollColors:
    """Sacred color codes for ScrollIntel visualizations."""
    GOLD = "#FFD700"  # ScrollGold
    WHITE = "#FFFFFF"  # ScrollWhite
    CRIMSON = "#DC143C"  # ScrollCrimson
    FLAME = ["#FF4500", "#FF8C00", "#FFA500"]  # Flame gradient
    BACKGROUND = "#1A1A1A"  # Dark background
    GRID = "rgba(255, 69, 0, 0.1)"  # Subtle grid

class ScrollGraph:
    """Sacred visualization engine with flame-based styling."""
    
    def __init__(self):
        self.colors = ScrollColors()
        self.watermark = "🔥 ScrollIntel Flame Interpreter v2"
    
    def create_sacred_chart(
        self,
        data: Union[pd.DataFrame, Dict[str, Any]],
        chart_type: str,
        title: str,
        **kwargs
    ) -> go.Figure:
        """Create a sacred chart with flame-based styling."""
        if isinstance(data, dict):
            data = pd.DataFrame(data)
        
        # Create base figure
        if chart_type == "line":
            fig = self._create_line_chart(data, title, **kwargs)
        elif chart_type == "bar":
            fig = self._create_bar_chart(data, title, **kwargs)
        elif chart_type == "scatter":
            fig = self._create_scatter_chart(data, title, **kwargs)
        else:
            raise ValueError(f"Unsupported chart type: {chart_type}")
        
        # Apply sacred styling
        self._apply_sacred_styling(fig, title)
        
        return fig
    
    def _create_line_chart(
        self,
        data: pd.DataFrame,
        title: str,
        **kwargs
    ) -> go.Figure:
        """Create a sacred line chart with flame-based styling."""
        fig = go.Figure()
        
        for column in data.columns:
            fig.add_trace(
                go.Scatter(
                    x=data.index,
                    y=data[column],
                    name=column,
                    line=dict(
                        color=self.colors.FLAME[0],
                        width=2,
                        shape="spline"
                    ),
                    mode="lines+markers",
                    marker=dict(
                        color=self.colors.GOLD,
                        size=8,
                        symbol="circle"
                    )
                )
            )
        
        return fig
    
    def _create_bar_chart(
        self,
        data: pd.DataFrame,
        title: str,
        **kwargs
    ) -> go.Figure:
        """Create a sacred bar chart with flame-based styling."""
        fig = go.Figure()
        
        for column in data.columns:
            fig.add_trace(
                go.Bar(
                    x=data.index,
                    y=data[column],
                    name=column,
                    marker_color=self.colors.FLAME[0],
                    marker_line_color=self.colors.GOLD,
                    marker_line_width=1.5
                )
            )
        
        return fig
    
    def _create_scatter_chart(
        self,
        data: pd.DataFrame,
        title: str,
        **kwargs
    ) -> go.Figure:
        """Create a sacred scatter chart with flame-based styling."""
        fig = go.Figure()
        
        for column in data.columns:
            fig.add_trace(
                go.Scatter(
                    x=data.index,
                    y=data[column],
                    name=column,
                    mode="markers",
                    marker=dict(
                        color=self.colors.FLAME[0],
                        size=12,
                        symbol="circle",
                        line=dict(
                            color=self.colors.GOLD,
                            width=2
                        )
                    )
                )
            )
        
        return fig
    
    def _apply_sacred_styling(self, fig: go.Figure, title: str):
        """Apply sacred styling to the figure."""
        # Update layout
        fig.update_layout(
            title=dict(
                text=f"{title}<br><sup>{self.watermark}</sup>",
                font=dict(
                    family="Arial",
                    size=24,
                    color=self.colors.GOLD
                ),
                x=0.5,
                y=0.95
            ),
            paper_bgcolor=self.colors.BACKGROUND,
            plot_bgcolor=self.colors.BACKGROUND,
            font=dict(
                family="Arial",
                size=12,
                color=self.colors.WHITE
            ),
            xaxis=dict(
                gridcolor=self.colors.GRID,
                zerolinecolor=self.colors.GRID,
                showgrid=True,
                showline=True,
                linecolor=self.colors.GOLD
            ),
            yaxis=dict(
                gridcolor=self.colors.GRID,
                zerolinecolor=self.colors.GRID,
                showgrid=True,
                showline=True,
                linecolor=self.colors.GOLD
            ),
            legend=dict(
                bgcolor="rgba(0,0,0,0)",
                bordercolor=self.colors.GOLD,
                borderwidth=1,
                font=dict(color=self.colors.WHITE)
            ),
            margin=dict(t=100, l=50, r=50, b=50)
        )
        
        # Add sacred annotations
        fig.add_annotation(
            text="🔥",
            xref="paper",
            yref="paper",
            x=0.02,
            y=0.98,
            showarrow=False,
            font=dict(size=20)
        )
        
        # Add timestamp
        fig.add_annotation(
            text=f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            xref="paper",
            yref="paper",
            x=0.98,
            y=0.02,
            showarrow=False,
            font=dict(
                size=10,
                color=self.colors.WHITE
            ),
            align="right"
        )
    
    def add_prophetic_caption(
        self,
        fig: go.Figure,
        caption: str,
        position: str = "bottom"
    ):
        """Add a prophetic caption to the figure."""
        y_pos = 0.02 if position == "bottom" else 0.98
        
        fig.add_annotation(
            text=caption,
            xref="paper",
            yref="paper",
            x=0.5,
            y=y_pos,
            showarrow=False,
            font=dict(
                family="Arial",
                size=14,
                color=self.colors.CRIMSON
            ),
            align="center"
        ) 