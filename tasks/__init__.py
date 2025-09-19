"""
Task management and definitions for the agentic framework.

This module contains base task classes and common task implementations
that can be used by agents within workflows.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass
from enum import Enum
import asyncio
import logging

logger = logging.getLogger(__name__)


class TaskStatus(Enum):
    """Possible statuses for a task."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TaskPriority(Enum):
    """Task priority levels."""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4


@dataclass
class TaskResult:
    """Result of task execution."""
    success: bool
    data: Any = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class BaseTask(ABC):
    """
    Abstract base class for all tasks.
    
    Defines the interface that all task implementations must follow.
    """
    
    def __init__(self, name: str, description: str = "", priority: TaskPriority = TaskPriority.NORMAL):
        self.name = name
        self.description = description
        self.priority = priority
        self.status = TaskStatus.PENDING
        self.parameters: Dict[str, Any] = {}
        self.context: Dict[str, Any] = {}
        self.result: Optional[TaskResult] = None
        self.created_at = asyncio.get_event_loop().time()
        self.started_at: Optional[float] = None
        self.completed_at: Optional[float] = None
    
    @abstractmethod
    async def execute(self, **kwargs) -> TaskResult:
        """
        Execute the task with given parameters.
        
        Returns:
            TaskResult: Result of task execution
        """
        pass
    
    def set_parameters(self, parameters: Dict[str, Any]) -> None:
        """Set task parameters."""
        self.parameters.update(parameters)
    
    def set_context(self, context: Dict[str, Any]) -> None:
        """Set task context."""
        self.context.update(context)
    
    def get_status_info(self) -> Dict[str, Any]:
        """Get task status information."""
        return {
            "name": self.name,
            "description": self.description,
            "status": self.status.value,
            "priority": self.priority.value,
            "created_at": self.created_at,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
            "execution_time": (self.completed_at - self.started_at) if self.started_at and self.completed_at else None,
            "has_result": self.result is not None,
            "success": self.result.success if self.result else None
        }
    
    async def run(self, **kwargs) -> TaskResult:
        """
        Run the task with error handling and status management.
        
        Returns:
            TaskResult: Result of task execution
        """
        self.status = TaskStatus.RUNNING
        self.started_at = asyncio.get_event_loop().time()
        
        try:
            logger.info(f"Starting task: {self.name}")
            
            # Merge kwargs with parameters
            exec_params = {**self.parameters, **kwargs}
            
            # Execute the task
            result = await self.execute(**exec_params)
            
            self.result = result
            self.status = TaskStatus.COMPLETED if result.success else TaskStatus.FAILED
            self.completed_at = asyncio.get_event_loop().time()
            
            logger.info(f"Task completed: {self.name} (success: {result.success})")
            return result
            
        except Exception as e:
            self.result = TaskResult(success=False, error=str(e))
            self.status = TaskStatus.FAILED
            self.completed_at = asyncio.get_event_loop().time()
            
            logger.error(f"Task failed: {self.name} - {str(e)}")
            return self.result


class DataProcessingTask(BaseTask):
    """
    Task for processing data using various operations.
    
    This task can perform common data processing operations like
    filtering, transforming, aggregating, etc.
    """
    
    def __init__(self, name: str = "Data Processing Task", description: str = ""):
        super().__init__(name, description or "Process data using specified operations")
    
    async def execute(self, data: Any = None, operations: List[str] = None, **kwargs) -> TaskResult:
        """
        Execute data processing operations.
        
        Args:
            data: Input data to process
            operations: List of operations to apply
            **kwargs: Additional parameters for operations
            
        Returns:
            TaskResult: Processed data result
        """
        if data is None:
            return TaskResult(success=False, error="No input data provided")
        
        operations = operations or ["passthrough"]
        processed_data = data
        operation_results = []
        
        try:
            for operation in operations:
                if operation == "passthrough":
                    # No operation, just pass data through
                    pass
                elif operation == "filter":
                    # Filter data based on criteria
                    criteria = kwargs.get("filter_criteria", {})
                    processed_data = self._filter_data(processed_data, criteria)
                elif operation == "transform":
                    # Transform data using transformation function
                    transform_func = kwargs.get("transform_function")
                    if transform_func:
                        processed_data = self._transform_data(processed_data, transform_func)
                elif operation == "aggregate":
                    # Aggregate data
                    agg_func = kwargs.get("aggregation_function", "count")
                    processed_data = self._aggregate_data(processed_data, agg_func)
                elif operation == "sort":
                    # Sort data
                    sort_key = kwargs.get("sort_key")
                    reverse = kwargs.get("reverse", False)
                    processed_data = self._sort_data(processed_data, sort_key, reverse)
                elif operation == "validate":
                    # Validate data
                    validation_schema = kwargs.get("validation_schema", {})
                    is_valid, validation_errors = self._validate_data(processed_data, validation_schema)
                    if not is_valid:
                        return TaskResult(
                            success=False, 
                            error=f"Data validation failed: {validation_errors}"
                        )
                else:
                    # Custom operation
                    custom_func = kwargs.get(f"{operation}_function")
                    if custom_func:
                        processed_data = custom_func(processed_data)
                    else:
                        logger.warning(f"Unknown operation: {operation}")
                
                operation_results.append({
                    "operation": operation,
                    "success": True,
                    "data_size": len(processed_data) if hasattr(processed_data, '__len__') else 1
                })
            
            return TaskResult(
                success=True,
                data=processed_data,
                metadata={
                    "original_data_size": len(data) if hasattr(data, '__len__') else 1,
                    "processed_data_size": len(processed_data) if hasattr(processed_data, '__len__') else 1,
                    "operations_applied": operation_results
                }
            )
            
        except Exception as e:
            return TaskResult(success=False, error=f"Data processing failed: {str(e)}")
    
    def _filter_data(self, data: Any, criteria: Dict[str, Any]) -> Any:
        """Filter data based on criteria."""
        if isinstance(data, list):
            if not criteria:
                return data
            
            # Simple filtering for dictionaries in list
            filtered_data = []
            for item in data:
                if isinstance(item, dict):
                    match = all(
                        item.get(key) == value for key, value in criteria.items()
                    )
                    if match:
                        filtered_data.append(item)
                else:
                    # For non-dict items, just include them
                    filtered_data.append(item)
            return filtered_data
        return data
    
    def _transform_data(self, data: Any, transform_func: callable) -> Any:
        """Transform data using a function."""
        if isinstance(data, list):
            return [transform_func(item) for item in data]
        else:
            return transform_func(data)
    
    def _aggregate_data(self, data: Any, agg_func: str) -> Any:
        """Aggregate data using specified function."""
        if not isinstance(data, list):
            return data
        
        if agg_func == "count":
            return {"count": len(data)}
        elif agg_func == "sum" and all(isinstance(x, (int, float)) for x in data):
            return {"sum": sum(data)}
        elif agg_func == "avg" and all(isinstance(x, (int, float)) for x in data):
            return {"average": sum(data) / len(data) if data else 0}
        elif agg_func == "min" and data:
            return {"minimum": min(data)}
        elif agg_func == "max" and data:
            return {"maximum": max(data)}
        else:
            return {"count": len(data)}
    
    def _sort_data(self, data: Any, sort_key: str = None, reverse: bool = False) -> Any:
        """Sort data."""
        if not isinstance(data, list):
            return data
        
        try:
            if sort_key and all(isinstance(item, dict) for item in data):
                return sorted(data, key=lambda x: x.get(sort_key, 0), reverse=reverse)
            else:
                return sorted(data, reverse=reverse)
        except Exception:
            return data
    
    def _validate_data(self, data: Any, schema: Dict[str, Any]) -> tuple[bool, List[str]]:
        """Validate data against schema."""
        errors = []
        
        if not schema:
            return True, errors
        
        # Simple validation rules
        if "type" in schema:
            expected_type = schema["type"]
            if expected_type == "list" and not isinstance(data, list):
                errors.append(f"Expected list, got {type(data).__name__}")
            elif expected_type == "dict" and not isinstance(data, dict):
                errors.append(f"Expected dict, got {type(data).__name__}")
            elif expected_type == "int" and not isinstance(data, int):
                errors.append(f"Expected int, got {type(data).__name__}")
            elif expected_type == "str" and not isinstance(data, str):
                errors.append(f"Expected str, got {type(data).__name__}")
        
        if "min_length" in schema and hasattr(data, '__len__'):
            if len(data) < schema["min_length"]:
                errors.append(f"Length {len(data)} is less than minimum {schema['min_length']}")
        
        if "max_length" in schema and hasattr(data, '__len__'):
            if len(data) > schema["max_length"]:
                errors.append(f"Length {len(data)} is greater than maximum {schema['max_length']}")
        
        return len(errors) == 0, errors


class AnalysisTask(BaseTask):
    """
    Task for performing analysis on data or content.
    
    Can perform various types of analysis including statistical,
    textual, or custom analysis operations.
    """
    
    def __init__(self, name: str = "Analysis Task", description: str = ""):
        super().__init__(name, description or "Perform analysis on input data")
    
    async def execute(self, data: Any = None, analysis_type: str = "basic", **kwargs) -> TaskResult:
        """
        Execute analysis operations.
        
        Args:
            data: Input data to analyze
            analysis_type: Type of analysis to perform
            **kwargs: Additional parameters for analysis
            
        Returns:
            TaskResult: Analysis results
        """
        if data is None:
            return TaskResult(success=False, error="No input data provided for analysis")
        
        try:
            if analysis_type == "basic":
                result = self._basic_analysis(data)
            elif analysis_type == "statistical":
                result = self._statistical_analysis(data)
            elif analysis_type == "text":
                result = self._text_analysis(data)
            elif analysis_type == "custom":
                analysis_func = kwargs.get("analysis_function")
                if not analysis_func:
                    return TaskResult(success=False, error="Custom analysis function not provided")
                result = analysis_func(data)
            else:
                return TaskResult(success=False, error=f"Unknown analysis type: {analysis_type}")
            
            return TaskResult(
                success=True,
                data=result,
                metadata={
                    "analysis_type": analysis_type,
                    "input_data_type": type(data).__name__,
                    "input_size": len(data) if hasattr(data, '__len__') else 1
                }
            )
            
        except Exception as e:
            return TaskResult(success=False, error=f"Analysis failed: {str(e)}")
    
    def _basic_analysis(self, data: Any) -> Dict[str, Any]:
        """Perform basic analysis on data."""
        analysis = {
            "data_type": type(data).__name__,
            "timestamp": asyncio.get_event_loop().time()
        }
        
        if hasattr(data, '__len__'):
            analysis["length"] = len(data)
        
        if isinstance(data, (list, tuple)):
            analysis["element_types"] = list(set(type(item).__name__ for item in data))
            if data:
                analysis["first_element"] = data[0]
                analysis["last_element"] = data[-1]
        
        if isinstance(data, dict):
            analysis["keys"] = list(data.keys())
            analysis["key_count"] = len(data.keys())
        
        if isinstance(data, str):
            analysis["character_count"] = len(data)
            analysis["word_count"] = len(data.split())
            analysis["line_count"] = len(data.splitlines())
        
        return analysis
    
    def _statistical_analysis(self, data: Any) -> Dict[str, Any]:
        """Perform statistical analysis on numerical data."""
        analysis = {"analysis_type": "statistical"}
        
        if isinstance(data, (list, tuple)):
            # Filter numerical values
            numerical_data = [x for x in data if isinstance(x, (int, float))]
            
            if numerical_data:
                analysis.update({
                    "count": len(numerical_data),
                    "sum": sum(numerical_data),
                    "mean": sum(numerical_data) / len(numerical_data),
                    "min": min(numerical_data),
                    "max": max(numerical_data),
                    "range": max(numerical_data) - min(numerical_data)
                })
                
                # Calculate median
                sorted_data = sorted(numerical_data)
                n = len(sorted_data)
                if n % 2 == 0:
                    analysis["median"] = (sorted_data[n//2 - 1] + sorted_data[n//2]) / 2
                else:
                    analysis["median"] = sorted_data[n//2]
            else:
                analysis["error"] = "No numerical data found for statistical analysis"
        
        elif isinstance(data, (int, float)):
            analysis.update({
                "value": data,
                "type": "single_number",
                "absolute_value": abs(data),
                "is_positive": data > 0,
                "is_negative": data < 0,
                "is_zero": data == 0
            })
        
        else:
            analysis["error"] = f"Statistical analysis not applicable to {type(data).__name__}"
        
        return analysis
    
    def _text_analysis(self, data: Any) -> Dict[str, Any]:
        """Perform text analysis on string data."""
        analysis = {"analysis_type": "text"}
        
        if isinstance(data, str):
            words = data.split()
            lines = data.splitlines()
            
            analysis.update({
                "character_count": len(data),
                "character_count_no_spaces": len(data.replace(" ", "")),
                "word_count": len(words),
                "line_count": len(lines),
                "paragraph_count": len([p for p in data.split('\n\n') if p.strip()]),
                "average_word_length": sum(len(word) for word in words) / len(words) if words else 0,
                "longest_word": max(words, key=len) if words else "",
                "shortest_word": min(words, key=len) if words else "",
                "unique_words": len(set(word.lower() for word in words)),
                "is_empty": len(data.strip()) == 0,
                "starts_with_uppercase": data[0].isupper() if data else False,
                "contains_numbers": any(char.isdigit() for char in data),
                "contains_special_chars": any(not char.isalnum() and not char.isspace() for char in data)
            })
            
            # Word frequency (top 10)
            word_freq = {}
            for word in words:
                word_lower = word.lower().strip('.,!?";:')
                word_freq[word_lower] = word_freq.get(word_lower, 0) + 1
            
            analysis["top_words"] = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:10]
        
        elif isinstance(data, (list, tuple)) and all(isinstance(item, str) for item in data):
            # Analysis for list of strings
            total_chars = sum(len(s) for s in data)
            total_words = sum(len(s.split()) for s in data)
            
            analysis.update({
                "string_count": len(data),
                "total_characters": total_chars,
                "total_words": total_words,
                "average_string_length": total_chars / len(data) if data else 0,
                "longest_string": max(data, key=len) if data else "",
                "shortest_string": min(data, key=len) if data else "",
                "empty_strings": sum(1 for s in data if not s.strip())
            })
        
        else:
            analysis["error"] = f"Text analysis not applicable to {type(data).__name__}"
        
        return analysis


class CommunicationTask(BaseTask):
    """
    Task for handling communication between agents or external systems.
    
    Can send messages, notifications, or coordinate with other components.
    """
    
    def __init__(self, name: str = "Communication Task", description: str = ""):
        super().__init__(name, description or "Handle communication operations")
    
    async def execute(self, message: str = None, recipient: str = None, 
                     communication_type: str = "message", **kwargs) -> TaskResult:
        """
        Execute communication operations.
        
        Args:
            message: Message content to send
            recipient: Target recipient
            communication_type: Type of communication
            **kwargs: Additional parameters
            
        Returns:
            TaskResult: Communication result
        """
        if not message:
            return TaskResult(success=False, error="No message content provided")
        
        try:
            if communication_type == "message":
                result = self._send_message(message, recipient, **kwargs)
            elif communication_type == "notification":
                result = self._send_notification(message, recipient, **kwargs)
            elif communication_type == "broadcast":
                result = self._broadcast_message(message, **kwargs)
            elif communication_type == "log":
                result = self._log_message(message, **kwargs)
            else:
                return TaskResult(success=False, error=f"Unknown communication type: {communication_type}")
            
            return TaskResult(
                success=True,
                data=result,
                metadata={
                    "communication_type": communication_type,
                    "recipient": recipient,
                    "message_length": len(message)
                }
            )
            
        except Exception as e:
            return TaskResult(success=False, error=f"Communication failed: {str(e)}")
    
    def _send_message(self, message: str, recipient: str, **kwargs) -> Dict[str, Any]:
        """Send a message to a specific recipient."""
        # Simulate message sending
        logger.info(f"Sending message to {recipient}: {message[:50]}...")
        
        return {
            "action": "message_sent",
            "recipient": recipient,
            "message": message,
            "timestamp": asyncio.get_event_loop().time(),
            "priority": kwargs.get("priority", "normal"),
            "status": "delivered"
        }
    
    def _send_notification(self, message: str, recipient: str, **kwargs) -> Dict[str, Any]:
        """Send a notification."""
        logger.info(f"Sending notification to {recipient}: {message[:50]}...")
        
        return {
            "action": "notification_sent",
            "recipient": recipient,
            "message": message,
            "timestamp": asyncio.get_event_loop().time(),
            "notification_type": kwargs.get("notification_type", "info"),
            "status": "sent"
        }
    
    def _broadcast_message(self, message: str, **kwargs) -> Dict[str, Any]:
        """Broadcast a message to multiple recipients."""
        recipients = kwargs.get("recipients", ["all"])
        logger.info(f"Broadcasting message to {recipients}: {message[:50]}...")
        
        return {
            "action": "message_broadcasted",
            "recipients": recipients,
            "message": message,
            "timestamp": asyncio.get_event_loop().time(),
            "reach": len(recipients),
            "status": "broadcasted"
        }
    
    def _log_message(self, message: str, **kwargs) -> Dict[str, Any]:
        """Log a message."""
        level = kwargs.get("level", "info")
        
        if level == "error":
            logger.error(message)
        elif level == "warning":
            logger.warning(message)
        elif level == "debug":
            logger.debug(message)
        else:
            logger.info(message)
        
        return {
            "action": "message_logged",
            "message": message,
            "level": level,
            "timestamp": asyncio.get_event_loop().time(),
            "status": "logged"
        }


class DecisionTask(BaseTask):
    """
    Task for making decisions based on input data and criteria.
    
    Can evaluate options, apply decision rules, and provide recommendations.
    """
    
    def __init__(self, name: str = "Decision Task", description: str = ""):
        super().__init__(name, description or "Make decisions based on input criteria")
    
    async def execute(self, options: List[Any] = None, criteria: Dict[str, Any] = None,
                     decision_type: str = "simple", **kwargs) -> TaskResult:
        """
        Execute decision-making operations.
        
        Args:
            options: List of options to choose from
            criteria: Decision criteria
            decision_type: Type of decision-making process
            **kwargs: Additional parameters
            
        Returns:
            TaskResult: Decision result
        """
        if not options:
            return TaskResult(success=False, error="No options provided for decision making")
        
        criteria = criteria or {}
        
        try:
            if decision_type == "simple":
                result = self._simple_decision(options, criteria)
            elif decision_type == "weighted":
                result = self._weighted_decision(options, criteria, **kwargs)
            elif decision_type == "random":
                result = self._random_decision(options)
            elif decision_type == "rule_based":
                result = self._rule_based_decision(options, criteria, **kwargs)
            else:
                return TaskResult(success=False, error=f"Unknown decision type: {decision_type}")
            
            return TaskResult(
                success=True,
                data=result,
                metadata={
                    "decision_type": decision_type,
                    "options_count": len(options),
                    "criteria_count": len(criteria)
                }
            )
            
        except Exception as e:
            return TaskResult(success=False, error=f"Decision making failed: {str(e)}")
    
    def _simple_decision(self, options: List[Any], criteria: Dict[str, Any]) -> Dict[str, Any]:
        """Make a simple decision based on basic criteria."""
        # Simple decision: choose first option that meets criteria, or first option
        selected_option = options[0]
        reasons = ["Default selection (first option)"]
        
        if criteria:
            for option in options:
                if isinstance(option, dict):
                    # Check if option meets all criteria
                    meets_criteria = all(
                        option.get(key) == value for key, value in criteria.items()
                    )
                    if meets_criteria:
                        selected_option = option
                        reasons = [f"Meets criteria: {criteria}"]
                        break
        
        return {
            "selected_option": selected_option,
            "decision_method": "simple",
            "reasons": reasons,
            "timestamp": asyncio.get_event_loop().time()
        }
    
    def _weighted_decision(self, options: List[Any], criteria: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """Make a weighted decision based on scoring."""
        weights = kwargs.get("weights", {})
        
        # Score each option
        option_scores = []
        for i, option in enumerate(options):
            score = 0
            score_details = {}
            
            if isinstance(option, dict):
                for criterion, target_value in criteria.items():
                    weight = weights.get(criterion, 1.0)
                    option_value = option.get(criterion, 0)
                    
                    # Simple scoring: 1 if matches, 0.5 if close, 0 if far
                    if option_value == target_value:
                        criterion_score = 1.0
                    elif isinstance(option_value, (int, float)) and isinstance(target_value, (int, float)):
                        # Numerical similarity
                        diff = abs(option_value - target_value)
                        max_diff = max(abs(target_value), 1)  # Avoid division by zero
                        criterion_score = max(0, 1 - (diff / max_diff))
                    else:
                        criterion_score = 0.0
                    
                    weighted_score = criterion_score * weight
                    score += weighted_score
                    score_details[criterion] = {
                        "value": option_value,
                        "target": target_value,
                        "criterion_score": criterion_score,
                        "weight": weight,
                        "weighted_score": weighted_score
                    }
            
            option_scores.append({
                "option": option,
                "index": i,
                "total_score": score,
                "score_details": score_details
            })
        
        # Select option with highest score
        best_option = max(option_scores, key=lambda x: x["total_score"])
        
        return {
            "selected_option": best_option["option"],
            "decision_method": "weighted",
            "total_score": best_option["total_score"],
            "score_details": best_option["score_details"],
            "all_scores": option_scores,
            "timestamp": asyncio.get_event_loop().time()
        }
    
    def _random_decision(self, options: List[Any]) -> Dict[str, Any]:
        """Make a random decision."""
        import random
        selected_option = random.choice(options)
        
        return {
            "selected_option": selected_option,
            "decision_method": "random",
            "reasons": ["Random selection"],
            "timestamp": asyncio.get_event_loop().time()
        }
    
    def _rule_based_decision(self, options: List[Any], criteria: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """Make a decision based on rules."""
        rules = kwargs.get("rules", [])
        
        # Apply rules in order
        for rule in rules:
            rule_type = rule.get("type", "filter")
            rule_criteria = rule.get("criteria", {})
            
            if rule_type == "filter":
                # Filter options that meet rule criteria
                filtered_options = []
                for option in options:
                    if isinstance(option, dict):
                        meets_rule = all(
                            option.get(key) == value for key, value in rule_criteria.items()
                        )
                        if meets_rule:
                            filtered_options.append(option)
                
                if filtered_options:
                    options = filtered_options
            
            elif rule_type == "sort":
                # Sort options by specified key
                sort_key = rule.get("key")
                reverse = rule.get("reverse", False)
                if sort_key:
                    options = sorted(
                        options,
                        key=lambda x: x.get(sort_key, 0) if isinstance(x, dict) else 0,
                        reverse=reverse
                    )
        
        # Select first option after applying rules
        selected_option = options[0] if options else None
        
        return {
            "selected_option": selected_option,
            "decision_method": "rule_based",
            "rules_applied": len(rules),
            "final_options_count": len(options),
            "timestamp": asyncio.get_event_loop().time()
        }