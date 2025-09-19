#!/usr/bin/env python3
"""
Example script demonstrating the agentic model framework.

This script shows how to:
1. Initialize the framework
2. Create custom agents
3. Define workflows
4. Execute tasks
5. Monitor results
"""

import asyncio
import json
from typing import Dict, Any

# Import framework components
from agent import create_agent, AgentBuilder
from workflow import WorkflowEngine, create_workflow, create_simple_agent_workflow
from tasks import DataProcessingTask, AnalysisTask, CommunicationTask, DecisionTask
from tasks.custom_tasks import ModelTrainingTask, DataIngestionTask, ReportGenerationTask
from config import initialize_system, create_default_config_file


async def demonstrate_basic_agent():
    """Demonstrate basic agent functionality."""
    print("\n" + "="*60)
    print("BASIC AGENT DEMONSTRATION")
    print("="*60)
    
    # Create a simple agent
    agent = create_agent(
        name="demo_agent",
        capabilities=["data_processing", "analysis", "communication"],
        config={"learning_enabled": True}
    )
    
    print(f"Created agent: {agent.name}")
    print(f"Agent capabilities: {list(agent.capabilities)}")
    
    # Test basic processing
    test_data = {"message": "Hello from the agentic framework!", "data": [1, 2, 3, 4, 5]}
    result = await agent.process(test_data)
    
    print(f"Agent processing result: {json.dumps(result, indent=2, default=str)}")
    
    # Test agent actions
    action_result = await agent.act("process_data", {"input": test_data})
    print(f"Agent action result: {json.dumps(action_result, indent=2, default=str)}")
    
    # Show agent status
    status = agent.get_status()
    print(f"Agent status: {json.dumps(status, indent=2)}")
    
    return agent


async def demonstrate_custom_agent_builder():
    """Demonstrate custom agent creation using the builder pattern."""
    print("\n" + "="*60)
    print("CUSTOM AGENT BUILDER DEMONSTRATION")
    print("="*60)
    
    # Define a custom action handler
    async def custom_greeting_handler(parameters: Dict[str, Any]) -> Dict[str, Any]:
        name = parameters.get("name", "Unknown")
        style = parameters.get("style", "formal")
        
        greetings = {
            "formal": f"Good day, {name}. How may I assist you today?",
            "casual": f"Hey {name}! What's up?",
            "enthusiastic": f"Hello there, {name}! Great to see you!"
        }
        
        return {
            "greeting": greetings.get(style, greetings["formal"]),
            "timestamp": asyncio.get_event_loop().time(),
            "style_used": style
        }
    
    # Build a custom agent with specific capabilities
    custom_agent = (AgentBuilder()
                   .with_name("custom_assistant")
                   .with_capability("greeting")
                   .with_capability("customer_service")
                   .with_capability("multilingual")
                   .with_config({"language": "english", "personality": "helpful"})
                   .with_action_handler("greet", custom_greeting_handler)
                   .build())
    
    print(f"Built custom agent: {custom_agent.name}")
    print(f"Capabilities: {list(custom_agent.capabilities)}")
    
    # Test the custom greeting action
    greeting_result = await custom_agent.act("greet", {
        "name": "Alice", 
        "style": "enthusiastic"
    })
    print(f"Custom greeting result: {json.dumps(greeting_result, indent=2, default=str)}")
    
    return custom_agent


async def demonstrate_tasks():
    """Demonstrate various task types."""
    print("\n" + "="*60)
    print("TASK DEMONSTRATION")
    print("="*60)
    
    # Create and run different types of tasks
    tasks_to_demo = [
        (DataProcessingTask("Data Processing Demo"), {
            "data": [{"id": i, "value": i*2, "category": "A" if i % 2 == 0 else "B"} for i in range(10)],
            "operations": ["filter", "sort", "aggregate"],
            "filter_criteria": {"category": "A"},
            "sort_key": "value",
            "aggregation_function": "sum"
        }),
        
        (AnalysisTask("Statistical Analysis Demo"), {
            "data": [1, 5, 3, 9, 2, 8, 4, 7, 6, 10],
            "analysis_type": "statistical"
        }),
        
        (CommunicationTask("Communication Demo"), {
            "message": "System status update: All agents operational",
            "recipient": "system_admin",
            "communication_type": "notification",
            "priority": "normal"
        }),
        
        (DecisionTask("Decision Making Demo"), {
            "options": [
                {"name": "Option A", "cost": 100, "quality": 8, "time": 5},
                {"name": "Option B", "cost": 150, "quality": 9, "time": 3},
                {"name": "Option C", "cost": 80, "quality": 6, "time": 7}
            ],
            "criteria": {"quality": 9, "cost": 100},
            "decision_type": "weighted",
            "weights": {"quality": 0.6, "cost": 0.4}
        }),
        
        (ModelTrainingTask("ML Training Demo"), {
            "training_data": [{"features": [i, i*2], "label": i % 2} for i in range(50)],
            "model_type": "neural_network",
            "hyperparameters": {"epochs": 5, "learning_rate": 0.01, "batch_size": 10}
        }),
        
        (DataIngestionTask("Data Ingestion Demo"), {
            "source": "sample_dataset.json",
            "source_type": "file",
            "validation_rules": {"min_records": 5, "schema": {"required_fields": ["id"]}}
        }),
        
        (ReportGenerationTask("Report Generation Demo"), {
            "data": [{"sales": 1000, "region": "North"}, {"sales": 1500, "region": "South"}],
            "report_type": "executive",
            "template": "business_summary"
        })
    ]
    
    task_results = []
    
    for task, params in tasks_to_demo:
        print(f"\nRunning task: {task.name}")
        print("-" * 40)
        
        result = await task.run(**params)
        task_results.append((task, result))
        
        print(f"Task success: {result.success}")
        if result.success:
            print(f"Result preview: {str(result.data)[:200]}...")
        else:
            print(f"Error: {result.error}")
        
        if result.metadata:
            print(f"Metadata: {json.dumps(result.metadata, indent=2, default=str)}")
    
    return task_results


async def demonstrate_workflow():
    """Demonstrate workflow creation and execution."""
    print("\n" + "="*60)
    print("WORKFLOW DEMONSTRATION")
    print("="*60)
    
    # Create workflow engine
    engine = WorkflowEngine()
    
    # Create and register agents
    data_agent = create_agent("data_processor", ["data_processing", "analysis"])
    comm_agent = create_agent("communicator", ["communication", "reporting"])
    
    engine.register_agent(data_agent)
    engine.register_agent(comm_agent)
    
    print(f"Registered agents: {list(engine.agents.keys())}")
    
    # Create a workflow using the builder pattern
    workflow = (create_workflow("Data Processing Pipeline", "Complete data processing workflow")
               .add_agent_task(
                   name="Ingest Data",
                   agent_name="data_processor",
                   config={
                       "action": "process",
                       "input": {"data": [1, 2, 3, 4, 5], "operations": ["validate", "clean"]},
                       "store_result_as": "cleaned_data"
                   },
                   step_id="step_1"
               )
               .add_agent_task(
                   name="Analyze Data",
                   agent_name="data_processor",
                   config={
                       "action": "process",
                       "input": {"analysis_type": "statistical"},
                       "store_result_as": "analysis_results"
                   },
                   dependencies=["step_1"],
                   step_id="step_2"
               )
               .add_delay(
                   name="Processing Delay",
                   seconds=0.5,
                   dependencies=["step_2"],
                   step_id="step_3"
               )
               .add_agent_task(
                   name="Generate Report",
                   agent_name="communicator",
                   config={
                       "action": "process",
                       "input": {"message": "Data processing completed successfully"},
                       "store_result_as": "final_report"
                   },
                   dependencies=["step_3"],
                   step_id="step_4"
               )
               .build())
    
    print(f"\nCreated workflow: {workflow.name}")
    print(f"Workflow steps: {len(workflow.steps)}")
    
    # Execute the workflow
    print("\nExecuting workflow...")
    context = await engine.execute_workflow(workflow)
    
    print(f"Workflow execution completed!")
    print(f"Final context data keys: {list(context.data.keys())}")
    print(f"Step results: {len(context.step_results)}")
    
    # Show workflow status
    status = workflow.get_status()
    print(f"Final workflow status: {json.dumps(status, indent=2, default=str)}")
    
    # Show detailed results
    print("\nDetailed step results:")
    for step_id, result in context.step_results.items():
        print(f"  {step_id}: Success={result.success}, Time={result.execution_time:.3f}s")
        if result.result:
            print(f"    Result: {str(result.result)[:100]}...")
    
    return workflow, context


async def demonstrate_simple_workflow():
    """Demonstrate simple workflow creation."""
    print("\n" + "="*60)
    print("SIMPLE WORKFLOW DEMONSTRATION")
    print("="*60)
    
    # Create workflow engine and agent
    engine = WorkflowEngine()
    agent = create_agent("simple_agent", ["general_processing"])
    engine.register_agent(agent)
    
    # Create a simple sequential workflow
    tasks = [
        {"name": "Task 1", "action": "process", "input": {"step": 1, "data": "initial"}},
        {"name": "Task 2", "action": "process", "input": {"step": 2, "data": "intermediate"}},
        {"name": "Task 3", "action": "process", "input": {"step": 3, "data": "final"}}
    ]
    
    simple_workflow = create_simple_agent_workflow(
        name="Simple Sequential Workflow",
        agent_name="simple_agent",
        tasks=tasks
    )
    
    print(f"Created simple workflow with {len(simple_workflow.steps)} steps")
    
    # Execute the simple workflow
    context = await engine.execute_workflow(simple_workflow)
    
    print("Simple workflow execution completed!")
    print(f"Results: {len(context.step_results)} steps completed")
    
    return simple_workflow, context


async def demonstrate_error_handling():
    """Demonstrate error handling and retry mechanisms."""
    print("\n" + "="*60)
    print("ERROR HANDLING DEMONSTRATION")
    print("="*60)
    
    # Create a task that will fail
    class FailingTask(DataProcessingTask):
        def __init__(self):
            super().__init__("Failing Task Demo")
            self.attempt_count = 0
        
        async def execute(self, **kwargs) -> Any:
            self.attempt_count += 1
            print(f"  Attempt {self.attempt_count}")
            
            if self.attempt_count < 3:
                # Fail the first two attempts
                raise Exception(f"Simulated failure on attempt {self.attempt_count}")
            else:
                # Succeed on the third attempt
                return {"success": True, "attempts": self.attempt_count}
    
    failing_task = FailingTask()
    failing_task.max_retries = 3
    
    print("Running task that fails twice then succeeds...")
    
    # This will be handled by the task's retry mechanism in the workflow
    try:
        result = await failing_task.run()
        print(f"Task eventually succeeded: {result.success}")
        print(f"Final result: {result.data}")
    except Exception as e:
        print(f"Task failed permanently: {e}")
    
    return failing_task


async def main():
    """Main demonstration function."""
    print("Agentic Model Framework Demonstration")
    print("="*60)
    
    # Initialize the system
    print("Initializing system...")
    config_manager = initialize_system()
    print("System initialized successfully!")
    
    try:
        # Run all demonstrations
        basic_agent = await demonstrate_basic_agent()
        custom_agent = await demonstrate_custom_agent_builder()
        task_results = await demonstrate_tasks()
        workflow, workflow_context = await demonstrate_workflow()
        simple_workflow, simple_context = await demonstrate_simple_workflow()
        failing_task = await demonstrate_error_handling()
        
        # Final summary
        print("\n" + "="*60)
        print("DEMONSTRATION SUMMARY")
        print("="*60)
        print(f"✓ Created {2} agents")
        print(f"✓ Executed {len(task_results)} different task types")
        print(f"✓ Ran {2} workflows with multiple steps")
        print(f"✓ Demonstrated error handling and retries")
        print(f"✓ Showcased agent capabilities and configurations")
        
        print("\nFramework capabilities demonstrated:")
        print("• Agent creation and customization")
        print("• Task definition and execution")
        print("• Workflow orchestration")
        print("• Error handling and retry logic")
        print("• Configuration management")
        print("• Modular architecture")
        
        print("\nThe agentic model framework is ready for building custom agents!")
        
    except Exception as e:
        print(f"Demonstration failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    # Create a default configuration file for reference
    try:
        create_default_config_file("example_config.json")
        print("Created example configuration file: example_config.json")
    except Exception as e:
        print(f"Note: Could not create config file: {e}")
    
    # Run the demonstration
    asyncio.run(main())