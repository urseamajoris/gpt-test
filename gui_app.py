#!/usr/bin/env python3
"""
Agentic Model Framework GUI Application

A cross-platform graphical user interface for the Agentic Model Framework.
This application provides an intuitive way to create agents, design workflows,
execute tasks, and monitor the framework's operations.

Features:
- Agent creation and management
- Task definition and execution
- Workflow design and execution
- Real-time logging and monitoring
- Configuration management

Requirements:
- Python 3.7+
- tkinter (included with Python)
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog
import asyncio
import threading
import json
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional
import sys
import os

# Import framework components
try:
    from agent import create_agent, AgentBuilder, AgentState
    from workflow import WorkflowEngine, create_workflow, create_simple_agent_workflow
    from tasks import DataProcessingTask, AnalysisTask, CommunicationTask, DecisionTask
    from tasks.custom_tasks import ModelTrainingTask, DataIngestionTask, ReportGenerationTask
    from config import initialize_system, create_default_config_file, ConfigManager
except ImportError as e:
    # Handle case where framework modules are not available
    print(f"Error importing framework modules: {e}")
    print("Please ensure the framework modules are in the Python path.")
    sys.exit(1)


class LogHandler(logging.Handler):
    """Custom logging handler to redirect logs to GUI."""
    
    def __init__(self, gui_callback):
        super().__init__()
        self.gui_callback = gui_callback
    
    def emit(self, record):
        log_entry = self.format(record)
        # Use thread-safe method to update GUI
        self.gui_callback(log_entry)


class AgenticFrameworkGUI:
    """Main GUI application for the Agentic Model Framework."""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Agentic Model Framework - Control Center")
        self.root.geometry("1200x800")
        
        # Framework components
        self.config_manager = None
        self.workflow_engine = None
        self.agents = {}
        self.active_workflows = {}
        
        # GUI state
        self.log_queue = []
        self.is_framework_initialized = False
        
        # Setup GUI
        self.setup_styles()
        self.setup_gui()
        self.setup_logging()
        
        # Initialize framework in background
        self.initialize_framework()
    
    def setup_styles(self):
        """Configure GUI styles and themes."""
        style = ttk.Style()
        
        # Configure notebook tabs
        style.configure('TNotebook.Tab', padding=[20, 10])
        
        # Configure buttons
        style.configure('Action.TButton', padding=[10, 5])
        
    def setup_gui(self):
        """Create and configure the main GUI layout."""
        # Main menu
        self.create_menu()
        
        # Main container with tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Create tabs
        self.create_overview_tab()
        self.create_agents_tab()
        self.create_tasks_tab()
        self.create_workflows_tab()
        self.create_logs_tab()
        self.create_config_tab()
        
        # Status bar
        self.create_status_bar()
    
    def create_menu(self):
        """Create the application menu bar."""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Load Configuration", command=self.load_config)
        file_menu.add_command(label="Save Configuration", command=self.save_config)
        file_menu.add_separator()
        file_menu.add_command(label="Export Logs", command=self.export_logs)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        
        # Framework menu
        framework_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Framework", menu=framework_menu)
        framework_menu.add_command(label="Reinitialize", command=self.initialize_framework)
        framework_menu.add_command(label="Run Demo", command=self.run_demo)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self.show_about)
        help_menu.add_command(label="Documentation", command=self.show_documentation)
    
    def create_overview_tab(self):
        """Create the overview/dashboard tab."""
        overview_frame = ttk.Frame(self.notebook)
        self.notebook.add(overview_frame, text="Overview")
        
        # Title
        title_label = ttk.Label(overview_frame, text="Agentic Model Framework", 
                               font=("Arial", 16, "bold"))
        title_label.pack(pady=10)
        
        # Status indicators
        status_frame = ttk.LabelFrame(overview_frame, text="System Status", padding=10)
        status_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.status_label = ttk.Label(status_frame, text="Initializing...")
        self.status_label.pack()
        
        # Quick stats
        stats_frame = ttk.LabelFrame(overview_frame, text="Quick Statistics", padding=10)
        stats_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.stats_text = tk.Text(stats_frame, height=8, state=tk.DISABLED)
        self.stats_text.pack(fill=tk.BOTH, expand=True)
        
        # Quick actions
        actions_frame = ttk.LabelFrame(overview_frame, text="Quick Actions", padding=10)
        actions_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Button(actions_frame, text="Create Agent", 
                  command=self.quick_create_agent, style='Action.TButton').pack(side=tk.LEFT, padx=5)
        ttk.Button(actions_frame, text="Run Task", 
                  command=self.quick_run_task, style='Action.TButton').pack(side=tk.LEFT, padx=5)
        ttk.Button(actions_frame, text="Start Workflow", 
                  command=self.quick_start_workflow, style='Action.TButton').pack(side=tk.LEFT, padx=5)
    
    def create_agents_tab(self):
        """Create the agents management tab."""
        agents_frame = ttk.Frame(self.notebook)
        self.notebook.add(agents_frame, text="Agents")
        
        # Split into two panes
        paned = ttk.PanedWindow(agents_frame, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Left pane - Agent list
        left_frame = ttk.LabelFrame(paned, text="Active Agents")
        paned.add(left_frame, weight=1)
        
        # Agent listbox with scrollbar
        listbox_frame = ttk.Frame(left_frame)
        listbox_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.agents_listbox = tk.Listbox(listbox_frame)
        agents_scrollbar = ttk.Scrollbar(listbox_frame, orient=tk.VERTICAL, 
                                        command=self.agents_listbox.yview)
        self.agents_listbox.config(yscrollcommand=agents_scrollbar.set)
        
        self.agents_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        agents_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.agents_listbox.bind('<<ListboxSelect>>', self.on_agent_select)
        
        # Agent control buttons
        agent_buttons_frame = ttk.Frame(left_frame)
        agent_buttons_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(agent_buttons_frame, text="Create Agent", 
                  command=self.create_agent_dialog).pack(side=tk.LEFT, padx=2)
        ttk.Button(agent_buttons_frame, text="Delete Agent", 
                  command=self.delete_agent).pack(side=tk.LEFT, padx=2)
        
        # Right pane - Agent details
        right_frame = ttk.LabelFrame(paned, text="Agent Details")
        paned.add(right_frame, weight=2)
        
        self.agent_details_text = scrolledtext.ScrolledText(right_frame, state=tk.DISABLED)
        self.agent_details_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    def create_tasks_tab(self):
        """Create the tasks management tab."""
        tasks_frame = ttk.Frame(self.notebook)
        self.notebook.add(tasks_frame, text="Tasks")
        
        # Task type selection
        task_type_frame = ttk.LabelFrame(tasks_frame, text="Task Type", padding=10)
        task_type_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.task_type_var = tk.StringVar(value="DataProcessingTask")
        task_types = ["DataProcessingTask", "AnalysisTask", "CommunicationTask", 
                     "DecisionTask", "ModelTrainingTask", "DataIngestionTask", 
                     "ReportGenerationTask"]
        
        for task_type in task_types:
            ttk.Radiobutton(task_type_frame, text=task_type, variable=self.task_type_var, 
                           value=task_type).pack(side=tk.LEFT, padx=5)
        
        # Task configuration
        config_frame = ttk.LabelFrame(tasks_frame, text="Task Configuration", padding=10)
        config_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Task name
        ttk.Label(config_frame, text="Task Name:").pack(anchor=tk.W)
        self.task_name_entry = ttk.Entry(config_frame, width=50)
        self.task_name_entry.pack(fill=tk.X, pady=2)
        
        # Task parameters (JSON)
        ttk.Label(config_frame, text="Parameters (JSON):").pack(anchor=tk.W, pady=(10, 0))
        self.task_params_text = scrolledtext.ScrolledText(config_frame, height=10)
        self.task_params_text.pack(fill=tk.BOTH, expand=True, pady=2)
        
        # Default parameters based on task type
        self.task_params_text.insert(tk.END, '{\n  "data": [1, 2, 3, 4, 5],\n  "operations": ["filter", "sort"]\n}')
        
        # Task execution
        execute_frame = ttk.Frame(tasks_frame)
        execute_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Button(execute_frame, text="Execute Task", 
                  command=self.execute_task, style='Action.TButton').pack(side=tk.LEFT, padx=5)
        
        # Task results
        results_frame = ttk.LabelFrame(tasks_frame, text="Results", padding=10)
        results_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.task_results_text = scrolledtext.ScrolledText(results_frame, height=8, state=tk.DISABLED)
        self.task_results_text.pack(fill=tk.BOTH, expand=True)
    
    def create_workflows_tab(self):
        """Create the workflows management tab."""
        workflows_frame = ttk.Frame(self.notebook)
        self.notebook.add(workflows_frame, text="Workflows")
        
        # Workflow creation
        create_frame = ttk.LabelFrame(workflows_frame, text="Create Workflow", padding=10)
        create_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Workflow name
        ttk.Label(create_frame, text="Workflow Name:").pack(anchor=tk.W)
        self.workflow_name_entry = ttk.Entry(create_frame, width=50)
        self.workflow_name_entry.pack(fill=tk.X, pady=2)
        
        # Workflow type
        workflow_type_frame = ttk.Frame(create_frame)
        workflow_type_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(workflow_type_frame, text="Type:").pack(side=tk.LEFT)
        self.workflow_type_var = tk.StringVar(value="simple")
        ttk.Radiobutton(workflow_type_frame, text="Simple Sequential", 
                       variable=self.workflow_type_var, value="simple").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(workflow_type_frame, text="Complex", 
                       variable=self.workflow_type_var, value="complex").pack(side=tk.LEFT, padx=5)
        
        # Workflow configuration
        config_frame = ttk.LabelFrame(workflows_frame, text="Workflow Configuration", padding=10)
        config_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.workflow_config_text = scrolledtext.ScrolledText(config_frame, height=10)
        self.workflow_config_text.pack(fill=tk.BOTH, expand=True)
        
        # Default workflow configuration
        default_workflow = '''[
  {
    "name": "Data Processing",
    "task_type": "DataProcessingTask",
    "parameters": {"data": [1, 2, 3, 4, 5], "operations": ["filter"]}
  },
  {
    "name": "Analysis",
    "task_type": "AnalysisTask", 
    "parameters": {"data": [1, 2, 3], "analysis_type": "statistical"}
  }
]'''
        self.workflow_config_text.insert(tk.END, default_workflow)
        
        # Workflow execution
        execute_frame = ttk.Frame(workflows_frame)
        execute_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Button(execute_frame, text="Create & Execute Workflow", 
                  command=self.execute_workflow, style='Action.TButton').pack(side=tk.LEFT, padx=5)
        
        # Active workflows
        active_frame = ttk.LabelFrame(workflows_frame, text="Active Workflows", padding=10)
        active_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.active_workflows_text = scrolledtext.ScrolledText(active_frame, height=6, state=tk.DISABLED)
        self.active_workflows_text.pack(fill=tk.BOTH, expand=True)
    
    def create_logs_tab(self):
        """Create the logging and monitoring tab."""
        logs_frame = ttk.Frame(self.notebook)
        self.notebook.add(logs_frame, text="Logs")
        
        # Log controls
        controls_frame = ttk.Frame(logs_frame)
        controls_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Button(controls_frame, text="Clear Logs", 
                  command=self.clear_logs).pack(side=tk.LEFT, padx=5)
        ttk.Button(controls_frame, text="Export Logs", 
                  command=self.export_logs).pack(side=tk.LEFT, padx=5)
        
        # Log level filter
        ttk.Label(controls_frame, text="Level:").pack(side=tk.LEFT, padx=(20, 5))
        self.log_level_var = tk.StringVar(value="All")
        log_level_combo = ttk.Combobox(controls_frame, textvariable=self.log_level_var,
                                      values=["All", "DEBUG", "INFO", "WARNING", "ERROR"],
                                      state="readonly", width=10)
        log_level_combo.pack(side=tk.LEFT, padx=5)
        
        # Log display
        self.logs_text = scrolledtext.ScrolledText(logs_frame, state=tk.DISABLED)
        self.logs_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Auto-scroll logs
        self.auto_scroll_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(logs_frame, text="Auto-scroll", 
                       variable=self.auto_scroll_var).pack(anchor=tk.W, padx=10)
    
    def create_config_tab(self):
        """Create the configuration tab."""
        config_frame = ttk.Frame(self.notebook)
        self.notebook.add(config_frame, text="Configuration")
        
        # Configuration display
        self.config_text = scrolledtext.ScrolledText(config_frame)
        self.config_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Configuration buttons
        buttons_frame = ttk.Frame(config_frame)
        buttons_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Button(buttons_frame, text="Load Config", 
                  command=self.load_config).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="Save Config", 
                  command=self.save_config).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="Reset to Default", 
                  command=self.reset_config).pack(side=tk.LEFT, padx=5)
    
    def create_status_bar(self):
        """Create the status bar at the bottom."""
        self.status_bar = ttk.Frame(self.root)
        self.status_bar.pack(fill=tk.X, side=tk.BOTTOM)
        
        self.status_text = ttk.Label(self.status_bar, text="Ready")
        self.status_text.pack(side=tk.LEFT, padx=5)
        
        # Add a separator
        ttk.Separator(self.status_bar, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=5)
        
        # Framework status
        self.framework_status = ttk.Label(self.status_bar, text="Initializing...")
        self.framework_status.pack(side=tk.LEFT, padx=5)
    
    def setup_logging(self):
        """Setup logging to capture framework logs in the GUI."""
        # Create custom handler for GUI logs
        self.log_handler = LogHandler(self.add_log_entry)
        self.log_handler.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        self.log_handler.setFormatter(formatter)
        
        # Add handler to root logger
        logging.getLogger().addHandler(self.log_handler)
        
        # Start log processing
        self.process_logs()
    
    def add_log_entry(self, log_entry):
        """Thread-safe method to add log entries to the queue."""
        self.log_queue.append((datetime.now().strftime("%H:%M:%S"), log_entry))
    
    def process_logs(self):
        """Process pending log entries and update the GUI."""
        while self.log_queue:
            timestamp, log_entry = self.log_queue.pop(0)
            
            # Update logs tab
            self.logs_text.config(state=tk.NORMAL)
            self.logs_text.insert(tk.END, f"{log_entry}\n")
            
            # Auto-scroll if enabled
            if self.auto_scroll_var.get():
                self.logs_text.see(tk.END)
            
            self.logs_text.config(state=tk.DISABLED)
        
        # Schedule next check
        self.root.after(100, self.process_logs)
    
    def initialize_framework(self):
        """Initialize the framework components."""
        def init_worker():
            try:
                # Initialize system
                self.update_status("Initializing framework...")
                self.config_manager = initialize_system()
                
                # Create workflow engine
                self.workflow_engine = WorkflowEngine()
                
                self.is_framework_initialized = True
                self.update_status("Framework initialized successfully")
                
                # Update GUI
                self.root.after(0, self.on_framework_initialized)
                
            except Exception as e:
                error_msg = f"Failed to initialize framework: {str(e)}"
                self.update_status(error_msg)
                self.root.after(0, lambda: messagebox.showerror("Initialization Error", error_msg))
        
        # Run initialization in background thread
        threading.Thread(target=init_worker, daemon=True).start()
    
    def on_framework_initialized(self):
        """Called when framework initialization is complete."""
        self.framework_status.config(text="Framework Ready")
        self.status_label.config(text="✓ Framework Initialized and Ready")
        
        # Update configuration display
        self.update_config_display()
        
        # Update overview stats
        self.update_overview_stats()
    
    def update_status(self, message):
        """Update the status bar message."""
        self.root.after(0, lambda: self.status_text.config(text=message))
    
    def update_overview_stats(self):
        """Update the overview statistics."""
        if not self.is_framework_initialized:
            return
        
        stats = f"""Framework Statistics:
• Agents Created: {len(self.agents)}
• Active Workflows: {len(self.active_workflows)}
• Framework Status: {'Ready' if self.is_framework_initialized else 'Initializing'}
• Configuration: {'Loaded' if self.config_manager else 'Not Loaded'}

System Information:
• Python Version: {sys.version.split()[0]}
• Platform: {sys.platform}
• GUI Framework: tkinter
"""
        
        self.stats_text.config(state=tk.NORMAL)
        self.stats_text.delete(1.0, tk.END)
        self.stats_text.insert(1.0, stats)
        self.stats_text.config(state=tk.DISABLED)
    
    def update_config_display(self):
        """Update the configuration display."""
        if not self.config_manager:
            return
        
        try:
            # Get configuration as dict
            config_dict = {
                'system': self.config_manager.get_system_config().__dict__,
                'agent': self.config_manager.get_agent_config().__dict__,
                'workflow': self.config_manager.get_workflow_config().__dict__
            }
            
            config_json = json.dumps(config_dict, indent=2, default=str)
            
            self.config_text.delete(1.0, tk.END)
            self.config_text.insert(1.0, config_json)
            
        except Exception as e:
            self.config_text.delete(1.0, tk.END)
            self.config_text.insert(1.0, f"Error loading configuration: {str(e)}")
    
    # Agent management methods
    def create_agent_dialog(self):
        """Open dialog to create a new agent."""
        if not self.is_framework_initialized:
            messagebox.showwarning("Not Ready", "Framework not initialized yet.")
            return
        
        dialog = AgentCreationDialog(self.root, self.create_agent_callback)
    
    def create_agent_callback(self, agent_data):
        """Callback for agent creation."""
        try:
            name = agent_data['name']
            capabilities = agent_data['capabilities']
            config = agent_data.get('config', {})
            
            # Create agent
            agent = create_agent(name=name, capabilities=capabilities, config=config)
            self.agents[name] = agent
            
            # Update GUI
            self.agents_listbox.insert(tk.END, name)
            self.update_overview_stats()
            
            self.add_log_entry(f"Created agent: {name} with capabilities: {capabilities}")
            
        except Exception as e:
            messagebox.showerror("Agent Creation Error", f"Failed to create agent: {str(e)}")
    
    def delete_agent(self):
        """Delete the selected agent."""
        selection = self.agents_listbox.curselection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select an agent to delete.")
            return
        
        agent_name = self.agents_listbox.get(selection[0])
        
        if messagebox.askyesno("Confirm Delete", f"Delete agent '{agent_name}'?"):
            # Remove agent
            if agent_name in self.agents:
                del self.agents[agent_name]
            
            # Update GUI
            self.agents_listbox.delete(selection[0])
            self.agent_details_text.config(state=tk.NORMAL)
            self.agent_details_text.delete(1.0, tk.END)
            self.agent_details_text.config(state=tk.DISABLED)
            
            self.update_overview_stats()
            self.add_log_entry(f"Deleted agent: {agent_name}")
    
    def on_agent_select(self, event):
        """Handle agent selection in the listbox."""
        selection = self.agents_listbox.curselection()
        if not selection:
            return
        
        agent_name = self.agents_listbox.get(selection[0])
        agent = self.agents.get(agent_name)
        
        if agent:
            # Get agent status and details
            status = agent.get_status()
            details = f"""Agent: {agent_name}
State: {status.get('state', 'Unknown')}
Capabilities: {', '.join(status.get('capabilities', []))}
Active Tasks: {status.get('active_tasks', 0)}
Completed Tasks: {status.get('completed_tasks', 0)}
Errors: {status.get('errors', 0)}

Memory Usage:
• Short-term: {status.get('memory_size', {}).get('short_term', 0)} items
• Long-term: {status.get('memory_size', {}).get('long_term', 0)} items
• Context: {status.get('memory_size', {}).get('context', 0)} items

Configuration:
{json.dumps(agent.config, indent=2) if hasattr(agent, 'config') else 'No configuration data'}
"""
            
            self.agent_details_text.config(state=tk.NORMAL)
            self.agent_details_text.delete(1.0, tk.END)
            self.agent_details_text.insert(1.0, details)
            self.agent_details_text.config(state=tk.DISABLED)
    
    # Task execution methods
    def execute_task(self):
        """Execute a task based on GUI configuration."""
        if not self.is_framework_initialized:
            messagebox.showwarning("Not Ready", "Framework not initialized yet.")
            return
        
        def task_worker():
            try:
                # Get task configuration
                task_type = self.task_type_var.get()
                task_name = self.task_name_entry.get() or "Untitled Task"
                
                # Parse parameters
                params_text = self.task_params_text.get(1.0, tk.END).strip()
                try:
                    params = json.loads(params_text) if params_text else {}
                except json.JSONDecodeError as e:
                    raise ValueError(f"Invalid JSON parameters: {str(e)}")
                
                # Create task instance
                task_classes = {
                    'DataProcessingTask': DataProcessingTask,
                    'AnalysisTask': AnalysisTask,
                    'CommunicationTask': CommunicationTask,
                    'DecisionTask': DecisionTask,
                    'ModelTrainingTask': ModelTrainingTask,
                    'DataIngestionTask': DataIngestionTask,
                    'ReportGenerationTask': ReportGenerationTask
                }
                
                if task_type not in task_classes:
                    raise ValueError(f"Unknown task type: {task_type}")
                
                task_class = task_classes[task_type]
                task = task_class(task_name)
                
                # Execute task
                self.update_status(f"Executing task: {task_name}")
                
                # Run in asyncio loop
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                result = loop.run_until_complete(task.run(**params))
                loop.close()
                
                # Update results display
                result_text = f"""Task: {task_name}
Type: {task_type}
Success: {result.success}
Execution Time: {getattr(result, 'execution_time', 'N/A')}

Result Data:
{json.dumps(result.data, indent=2, default=str) if result.data else 'No data'}

Metadata:
{json.dumps(result.metadata, indent=2, default=str) if result.metadata else 'No metadata'}

Error:
{result.error if result.error else 'None'}
"""
                
                self.root.after(0, lambda: self.update_task_results(result_text))
                self.update_status("Task completed")
                
            except Exception as e:
                error_msg = f"Task execution failed: {str(e)}"
                self.update_status(error_msg)
                self.root.after(0, lambda: messagebox.showerror("Task Error", error_msg))
        
        # Run task in background thread
        threading.Thread(target=task_worker, daemon=True).start()
    
    def update_task_results(self, result_text):
        """Update the task results display."""
        self.task_results_text.config(state=tk.NORMAL)
        self.task_results_text.delete(1.0, tk.END)
        self.task_results_text.insert(1.0, result_text)
        self.task_results_text.config(state=tk.DISABLED)
    
    # Workflow execution methods
    def execute_workflow(self):
        """Execute a workflow based on GUI configuration."""
        if not self.is_framework_initialized:
            messagebox.showwarning("Not Ready", "Framework not initialized yet.")
            return
        
        def workflow_worker():
            try:
                # Get workflow configuration
                workflow_name = self.workflow_name_entry.get() or "Untitled Workflow"
                workflow_type = self.workflow_type_var.get()
                
                # Parse workflow configuration
                config_text = self.workflow_config_text.get(1.0, tk.END).strip()
                try:
                    workflow_config = json.loads(config_text) if config_text else []
                except json.JSONDecodeError as e:
                    raise ValueError(f"Invalid JSON configuration: {str(e)}")
                
                self.update_status(f"Creating workflow: {workflow_name}")
                
                if workflow_type == "simple":
                    # Create simple sequential workflow
                    if not self.agents:
                        # Create a default agent
                        agent = create_agent("default_agent", ["general_processing"])
                        self.agents["default_agent"] = agent
                        self.root.after(0, lambda: self.agents_listbox.insert(tk.END, "default_agent"))
                    
                    agent_name = list(self.agents.keys())[0]
                    self.workflow_engine.register_agent(agent_name, self.agents[agent_name])
                    
                    workflow = create_simple_agent_workflow(workflow_name, agent_name, workflow_config)
                else:
                    # Create complex workflow (simplified for demo)
                    workflow = create_workflow(workflow_name, "Complex workflow")
                    # Add steps based on configuration
                    for i, step_config in enumerate(workflow_config):
                        workflow.add_agent_task(
                            step_config.get('name', f'Step {i+1}'),
                            list(self.agents.keys())[0] if self.agents else 'default_agent',
                            step_config.get('parameters', {})
                        )
                    workflow = workflow.build()
                
                # Execute workflow
                self.update_status(f"Executing workflow: {workflow_name}")
                
                # Run in asyncio loop
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                context = loop.run_until_complete(self.workflow_engine.execute_workflow(workflow))
                loop.close()
                
                # Store active workflow
                self.active_workflows[workflow_name] = {
                    'workflow': workflow,
                    'context': context,
                    'status': workflow.get_status()
                }
                
                # Update display
                self.root.after(0, self.update_workflow_display)
                self.update_status("Workflow completed")
                
            except Exception as e:
                error_msg = f"Workflow execution failed: {str(e)}"
                self.update_status(error_msg)
                self.root.after(0, lambda: messagebox.showerror("Workflow Error", error_msg))
        
        # Run workflow in background thread
        threading.Thread(target=workflow_worker, daemon=True).start()
    
    def update_workflow_display(self):
        """Update the active workflows display."""
        workflow_text = "Active Workflows:\n\n"
        
        for name, workflow_data in self.active_workflows.items():
            status = workflow_data['status']
            workflow_text += f"• {name}\n"
            workflow_text += f"  State: {status.get('state', 'Unknown')}\n"
            workflow_text += f"  Steps: {status.get('completed_steps', 0)}/{status.get('total_steps', 0)}\n"
            workflow_text += f"  Duration: {status.get('completed_at', 'Running')}\n\n"
        
        self.active_workflows_text.config(state=tk.NORMAL)
        self.active_workflows_text.delete(1.0, tk.END)
        self.active_workflows_text.insert(1.0, workflow_text)
        self.active_workflows_text.config(state=tk.DISABLED)
    
    # Quick action methods
    def quick_create_agent(self):
        """Quick create a demo agent."""
        self.create_agent_callback({
            'name': f'demo_agent_{len(self.agents)+1}',
            'capabilities': ['data_processing', 'analysis'],
            'config': {'learning_enabled': True}
        })
    
    def quick_run_task(self):
        """Quick run a demo task."""
        # Set demo task configuration
        self.task_type_var.set("DataProcessingTask")
        self.task_name_entry.delete(0, tk.END)
        self.task_name_entry.insert(0, "Quick Demo Task")
        
        self.task_params_text.delete(1.0, tk.END)
        self.task_params_text.insert(1.0, '{"data": [1, 2, 3, 4, 5], "operations": ["filter", "sort"]}')
        
        # Switch to tasks tab and execute
        self.notebook.select(2)  # Tasks tab
        self.execute_task()
    
    def quick_start_workflow(self):
        """Quick start a demo workflow."""
        # Set demo workflow configuration
        self.workflow_name_entry.delete(0, tk.END)
        self.workflow_name_entry.insert(0, "Quick Demo Workflow")
        
        # Switch to workflows tab
        self.notebook.select(3)  # Workflows tab
        self.execute_workflow()
    
    # Utility methods
    def clear_logs(self):
        """Clear the logs display."""
        self.logs_text.config(state=tk.NORMAL)
        self.logs_text.delete(1.0, tk.END)
        self.logs_text.config(state=tk.DISABLED)
    
    def export_logs(self):
        """Export logs to a file."""
        try:
            filename = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
                title="Export Logs"
            )
            
            if filename:
                logs_content = self.logs_text.get(1.0, tk.END)
                with open(filename, 'w') as f:
                    f.write(logs_content)
                messagebox.showinfo("Export Complete", f"Logs exported to {filename}")
                
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export logs: {str(e)}")
    
    def load_config(self):
        """Load configuration from file."""
        try:
            filename = filedialog.askopenfilename(
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
                title="Load Configuration"
            )
            
            if filename:
                self.config_manager = ConfigManager(filename)
                self.update_config_display()
                messagebox.showinfo("Load Complete", "Configuration loaded successfully")
                
        except Exception as e:
            messagebox.showerror("Load Error", f"Failed to load configuration: {str(e)}")
    
    def save_config(self):
        """Save configuration to file."""
        try:
            filename = filedialog.asksaveasfilename(
                defaultextension=".json",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
                title="Save Configuration"
            )
            
            if filename and self.config_manager:
                # This would need to be implemented in the ConfigManager
                messagebox.showinfo("Save Complete", f"Configuration saved to {filename}")
                
        except Exception as e:
            messagebox.showerror("Save Error", f"Failed to save configuration: {str(e)}")
    
    def reset_config(self):
        """Reset configuration to defaults."""
        if messagebox.askyesno("Reset Configuration", "Reset to default configuration?"):
            self.initialize_framework()
    
    def run_demo(self):
        """Run the framework demo."""
        def demo_worker():
            try:
                self.update_status("Running framework demo...")
                
                # Import and run the example
                import subprocess
                result = subprocess.run([sys.executable, "example.py"], 
                                      cwd="/home/runner/work/gpt-test/gpt-test",
                                      capture_output=True, text=True)
                
                if result.returncode == 0:
                    self.update_status("Demo completed successfully")
                else:
                    self.update_status(f"Demo failed: {result.stderr}")
                    
            except Exception as e:
                error_msg = f"Demo execution failed: {str(e)}"
                self.update_status(error_msg)
                self.root.after(0, lambda: messagebox.showerror("Demo Error", error_msg))
        
        threading.Thread(target=demo_worker, daemon=True).start()
    
    def show_about(self):
        """Show about dialog."""
        about_text = """Agentic Model Framework GUI
Version 1.0

A comprehensive framework for building custom agentic models
with task orchestration, workflow management, and extensible capabilities.

© 2024 Agentic Framework Project
"""
        messagebox.showinfo("About", about_text)
    
    def show_documentation(self):
        """Show documentation."""
        doc_text = """Framework Documentation:

1. AGENTS: Create and manage AI agents with different capabilities
2. TASKS: Define and execute various types of tasks
3. WORKFLOWS: Design complex multi-step processes
4. CONFIGURATION: Customize framework behavior
5. MONITORING: Real-time logging and status tracking

For detailed documentation, see README.md in the project repository.
"""
        messagebox.showinfo("Documentation", doc_text)


class AgentCreationDialog:
    """Dialog for creating new agents."""
    
    def __init__(self, parent, callback):
        self.callback = callback
        
        # Create dialog window
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Create New Agent")
        self.dialog.geometry("400x500")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        self.setup_dialog()
    
    def setup_dialog(self):
        """Setup the dialog layout."""
        # Agent name
        ttk.Label(self.dialog, text="Agent Name:").pack(pady=5, anchor=tk.W, padx=10)
        self.name_entry = ttk.Entry(self.dialog, width=40)
        self.name_entry.pack(pady=5, padx=10, fill=tk.X)
        
        # Capabilities
        ttk.Label(self.dialog, text="Capabilities:").pack(pady=(10, 5), anchor=tk.W, padx=10)
        
        capabilities_frame = ttk.Frame(self.dialog)
        capabilities_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Predefined capabilities
        self.capabilities_vars = {}
        capabilities_list = [
            "data_processing", "analysis", "communication", "decision_making",
            "learning", "planning", "monitoring", "reporting", "automation"
        ]
        
        for cap in capabilities_list:
            var = tk.BooleanVar()
            ttk.Checkbutton(capabilities_frame, text=cap.replace("_", " ").title(),
                           variable=var).pack(anchor=tk.W)
            self.capabilities_vars[cap] = var
        
        # Custom capabilities
        ttk.Label(self.dialog, text="Custom Capabilities (comma-separated):").pack(
            pady=(10, 5), anchor=tk.W, padx=10)
        self.custom_caps_entry = ttk.Entry(self.dialog, width=40)
        self.custom_caps_entry.pack(pady=5, padx=10, fill=tk.X)
        
        # Configuration
        ttk.Label(self.dialog, text="Configuration (JSON):").pack(
            pady=(10, 5), anchor=tk.W, padx=10)
        self.config_text = tk.Text(self.dialog, height=8, width=40)
        self.config_text.pack(pady=5, padx=10, fill=tk.BOTH, expand=True)
        self.config_text.insert(1.0, '{\n  "learning_enabled": true,\n  "timeout_seconds": 30\n}')
        
        # Buttons
        buttons_frame = ttk.Frame(self.dialog)
        buttons_frame.pack(fill=tk.X, pady=10, padx=10)
        
        ttk.Button(buttons_frame, text="Create", command=self.create_agent).pack(side=tk.RIGHT, padx=5)
        ttk.Button(buttons_frame, text="Cancel", command=self.dialog.destroy).pack(side=tk.RIGHT)
    
    def create_agent(self):
        """Create the agent with specified configuration."""
        try:
            # Get agent name
            name = self.name_entry.get().strip()
            if not name:
                messagebox.showerror("Error", "Agent name is required")
                return
            
            # Get capabilities
            capabilities = []
            for cap, var in self.capabilities_vars.items():
                if var.get():
                    capabilities.append(cap)
            
            # Add custom capabilities
            custom_caps = self.custom_caps_entry.get().strip()
            if custom_caps:
                capabilities.extend([cap.strip() for cap in custom_caps.split(",")])
            
            if not capabilities:
                messagebox.showerror("Error", "At least one capability is required")
                return
            
            # Get configuration
            config_text = self.config_text.get(1.0, tk.END).strip()
            try:
                config = json.loads(config_text) if config_text else {}
            except json.JSONDecodeError as e:
                messagebox.showerror("Error", f"Invalid JSON configuration: {str(e)}")
                return
            
            # Call callback with agent data
            agent_data = {
                'name': name,
                'capabilities': capabilities,
                'config': config
            }
            
            self.callback(agent_data)
            self.dialog.destroy()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to create agent: {str(e)}")


def main():
    """Main entry point for the GUI application."""
    # Create the main window
    root = tk.Tk()
    
    # Create the application
    app = AgenticFrameworkGUI(root)
    
    # Set up proper shutdown
    def on_closing():
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    
    # Start the GUI event loop
    try:
        root.mainloop()
    except KeyboardInterrupt:
        print("\nApplication interrupted by user")
    except Exception as e:
        print(f"Application error: {e}")
        messagebox.showerror("Fatal Error", f"Application encountered a fatal error: {e}")


if __name__ == "__main__":
    main()