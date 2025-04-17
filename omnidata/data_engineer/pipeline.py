"""
Enhanced Data Engineering Pipeline Module for OmniData.AI with autonomous capabilities.
"""

from typing import Dict, List, Optional, Union, Any
import pandas as pd
import dask.dataframe as dd
from sqlalchemy import create_engine
import json
import os
from datetime import datetime
from pathlib import Path
import logging
from concurrent.futures import ThreadPoolExecutor
import numpy as np
from sklearn.preprocessing import StandardScaler

class DataPipeline:
    """Enhanced data pipeline with autonomous capabilities."""
    
    def __init__(
        self,
        name: str,
        source_config: Dict[str, Any],
        destination_config: Dict[str, Any],
        transform_steps: List[Dict[str, Any]],
        auto_optimize: bool = True,
        max_retries: int = 3
    ):
        self.name = name
        self.source_config = source_config
        self.destination_config = destination_config
        self.transform_steps = transform_steps
        self.auto_optimize = auto_optimize
        self.max_retries = max_retries
        self.data = None
        self.metadata = {
            "pipeline_id": f"pipe_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "status": "initialized",
            "start_time": None,
            "end_time": None,
            "rows_processed": 0,
            "optimizations": [],
            "validations": [],
            "errors": []
        }
        
        # Initialize logging
        self.logger = logging.getLogger(f"Pipeline-{self.name}")
        self.logger.setLevel(logging.INFO)
        
        # Initialize optimization metrics
        self.performance_metrics = {
            "memory_usage": [],
            "processing_time": [],
            "throughput": []
        }

    async def extract(self) -> None:
        """Extract data with automated validation and optimization."""
        try:
            self.metadata["status"] = "extracting"
            self.metadata["start_time"] = datetime.now().isoformat()

            # Validate source configuration
            self._validate_source_config()

            # Determine optimal chunk size for reading
            chunk_size = self._calculate_optimal_chunk_size()

            if self.source_config["type"] == "csv":
                if self.auto_optimize:
                    # Use dask for large files
                    file_size = os.path.getsize(self.source_config["path"])
                    if file_size > 1e9:  # 1GB
                        self.data = dd.read_csv(self.source_config["path"])
                        self.metadata["optimizations"].append("Using Dask for large CSV")
                    else:
                        self.data = pd.read_csv(
                            self.source_config["path"],
                            chunksize=chunk_size
                        )
                else:
                    self.data = pd.read_csv(self.source_config["path"])
                    
            elif self.source_config["type"] == "database":
                engine = create_engine(self.source_config["connection_string"])
                if self.auto_optimize:
                    # Use parallel processing for large queries
                    with ThreadPoolExecutor() as executor:
                        self.data = executor.submit(
                            pd.read_sql,
                            self.source_config["query"],
                            engine
                        ).result()
                else:
                    self.data = pd.read_sql(self.source_config["query"], engine)
                    
            elif self.source_config["type"] == "api":
                self.data = self._fetch_api_data()
            
            # Validate extracted data
            self._validate_data_quality()
            
            self.metadata["rows_processed"] = len(self.data)
            
        except Exception as e:
            self.metadata["status"] = "failed"
            self.metadata["errors"].append(str(e))
            self.logger.error(f"Extraction failed: {str(e)}")
            
            if len(self.metadata["errors"]) < self.max_retries:
                self.logger.info("Attempting retry...")
                await self.extract()
            else:
                raise

    async def transform(self) -> None:
        """Transform data with automated optimization and validation."""
        try:
            self.metadata["status"] = "transforming"
            
            # Optimize memory usage
            if self.auto_optimize:
                self._optimize_memory_usage()
            
            for step in self.transform_steps:
                # Validate step configuration
                self._validate_transform_step(step)
                
                # Apply transformation with monitoring
                with self._monitor_transform_step(step):
                    if step["type"] == "filter":
                        self.data = self.data.query(step["condition"])
                    elif step["type"] == "select":
                        self.data = self.data[step["columns"]]
                    elif step["type"] == "rename":
                        self.data = self.data.rename(columns=step["mapping"])
                    elif step["type"] == "aggregate":
                        self.data = self.data.groupby(step["group_by"]).agg(step["aggregations"])
                    elif step["type"] == "custom":
                        custom_func = step["function"]
                        self.data = custom_func(self.data)
                    elif step["type"] == "normalize":
                        self._normalize_numeric_columns(step.get("columns"))
                    elif step["type"] == "clean":
                        self._clean_data(step.get("operations", []))
                
                # Validate transformation result
                self._validate_transformation_result(step)
            
            self.metadata["rows_processed"] = len(self.data)
            
        except Exception as e:
            self.metadata["status"] = "failed"
            self.metadata["errors"].append(str(e))
            self.logger.error(f"Transformation failed: {str(e)}")
            
            if len(self.metadata["errors"]) < self.max_retries:
                self.logger.info("Attempting retry with modified parameters...")
                self._adjust_transform_parameters()
                await self.transform()
            else:
                raise

    async def load(self) -> None:
        """Load data with automated validation and error handling."""
        try:
            self.metadata["status"] = "loading"
            
            # Validate destination configuration
            self._validate_destination_config()
            
            if self.destination_config["type"] == "csv":
                self.data.to_csv(
                    self.destination_config["path"],
                    index=False,
                    compression=self._determine_optimal_compression()
                )
            elif self.destination_config["type"] == "database":
                engine = create_engine(self.destination_config["connection_string"])
                
                if self.auto_optimize:
                    # Use optimal chunk size for database loading
                    chunk_size = self._calculate_optimal_chunk_size()
                    for chunk_start in range(0, len(self.data), chunk_size):
                        chunk = self.data.iloc[chunk_start:chunk_start + chunk_size]
                        chunk.to_sql(
                            self.destination_config["table"],
                            engine,
                            if_exists=self.destination_config.get("if_exists", "fail"),
                            index=False,
                            method='multi'
                        )
                else:
                    self.data.to_sql(
                        self.destination_config["table"],
                        engine,
                        if_exists=self.destination_config.get("if_exists", "fail"),
                        index=False
                    )
            elif self.destination_config["type"] == "parquet":
                self.data.to_parquet(
                    self.destination_config["path"],
                    compression=self._determine_optimal_compression()
                )
            
            self.metadata["status"] = "completed"
            self.metadata["end_time"] = datetime.now().isoformat()
            
        except Exception as e:
            self.metadata["status"] = "failed"
            self.metadata["errors"].append(str(e))
            self.logger.error(f"Loading failed: {str(e)}")
            
            if len(self.metadata["errors"]) < self.max_retries:
                self.logger.info("Attempting retry with modified parameters...")
                self._adjust_load_parameters()
                await self.load()
            else:
                raise

    def _validate_data_quality(self) -> None:
        """Validate data quality with comprehensive checks."""
        validations = []
        
        # Check for missing values
        missing_stats = self.data.isnull().sum()
        if missing_stats.any():
            validations.append({
                "type": "missing_values",
                "details": missing_stats.to_dict()
            })
        
        # Check data types
        type_issues = []
        for column in self.data.columns:
            expected_type = self.source_config.get("schema", {}).get(column, {}).get("type")
            if expected_type and str(self.data[column].dtype) != expected_type:
                type_issues.append({
                    "column": column,
                    "expected": expected_type,
                    "actual": str(self.data[column].dtype)
                })
        
        if type_issues:
            validations.append({
                "type": "data_types",
                "issues": type_issues
            })
        
        # Check for duplicates
        duplicates = self.data.duplicated().sum()
        if duplicates > 0:
            validations.append({
                "type": "duplicates",
                "count": int(duplicates)
            })
        
        self.metadata["validations"].extend(validations)

    def _optimize_memory_usage(self) -> None:
        """Optimize memory usage of the dataframe."""
        initial_memory = self.data.memory_usage().sum()
        
        # Optimize numeric columns
        for column in self.data.select_dtypes(include=['int64', 'float64']).columns:
            col_min = self.data[column].min()
            col_max = self.data[column].max()
            
            if str(self.data[column].dtype) == 'int64':
                if col_min > np.iinfo(np.int32).min and col_max < np.iinfo(np.int32).max:
                    self.data[column] = self.data[column].astype(np.int32)
                elif col_min > np.iinfo(np.int16).min and col_max < np.iinfo(np.int16).max:
                    self.data[column] = self.data[column].astype(np.int16)
            
            elif str(self.data[column].dtype) == 'float64':
                if col_min > np.finfo(np.float32).min and col_max < np.finfo(np.float32).max:
                    self.data[column] = self.data[column].astype(np.float32)
        
        # Optimize categorical columns
        for column in self.data.select_dtypes(include=['object']).columns:
            if self.data[column].nunique() / len(self.data) < 0.5:  # If less than 50% unique values
                self.data[column] = self.data[column].astype('category')
        
        final_memory = self.data.memory_usage().sum()
        memory_saved = initial_memory - final_memory
        
        self.metadata["optimizations"].append({
            "type": "memory_optimization",
            "initial_memory": int(initial_memory),
            "final_memory": int(final_memory),
            "memory_saved": int(memory_saved),
            "percentage_saved": round((memory_saved / initial_memory) * 100, 2)
        })

    def _normalize_numeric_columns(self, columns: Optional[List[str]] = None) -> None:
        """Normalize specified numeric columns."""
        if columns is None:
            columns = self.data.select_dtypes(include=['int64', 'float64']).columns
        
        scaler = StandardScaler()
        self.data[columns] = scaler.fit_transform(self.data[columns])
        
        self.metadata["optimizations"].append({
            "type": "normalization",
            "columns": list(columns)
        })

    def _clean_data(self, operations: List[Dict[str, Any]]) -> None:
        """Clean data based on specified operations."""
        for operation in operations:
            if operation["type"] == "remove_outliers":
                self._remove_outliers(operation["columns"], operation.get("method", "iqr"))
            elif operation["type"] == "fill_missing":
                self._fill_missing_values(operation["columns"], operation.get("method", "mean"))
            elif operation["type"] == "remove_duplicates":
                self.data = self.data.drop_duplicates(
                    subset=operation.get("columns"),
                    keep=operation.get("keep", "first")
                )

    def _calculate_optimal_chunk_size(self) -> int:
        """Calculate optimal chunk size based on available memory."""
        available_memory = os.sysconf('SC_PAGE_SIZE') * os.sysconf('SC_PHYS_PAGES')
        return min(100000, max(1000, int(available_memory / (self.data.memory_usage().mean() * 10))))

    def _determine_optimal_compression(self) -> str:
        """Determine optimal compression method."""
        file_size = self.data.memory_usage().sum()
        if file_size > 1e9:  # 1GB
            return 'gzip'  # Best compression
        elif file_size > 1e8:  # 100MB
            return 'snappy'  # Balance between speed and compression
        else:
            return None  # No compression for small files

    def get_status(self) -> Dict[str, Any]:
        """Get detailed pipeline status and metrics."""
        return {
            "pipeline_id": self.metadata["pipeline_id"],
            "name": self.name,
            "status": self.metadata["status"],
            "progress": {
                "start_time": self.metadata["start_time"],
                "end_time": self.metadata["end_time"],
                "rows_processed": self.metadata["rows_processed"]
            },
            "optimizations": self.metadata["optimizations"],
            "validations": self.metadata["validations"],
            "errors": self.metadata["errors"],
            "performance_metrics": self.performance_metrics
        }

    @staticmethod
    def validate_config(config: Dict[str, Any]) -> bool:
        """Validate pipeline configuration with detailed checks."""
        try:
            # Validate source configuration
            if "source" not in config:
                return False
            
            source_type = config["source"].get("type")
            if source_type not in ["csv", "database", "api", "parquet"]:
                return False
            
            # Validate source-specific requirements
            if source_type in ["csv", "parquet"]:
                if "path" not in config["source"]:
                    return False
            elif source_type == "database":
                if "connection_string" not in config["source"]:
                    return False
            elif source_type == "api":
                if "url" not in config["source"]:
                    return False
            
            # Validate destination configuration
            if "destination" not in config:
                return False
            
            dest_type = config["destination"].get("type")
            if dest_type not in ["csv", "database", "parquet"]:
                return False
            
            # Validate destination-specific requirements
            if dest_type in ["csv", "parquet"]:
                if "path" not in config["destination"]:
                    return False
            elif dest_type == "database":
                if not all(key in config["destination"] for key in ["connection_string", "table"]):
                    return False
            
            # Validate transform steps
            if "transform_steps" not in config or not isinstance(config["transform_steps"], list):
                return False
            
            # Validate each transform step
            valid_step_types = ["filter", "select", "rename", "aggregate", "custom", "normalize", "clean"]
            for step in config["transform_steps"]:
                if "type" not in step or step["type"] not in valid_step_types:
                    return False
                
                # Validate step-specific requirements
                if step["type"] == "filter" and "condition" not in step:
                    return False
                elif step["type"] == "select" and "columns" not in step:
                    return False
                elif step["type"] == "rename" and "mapping" not in step:
                    return False
                elif step["type"] == "aggregate" and not all(key in step for key in ["group_by", "aggregations"]):
                    return False
                elif step["type"] == "custom" and "function" not in step:
                    return False
            
            return True
            
        except Exception:
            return False 