# Agentic Model Framework

A comprehensive framework for building custom agentic models that can be used to create sophisticated AI agents and workflows. This framework provides a foundation for developing multi-agent systems with task orchestration, workflow management, and extensible capabilities.

## Features

- **Modular Agent Architecture**: Create custom agents with specific capabilities and behaviors
- **Workflow Orchestration**: Define and execute complex workflows with dependency management
- **Task System**: Comprehensive task library with built-in processing, analysis, and communication tasks
- **Configuration Management**: Flexible configuration system with environment variable support
- **Error Handling**: Robust error handling with retry mechanisms and graceful degradation
- **Extensibility**: Easy to extend with custom tasks, agents, and workflow steps

## Project Structure

```
gpt-test/
├── agent.py              # Core agent implementation and base classes
├── workflow.py           # Workflow engine and orchestration system
├── tasks/                # Task definitions and implementations
│   ├── __init__.py       # Base task classes and common tasks
│   └── custom_tasks.py   # Specialized custom task implementations
├── config.py             # Configuration management and system initialization
├── example.py            # Comprehensive usage examples and demonstrations
└── README.md             # This documentation
```

## Quick Start

### 1. Basic Agent Creation

```python
from agent import create_agent

# Create a simple agent
agent = create_agent(
    name="my_agent",
    capabilities=["data_processing", "analysis"],
    config={"learning_enabled": True}
)

# Process data with the agent
result = await agent.process({"data": [1, 2, 3, 4, 5]})
print(result)
```

### 2. Custom Agent with Builder Pattern

```python
from agent import AgentBuilder

# Define custom action handler
async def custom_action(parameters):
    return {"result": "custom processing completed", "input": parameters}

# Build custom agent
agent = (AgentBuilder()
         .with_name("custom_agent")
         .with_capability("custom_processing")
         .with_action_handler("custom_action", custom_action)
         .build())
```

### 3. Task Execution

```python
from tasks import DataProcessingTask, AnalysisTask

# Create and run a data processing task
task = DataProcessingTask("Process Dataset")
result = await task.run(
    data=[{"id": 1, "value": 10}, {"id": 2, "value": 20}],
    operations=["filter", "sort"],
    filter_criteria={"value": 10}
)

# Run analysis task
analysis_task = AnalysisTask("Analyze Numbers")
analysis_result = await analysis_task.run(
    data=[1, 2, 3, 4, 5],
    analysis_type="statistical"
)
```

### 4. Workflow Creation and Execution

```python
from workflow import WorkflowEngine, create_workflow

# Create workflow engine and register agents
engine = WorkflowEngine()
engine.register_agent(agent)

# Build workflow
workflow = (create_workflow("Data Pipeline")
           .add_agent_task("Process Data", "my_agent", 
                          config={"input": data})
           .add_agent_task("Analyze Results", "my_agent",
                          dependencies=["step_1"])
           .build())

# Execute workflow
context = await engine.execute_workflow(workflow)
```

## Core Components

### Agents (`agent.py`)

The agent system provides the foundation for creating intelligent agents:

- **BaseAgent**: Abstract base class defining the core agent interface
- **CustomAgent**: Configurable agent implementation with action handlers
- **AgentBuilder**: Fluent builder pattern for creating custom agents
- **AgentMemory**: Memory management for context and history

Key capabilities:
- Asynchronous processing
- State management
- Memory and context handling
- Custom action registration
- Capability-based task routing

### Workflows (`workflow.py`)

The workflow system orchestrates complex multi-step processes:

- **WorkflowEngine**: Executes workflows with agent coordination
- **BaseWorkflow**: Abstract workflow definition
- **WorkflowStep**: Individual workflow step definitions
- **WorkflowContext**: Shared context across workflow execution

Features:
- Dependency-based execution
- Parallel and sequential step execution
- Error handling and retry mechanisms
- Conditional and custom step types
- Real-time workflow monitoring

### Tasks (`tasks/`)

Comprehensive task library for common operations:

**Base Tasks** (`tasks/__init__.py`):
- `DataProcessingTask`: Data filtering, transformation, aggregation
- `AnalysisTask`: Statistical, textual, and custom analysis
- `CommunicationTask`: Messaging, notifications, logging
- `DecisionTask`: Decision-making with multiple criteria

**Custom Tasks** (`tasks/custom_tasks.py`):
- `ModelTrainingTask`: Simulated ML model training
- `DataIngestionTask`: Data loading from various sources
- `ReportGenerationTask`: Automated report generation

### Configuration (`config.py`)

Flexible configuration management:

- JSON-based configuration files
- Environment variable support
- Role-based agent configurations
- Complexity-based workflow configurations
- System initialization and setup

## Usage Examples

### Running the Demo

```bash
python example.py
```

This will demonstrate:
- Basic agent functionality
- Custom agent creation
- Various task types
- Workflow execution
- Error handling

### Running the GUI Application

The framework now includes a cross-platform graphical user interface:

```bash
# Start the web-based GUI
python launcher.py

# Or run directly
python web_gui.py
```

The GUI provides:
- **Agent Management**: Create and monitor agents
- **Task Execution**: Run tasks with visual feedback
- **Workflow Design**: Build complex workflows
- **Real-time Monitoring**: Live logs and status updates
- **Cross-platform**: Runs on Windows, Mac, and Linux

For more details, see [README_GUI.md](README_GUI.md).

### Creating Custom Tasks

```python
from tasks import BaseTask, TaskResult

class MyCustomTask(BaseTask):
    async def execute(self, input_data=None, **kwargs):
        # Custom task logic here
        processed_data = self.process_input(input_data)
        
        return TaskResult(
            success=True,
            data=processed_data,
            metadata={"processing_time": 0.1}
        )
```

### Advanced Workflow Configuration

```python
from workflow import WorkflowBuilder, StepType

# Create complex workflow with conditional logic
workflow = (WorkflowBuilder()
           .with_name("Advanced Pipeline")
           .add_conditional(
               name="Data Quality Check",
               condition=lambda ctx: ctx.get_data("quality_score", 0) > 0.8,
               if_config={"step_type": "agent_task", "agent_name": "processor"},
               else_config={"step_type": "agent_task", "agent_name": "cleaner"}
           )
           .build())
```

## Configuration

### Default Configuration

Create a default configuration file:

```python
from config import create_default_config_file
create_default_config_file("config.json")
```

### Environment Variables

Set configuration via environment variables:

```bash
export AGENTIC_LOG_LEVEL=DEBUG
export AGENTIC_AGENT_TIMEOUT=60
export AGENTIC_DATA_PATH=./data
export AGENTIC_TEMP_PATH=./tmp
```

### Custom Configuration

```json
{
  "system": {
    "log_level": "INFO",
    "enable_performance_monitoring": true,
    "data_storage_path": "./data"
  },
  "agent": {
    "capabilities": ["data_processing", "analysis"],
    "max_concurrent_tasks": 5,
    "timeout_seconds": 30.0
  },
  "workflow": {
    "max_concurrent_workflows": 10,
    "auto_retry_failed_steps": true
  }
}
```

## Extending the Framework

### Custom Agent Types

Create specialized agents by extending `BaseAgent`:

```python
class SpecializedAgent(BaseAgent):
    def __init__(self, name, specialization):
        super().__init__(name)
        self.specialization = specialization
        self.add_capability(f"specialized_{specialization}")
    
    async def process(self, input_data):
        # Specialized processing logic
        return await self.specialized_processing(input_data)
```

### Custom Workflow Steps

Register custom step executors:

```python
async def custom_step_executor(step, context, agents):
    # Custom step execution logic
    return {"step": step.name, "completed": True}

engine.register_step_executor(StepType.CUSTOM, custom_step_executor)
```

## Architecture Benefits

1. **Modularity**: Each component is independent and can be used separately
2. **Extensibility**: Easy to add new agents, tasks, and workflow types
3. **Scalability**: Async execution and parallel processing support
4. **Flexibility**: Configuration-driven behavior and runtime customization
5. **Maintainability**: Clean separation of concerns and well-defined interfaces

## Best Practices

1. **Agent Design**: Keep agents focused on specific capabilities
2. **Task Granularity**: Design tasks to be atomic and reusable
3. **Workflow Planning**: Use dependencies to ensure proper execution order
4. **Error Handling**: Implement proper retry logic and fallback mechanisms
5. **Configuration**: Use environment-specific configurations
6. **Testing**: Test agents and workflows in isolation before integration

## Future Enhancements

- Distributed execution across multiple nodes
- Machine learning integration for adaptive agents
- Real-time monitoring and metrics dashboard
- Integration with external AI services
- Persistent workflow state and resume capability
- Advanced scheduling and resource management

This framework provides a solid foundation for building sophisticated agentic systems while maintaining simplicity and extensibility.