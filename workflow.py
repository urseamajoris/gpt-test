"""
Workflow management system for orchestrating agent tasks and processes.

This module provides workflow definitions, execution engines, and coordination
mechanisms for complex multi-agent operations.
"""

import asyncio
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Callable, Union
from dataclasses import dataclass, field
from enum import Enum
import logging
from datetime import datetime
import uuid

from agent import BaseAgent, AgentState

logger = logging.getLogger(__name__)


class WorkflowState(Enum):
    """Possible states for a workflow."""
    PENDING = "pending"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class StepType(Enum):
    """Types of workflow steps."""
    AGENT_TASK = "agent_task"
    PARALLEL = "parallel"
    SEQUENTIAL = "sequential"
    CONDITIONAL = "conditional"
    DELAY = "delay"
    CUSTOM = "custom"


@dataclass
class WorkflowStep:
    """Represents a single step in a workflow."""
    id: str
    name: str
    step_type: StepType
    config: Dict[str, Any] = field(default_factory=dict)
    dependencies: List[str] = field(default_factory=list)
    agent_name: Optional[str] = None
    condition: Optional[Callable] = None
    timeout: Optional[float] = None
    retry_count: int = 0
    max_retries: int = 3
    
    def __post_init__(self):
        if not self.id:
            self.id = str(uuid.uuid4())


@dataclass
class StepResult:
    """Result of executing a workflow step."""
    step_id: str
    success: bool
    result: Any = None
    error: Optional[str] = None
    execution_time: float = 0.0
    timestamp: datetime = field(default_factory=datetime.now)
    retry_count: int = 0


@dataclass
class WorkflowContext:
    """Context shared across workflow execution."""
    workflow_id: str
    data: Dict[str, Any] = field(default_factory=dict)
    step_results: Dict[str, StepResult] = field(default_factory=dict)
    global_config: Dict[str, Any] = field(default_factory=dict)
    
    def get_step_result(self, step_id: str) -> Optional[StepResult]:
        """Get result of a specific step."""
        return self.step_results.get(step_id)
    
    def get_data(self, key: str, default: Any = None) -> Any:
        """Get data from context."""
        return self.data.get(key, default)
    
    def set_data(self, key: str, value: Any) -> None:
        """Set data in context."""
        self.data[key] = value
    
    def update_data(self, updates: Dict[str, Any]) -> None:
        """Update context data with multiple values."""
        self.data.update(updates)


class BaseWorkflow(ABC):
    """
    Abstract base class for all workflows.
    
    Defines the interface that all workflow implementations must follow.
    """
    
    def __init__(self, name: str, description: str = ""):
        self.name = name
        self.description = description
        self.id = str(uuid.uuid4())
        self.state = WorkflowState.PENDING
        self.steps: List[WorkflowStep] = []
        self.context = WorkflowContext(workflow_id=self.id)
        self.created_at = datetime.now()
        self.started_at: Optional[datetime] = None
        self.completed_at: Optional[datetime] = None
    
    @abstractmethod
    def define_steps(self) -> List[WorkflowStep]:
        """Define the steps that make up this workflow."""
        pass
    
    def add_step(self, step: WorkflowStep) -> None:
        """Add a step to the workflow."""
        self.steps.append(step)
    
    def get_step(self, step_id: str) -> Optional[WorkflowStep]:
        """Get a step by its ID."""
        return next((step for step in self.steps if step.id == step_id), None)
    
    def get_status(self) -> Dict[str, Any]:
        """Get current workflow status."""
        return {
            "id": self.id,
            "name": self.name,
            "state": self.state.value,
            "total_steps": len(self.steps),
            "completed_steps": len([r for r in self.context.step_results.values() if r.success]),
            "failed_steps": len([r for r in self.context.step_results.values() if not r.success]),
            "created_at": self.created_at.isoformat(),
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
        }


class WorkflowEngine:
    """
    Engine for executing workflows with agent coordination.
    
    Manages workflow execution, agent assignment, and result collection.
    """
    
    def __init__(self):
        self.agents: Dict[str, BaseAgent] = {}
        self.active_workflows: Dict[str, BaseWorkflow] = {}
        self.completed_workflows: List[BaseWorkflow] = []
        self.step_executors: Dict[StepType, Callable] = {}
        
        # Register default step executors
        self._register_default_executors()
    
    def register_agent(self, agent: BaseAgent) -> None:
        """Register an agent with the workflow engine."""
        self.agents[agent.name] = agent
        logger.info(f"Registered agent: {agent.name}")
    
    def unregister_agent(self, agent_name: str) -> None:
        """Unregister an agent from the workflow engine."""
        if agent_name in self.agents:
            del self.agents[agent_name]
            logger.info(f"Unregistered agent: {agent_name}")
    
    def get_agent(self, agent_name: str) -> Optional[BaseAgent]:
        """Get an agent by name."""
        return self.agents.get(agent_name)
    
    def register_step_executor(self, step_type: StepType, executor: Callable) -> None:
        """Register a custom step executor."""
        self.step_executors[step_type] = executor
        logger.info(f"Registered step executor for type: {step_type.value}")
    
    async def execute_workflow(self, workflow: BaseWorkflow) -> WorkflowContext:
        """
        Execute a complete workflow.
        
        Args:
            workflow: The workflow to execute
            
        Returns:
            WorkflowContext: Final context with all results
        """
        workflow.state = WorkflowState.RUNNING
        workflow.started_at = datetime.now()
        self.active_workflows[workflow.id] = workflow
        
        logger.info(f"Starting workflow execution: {workflow.name} ({workflow.id})")
        
        try:
            # Initialize workflow steps if not already done
            if not workflow.steps:
                workflow.steps = workflow.define_steps()
            
            # Execute steps based on dependencies
            await self._execute_steps(workflow)
            
            workflow.state = WorkflowState.COMPLETED
            workflow.completed_at = datetime.now()
            
            logger.info(f"Workflow completed successfully: {workflow.name}")
            
        except Exception as e:
            workflow.state = WorkflowState.FAILED
            workflow.completed_at = datetime.now()
            logger.error(f"Workflow failed: {workflow.name} - {str(e)}")
            raise
        
        finally:
            # Move to completed workflows
            if workflow.id in self.active_workflows:
                del self.active_workflows[workflow.id]
                self.completed_workflows.append(workflow)
        
        return workflow.context
    
    async def _execute_steps(self, workflow: BaseWorkflow) -> None:
        """Execute all steps in the workflow respecting dependencies."""
        remaining_steps = workflow.steps.copy()
        executed_steps = set()
        
        while remaining_steps:
            # Find steps that can be executed (all dependencies met)
            ready_steps = []
            for step in remaining_steps:
                if all(dep in executed_steps for dep in step.dependencies):
                    ready_steps.append(step)
            
            if not ready_steps:
                # Check for circular dependencies or missing steps
                remaining_step_ids = [step.id for step in remaining_steps]
                missing_deps = []
                for step in remaining_steps:
                    for dep in step.dependencies:
                        if dep not in executed_steps and dep not in remaining_step_ids:
                            missing_deps.append(f"Step {step.id} depends on missing step {dep}")
                
                if missing_deps:
                    raise ValueError(f"Missing dependencies: {'; '.join(missing_deps)}")
                else:
                    raise ValueError("Circular dependency detected in workflow steps")
            
            # Execute ready steps (can be done in parallel)
            tasks = []
            for step in ready_steps:
                task = asyncio.create_task(self._execute_step(step, workflow.context))
                tasks.append(task)
            
            # Wait for all ready steps to complete
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Process results
            for i, (step, result) in enumerate(zip(ready_steps, results)):
                if isinstance(result, Exception):
                    step_result = StepResult(
                        step_id=step.id,
                        success=False,
                        error=str(result),
                        retry_count=step.retry_count
                    )
                    workflow.context.step_results[step.id] = step_result
                    
                    # Handle retries
                    if step.retry_count < step.max_retries:
                        step.retry_count += 1
                        logger.warning(f"Step {step.id} failed, retrying ({step.retry_count}/{step.max_retries})")
                        continue  # Don't mark as executed, will retry
                    else:
                        logger.error(f"Step {step.id} failed after {step.max_retries} retries")
                        raise result
                else:
                    workflow.context.step_results[step.id] = result
                
                executed_steps.add(step.id)
                remaining_steps.remove(step)
    
    async def _execute_step(self, step: WorkflowStep, context: WorkflowContext) -> StepResult:
        """Execute a single workflow step."""
        start_time = asyncio.get_event_loop().time()
        
        logger.info(f"Executing step: {step.name} ({step.id})")
        
        try:
            # Get appropriate executor
            executor = self.step_executors.get(step.step_type)
            if not executor:
                raise ValueError(f"No executor registered for step type: {step.step_type.value}")
            
            # Execute with timeout if specified
            if step.timeout:
                result_data = await asyncio.wait_for(
                    executor(step, context, self.agents),
                    timeout=step.timeout
                )
            else:
                result_data = await executor(step, context, self.agents)
            
            execution_time = asyncio.get_event_loop().time() - start_time
            
            return StepResult(
                step_id=step.id,
                success=True,
                result=result_data,
                execution_time=execution_time,
                retry_count=step.retry_count
            )
            
        except Exception as e:
            execution_time = asyncio.get_event_loop().time() - start_time
            
            return StepResult(
                step_id=step.id,
                success=False,
                error=str(e),
                execution_time=execution_time,
                retry_count=step.retry_count
            )
    
    def _register_default_executors(self) -> None:
        """Register default step executors."""
        self.step_executors[StepType.AGENT_TASK] = self._execute_agent_task
        self.step_executors[StepType.PARALLEL] = self._execute_parallel
        self.step_executors[StepType.SEQUENTIAL] = self._execute_sequential
        self.step_executors[StepType.CONDITIONAL] = self._execute_conditional
        self.step_executors[StepType.DELAY] = self._execute_delay
    
    async def _execute_agent_task(self, step: WorkflowStep, context: WorkflowContext, agents: Dict[str, BaseAgent]) -> Any:
        """Execute an agent task step."""
        if not step.agent_name:
            raise ValueError(f"Agent task step {step.id} missing agent_name")
        
        agent = agents.get(step.agent_name)
        if not agent:
            raise ValueError(f"Agent '{step.agent_name}' not found")
        
        # Prepare input data from context and step config
        input_data = step.config.copy()
        input_data.update(context.data)
        
        # Execute agent processing
        result = await agent.process(input_data)
        
        # Update context with result if specified
        if step.config.get("store_result_as"):
            context.set_data(step.config["store_result_as"], result)
        
        return result
    
    async def _execute_parallel(self, step: WorkflowStep, context: WorkflowContext, agents: Dict[str, BaseAgent]) -> Any:
        """Execute parallel sub-steps."""
        sub_steps = step.config.get("steps", [])
        tasks = []
        
        for sub_step_config in sub_steps:
            sub_step = WorkflowStep(**sub_step_config)
            task = asyncio.create_task(self._execute_step(sub_step, context))
            tasks.append(task)
        
        results = await asyncio.gather(*tasks)
        return [r.result for r in results if r.success]
    
    async def _execute_sequential(self, step: WorkflowStep, context: WorkflowContext, agents: Dict[str, BaseAgent]) -> Any:
        """Execute sequential sub-steps."""
        sub_steps = step.config.get("steps", [])
        results = []
        
        for sub_step_config in sub_steps:
            sub_step = WorkflowStep(**sub_step_config)
            result = await self._execute_step(sub_step, context)
            results.append(result.result if result.success else None)
        
        return results
    
    async def _execute_conditional(self, step: WorkflowStep, context: WorkflowContext, agents: Dict[str, BaseAgent]) -> Any:
        """Execute conditional step based on condition."""
        if not step.condition:
            raise ValueError(f"Conditional step {step.id} missing condition")
        
        # Evaluate condition
        condition_result = step.condition(context)
        
        if condition_result:
            # Execute 'if' branch
            if_config = step.config.get("if")
            if if_config:
                if_step = WorkflowStep(**if_config)
                result = await self._execute_step(if_step, context)
                return result.result
        else:
            # Execute 'else' branch
            else_config = step.config.get("else")
            if else_config:
                else_step = WorkflowStep(**else_config)
                result = await self._execute_step(else_step, context)
                return result.result
        
        return None
    
    async def _execute_delay(self, step: WorkflowStep, context: WorkflowContext, agents: Dict[str, BaseAgent]) -> Any:
        """Execute delay step."""
        delay_seconds = step.config.get("seconds", 1.0)
        await asyncio.sleep(delay_seconds)
        return {"delayed": delay_seconds}
    
    def get_workflow_status(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a specific workflow."""
        # Check active workflows
        if workflow_id in self.active_workflows:
            return self.active_workflows[workflow_id].get_status()
        
        # Check completed workflows
        for workflow in self.completed_workflows:
            if workflow.id == workflow_id:
                return workflow.get_status()
        
        return None
    
    def list_workflows(self) -> Dict[str, List[Dict[str, Any]]]:
        """List all workflows grouped by status."""
        return {
            "active": [wf.get_status() for wf in self.active_workflows.values()],
            "completed": [wf.get_status() for wf in self.completed_workflows]
        }


class SimpleWorkflow(BaseWorkflow):
    """
    A simple workflow implementation for basic use cases.
    
    Allows for easy creation of workflows through step definitions.
    """
    
    def __init__(self, name: str, description: str = "", steps: List[Dict[str, Any]] = None):
        super().__init__(name, description)
        self._step_definitions = steps or []
    
    def define_steps(self) -> List[WorkflowStep]:
        """Define steps from the provided step definitions."""
        steps = []
        for step_def in self._step_definitions:
            step = WorkflowStep(
                id=step_def.get("id", str(uuid.uuid4())),
                name=step_def["name"],
                step_type=StepType(step_def["step_type"]),
                config=step_def.get("config", {}),
                dependencies=step_def.get("dependencies", []),
                agent_name=step_def.get("agent_name"),
                timeout=step_def.get("timeout"),
                max_retries=step_def.get("max_retries", 3)
            )
            steps.append(step)
        return steps


class WorkflowBuilder:
    """
    Builder class for creating workflows with a fluent interface.
    """
    
    def __init__(self):
        self.name = None
        self.description = ""
        self.steps = []
    
    def with_name(self, name: str) -> 'WorkflowBuilder':
        """Set workflow name."""
        self.name = name
        return self
    
    def with_description(self, description: str) -> 'WorkflowBuilder':
        """Set workflow description."""
        self.description = description
        return self
    
    def add_agent_task(self, name: str, agent_name: str, config: Dict[str, Any] = None, 
                      dependencies: List[str] = None, step_id: str = None) -> 'WorkflowBuilder':
        """Add an agent task step."""
        step = {
            "id": step_id or str(uuid.uuid4()),
            "name": name,
            "step_type": "agent_task",
            "agent_name": agent_name,
            "config": config or {},
            "dependencies": dependencies or []
        }
        self.steps.append(step)
        return self
    
    def add_delay(self, name: str, seconds: float, dependencies: List[str] = None, 
                 step_id: str = None) -> 'WorkflowBuilder':
        """Add a delay step."""
        step = {
            "id": step_id or str(uuid.uuid4()),
            "name": name,
            "step_type": "delay",
            "config": {"seconds": seconds},
            "dependencies": dependencies or []
        }
        self.steps.append(step)
        return self
    
    def add_conditional(self, name: str, condition: Callable, if_config: Dict[str, Any] = None,
                       else_config: Dict[str, Any] = None, dependencies: List[str] = None,
                       step_id: str = None) -> 'WorkflowBuilder':
        """Add a conditional step."""
        step = {
            "id": step_id or str(uuid.uuid4()),
            "name": name,
            "step_type": "conditional",
            "config": {
                "if": if_config,
                "else": else_config
            },
            "dependencies": dependencies or []
        }
        # Note: condition function would need to be set separately as it's not serializable
        self.steps.append(step)
        return self
    
    def build(self) -> SimpleWorkflow:
        """Build the workflow."""
        if not self.name:
            raise ValueError("Workflow name is required")
        
        return SimpleWorkflow(self.name, self.description, self.steps)


# Convenience functions
def create_workflow(name: str, description: str = "") -> WorkflowBuilder:
    """Create a new workflow builder."""
    return WorkflowBuilder().with_name(name).with_description(description)


def create_simple_agent_workflow(name: str, agent_name: str, tasks: List[Dict[str, Any]]) -> SimpleWorkflow:
    """
    Create a simple workflow that executes a series of tasks with a single agent.
    
    Args:
        name: Workflow name
        agent_name: Name of the agent to use
        tasks: List of task configurations
        
    Returns:
        SimpleWorkflow instance
    """
    steps = []
    for i, task in enumerate(tasks):
        step = {
            "id": f"task_{i}",
            "name": task.get("name", f"Task {i + 1}"),
            "step_type": "agent_task",
            "agent_name": agent_name,
            "config": task,
            "dependencies": [f"task_{i-1}"] if i > 0 else []
        }
        steps.append(step)
    
    return SimpleWorkflow(name, f"Sequential workflow for {agent_name}", steps)