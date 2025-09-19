"""
Configuration and initialization module for the agentic framework.

This module provides configuration management, logging setup, and
initialization utilities for the agentic model system.
"""

import logging
import os
from typing import Dict, Any, Optional
from dataclasses import dataclass, field
import json


@dataclass
class AgentConfig:
    """Configuration for individual agents."""
    name: str
    capabilities: list = field(default_factory=list)
    max_concurrent_tasks: int = 5
    timeout_seconds: float = 30.0
    retry_attempts: int = 3
    memory_limit_mb: int = 512
    custom_settings: Dict[str, Any] = field(default_factory=dict)


@dataclass
class WorkflowConfig:
    """Configuration for workflow execution."""
    max_concurrent_workflows: int = 10
    default_timeout_seconds: float = 300.0
    auto_retry_failed_steps: bool = True
    step_execution_timeout: float = 60.0
    enable_step_parallelization: bool = True
    custom_settings: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SystemConfig:
    """Main system configuration."""
    log_level: str = "INFO"
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    enable_performance_monitoring: bool = True
    enable_memory_monitoring: bool = True
    max_system_memory_usage: int = 2048  # MB
    data_storage_path: str = "./data"
    temp_storage_path: str = "./tmp"
    enable_persistence: bool = True
    agent_config: AgentConfig = field(default_factory=lambda: AgentConfig("default"))
    workflow_config: WorkflowConfig = field(default_factory=WorkflowConfig)
    custom_settings: Dict[str, Any] = field(default_factory=dict)


class ConfigManager:
    """Manages configuration loading and validation."""
    
    def __init__(self, config_file: Optional[str] = None):
        self.config_file = config_file
        self.system_config = SystemConfig()
        
        if config_file and os.path.exists(config_file):
            self.load_from_file(config_file)
    
    def load_from_file(self, config_file: str) -> None:
        """Load configuration from JSON file."""
        try:
            with open(config_file, 'r') as f:
                config_data = json.load(f)
            
            # Update system config from loaded data
            self._update_config_from_dict(config_data)
            
            logging.info(f"Configuration loaded from {config_file}")
            
        except Exception as e:
            logging.error(f"Failed to load configuration from {config_file}: {e}")
            raise
    
    def save_to_file(self, config_file: str) -> None:
        """Save current configuration to JSON file."""
        try:
            config_data = self._config_to_dict()
            
            with open(config_file, 'w') as f:
                json.dump(config_data, f, indent=2)
            
            logging.info(f"Configuration saved to {config_file}")
            
        except Exception as e:
            logging.error(f"Failed to save configuration to {config_file}: {e}")
            raise
    
    def _update_config_from_dict(self, config_data: Dict[str, Any]) -> None:
        """Update configuration from dictionary."""
        # Update system settings
        for key, value in config_data.get("system", {}).items():
            if hasattr(self.system_config, key):
                setattr(self.system_config, key, value)
        
        # Update agent config
        agent_data = config_data.get("agent", {})
        if agent_data:
            agent_config = AgentConfig(
                name=agent_data.get("name", "default"),
                capabilities=agent_data.get("capabilities", []),
                max_concurrent_tasks=agent_data.get("max_concurrent_tasks", 5),
                timeout_seconds=agent_data.get("timeout_seconds", 30.0),
                retry_attempts=agent_data.get("retry_attempts", 3),
                memory_limit_mb=agent_data.get("memory_limit_mb", 512),
                custom_settings=agent_data.get("custom_settings", {})
            )
            self.system_config.agent_config = agent_config
        
        # Update workflow config
        workflow_data = config_data.get("workflow", {})
        if workflow_data:
            workflow_config = WorkflowConfig(
                max_concurrent_workflows=workflow_data.get("max_concurrent_workflows", 10),
                default_timeout_seconds=workflow_data.get("default_timeout_seconds", 300.0),
                auto_retry_failed_steps=workflow_data.get("auto_retry_failed_steps", True),
                step_execution_timeout=workflow_data.get("step_execution_timeout", 60.0),
                enable_step_parallelization=workflow_data.get("enable_step_parallelization", True),
                custom_settings=workflow_data.get("custom_settings", {})
            )
            self.system_config.workflow_config = workflow_config
    
    def _config_to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return {
            "system": {
                "log_level": self.system_config.log_level,
                "log_format": self.system_config.log_format,
                "enable_performance_monitoring": self.system_config.enable_performance_monitoring,
                "enable_memory_monitoring": self.system_config.enable_memory_monitoring,
                "max_system_memory_usage": self.system_config.max_system_memory_usage,
                "data_storage_path": self.system_config.data_storage_path,
                "temp_storage_path": self.system_config.temp_storage_path,
                "enable_persistence": self.system_config.enable_persistence,
                "custom_settings": self.system_config.custom_settings
            },
            "agent": {
                "name": self.system_config.agent_config.name,
                "capabilities": self.system_config.agent_config.capabilities,
                "max_concurrent_tasks": self.system_config.agent_config.max_concurrent_tasks,
                "timeout_seconds": self.system_config.agent_config.timeout_seconds,
                "retry_attempts": self.system_config.agent_config.retry_attempts,
                "memory_limit_mb": self.system_config.agent_config.memory_limit_mb,
                "custom_settings": self.system_config.agent_config.custom_settings
            },
            "workflow": {
                "max_concurrent_workflows": self.system_config.workflow_config.max_concurrent_workflows,
                "default_timeout_seconds": self.system_config.workflow_config.default_timeout_seconds,
                "auto_retry_failed_steps": self.system_config.workflow_config.auto_retry_failed_steps,
                "step_execution_timeout": self.system_config.workflow_config.step_execution_timeout,
                "enable_step_parallelization": self.system_config.workflow_config.enable_step_parallelization,
                "custom_settings": self.system_config.workflow_config.custom_settings
            }
        }
    
    def get_agent_config(self, agent_name: str = None) -> AgentConfig:
        """Get agent configuration."""
        if agent_name:
            # In a more complex system, you might have per-agent configs
            config = AgentConfig(
                name=agent_name,
                capabilities=self.system_config.agent_config.capabilities.copy(),
                max_concurrent_tasks=self.system_config.agent_config.max_concurrent_tasks,
                timeout_seconds=self.system_config.agent_config.timeout_seconds,
                retry_attempts=self.system_config.agent_config.retry_attempts,
                memory_limit_mb=self.system_config.agent_config.memory_limit_mb,
                custom_settings=self.system_config.agent_config.custom_settings.copy()
            )
            return config
        return self.system_config.agent_config
    
    def get_workflow_config(self) -> WorkflowConfig:
        """Get workflow configuration."""
        return self.system_config.workflow_config
    
    def get_system_config(self) -> SystemConfig:
        """Get system configuration."""
        return self.system_config


def setup_logging(config: SystemConfig) -> None:
    """Setup logging configuration."""
    # Convert log level string to logging constant
    log_level = getattr(logging, config.log_level.upper(), logging.INFO)
    
    # Configure logging
    logging.basicConfig(
        level=log_level,
        format=config.log_format,
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler("agentic_framework.log") if config.enable_persistence else logging.NullHandler()
        ]
    )
    
    # Set specific logger levels
    logging.getLogger("agent").setLevel(log_level)
    logging.getLogger("workflow").setLevel(log_level)
    logging.getLogger("tasks").setLevel(log_level)


def ensure_directories(config: SystemConfig) -> None:
    """Ensure required directories exist."""
    directories = [
        config.data_storage_path,
        config.temp_storage_path
    ]
    
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)
            logging.info(f"Created directory: {directory}")


def initialize_system(config_file: Optional[str] = None) -> ConfigManager:
    """
    Initialize the agentic framework system.
    
    Args:
        config_file: Optional path to configuration file
        
    Returns:
        ConfigManager: Initialized configuration manager
    """
    # Load configuration
    config_manager = ConfigManager(config_file)
    system_config = config_manager.get_system_config()
    
    # Setup logging
    setup_logging(system_config)
    
    # Ensure directories exist
    ensure_directories(system_config)
    
    logging.info("Agentic framework system initialized successfully")
    
    return config_manager


def create_default_config_file(file_path: str = "config.json") -> None:
    """Create a default configuration file."""
    default_config = {
        "system": {
            "log_level": "INFO",
            "log_format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            "enable_performance_monitoring": True,
            "enable_memory_monitoring": True,
            "max_system_memory_usage": 2048,
            "data_storage_path": "./data",
            "temp_storage_path": "./tmp",
            "enable_persistence": True,
            "custom_settings": {}
        },
        "agent": {
            "name": "default",
            "capabilities": [
                "general_processing",
                "task_execution",
                "data_analysis"
            ],
            "max_concurrent_tasks": 5,
            "timeout_seconds": 30.0,
            "retry_attempts": 3,
            "memory_limit_mb": 512,
            "custom_settings": {
                "enable_learning": True,
                "learning_rate": 0.01
            }
        },
        "workflow": {
            "max_concurrent_workflows": 10,
            "default_timeout_seconds": 300.0,
            "auto_retry_failed_steps": True,
            "step_execution_timeout": 60.0,
            "enable_step_parallelization": True,
            "custom_settings": {
                "enable_checkpointing": True,
                "checkpoint_interval": 60
            }
        }
    }
    
    with open(file_path, 'w') as f:
        json.dump(default_config, f, indent=2)
    
    print(f"Default configuration file created: {file_path}")


# Global configuration manager instance
_global_config_manager: Optional[ConfigManager] = None


def get_global_config() -> ConfigManager:
    """Get the global configuration manager instance."""
    global _global_config_manager
    if _global_config_manager is None:
        _global_config_manager = initialize_system()
    return _global_config_manager


def set_global_config(config_manager: ConfigManager) -> None:
    """Set the global configuration manager instance."""
    global _global_config_manager
    _global_config_manager = config_manager


# Environment-based configuration
def load_config_from_environment() -> Dict[str, Any]:
    """Load configuration from environment variables."""
    config = {}
    
    # System configuration from environment
    if os.getenv("AGENTIC_LOG_LEVEL"):
        config.setdefault("system", {})["log_level"] = os.getenv("AGENTIC_LOG_LEVEL")
    
    if os.getenv("AGENTIC_DATA_PATH"):
        config.setdefault("system", {})["data_storage_path"] = os.getenv("AGENTIC_DATA_PATH")
    
    if os.getenv("AGENTIC_TEMP_PATH"):
        config.setdefault("system", {})["temp_storage_path"] = os.getenv("AGENTIC_TEMP_PATH")
    
    # Agent configuration from environment
    if os.getenv("AGENTIC_AGENT_TIMEOUT"):
        config.setdefault("agent", {})["timeout_seconds"] = float(os.getenv("AGENTIC_AGENT_TIMEOUT"))
    
    if os.getenv("AGENTIC_AGENT_MEMORY"):
        config.setdefault("agent", {})["memory_limit_mb"] = int(os.getenv("AGENTIC_AGENT_MEMORY"))
    
    # Workflow configuration from environment
    if os.getenv("AGENTIC_WORKFLOW_TIMEOUT"):
        config.setdefault("workflow", {})["default_timeout_seconds"] = float(os.getenv("AGENTIC_WORKFLOW_TIMEOUT"))
    
    if os.getenv("AGENTIC_MAX_WORKFLOWS"):
        config.setdefault("workflow", {})["max_concurrent_workflows"] = int(os.getenv("AGENTIC_MAX_WORKFLOWS"))
    
    return config


# Utility functions for common configuration patterns
def create_agent_config_for_role(role: str) -> AgentConfig:
    """Create agent configuration optimized for a specific role."""
    role_configs = {
        "data_processor": AgentConfig(
            name=f"data_processor_agent",
            capabilities=["data_processing", "analysis", "transformation"],
            max_concurrent_tasks=3,
            timeout_seconds=60.0,
            memory_limit_mb=1024
        ),
        "coordinator": AgentConfig(
            name=f"coordinator_agent",
            capabilities=["workflow_management", "task_coordination", "communication"],
            max_concurrent_tasks=10,
            timeout_seconds=30.0,
            memory_limit_mb=256
        ),
        "analyzer": AgentConfig(
            name=f"analyzer_agent",
            capabilities=["analysis", "reporting", "insights"],
            max_concurrent_tasks=2,
            timeout_seconds=120.0,
            memory_limit_mb=2048
        ),
        "communicator": AgentConfig(
            name=f"communicator_agent",
            capabilities=["communication", "notifications", "reporting"],
            max_concurrent_tasks=5,
            timeout_seconds=15.0,
            memory_limit_mb=128
        )
    }
    
    return role_configs.get(role, AgentConfig(name=f"{role}_agent"))


def create_workflow_config_for_complexity(complexity: str) -> WorkflowConfig:
    """Create workflow configuration optimized for complexity level."""
    complexity_configs = {
        "simple": WorkflowConfig(
            max_concurrent_workflows=20,
            default_timeout_seconds=60.0,
            step_execution_timeout=30.0,
            enable_step_parallelization=False
        ),
        "medium": WorkflowConfig(
            max_concurrent_workflows=10,
            default_timeout_seconds=300.0,
            step_execution_timeout=60.0,
            enable_step_parallelization=True
        ),
        "complex": WorkflowConfig(
            max_concurrent_workflows=3,
            default_timeout_seconds=1800.0,
            step_execution_timeout=300.0,
            enable_step_parallelization=True,
            auto_retry_failed_steps=True
        )
    }
    
    return complexity_configs.get(complexity, WorkflowConfig())