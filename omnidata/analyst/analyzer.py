"""
Data Analysis Module for OmniData.AI
"""

from typing import Dict, List, Optional, Union, Any
import pandas as pd
import numpy as np
from sqlalchemy import create_engine, text
import plotly.express as px
import plotly.graph_objects as go
from scipy import stats
import json
from pathlib import Path

class DataAnalyzer:
    """Data analysis and visualization tool."""
    
    def __init__(
        self,
        data: Optional[Union[pd.DataFrame, str]] = None,
        connection_string: Optional[str] = None
    ):
        self.data = None
        self.connection_string = connection_string
        self.engine = None
        
        if isinstance(data, pd.DataFrame):
            self.data = data
        elif isinstance(data, str):
            self.load_data(data)
            
        if connection_string:
            self.engine = create_engine(connection_string)

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

    def execute_query(self, query: str) -> pd.DataFrame:
        """Execute SQL query."""
        if not self.engine:
            raise ValueError("Database connection not configured")
        
        return pd.read_sql(text(query), self.engine)

    def generate_summary(self) -> Dict[str, Any]:
        """Generate statistical summary of the data."""
        if self.data is None:
            raise ValueError("No data loaded")
            
        summary = {
            "shape": self.data.shape,
            "columns": list(self.data.columns),
            "numeric_summary": self.data.describe().to_dict(),
            "missing_values": self.data.isnull().sum().to_dict(),
            "data_types": self.data.dtypes.astype(str).to_dict()
        }
        
        return summary

    def analyze_column(self, column: str) -> Dict[str, Any]:
        """Analyze a specific column."""
        if self.data is None:
            raise ValueError("No data loaded")
            
        if column not in self.data.columns:
            raise ValueError(f"Column {column} not found in data")
            
        col_data = self.data[column]
        
        analysis = {
            "name": column,
            "dtype": str(col_data.dtype),
            "missing_count": col_data.isnull().sum(),
            "unique_count": col_data.nunique()
        }
        
        if np.issubdtype(col_data.dtype, np.number):
            analysis.update({
                "mean": col_data.mean(),
                "median": col_data.median(),
                "std": col_data.std(),
                "skewness": col_data.skew(),
                "kurtosis": col_data.kurtosis(),
                "outliers": self._detect_outliers(col_data)
            })
        elif col_data.dtype == 'object' or col_data.dtype == 'category':
            analysis.update({
                "value_counts": col_data.value_counts().to_dict(),
                "most_common": col_data.mode()[0] if not col_data.empty else None
            })
            
        return analysis

    def create_visualization(
        self,
        viz_type: str,
        x: Optional[str] = None,
        y: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Create visualization using plotly."""
        if self.data is None:
            raise ValueError("No data loaded")
            
        try:
            if viz_type == "scatter":
                fig = px.scatter(self.data, x=x, y=y, **kwargs)
            elif viz_type == "line":
                fig = px.line(self.data, x=x, y=y, **kwargs)
            elif viz_type == "bar":
                fig = px.bar(self.data, x=x, y=y, **kwargs)
            elif viz_type == "histogram":
                fig = px.histogram(self.data, x=x, **kwargs)
            elif viz_type == "box":
                fig = px.box(self.data, x=x, y=y, **kwargs)
            elif viz_type == "heatmap":
                fig = px.imshow(self.data.corr(), **kwargs)
            else:
                raise ValueError(f"Unsupported visualization type: {viz_type}")
                
            return {
                "type": viz_type,
                "figure": fig.to_json()
            }
            
        except Exception as e:
            return {
                "error": str(e)
            }

    def correlation_analysis(
        self,
        columns: Optional[List[str]] = None,
        method: str = 'pearson'
    ) -> Dict[str, Any]:
        """Perform correlation analysis."""
        if self.data is None:
            raise ValueError("No data loaded")
            
        if columns:
            data = self.data[columns]
        else:
            data = self.data.select_dtypes(include=[np.number])
            
        corr_matrix = data.corr(method=method)
        
        return {
            "correlation_matrix": corr_matrix.to_dict(),
            "method": method
        }

    def time_series_analysis(
        self,
        date_column: str,
        value_column: str,
        freq: str = 'D'
    ) -> Dict[str, Any]:
        """Perform time series analysis."""
        if self.data is None:
            raise ValueError("No data loaded")
            
        try:
            # Convert to datetime if needed
            if self.data[date_column].dtype != 'datetime64[ns]':
                self.data[date_column] = pd.to_datetime(self.data[date_column])
            
            # Resample data
            ts_data = self.data.set_index(date_column)[value_column].resample(freq).mean()
            
            analysis = {
                "trend": self._calculate_trend(ts_data),
                "seasonality": self._detect_seasonality(ts_data),
                "statistics": {
                    "mean": ts_data.mean(),
                    "std": ts_data.std(),
                    "min": ts_data.min(),
                    "max": ts_data.max()
                }
            }
            
            return analysis
            
        except Exception as e:
            return {"error": str(e)}

    def _detect_outliers(self, series: pd.Series) -> Dict[str, Any]:
        """Detect outliers using IQR method."""
        Q1 = series.quantile(0.25)
        Q3 = series.quantile(0.75)
        IQR = Q3 - Q1
        
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        
        outliers = series[(series < lower_bound) | (series > upper_bound)]
        
        return {
            "count": len(outliers),
            "percentage": (len(outliers) / len(series)) * 100,
            "bounds": {
                "lower": lower_bound,
                "upper": upper_bound
            }
        }

    def _calculate_trend(self, series: pd.Series) -> Dict[str, float]:
        """Calculate trend using linear regression."""
        x = np.arange(len(series))
        slope, intercept, r_value, p_value, std_err = stats.linregress(x, series)
        
        return {
            "slope": slope,
            "intercept": intercept,
            "r_squared": r_value ** 2,
            "p_value": p_value
        }

    def _detect_seasonality(self, series: pd.Series) -> Dict[str, Any]:
        """Detect seasonality in time series."""
        # Simple seasonality detection using autocorrelation
        acf = pd.Series(series).autocorr(lag=1)
        
        return {
            "autocorrelation": acf,
            "has_seasonality": abs(acf) > 0.7
        } 