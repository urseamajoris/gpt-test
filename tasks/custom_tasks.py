"""
Custom task implementations for specialized use cases.

This module contains custom tasks that extend the base task functionality
for specific domain applications.
"""

import asyncio
import json
from typing import Any, Dict, List, Optional
from tasks import BaseTask, TaskResult, TaskPriority
import logging

logger = logging.getLogger(__name__)


class ModelTrainingTask(BaseTask):
    """
    Task for training machine learning models.
    
    This is a simulation of model training for demonstration purposes.
    """
    
    def __init__(self, name: str = "Model Training Task"):
        super().__init__(name, "Train a machine learning model", TaskPriority.HIGH)
    
    async def execute(self, training_data: Any = None, model_type: str = "linear",
                     hyperparameters: Dict[str, Any] = None, **kwargs) -> TaskResult:
        """
        Execute model training.
        
        Args:
            training_data: Data to train the model on
            model_type: Type of model to train
            hyperparameters: Model hyperparameters
            
        Returns:
            TaskResult: Training results
        """
        if training_data is None:
            return TaskResult(success=False, error="No training data provided")
        
        hyperparameters = hyperparameters or {}
        
        try:
            # Simulate training process
            logger.info(f"Starting {model_type} model training...")
            
            # Simulate training steps
            epochs = hyperparameters.get("epochs", 10)
            learning_rate = hyperparameters.get("learning_rate", 0.01)
            
            training_history = []
            for epoch in range(epochs):
                # Simulate training epoch
                await asyncio.sleep(0.1)  # Simulate computation time
                
                # Simulate loss and accuracy
                loss = 1.0 - (epoch / epochs) * 0.8 + (0.1 * (epoch % 3))
                accuracy = (epoch / epochs) * 0.9 + 0.1
                
                training_history.append({
                    "epoch": epoch + 1,
                    "loss": round(loss, 4),
                    "accuracy": round(accuracy, 4)
                })
                
                logger.debug(f"Epoch {epoch + 1}/{epochs} - Loss: {loss:.4f}, Accuracy: {accuracy:.4f}")
            
            # Simulate model evaluation
            final_accuracy = training_history[-1]["accuracy"]
            final_loss = training_history[-1]["loss"]
            
            model_info = {
                "model_type": model_type,
                "hyperparameters": hyperparameters,
                "training_samples": len(training_data) if hasattr(training_data, '__len__') else 1,
                "epochs_completed": epochs,
                "final_accuracy": final_accuracy,
                "final_loss": final_loss,
                "training_history": training_history,
                "model_size": f"{epochs * 100}KB",  # Simulated model size
                "convergence": final_loss < 0.5
            }
            
            logger.info(f"Model training completed. Final accuracy: {final_accuracy:.4f}")
            
            return TaskResult(
                success=True,
                data=model_info,
                metadata={
                    "training_time": epochs * 0.1,
                    "converged": final_loss < 0.5,
                    "performance_tier": "high" if final_accuracy > 0.8 else "medium" if final_accuracy > 0.6 else "low"
                }
            )
            
        except Exception as e:
            return TaskResult(success=False, error=f"Model training failed: {str(e)}")


class DataIngestionTask(BaseTask):
    """
    Task for ingesting data from various sources.
    
    Handles data loading, validation, and preprocessing.
    """
    
    def __init__(self, name: str = "Data Ingestion Task"):
        super().__init__(name, "Ingest data from external sources")
    
    async def execute(self, source: str = None, source_type: str = "file",
                     validation_rules: Dict[str, Any] = None, **kwargs) -> TaskResult:
        """
        Execute data ingestion.
        
        Args:
            source: Data source location/identifier
            source_type: Type of data source
            validation_rules: Rules for data validation
            
        Returns:
            TaskResult: Ingestion results
        """
        if not source:
            return TaskResult(success=False, error="No data source specified")
        
        validation_rules = validation_rules or {}
        
        try:
            logger.info(f"Starting data ingestion from {source_type}: {source}")
            
            # Simulate data loading based on source type
            if source_type == "file":
                data = await self._load_file_data(source, **kwargs)
            elif source_type == "database":
                data = await self._load_database_data(source, **kwargs)
            elif source_type == "api":
                data = await self._load_api_data(source, **kwargs)
            elif source_type == "stream":
                data = await self._load_stream_data(source, **kwargs)
            else:
                return TaskResult(success=False, error=f"Unsupported source type: {source_type}")
            
            # Validate ingested data
            validation_result = self._validate_ingested_data(data, validation_rules)
            
            if not validation_result["valid"]:
                return TaskResult(
                    success=False,
                    error=f"Data validation failed: {validation_result['errors']}"
                )
            
            # Generate ingestion summary
            summary = {
                "source": source,
                "source_type": source_type,
                "records_ingested": len(data) if hasattr(data, '__len__') else 1,
                "data_size_mb": self._estimate_data_size(data),
                "validation_passed": validation_result["valid"],
                "validation_warnings": validation_result.get("warnings", []),
                "ingestion_timestamp": asyncio.get_event_loop().time(),
                "data_schema": self._infer_schema(data)
            }
            
            logger.info(f"Data ingestion completed. Records: {summary['records_ingested']}")
            
            return TaskResult(
                success=True,
                data=data,
                metadata=summary
            )
            
        except Exception as e:
            return TaskResult(success=False, error=f"Data ingestion failed: {str(e)}")
    
    async def _load_file_data(self, file_path: str, **kwargs) -> Any:
        """Simulate loading data from a file."""
        await asyncio.sleep(0.2)  # Simulate file I/O
        
        # Simulate different file types
        if file_path.endswith('.json'):
            return [{"id": i, "value": f"item_{i}"} for i in range(100)]
        elif file_path.endswith('.csv'):
            return [{"col1": i, "col2": f"data_{i}", "col3": i * 2} for i in range(50)]
        else:
            return [f"line_{i}" for i in range(75)]
    
    async def _load_database_data(self, connection_string: str, **kwargs) -> Any:
        """Simulate loading data from a database."""
        await asyncio.sleep(0.5)  # Simulate database query
        
        query = kwargs.get("query", "SELECT * FROM table")
        
        # Simulate query results
        return [
            {"id": i, "name": f"record_{i}", "created_at": f"2024-01-{i+1:02d}"}
            for i in range(30)
        ]
    
    async def _load_api_data(self, api_endpoint: str, **kwargs) -> Any:
        """Simulate loading data from an API."""
        await asyncio.sleep(0.3)  # Simulate HTTP request
        
        # Simulate API response
        return {
            "status": "success",
            "data": [{"item": i, "value": i ** 2} for i in range(20)],
            "metadata": {"total": 20, "page": 1}
        }
    
    async def _load_stream_data(self, stream_source: str, **kwargs) -> Any:
        """Simulate loading data from a stream."""
        batch_size = kwargs.get("batch_size", 10)
        
        # Simulate streaming data in batches
        batches = []
        for batch in range(3):
            await asyncio.sleep(0.1)  # Simulate stream delay
            batch_data = [
                {"timestamp": asyncio.get_event_loop().time(), "event": f"event_{batch}_{i}"}
                for i in range(batch_size)
            ]
            batches.append(batch_data)
        
        return batches
    
    def _validate_ingested_data(self, data: Any, rules: Dict[str, Any]) -> Dict[str, Any]:
        """Validate ingested data against rules."""
        errors = []
        warnings = []
        
        # Basic validation
        if rules.get("required") and not data:
            errors.append("Data is empty but required")
        
        if rules.get("min_records") and hasattr(data, '__len__'):
            if len(data) < rules["min_records"]:
                errors.append(f"Insufficient records: {len(data)} < {rules['min_records']}")
        
        if rules.get("max_records") and hasattr(data, '__len__'):
            if len(data) > rules["max_records"]:
                warnings.append(f"Large dataset: {len(data)} > {rules['max_records']}")
        
        # Schema validation
        expected_schema = rules.get("schema")
        if expected_schema and isinstance(data, list) and data:
            first_item = data[0]
            if isinstance(first_item, dict):
                for required_field in expected_schema.get("required_fields", []):
                    if required_field not in first_item:
                        errors.append(f"Missing required field: {required_field}")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings
        }
    
    def _estimate_data_size(self, data: Any) -> float:
        """Estimate data size in MB."""
        try:
            # Simple estimation based on JSON serialization
            json_str = json.dumps(data, default=str)
            size_bytes = len(json_str.encode('utf-8'))
            return round(size_bytes / (1024 * 1024), 3)
        except:
            return 0.0
    
    def _infer_schema(self, data: Any) -> Dict[str, Any]:
        """Infer basic schema from data."""
        schema = {"type": type(data).__name__}
        
        if isinstance(data, list) and data:
            schema["length"] = len(data)
            
            # Analyze first item for structure
            first_item = data[0]
            schema["item_type"] = type(first_item).__name__
            
            if isinstance(first_item, dict):
                schema["fields"] = list(first_item.keys())
                schema["field_types"] = {
                    field: type(value).__name__
                    for field, value in first_item.items()
                }
        
        elif isinstance(data, dict):
            schema["keys"] = list(data.keys())
            schema["key_types"] = {
                key: type(value).__name__
                for key, value in data.items()
            }
        
        return schema


class ReportGenerationTask(BaseTask):
    """
    Task for generating reports from processed data.
    
    Creates formatted reports with summaries, visualizations, and insights.
    """
    
    def __init__(self, name: str = "Report Generation Task"):
        super().__init__(name, "Generate reports from data")
    
    async def execute(self, data: Any = None, report_type: str = "summary",
                     template: str = "default", **kwargs) -> TaskResult:
        """
        Execute report generation.
        
        Args:
            data: Input data for the report
            report_type: Type of report to generate
            template: Report template to use
            
        Returns:
            TaskResult: Generated report
        """
        if data is None:
            return TaskResult(success=False, error="No data provided for report generation")
        
        try:
            logger.info(f"Generating {report_type} report using {template} template")
            
            if report_type == "summary":
                report = await self._generate_summary_report(data, template, **kwargs)
            elif report_type == "detailed":
                report = await self._generate_detailed_report(data, template, **kwargs)
            elif report_type == "executive":
                report = await self._generate_executive_report(data, template, **kwargs)
            elif report_type == "technical":
                report = await self._generate_technical_report(data, template, **kwargs)
            else:
                return TaskResult(success=False, error=f"Unknown report type: {report_type}")
            
            logger.info("Report generation completed")
            
            return TaskResult(
                success=True,
                data=report,
                metadata={
                    "report_type": report_type,
                    "template": template,
                    "data_size": len(data) if hasattr(data, '__len__') else 1,
                    "report_length": len(str(report)),
                    "generation_timestamp": asyncio.get_event_loop().time()
                }
            )
            
        except Exception as e:
            return TaskResult(success=False, error=f"Report generation failed: {str(e)}")
    
    async def _generate_summary_report(self, data: Any, template: str, **kwargs) -> Dict[str, Any]:
        """Generate a summary report."""
        await asyncio.sleep(0.1)  # Simulate processing time
        
        report = {
            "title": "Data Summary Report",
            "template": template,
            "generated_at": asyncio.get_event_loop().time(),
            "overview": {
                "data_type": type(data).__name__,
                "total_items": len(data) if hasattr(data, '__len__') else 1
            },
            "sections": []
        }
        
        # Add basic statistics
        if isinstance(data, list):
            if data and isinstance(data[0], dict):
                # Analyze structured data
                fields = list(data[0].keys()) if data else []
                report["sections"].append({
                    "title": "Data Structure",
                    "content": {
                        "fields": fields,
                        "sample_record": data[0] if data else None,
                        "field_count": len(fields)
                    }
                })
            
            # Add summary statistics
            numeric_values = []
            for item in data:
                if isinstance(item, (int, float)):
                    numeric_values.append(item)
                elif isinstance(item, dict):
                    for value in item.values():
                        if isinstance(value, (int, float)):
                            numeric_values.append(value)
            
            if numeric_values:
                report["sections"].append({
                    "title": "Numeric Summary",
                    "content": {
                        "count": len(numeric_values),
                        "sum": sum(numeric_values),
                        "average": sum(numeric_values) / len(numeric_values),
                        "min": min(numeric_values),
                        "max": max(numeric_values)
                    }
                })
        
        # Add insights
        insights = self._generate_insights(data)
        if insights:
            report["sections"].append({
                "title": "Key Insights",
                "content": insights
            })
        
        return report
    
    async def _generate_detailed_report(self, data: Any, template: str, **kwargs) -> Dict[str, Any]:
        """Generate a detailed report."""
        await asyncio.sleep(0.2)  # Simulate processing time
        
        # Start with summary and add more detail
        report = await self._generate_summary_report(data, template, **kwargs)
        report["title"] = "Detailed Analysis Report"
        
        # Add detailed analysis sections
        if isinstance(data, list) and data:
            # Data quality analysis
            report["sections"].append({
                "title": "Data Quality Analysis",
                "content": self._analyze_data_quality(data)
            })
            
            # Trend analysis
            report["sections"].append({
                "title": "Trend Analysis",
                "content": self._analyze_trends(data)
            })
            
            # Distribution analysis
            report["sections"].append({
                "title": "Distribution Analysis",
                "content": self._analyze_distribution(data)
            })
        
        return report
    
    async def _generate_executive_report(self, data: Any, template: str, **kwargs) -> Dict[str, Any]:
        """Generate an executive summary report."""
        await asyncio.sleep(0.15)  # Simulate processing time
        
        report = {
            "title": "Executive Summary",
            "template": template,
            "generated_at": asyncio.get_event_loop().time(),
            "executive_summary": self._create_executive_summary(data),
            "key_metrics": self._extract_key_metrics(data),
            "recommendations": self._generate_recommendations(data),
            "risk_assessment": self._assess_risks(data)
        }
        
        return report
    
    async def _generate_technical_report(self, data: Any, template: str, **kwargs) -> Dict[str, Any]:
        """Generate a technical report."""
        await asyncio.sleep(0.25)  # Simulate processing time
        
        report = {
            "title": "Technical Analysis Report",
            "template": template,
            "generated_at": asyncio.get_event_loop().time(),
            "technical_specifications": {
                "data_format": type(data).__name__,
                "data_size": len(data) if hasattr(data, '__len__') else 1,
                "memory_usage": f"{self._estimate_memory_usage(data)} MB",
                "processing_complexity": self._assess_complexity(data)
            },
            "methodology": {
                "analysis_methods": ["statistical_analysis", "pattern_recognition", "outlier_detection"],
                "tools_used": ["python", "statistical_libraries"],
                "validation_approach": "cross_validation"
            },
            "detailed_findings": self._generate_technical_findings(data),
            "limitations": [
                "Limited to provided dataset",
                "Assumes data quality is adequate",
                "Results may vary with different parameters"
            ]
        }
        
        return report
    
    def _generate_insights(self, data: Any) -> List[str]:
        """Generate insights from data."""
        insights = []
        
        if isinstance(data, list):
            if len(data) > 100:
                insights.append("Large dataset detected - suitable for statistical analysis")
            elif len(data) < 10:
                insights.append("Small dataset - results may have limited statistical significance")
            
            # Check for patterns
            if data and isinstance(data[0], dict):
                first_item = data[0]
                if "timestamp" in first_item or "date" in first_item:
                    insights.append("Time-series data detected - temporal analysis recommended")
                if "id" in first_item:
                    insights.append("Structured records with identifiers - suitable for relational analysis")
        
        return insights
    
    def _analyze_data_quality(self, data: List[Any]) -> Dict[str, Any]:
        """Analyze data quality metrics."""
        quality_metrics = {
            "completeness": 0.0,
            "consistency": 0.0,
            "duplicates_found": 0,
            "null_values": 0,
            "quality_score": 0.0
        }
        
        if not data:
            return quality_metrics
        
        # Check completeness (non-null values)
        total_fields = 0
        complete_fields = 0
        
        for item in data:
            if isinstance(item, dict):
                for value in item.values():
                    total_fields += 1
                    if value is not None and value != "":
                        complete_fields += 1
        
        if total_fields > 0:
            quality_metrics["completeness"] = complete_fields / total_fields
        
        # Simple duplicate detection (for demonstration)
        unique_items = len(set(str(item) for item in data))
        quality_metrics["duplicates_found"] = len(data) - unique_items
        
        # Calculate overall quality score
        completeness_score = quality_metrics["completeness"]
        duplicate_penalty = min(0.3, quality_metrics["duplicates_found"] / len(data))
        quality_metrics["quality_score"] = max(0, completeness_score - duplicate_penalty)
        
        return quality_metrics
    
    def _analyze_trends(self, data: List[Any]) -> Dict[str, Any]:
        """Analyze trends in the data."""
        trends = {
            "overall_trend": "stable",
            "growth_rate": 0.0,
            "volatility": "low",
            "seasonality_detected": False
        }
        
        # Simple trend analysis for numeric sequences
        if data and all(isinstance(item, (int, float)) for item in data):
            if len(data) > 1:
                first_half_avg = sum(data[:len(data)//2]) / (len(data)//2)
                second_half_avg = sum(data[len(data)//2:]) / (len(data) - len(data)//2)
                
                if second_half_avg > first_half_avg * 1.1:
                    trends["overall_trend"] = "increasing"
                    trends["growth_rate"] = (second_half_avg - first_half_avg) / first_half_avg
                elif second_half_avg < first_half_avg * 0.9:
                    trends["overall_trend"] = "decreasing"
                    trends["growth_rate"] = (second_half_avg - first_half_avg) / first_half_avg
        
        return trends
    
    def _analyze_distribution(self, data: List[Any]) -> Dict[str, Any]:
        """Analyze data distribution."""
        distribution = {
            "distribution_type": "unknown",
            "skewness": "normal",
            "outliers_detected": 0,
            "distribution_summary": {}
        }
        
        # Simple distribution analysis for numeric data
        numeric_data = [item for item in data if isinstance(item, (int, float))]
        
        if numeric_data:
            mean_val = sum(numeric_data) / len(numeric_data)
            variance = sum((x - mean_val) ** 2 for x in numeric_data) / len(numeric_data)
            std_dev = variance ** 0.5
            
            # Simple outlier detection (values beyond 2 standard deviations)
            outliers = [x for x in numeric_data if abs(x - mean_val) > 2 * std_dev]
            
            distribution.update({
                "distribution_type": "numeric",
                "outliers_detected": len(outliers),
                "distribution_summary": {
                    "mean": mean_val,
                    "std_dev": std_dev,
                    "variance": variance,
                    "range": max(numeric_data) - min(numeric_data) if numeric_data else 0
                }
            })
        
        return distribution
    
    def _create_executive_summary(self, data: Any) -> str:
        """Create executive summary text."""
        data_size = len(data) if hasattr(data, '__len__') else 1
        
        summary = f"Analysis of dataset containing {data_size} records. "
        
        if isinstance(data, list) and data:
            if isinstance(data[0], dict):
                summary += "Structured data with multiple attributes identified. "
            
            if data_size > 1000:
                summary += "Large-scale dataset suitable for comprehensive analysis. "
            elif data_size > 100:
                summary += "Medium-scale dataset with adequate statistical power. "
            else:
                summary += "Small dataset requiring careful interpretation. "
        
        summary += "Key patterns and insights have been identified for strategic decision-making."
        
        return summary
    
    def _extract_key_metrics(self, data: Any) -> Dict[str, Any]:
        """Extract key business metrics."""
        metrics = {
            "data_volume": len(data) if hasattr(data, '__len__') else 1,
            "data_coverage": "comprehensive" if hasattr(data, '__len__') and len(data) > 100 else "limited",
            "processing_efficiency": "high",
            "data_freshness": "current"
        }
        
        return metrics
    
    def _generate_recommendations(self, data: Any) -> List[str]:
        """Generate business recommendations."""
        recommendations = []
        
        data_size = len(data) if hasattr(data, '__len__') else 1
        
        if data_size > 1000:
            recommendations.append("Consider implementing automated monitoring for this large dataset")
            recommendations.append("Explore machine learning opportunities given the substantial data volume")
        elif data_size < 50:
            recommendations.append("Increase data collection to improve analysis reliability")
            recommendations.append("Consider combining with additional data sources")
        
        recommendations.append("Establish regular reporting cadence for ongoing insights")
        recommendations.append("Implement data quality monitoring to maintain analysis accuracy")
        
        return recommendations
    
    def _assess_risks(self, data: Any) -> Dict[str, str]:
        """Assess risks related to the data and analysis."""
        risks = {
            "data_quality": "low",
            "sample_size": "medium",
            "bias_potential": "low",
            "interpretation": "medium"
        }
        
        data_size = len(data) if hasattr(data, '__len__') else 1
        
        if data_size < 30:
            risks["sample_size"] = "high"
        elif data_size < 100:
            risks["sample_size"] = "medium"
        
        return risks
    
    def _generate_technical_findings(self, data: Any) -> Dict[str, Any]:
        """Generate technical findings and analysis."""
        findings = {
            "data_structure_analysis": {
                "type": type(data).__name__,
                "complexity": "medium",
                "nested_levels": 1
            },
            "performance_metrics": {
                "processing_time": "< 1 second",
                "memory_efficiency": "optimal",
                "scalability": "good"
            },
            "statistical_summary": {},
            "anomaly_detection": {
                "anomalies_found": 0,
                "confidence_level": 0.95,
                "detection_method": "statistical_threshold"
            }
        }
        
        # Add statistical summary if applicable
        if isinstance(data, list) and data:
            numeric_items = [item for item in data if isinstance(item, (int, float))]
            if numeric_items:
                findings["statistical_summary"] = {
                    "sample_size": len(numeric_items),
                    "mean": sum(numeric_items) / len(numeric_items),
                    "median": sorted(numeric_items)[len(numeric_items)//2],
                    "std_deviation": "calculated",
                    "distribution": "analyzed"
                }
        
        return findings
    
    def _estimate_memory_usage(self, data: Any) -> float:
        """Estimate memory usage in MB."""
        try:
            import sys
            size_bytes = sys.getsizeof(data)
            return round(size_bytes / (1024 * 1024), 3)
        except:
            return 0.1  # Default estimate
    
    def _assess_complexity(self, data: Any) -> str:
        """Assess computational complexity of the data."""
        if not hasattr(data, '__len__'):
            return "low"
        
        size = len(data)
        if size < 100:
            return "low"
        elif size < 10000:
            return "medium"
        else:
            return "high"