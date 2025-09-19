"""
Core agent implementation for the agentic model framework.

This module provides the base Agent class that can be extended to create
custom agentic models with different capabilities and behaviors.
"""

import asyncio
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Callable
from dataclasses import dataclass
from enum import Enum
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AgentState(Enum):
    """Possible states for an agent."""
    IDLE = "idle"
    THINKING = "thinking"
    ACTING = "acting"
    WAITING = "waiting"
    COMPLETED = "completed"
    ERROR = "error"


@dataclass
class AgentMemory:
    """Memory structure for storing agent's context and history."""
    short_term: Dict[str, Any]
    long_term: List[Dict[str, Any]]
    context: Dict[str, Any]
    
    def __init__(self):
        self.short_term = {}
        self.long_term = []
        self.context = {}
    
    def store_short_term(self, key: str, value: Any) -> None:
        """Store information in short-term memory."""
        self.short_term[key] = value
    
    def store_long_term(self, entry: Dict[str, Any]) -> None:
        """Store information in long-term memory."""
        self.long_term.append(entry)
    
    def get_context(self, key: str, default: Any = None) -> Any:
        """Retrieve context information."""
        return self.context.get(key, default)
    
    def update_context(self, updates: Dict[str, Any]) -> None:
        """Update context with new information."""
        self.context.update(updates)


class BaseAgent(ABC):
    """
    Base class for all agents in the framework.
    
    This abstract class defines the core interface that all agents must implement,
    providing a foundation for building custom agentic models.
    """
    
    def __init__(self, name: str, config: Optional[Dict[str, Any]] = None):
        self.name = name
        self.config = config or {}
        self.state = AgentState.IDLE
        self.memory = AgentMemory()
        self.capabilities = set()
        self.active_tasks = []
        self.completed_tasks = []
        self.error_log = []
        
        # Initialize agent-specific setup
        self._initialize()
    
    def _initialize(self) -> None:
        """Initialize agent-specific configuration."""
        logger.info(f"Initializing agent: {self.name}")
    
    @abstractmethod
    async def process(self, input_data: Any) -> Any:
        """
        Process input data and return a response.
        
        This is the core method that defines how the agent processes information
        and must be implemented by all concrete agent classes.
        """
        pass
    
    @abstractmethod
    def can_handle(self, task_type: str) -> bool:
        """
        Determine if the agent can handle a specific task type.
        
        Args:
            task_type: The type of task to check
            
        Returns:
            bool: True if the agent can handle the task, False otherwise
        """
        pass
    
    def add_capability(self, capability: str) -> None:
        """Add a capability to the agent."""
        self.capabilities.add(capability)
        logger.info(f"Added capability '{capability}' to agent {self.name}")
    
    def has_capability(self, capability: str) -> bool:
        """Check if agent has a specific capability."""
        return capability in self.capabilities
    
    def set_state(self, state: AgentState) -> None:
        """Update agent state."""
        old_state = self.state
        self.state = state
        logger.info(f"Agent {self.name} state changed: {old_state.value} -> {state.value}")
    
    async def think(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perform reasoning/thinking operations.
        
        Args:
            context: Current context for thinking
            
        Returns:
            Dict containing thoughts and decisions
        """
        self.set_state(AgentState.THINKING)
        
        # Update memory with new context
        self.memory.update_context(context)
        
        # Basic thinking logic - can be overridden by subclasses
        thoughts = {
            "timestamp": asyncio.get_event_loop().time(),
            "context": context,
            "capabilities": list(self.capabilities),
            "state": self.state.value
        }
        
        # Store in short-term memory
        self.memory.store_short_term("last_thoughts", thoughts)
        
        return thoughts
    
    async def act(self, action: str, parameters: Dict[str, Any] = None) -> Any:
        """
        Execute an action with given parameters.
        
        Args:
            action: The action to execute
            parameters: Parameters for the action
            
        Returns:
            Result of the action
        """
        self.set_state(AgentState.ACTING)
        parameters = parameters or {}
        
        logger.info(f"Agent {self.name} executing action: {action}")
        
        try:
            # Record action in memory
            action_record = {
                "action": action,
                "parameters": parameters,
                "timestamp": asyncio.get_event_loop().time()
            }
            self.memory.store_long_term(action_record)
            
            # Execute action (to be implemented by subclasses)
            result = await self._execute_action(action, parameters)
            
            action_record["result"] = result
            action_record["status"] = "success"
            
            return result
            
        except Exception as e:
            error_info = {
                "action": action,
                "parameters": parameters,
                "error": str(e),
                "timestamp": asyncio.get_event_loop().time()
            }
            self.error_log.append(error_info)
            self.set_state(AgentState.ERROR)
            logger.error(f"Error executing action {action}: {e}")
            raise
    
    async def _execute_action(self, action: str, parameters: Dict[str, Any]) -> Any:
        """
        Execute a specific action. Override in subclasses.
        
        Args:
            action: Action name
            parameters: Action parameters
            
        Returns:
            Action result
        """
        # Default implementation
        return {"action": action, "parameters": parameters, "executed": True}
    
    def get_status(self) -> Dict[str, Any]:
        """Get current agent status."""
        return {
            "name": self.name,
            "state": self.state.value,
            "capabilities": list(self.capabilities),
            "active_tasks": len(self.active_tasks),
            "completed_tasks": len(self.completed_tasks),
            "errors": len(self.error_log),
            "memory_size": {
                "short_term": len(self.memory.short_term),
                "long_term": len(self.memory.long_term),
                "context": len(self.memory.context)
            }
        }


class CustomAgent(BaseAgent):
    """
    A customizable agent implementation that can be configured for specific use cases.
    
    This class provides a concrete implementation of BaseAgent that can be easily
    customized through configuration and capability injection.
    """
    
    def __init__(self, name: str, config: Optional[Dict[str, Any]] = None):
        super().__init__(name, config)
        
        # Add default capabilities
        self.add_capability("general_processing")
        self.add_capability("task_execution")
        
        # Custom action handlers
        self.action_handlers: Dict[str, Callable] = {}
        
        # Configure based on config
        if self.config.get("capabilities"):
            for capability in self.config["capabilities"]:
                self.add_capability(capability)
    
    def register_action_handler(self, action: str, handler: Callable) -> None:
        """Register a custom action handler."""
        self.action_handlers[action] = handler
        logger.info(f"Registered action handler for '{action}' in agent {self.name}")
    
    async def process(self, input_data: Any) -> Any:
        """Process input data through the agent's reasoning pipeline."""
        try:
            # Think about the input
            thoughts = await self.think({"input": input_data})
            
            # Determine action based on input
            if isinstance(input_data, dict) and "action" in input_data:
                action = input_data["action"]
                parameters = input_data.get("parameters", {})
                result = await self.act(action, parameters)
            else:
                # Default processing
                result = {
                    "processed_input": input_data,
                    "thoughts": thoughts,
                    "agent": self.name,
                    "timestamp": asyncio.get_event_loop().time()
                }
            
            self.set_state(AgentState.COMPLETED)
            return result
            
        except Exception as e:
            self.set_state(AgentState.ERROR)
            logger.error(f"Error processing input in agent {self.name}: {e}")
            raise
    
    def can_handle(self, task_type: str) -> bool:
        """Check if agent can handle a specific task type."""
        # Basic capability matching
        return task_type in self.capabilities or "general_processing" in self.capabilities
    
    async def _execute_action(self, action: str, parameters: Dict[str, Any]) -> Any:
        """Execute custom actions using registered handlers."""
        if action in self.action_handlers:
            return await self.action_handlers[action](parameters)
        
        # Default action execution
        return await super()._execute_action(action, parameters)


class AgentBuilder:
    """
    Builder class for creating and configuring agents.
    
    This class provides a fluent interface for building custom agents with
    specific capabilities and configurations.
    """
    
    def __init__(self):
        self.name = None
        self.config = {}
        self.capabilities = []
        self.action_handlers = {}
    
    def with_name(self, name: str) -> 'AgentBuilder':
        """Set the agent name."""
        self.name = name
        return self
    
    def with_capability(self, capability: str) -> 'AgentBuilder':
        """Add a capability to the agent."""
        self.capabilities.append(capability)
        return self
    
    def with_config(self, config: Dict[str, Any]) -> 'AgentBuilder':
        """Set agent configuration."""
        self.config.update(config)
        return self
    
    def with_action_handler(self, action: str, handler: Callable) -> 'AgentBuilder':
        """Add an action handler."""
        self.action_handlers[action] = handler
        return self
    
    def build(self) -> CustomAgent:
        """Build and return the configured agent."""
        if not self.name:
            raise ValueError("Agent name is required")
        
        # Add capabilities to config
        if self.capabilities:
            self.config["capabilities"] = self.capabilities
        
        # Create agent
        agent = CustomAgent(self.name, self.config)
        
        # Register action handlers
        for action, handler in self.action_handlers.items():
            agent.register_action_handler(action, handler)
        
        return agent


# Convenience function for quick agent creation
def create_agent(name: str, capabilities: List[str] = None, config: Dict[str, Any] = None) -> CustomAgent:
    """
    Convenience function to create a basic agent.
    
    Args:
        name: Agent name
        capabilities: List of capabilities
        config: Configuration dictionary
        
    Returns:
        Configured CustomAgent instance
    """
    builder = AgentBuilder().with_name(name)
    
    if capabilities:
        for capability in capabilities:
            builder.with_capability(capability)
    
    if config:
        builder.with_config(config)
    
    return builder.build()