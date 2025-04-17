"""
Healthcare Data Visualization Module for OmniData.AI

This module provides a comprehensive set of visualization tools for healthcare data analysis,
including risk scores, length of stay, laboratory trends, and readmission patterns.
"""

from typing import List, Optional, Tuple, Union

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots


class HealthcareVisualizer:
    """A class for creating interactive healthcare data visualizations using Plotly."""

    def __init__(self, theme: str = "plotly_white"):
        """
        Initialize the HealthcareVisualizer with a specified theme.

        Args:
            theme (str): The Plotly theme to use for visualizations. Defaults to "plotly_white".
        """
        self.theme = theme

    def create_risk_timeline(
        self,
        timestamps: List[str],
        risk_scores: List[float],
        thresholds: Optional[List[Tuple[str, float]]] = None,
        title: str = "Risk Score Timeline",
    ) -> go.Figure:
        """
        Create a timeline visualization of risk scores with optional threshold lines.

        Args:
            timestamps: List of timestamp strings
            risk_scores: List of risk score values
            thresholds: List of tuples containing (threshold_name, threshold_value)
            title: Title for the visualization

        Returns:
            Plotly Figure object
        """
        fig = go.Figure()

        # Add main risk score line
        fig.add_trace(
            go.Scatter(
                x=timestamps,
                y=risk_scores,
                mode="lines+markers",
                name="Risk Score",
                line=dict(color="#1f77b4", width=2),
                marker=dict(size=8),
            )
        )

        # Add threshold lines if provided
        if thresholds:
            for threshold_name, threshold_value in thresholds:
                fig.add_hline(
                    y=threshold_value,
                    line_dash="dash",
                    line_color="red",
                    annotation_text=threshold_name,
                    annotation_position="right",
                )

        fig.update_layout(
            template=self.theme,
            title=title,
            xaxis_title="Time",
            yaxis_title="Risk Score",
            showlegend=True,
            hovermode="x unified",
        )

        return fig

    def create_los_distribution(
        self,
        actual_los: List[float],
        predicted_los: List[float],
        title: str = "Length of Stay Distribution",
    ) -> go.Figure:
        """
        Create a distribution plot comparing actual vs predicted length of stay.

        Args:
            actual_los: List of actual length of stay values
            predicted_los: List of predicted length of stay values
            title: Title for the visualization

        Returns:
            Plotly Figure object
        """
        fig = go.Figure()

        fig.add_trace(
            go.Histogram(
                x=actual_los,
                name="Actual LOS",
                opacity=0.75,
                nbinsx=30,
            )
        )

        fig.add_trace(
            go.Histogram(
                x=predicted_los,
                name="Predicted LOS",
                opacity=0.75,
                nbinsx=30,
            )
        )

        fig.update_layout(
            template=self.theme,
            title=title,
            xaxis_title="Length of Stay (days)",
            yaxis_title="Count",
            barmode="overlay",
            showlegend=True,
        )

        return fig

    def create_lab_trend(
        self,
        timestamps: List[str],
        values: List[float],
        lab_name: str,
        unit: str,
        reference_range: Optional[Tuple[float, float]] = None,
    ) -> go.Figure:
        """
        Create a trend visualization for laboratory results.

        Args:
            timestamps: List of timestamp strings
            values: List of laboratory result values
            lab_name: Name of the laboratory test
            unit: Unit of measurement
            reference_range: Tuple of (lower_bound, upper_bound) for reference range

        Returns:
            Plotly Figure object
        """
        fig = go.Figure()

        # Add main lab value line
        fig.add_trace(
            go.Scatter(
                x=timestamps,
                y=values,
                mode="lines+markers",
                name=f"{lab_name} ({unit})",
                line=dict(color="#2ecc71", width=2),
                marker=dict(size=8),
            )
        )

        # Add reference range if provided
        if reference_range:
            lower, upper = reference_range
            fig.add_hrect(
                y0=lower,
                y1=upper,
                fillcolor="rgba(128, 128, 128, 0.2)",
                line_width=0,
                name="Reference Range",
            )

        fig.update_layout(
            template=self.theme,
            title=f"{lab_name} Trend Over Time",
            xaxis_title="Time",
            yaxis_title=f"{lab_name} ({unit})",
            showlegend=True,
            hovermode="x unified",
        )

        return fig

    def create_readmission_heatmap(
        self,
        data: pd.DataFrame,
        departments: List[str],
        time_periods: List[str],
        title: str = "Readmission Rates by Department",
    ) -> go.Figure:
        """
        Create a heatmap of readmission rates by department and time period.

        Args:
            data: DataFrame containing readmission rates
            departments: List of department names
            time_periods: List of time period labels
            title: Title for the visualization

        Returns:
            Plotly Figure object
        """
        fig = go.Figure(
            data=go.Heatmap(
                z=data.values,
                x=time_periods,
                y=departments,
                colorscale="RdYlBu_r",
                text=data.values,
                texttemplate="%{text:.1%}",
                textfont={"size": 10},
                hoverongaps=False,
            )
        )

        fig.update_layout(
            template=self.theme,
            title=title,
            xaxis_title="Time Period",
            yaxis_title="Department",
            yaxis_autorange="reversed",
        )

        return fig

    def create_los_boxplot(
        self,
        los_values: List[float],
        categories: List[str],
        category_name: str,
        title: str = "Length of Stay Distribution by Category",
    ) -> go.Figure:
        """
        Create a box plot of length of stay data grouped by category.

        Args:
            los_values: List of length of stay values
            categories: List of category labels
            category_name: Name of the grouping category
            title: Title for the visualization

        Returns:
            Plotly Figure object
        """
        df = pd.DataFrame({
            "LOS": los_values,
            category_name: categories
        })

        fig = px.box(
            df,
            x=category_name,
            y="LOS",
            title=title,
            template=self.theme,
        )

        fig.update_layout(
            yaxis_title="Length of Stay (days)",
            showlegend=False,
        )

        return fig

    def create_risk_factors_chart(
        self,
        factors: List[str],
        importance_scores: List[float],
        title: str = "Risk Factor Importance",
    ) -> go.Figure:
        """
        Create a horizontal bar chart of risk factors and their importance scores.

        Args:
            factors: List of risk factor names
            importance_scores: List of importance scores
            title: Title for the visualization

        Returns:
            Plotly Figure object
        """
        # Sort factors by importance
        sorted_indices = np.argsort(importance_scores)
        factors = [factors[i] for i in sorted_indices]
        importance_scores = [importance_scores[i] for i in sorted_indices]

        fig = go.Figure(
            go.Bar(
                x=importance_scores,
                y=factors,
                orientation="h",
                marker_color="#3498db",
            )
        )

        fig.update_layout(
            template=self.theme,
            title=title,
            xaxis_title="Importance Score",
            yaxis_title="Risk Factor",
            showlegend=False,
        )

        return fig 