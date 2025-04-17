"""
Business Intelligence Dashboard Module for OmniData.AI
"""

from typing import Dict, List, Optional, Union, Any
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json
from datetime import datetime, timedelta
from pathlib import Path

class Dashboard:
    """Business Intelligence Dashboard Generator."""
    
    def __init__(
        self,
        data: Optional[Union[pd.DataFrame, str]] = None,
        title: str = "OmniData.AI Dashboard",
        description: str = ""
    ):
        self.data = None
        self.title = title
        self.description = description
        self.charts = []
        self.filters = {}
        self.layout = {}
        
        if isinstance(data, pd.DataFrame):
            self.data = data
        elif isinstance(data, str):
            self.load_data(data)

    def load_data(self, path: str) -> None:
        """Load data from file."""
        if path.endswith('.csv'):
            self.data = pd.read_csv(path)
        elif path.endswith('.parquet'):
            self.data = pd.read_parquet(path)
        elif path.endswith('.json'):
            self.data = pd.read_json(path)
        else:
            raise ValueError("Unsupported file format")

    def add_chart(
        self,
        chart_type: str,
        metrics: List[str],
        dimensions: List[str],
        title: str,
        filters: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Add a chart to the dashboard."""
        try:
            # Apply filters if provided
            data = self.data.copy()
            if filters:
                for col, value in filters.items():
                    if isinstance(value, (list, tuple)):
                        data = data[data[col].isin(value)]
                    else:
                        data = data[data[col] == value]
            
            # Create chart based on type
            if chart_type == "line":
                fig = self._create_line_chart(data, metrics, dimensions, **kwargs)
            elif chart_type == "bar":
                fig = self._create_bar_chart(data, metrics, dimensions, **kwargs)
            elif chart_type == "pie":
                fig = self._create_pie_chart(data, metrics[0], dimensions[0], **kwargs)
            elif chart_type == "scatter":
                fig = self._create_scatter_chart(data, metrics, dimensions, **kwargs)
            elif chart_type == "table":
                fig = self._create_table_chart(data, metrics, dimensions, **kwargs)
            else:
                raise ValueError(f"Unsupported chart type: {chart_type}")
            
            # Update chart layout
            fig.update_layout(
                title=title,
                template="plotly_white",
                **kwargs.get("layout", {})
            )
            
            # Add chart to dashboard
            chart_id = f"chart_{len(self.charts)}"
            self.charts.append({
                "id": chart_id,
                "type": chart_type,
                "title": title,
                "figure": fig,
                "metrics": metrics,
                "dimensions": dimensions,
                "filters": filters
            })
            
            return {
                "status": "success",
                "chart_id": chart_id
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }

    def add_filter(
        self,
        column: str,
        filter_type: str = "select",
        default_value: Any = None
    ) -> Dict[str, Any]:
        """Add a filter to the dashboard."""
        try:
            if column not in self.data.columns:
                raise ValueError(f"Column {column} not found in data")
            
            filter_id = f"filter_{len(self.filters)}"
            self.filters[filter_id] = {
                "column": column,
                "type": filter_type,
                "default": default_value,
                "values": self.data[column].unique().tolist() if filter_type == "select" else None
            }
            
            return {
                "status": "success",
                "filter_id": filter_id
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }

    def update_layout(
        self,
        layout_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update dashboard layout configuration."""
        try:
            self.layout = {
                **self.layout,
                **layout_config
            }
            
            return {
                "status": "success",
                "layout": self.layout
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }

    def generate_dashboard(self) -> Dict[str, Any]:
        """Generate the complete dashboard."""
        try:
            # Create dashboard container
            dashboard = {
                "title": self.title,
                "description": self.description,
                "created_at": datetime.now().isoformat(),
                "charts": [],
                "filters": self.filters,
                "layout": self.layout
            }
            
            # Add charts
            for chart in self.charts:
                dashboard["charts"].append({
                    "id": chart["id"],
                    "type": chart["type"],
                    "title": chart["title"],
                    "figure": chart["figure"].to_json(),
                    "metrics": chart["metrics"],
                    "dimensions": chart["dimensions"],
                    "filters": chart["filters"]
                })
            
            return {
                "status": "success",
                "dashboard": dashboard
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }

    def save_dashboard(self, path: str) -> Dict[str, Any]:
        """Save dashboard to file."""
        try:
            dashboard = self.generate_dashboard()
            
            if dashboard["status"] == "error":
                return dashboard
            
            # Save to file
            with open(path, "w") as f:
                json.dump(dashboard["dashboard"], f)
            
            return {
                "status": "success",
                "path": path
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }

    def _create_line_chart(
        self,
        data: pd.DataFrame,
        metrics: List[str],
        dimensions: List[str],
        **kwargs
    ) -> go.Figure:
        """Create a line chart."""
        fig = go.Figure()
        
        for metric in metrics:
            for dim_value in data[dimensions[0]].unique():
                dim_data = data[data[dimensions[0]] == dim_value]
                fig.add_trace(
                    go.Scatter(
                        x=dim_data[dimensions[1]] if len(dimensions) > 1 else dim_data.index,
                        y=dim_data[metric],
                        name=f"{metric} - {dim_value}",
                        mode="lines+markers"
                    )
                )
        
        return fig

    def _create_bar_chart(
        self,
        data: pd.DataFrame,
        metrics: List[str],
        dimensions: List[str],
        **kwargs
    ) -> go.Figure:
        """Create a bar chart."""
        if len(dimensions) > 1:
            # Grouped bar chart
            fig = px.bar(
                data,
                x=dimensions[0],
                y=metrics[0],
                color=dimensions[1],
                barmode="group"
            )
        else:
            # Simple bar chart
            fig = px.bar(
                data,
                x=dimensions[0],
                y=metrics
            )
        
        return fig

    def _create_pie_chart(
        self,
        data: pd.DataFrame,
        metric: str,
        dimension: str,
        **kwargs
    ) -> go.Figure:
        """Create a pie chart."""
        fig = px.pie(
            data,
            values=metric,
            names=dimension
        )
        
        return fig

    def _create_scatter_chart(
        self,
        data: pd.DataFrame,
        metrics: List[str],
        dimensions: List[str],
        **kwargs
    ) -> go.Figure:
        """Create a scatter chart."""
        fig = px.scatter(
            data,
            x=metrics[0],
            y=metrics[1] if len(metrics) > 1 else None,
            color=dimensions[0] if dimensions else None,
            size=metrics[2] if len(metrics) > 2 else None
        )
        
        return fig

    def _create_table_chart(
        self,
        data: pd.DataFrame,
        metrics: List[str],
        dimensions: List[str],
        **kwargs
    ) -> go.Figure:
        """Create a table visualization."""
        fig = go.Figure(data=[
            go.Table(
                header=dict(
                    values=[*dimensions, *metrics],
                    fill_color="paleturquoise",
                    align="left"
                ),
                cells=dict(
                    values=[data[col] for col in [*dimensions, *metrics]],
                    fill_color="lavender",
                    align="left"
                )
            )
        ])
        
        return fig 