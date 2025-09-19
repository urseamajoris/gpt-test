#!/usr/bin/env python3
"""
Agentic Model Framework Web GUI Application

A cross-platform web-based graphical user interface for the Agentic Model Framework.
This application provides an intuitive web interface to create agents, design workflows,
execute tasks, and monitor the framework's operations.

Features:
- Agent creation and management
- Task definition and execution
- Workflow design and execution
- Real-time logging and monitoring
- Configuration management
- Cross-platform executable

Requirements:
- Python 3.7+
- Flask
- Flask-SocketIO
"""

import os
import sys
import json
import asyncio
import threading
import logging
import webbrowser
from datetime import datetime
from typing import Dict, Any, List, Optional
from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_socketio import SocketIO, emit
import time

# Import framework components
try:
    from agent import create_agent, AgentBuilder, AgentState
    from workflow import WorkflowEngine, create_workflow, create_simple_agent_workflow
    from tasks import DataProcessingTask, AnalysisTask, CommunicationTask, DecisionTask
    from tasks.custom_tasks import ModelTrainingTask, DataIngestionTask, ReportGenerationTask
    from config import initialize_system, create_default_config_file, ConfigManager
except ImportError as e:
    print(f"Error importing framework modules: {e}")
    print("Please ensure the framework modules are in the Python path.")
    sys.exit(1)


class WebGUIHandler(logging.Handler):
    """Custom logging handler to send logs to web clients."""
    
    def __init__(self, socketio):
        super().__init__()
        self.socketio = socketio
    
    def emit(self, record):
        log_entry = self.format(record)
        # Send log to all connected clients
        self.socketio.emit('log_message', {
            'timestamp': datetime.now().isoformat(),
            'level': record.levelname,
            'message': log_entry
        })


class AgenticFrameworkWebApp:
    """Web application for the Agentic Model Framework."""
    
    def __init__(self):
        # Flask setup
        self.app = Flask(__name__, 
                         template_folder='templates',
                         static_folder='static')
        self.app.config['SECRET_KEY'] = 'agentic-framework-secret-key'
        
        # SocketIO for real-time communication
        self.socketio = SocketIO(self.app, cors_allowed_origins="*")
        
        # Framework components
        self.config_manager = None
        self.workflow_engine = None
        self.agents = {}
        self.active_workflows = {}
        self.task_results = {}
        
        # Application state
        self.is_framework_initialized = False
        self.initialization_error = None
        
        # Setup routes and handlers
        self.setup_routes()
        self.setup_socketio_handlers()
        self.setup_logging()
        
        # Create templates directory and files
        self.create_web_templates()
        
    def create_web_templates(self):
        """Create HTML templates for the web interface."""
        # Create templates directory
        templates_dir = os.path.join(os.path.dirname(__file__), 'templates')
        os.makedirs(templates_dir, exist_ok=True)
        
        # Create static directory
        static_dir = os.path.join(os.path.dirname(__file__), 'static')
        os.makedirs(static_dir, exist_ok=True)
        
        # Create main template
        main_template = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Agentic Model Framework - Control Center</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.0.1/socket.io.js"></script>
    <style>
        .framework-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 1rem 0;
        }
        .status-card {
            border-left: 4px solid #28a745;
        }
        .log-container {
            height: 400px;
            overflow-y: auto;
            background-color: #f8f9fa;
            border: 1px solid #dee2e6;
            border-radius: 0.375rem;
            padding: 10px;
            font-family: 'Monaco', 'Courier New', monospace;
            font-size: 0.875rem;
        }
        .agent-card {
            transition: transform 0.2s;
        }
        .agent-card:hover {
            transform: translateY(-2px);
        }
        .task-result {
            background-color: #f8f9fa;
            border-radius: 0.375rem;
            padding: 1rem;
            margin-top: 1rem;
        }
        .workflow-step {
            padding: 0.5rem;
            margin: 0.25rem 0;
            border-radius: 0.25rem;
            background-color: #e9ecef;
        }
        .step-completed {
            background-color: #d4edda;
            border-left: 4px solid #28a745;
        }
        .step-running {
            background-color: #fff3cd;
            border-left: 4px solid #ffc107;
        }
        .step-failed {
            background-color: #f8d7da;
            border-left: 4px solid #dc3545;
        }
    </style>
</head>
<body>
    <!-- Header -->
    <div class="framework-header">
        <div class="container">
            <div class="row align-items-center">
                <div class="col">
                    <h1 class="h3 mb-0">
                        <i class="fas fa-robot me-2"></i>
                        Agentic Model Framework
                    </h1>
                    <p class="mb-0">Control Center & Dashboard</p>
                </div>
                <div class="col-auto">
                    <span id="framework-status" class="badge bg-warning">Initializing...</span>
                </div>
            </div>
        </div>
    </div>

    <!-- Main Content -->
    <div class="container-fluid mt-4">
        <!-- Navigation Tabs -->
        <ul class="nav nav-tabs" id="mainTabs" role="tablist">
            <li class="nav-item" role="presentation">
                <button class="nav-link active" id="overview-tab" data-bs-toggle="tab" data-bs-target="#overview" type="button" role="tab">
                    <i class="fas fa-tachometer-alt me-1"></i> Overview
                </button>
            </li>
            <li class="nav-item" role="presentation">
                <button class="nav-link" id="agents-tab" data-bs-toggle="tab" data-bs-target="#agents" type="button" role="tab">
                    <i class="fas fa-users me-1"></i> Agents
                </button>
            </li>
            <li class="nav-item" role="presentation">
                <button class="nav-link" id="tasks-tab" data-bs-toggle="tab" data-bs-target="#tasks" type="button" role="tab">
                    <i class="fas fa-tasks me-1"></i> Tasks
                </button>
            </li>
            <li class="nav-item" role="presentation">
                <button class="nav-link" id="workflows-tab" data-bs-toggle="tab" data-bs-target="#workflows" type="button" role="tab">
                    <i class="fas fa-project-diagram me-1"></i> Workflows
                </button>
            </li>
            <li class="nav-item" role="presentation">
                <button class="nav-link" id="logs-tab" data-bs-toggle="tab" data-bs-target="#logs" type="button" role="tab">
                    <i class="fas fa-file-alt me-1"></i> Logs
                </button>
            </li>
            <li class="nav-item" role="presentation">
                <button class="nav-link" id="config-tab" data-bs-toggle="tab" data-bs-target="#config" type="button" role="tab">
                    <i class="fas fa-cog me-1"></i> Configuration
                </button>
            </li>
        </ul>

        <!-- Tab Content -->
        <div class="tab-content mt-3" id="mainTabContent">
            <!-- Overview Tab -->
            <div class="tab-pane fade show active" id="overview" role="tabpanel">
                <div class="row">
                    <div class="col-md-8">
                        <div class="card status-card">
                            <div class="card-body">
                                <h5 class="card-title">
                                    <i class="fas fa-info-circle me-2"></i>Framework Status
                                </h5>
                                <p id="framework-status-text" class="card-text">Initializing framework...</p>
                                <div class="row mt-3">
                                    <div class="col-md-3 text-center">
                                        <h3 id="agents-count" class="text-primary">0</h3>
                                        <small class="text-muted">Active Agents</small>
                                    </div>
                                    <div class="col-md-3 text-center">
                                        <h3 id="workflows-count" class="text-success">0</h3>
                                        <small class="text-muted">Workflows</small>
                                    </div>
                                    <div class="col-md-3 text-center">
                                        <h3 id="tasks-count" class="text-info">0</h3>
                                        <small class="text-muted">Tasks Executed</small>
                                    </div>
                                    <div class="col-md-3 text-center">
                                        <h3 id="logs-count" class="text-warning">0</h3>
                                        <small class="text-muted">Log Entries</small>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-4">
                        <div class="card">
                            <div class="card-body">
                                <h5 class="card-title">
                                    <i class="fas fa-bolt me-2"></i>Quick Actions
                                </h5>
                                <div class="d-grid gap-2">
                                    <button class="btn btn-primary" onclick="quickCreateAgent()">
                                        <i class="fas fa-plus me-1"></i> Create Agent
                                    </button>
                                    <button class="btn btn-success" onclick="quickRunTask()">
                                        <i class="fas fa-play me-1"></i> Run Task
                                    </button>
                                    <button class="btn btn-info" onclick="quickStartWorkflow()">
                                        <i class="fas fa-rocket me-1"></i> Start Workflow
                                    </button>
                                    <button class="btn btn-warning" onclick="runDemo()">
                                        <i class="fas fa-demo me-1"></i> Run Demo
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Agents Tab -->
            <div class="tab-pane fade" id="agents" role="tabpanel">
                <div class="row">
                    <div class="col-md-6">
                        <div class="card">
                            <div class="card-header">
                                <h5 class="mb-0">
                                    <i class="fas fa-users me-2"></i>Active Agents
                                </h5>
                            </div>
                            <div class="card-body">
                                <div class="mb-3">
                                    <button class="btn btn-primary" data-bs-toggle="modal" data-bs-target="#createAgentModal">
                                        <i class="fas fa-plus me-1"></i> Create Agent
                                    </button>
                                </div>
                                <div id="agents-list">
                                    <p class="text-muted">No agents created yet.</p>
                                </div>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-6">
                        <div class="card">
                            <div class="card-header">
                                <h5 class="mb-0">
                                    <i class="fas fa-info me-2"></i>Agent Details
                                </h5>
                            </div>
                            <div class="card-body">
                                <div id="agent-details">
                                    <p class="text-muted">Select an agent to view details.</p>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Tasks Tab -->
            <div class="tab-pane fade" id="tasks" role="tabpanel">
                <div class="card">
                    <div class="card-header">
                        <h5 class="mb-0">
                            <i class="fas fa-tasks me-2"></i>Task Execution
                        </h5>
                    </div>
                    <div class="card-body">
                        <form id="task-form">
                            <div class="row">
                                <div class="col-md-6">
                                    <div class="mb-3">
                                        <label for="task-name" class="form-label">Task Name</label>
                                        <input type="text" class="form-control" id="task-name" placeholder="Enter task name">
                                    </div>
                                    <div class="mb-3">
                                        <label for="task-type" class="form-label">Task Type</label>
                                        <select class="form-select" id="task-type">
                                            <option value="DataProcessingTask">Data Processing Task</option>
                                            <option value="AnalysisTask">Analysis Task</option>
                                            <option value="CommunicationTask">Communication Task</option>
                                            <option value="DecisionTask">Decision Task</option>
                                            <option value="ModelTrainingTask">Model Training Task</option>
                                            <option value="DataIngestionTask">Data Ingestion Task</option>
                                            <option value="ReportGenerationTask">Report Generation Task</option>
                                        </select>
                                    </div>
                                </div>
                                <div class="col-md-6">
                                    <div class="mb-3">
                                        <label for="task-params" class="form-label">Parameters (JSON)</label>
                                        <textarea class="form-control" id="task-params" rows="8" placeholder="Enter task parameters as JSON">{"data": [1, 2, 3, 4, 5], "operations": ["filter", "sort"]}</textarea>
                                    </div>
                                </div>
                            </div>
                            <button type="button" class="btn btn-success" onclick="executeTask()">
                                <i class="fas fa-play me-1"></i> Execute Task
                            </button>
                        </form>
                        
                        <div id="task-results" class="mt-4" style="display: none;">
                            <h6>Task Results:</h6>
                            <div id="task-results-content" class="task-result"></div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Workflows Tab -->
            <div class="tab-pane fade" id="workflows" role="tabpanel">
                <div class="card">
                    <div class="card-header">
                        <h5 class="mb-0">
                            <i class="fas fa-project-diagram me-2"></i>Workflow Management
                        </h5>
                    </div>
                    <div class="card-body">
                        <form id="workflow-form">
                            <div class="row">
                                <div class="col-md-6">
                                    <div class="mb-3">
                                        <label for="workflow-name" class="form-label">Workflow Name</label>
                                        <input type="text" class="form-control" id="workflow-name" placeholder="Enter workflow name">
                                    </div>
                                    <div class="mb-3">
                                        <label for="workflow-type" class="form-label">Workflow Type</label>
                                        <select class="form-select" id="workflow-type">
                                            <option value="simple">Simple Sequential</option>
                                            <option value="complex">Complex</option>
                                        </select>
                                    </div>
                                </div>
                                <div class="col-md-6">
                                    <div class="mb-3">
                                        <label for="workflow-config" class="form-label">Workflow Configuration (JSON)</label>
                                        <textarea class="form-control" id="workflow-config" rows="8" placeholder="Enter workflow configuration">[
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
]</textarea>
                                    </div>
                                </div>
                            </div>
                            <button type="button" class="btn btn-primary" onclick="executeWorkflow()">
                                <i class="fas fa-rocket me-1"></i> Create & Execute Workflow
                            </button>
                        </form>
                        
                        <div id="workflow-results" class="mt-4" style="display: none;">
                            <h6>Active Workflows:</h6>
                            <div id="workflow-results-content"></div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Logs Tab -->
            <div class="tab-pane fade" id="logs" role="tabpanel">
                <div class="card">
                    <div class="card-header d-flex justify-content-between align-items-center">
                        <h5 class="mb-0">
                            <i class="fas fa-file-alt me-2"></i>System Logs
                        </h5>
                        <div>
                            <button class="btn btn-sm btn-outline-secondary" onclick="clearLogs()">
                                <i class="fas fa-trash me-1"></i> Clear
                            </button>
                            <button class="btn btn-sm btn-outline-primary" onclick="exportLogs()">
                                <i class="fas fa-download me-1"></i> Export
                            </button>
                        </div>
                    </div>
                    <div class="card-body">
                        <div id="logs-container" class="log-container"></div>
                    </div>
                </div>
            </div>

            <!-- Configuration Tab -->
            <div class="tab-pane fade" id="config" role="tabpanel">
                <div class="card">
                    <div class="card-header">
                        <h5 class="mb-0">
                            <i class="fas fa-cog me-2"></i>Framework Configuration
                        </h5>
                    </div>
                    <div class="card-body">
                        <div class="mb-3">
                            <button class="btn btn-outline-primary me-2" onclick="loadConfig()">
                                <i class="fas fa-upload me-1"></i> Load Config
                            </button>
                            <button class="btn btn-outline-success me-2" onclick="saveConfig()">
                                <i class="fas fa-save me-1"></i> Save Config
                            </button>
                            <button class="btn btn-outline-warning" onclick="resetConfig()">
                                <i class="fas fa-undo me-1"></i> Reset to Default
                            </button>
                        </div>
                        <textarea id="config-content" class="form-control" rows="20" placeholder="Configuration will appear here..."></textarea>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- Create Agent Modal -->
    <div class="modal fade" id="createAgentModal" tabindex="-1">
        <div class="modal-dialog">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title">Create New Agent</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                </div>
                <div class="modal-body">
                    <form id="create-agent-form">
                        <div class="mb-3">
                            <label for="agent-name" class="form-label">Agent Name</label>
                            <input type="text" class="form-control" id="agent-name" required>
                        </div>
                        <div class="mb-3">
                            <label class="form-label">Capabilities</label>
                            <div class="row">
                                <div class="col-md-6">
                                    <div class="form-check">
                                        <input class="form-check-input" type="checkbox" value="data_processing" id="cap-data-processing">
                                        <label class="form-check-label" for="cap-data-processing">Data Processing</label>
                                    </div>
                                    <div class="form-check">
                                        <input class="form-check-input" type="checkbox" value="analysis" id="cap-analysis">
                                        <label class="form-check-label" for="cap-analysis">Analysis</label>
                                    </div>
                                    <div class="form-check">
                                        <input class="form-check-input" type="checkbox" value="communication" id="cap-communication">
                                        <label class="form-check-label" for="cap-communication">Communication</label>
                                    </div>
                                    <div class="form-check">
                                        <input class="form-check-input" type="checkbox" value="decision_making" id="cap-decision-making">
                                        <label class="form-check-label" for="cap-decision-making">Decision Making</label>
                                    </div>
                                </div>
                                <div class="col-md-6">
                                    <div class="form-check">
                                        <input class="form-check-input" type="checkbox" value="learning" id="cap-learning">
                                        <label class="form-check-label" for="cap-learning">Learning</label>
                                    </div>
                                    <div class="form-check">
                                        <input class="form-check-input" type="checkbox" value="planning" id="cap-planning">
                                        <label class="form-check-label" for="cap-planning">Planning</label>
                                    </div>
                                    <div class="form-check">
                                        <input class="form-check-input" type="checkbox" value="monitoring" id="cap-monitoring">
                                        <label class="form-check-label" for="cap-monitoring">Monitoring</label>
                                    </div>
                                    <div class="form-check">
                                        <input class="form-check-input" type="checkbox" value="reporting" id="cap-reporting">
                                        <label class="form-check-label" for="cap-reporting">Reporting</label>
                                    </div>
                                </div>
                            </div>
                        </div>
                        <div class="mb-3">
                            <label for="agent-config" class="form-label">Configuration (JSON)</label>
                            <textarea class="form-control" id="agent-config" rows="4">{"learning_enabled": true, "timeout_seconds": 30}</textarea>
                        </div>
                    </form>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                    <button type="button" class="btn btn-primary" onclick="createAgent()">Create Agent</button>
                </div>
            </div>
        </div>
    </div>

    <script>
        // Socket.IO connection
        const socket = io();
        
        // Global state
        let logCount = 0;
        let tasksExecuted = 0;
        
        // Socket event handlers
        socket.on('connect', function() {
            console.log('Connected to server');
            requestStatus();
        });
        
        socket.on('framework_status', function(data) {
            updateFrameworkStatus(data);
        });
        
        socket.on('log_message', function(data) {
            addLogMessage(data);
        });
        
        socket.on('agents_updated', function(data) {
            updateAgentsList(data.agents);
        });
        
        socket.on('task_completed', function(data) {
            displayTaskResults(data);
        });
        
        socket.on('workflow_updated', function(data) {
            displayWorkflowResults(data);
        });
        
        socket.on('config_updated', function(data) {
            displayConfiguration(data.config);
        });
        
        // Framework functions
        function requestStatus() {
            socket.emit('get_status');
        }
        
        function updateFrameworkStatus(data) {
            const statusBadge = document.getElementById('framework-status');
            const statusText = document.getElementById('framework-status-text');
            
            if (data.initialized) {
                statusBadge.className = 'badge bg-success';
                statusBadge.textContent = 'Ready';
                statusText.textContent = '✓ Framework initialized and ready for operations.';
            } else {
                statusBadge.className = 'badge bg-warning';
                statusBadge.textContent = 'Initializing';
                statusText.textContent = 'Framework is initializing...';
            }
            
            // Update counts
            document.getElementById('agents-count').textContent = data.agents_count || 0;
            document.getElementById('workflows-count').textContent = data.workflows_count || 0;
            document.getElementById('tasks-count').textContent = tasksExecuted;
            document.getElementById('logs-count').textContent = logCount;
        }
        
        // Agent functions
        function createAgent() {
            const name = document.getElementById('agent-name').value;
            const capabilities = [];
            
            // Collect selected capabilities
            document.querySelectorAll('#createAgentModal input[type="checkbox"]:checked').forEach(cb => {
                capabilities.push(cb.value);
            });
            
            const configText = document.getElementById('agent-config').value;
            let config = {};
            
            try {
                config = JSON.parse(configText);
            } catch (e) {
                alert('Invalid JSON configuration');
                return;
            }
            
            if (!name) {
                alert('Agent name is required');
                return;
            }
            
            if (capabilities.length === 0) {
                alert('At least one capability is required');
                return;
            }
            
            socket.emit('create_agent', {
                name: name,
                capabilities: capabilities,
                config: config
            });
            
            // Close modal and reset form
            bootstrap.Modal.getInstance(document.getElementById('createAgentModal')).hide();
            document.getElementById('create-agent-form').reset();
        }
        
        function updateAgentsList(agents) {
            const agentsList = document.getElementById('agents-list');
            
            if (agents.length === 0) {
                agentsList.innerHTML = '<p class="text-muted">No agents created yet.</p>';
                return;
            }
            
            let html = '';
            agents.forEach(agent => {
                html += `
                    <div class="agent-card card mb-2" onclick="selectAgent('${agent.name}')">
                        <div class="card-body p-3">
                            <div class="d-flex justify-content-between align-items-center">
                                <div>
                                    <h6 class="mb-1">${agent.name}</h6>
                                    <small class="text-muted">${agent.capabilities.join(', ')}</small>
                                </div>
                                <div>
                                    <span class="badge bg-${agent.state === 'idle' ? 'success' : 'warning'}">${agent.state}</span>
                                </div>
                            </div>
                        </div>
                    </div>
                `;
            });
            
            agentsList.innerHTML = html;
        }
        
        function selectAgent(agentName) {
            socket.emit('get_agent_details', {name: agentName});
        }
        
        function quickCreateAgent() {
            socket.emit('create_agent', {
                name: `demo_agent_${Date.now()}`,
                capabilities: ['data_processing', 'analysis'],
                config: {'learning_enabled': true}
            });
        }
        
        // Task functions
        function executeTask() {
            const name = document.getElementById('task-name').value || 'Untitled Task';
            const type = document.getElementById('task-type').value;
            const paramsText = document.getElementById('task-params').value;
            
            let params = {};
            try {
                params = JSON.parse(paramsText);
            } catch (e) {
                alert('Invalid JSON parameters');
                return;
            }
            
            socket.emit('execute_task', {
                name: name,
                type: type,
                parameters: params
            });
            
            tasksExecuted++;
            document.getElementById('tasks-count').textContent = tasksExecuted;
        }
        
        function displayTaskResults(data) {
            const resultsDiv = document.getElementById('task-results');
            const contentDiv = document.getElementById('task-results-content');
            
            let html = `
                <h6>Task: ${data.name}</h6>
                <p><strong>Type:</strong> ${data.type}</p>
                <p><strong>Success:</strong> <span class="badge bg-${data.success ? 'success' : 'danger'}">${data.success}</span></p>
            `;
            
            if (data.result) {
                html += `<p><strong>Result:</strong></p><pre class="bg-light p-2">${JSON.stringify(data.result, null, 2)}</pre>`;
            }
            
            if (data.error) {
                html += `<p><strong>Error:</strong> <span class="text-danger">${data.error}</span></p>`;
            }
            
            contentDiv.innerHTML = html;
            resultsDiv.style.display = 'block';
        }
        
        function quickRunTask() {
            document.getElementById('tasks-tab').click();
            setTimeout(() => {
                document.getElementById('task-name').value = 'Quick Demo Task';
                document.getElementById('task-params').value = '{"data": [1, 2, 3, 4, 5], "operations": ["filter", "sort"]}';
                executeTask();
            }, 300);
        }
        
        // Workflow functions
        function executeWorkflow() {
            const name = document.getElementById('workflow-name').value || 'Untitled Workflow';
            const type = document.getElementById('workflow-type').value;
            const configText = document.getElementById('workflow-config').value;
            
            let config = [];
            try {
                config = JSON.parse(configText);
            } catch (e) {
                alert('Invalid JSON configuration');
                return;
            }
            
            socket.emit('execute_workflow', {
                name: name,
                type: type,
                config: config
            });
        }
        
        function displayWorkflowResults(data) {
            const resultsDiv = document.getElementById('workflow-results');
            const contentDiv = document.getElementById('workflow-results-content');
            
            let html = '';
            data.workflows.forEach(workflow => {
                html += `
                    <div class="workflow-step">
                        <h6>${workflow.name}</h6>
                        <p><strong>Status:</strong> <span class="badge bg-${workflow.state === 'completed' ? 'success' : 'warning'}">${workflow.state}</span></p>
                        <p><strong>Steps:</strong> ${workflow.completed_steps}/${workflow.total_steps}</p>
                    </div>
                `;
            });
            
            contentDiv.innerHTML = html;
            resultsDiv.style.display = 'block';
        }
        
        function quickStartWorkflow() {
            document.getElementById('workflows-tab').click();
            setTimeout(() => {
                document.getElementById('workflow-name').value = 'Quick Demo Workflow';
                executeWorkflow();
            }, 300);
        }
        
        // Log functions
        function addLogMessage(data) {
            const logsContainer = document.getElementById('logs-container');
            const logDiv = document.createElement('div');
            logDiv.className = `log-entry text-${data.level.toLowerCase() === 'error' ? 'danger' : 
                                data.level.toLowerCase() === 'warning' ? 'warning' : 'dark'}`;
            logDiv.innerHTML = `[${data.timestamp.split('T')[1].split('.')[0]}] ${data.level}: ${data.message}`;
            
            logsContainer.appendChild(logDiv);
            logsContainer.scrollTop = logsContainer.scrollHeight;
            
            logCount++;
            document.getElementById('logs-count').textContent = logCount;
        }
        
        function clearLogs() {
            document.getElementById('logs-container').innerHTML = '';
            logCount = 0;
            document.getElementById('logs-count').textContent = logCount;
        }
        
        function exportLogs() {
            const logs = document.getElementById('logs-container').innerText;
            const blob = new Blob([logs], {type: 'text/plain'});
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `agentic_framework_logs_${new Date().toISOString().split('T')[0]}.txt`;
            a.click();
            window.URL.revokeObjectURL(url);
        }
        
        // Configuration functions
        function displayConfiguration(config) {
            document.getElementById('config-content').value = JSON.stringify(config, null, 2);
        }
        
        function loadConfig() {
            socket.emit('get_config');
        }
        
        function saveConfig() {
            const configText = document.getElementById('config-content').value;
            try {
                const config = JSON.parse(configText);
                socket.emit('save_config', {config: config});
            } catch (e) {
                alert('Invalid JSON configuration');
            }
        }
        
        function resetConfig() {
            if (confirm('Reset configuration to defaults?')) {
                socket.emit('reset_config');
            }
        }
        
        // Demo function
        function runDemo() {
            socket.emit('run_demo');
        }
        
        // Initialize
        document.addEventListener('DOMContentLoaded', function() {
            requestStatus();
            loadConfig();
        });
    </script>
</body>
</html>'''
        
        with open(os.path.join(templates_dir, 'index.html'), 'w') as f:
            f.write(main_template)
    
    def setup_routes(self):
        """Setup Flask routes."""
        
        @self.app.route('/')
        def index():
            return render_template('index.html')
        
        @self.app.route('/api/status')
        def get_status():
            return jsonify({
                'initialized': self.is_framework_initialized,
                'agents_count': len(self.agents),
                'workflows_count': len(self.active_workflows),
                'error': self.initialization_error
            })
    
    def setup_socketio_handlers(self):
        """Setup SocketIO event handlers."""
        
        @self.socketio.on('connect')
        def handle_connect():
            print('Client connected')
            # Send initial status
            self.socketio.emit('framework_status', {
                'initialized': self.is_framework_initialized,
                'agents_count': len(self.agents),
                'workflows_count': len(self.active_workflows)
            })
        
        @self.socketio.on('get_status')
        def handle_get_status():
            self.socketio.emit('framework_status', {
                'initialized': self.is_framework_initialized,
                'agents_count': len(self.agents),
                'workflows_count': len(self.active_workflows)
            })
        
        @self.socketio.on('create_agent')
        def handle_create_agent(data):
            if not self.is_framework_initialized:
                self.socketio.emit('error', {'message': 'Framework not initialized'})
                return
            
            try:
                agent = create_agent(
                    name=data['name'],
                    capabilities=data['capabilities'],
                    config=data.get('config', {})
                )
                self.agents[data['name']] = agent
                
                # Send updated agents list
                agents_data = []
                for name, agent in self.agents.items():
                    status = agent.get_status()
                    agents_data.append({
                        'name': name,
                        'capabilities': status.get('capabilities', []),
                        'state': status.get('state', 'idle')
                    })
                
                self.socketio.emit('agents_updated', {'agents': agents_data})
                
            except Exception as e:
                self.socketio.emit('error', {'message': f'Failed to create agent: {str(e)}'})
        
        @self.socketio.on('execute_task')
        def handle_execute_task(data):
            if not self.is_framework_initialized:
                self.socketio.emit('error', {'message': 'Framework not initialized'})
                return
            
            def task_worker():
                try:
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
                    
                    task_class = task_classes.get(data['type'])
                    if not task_class:
                        raise ValueError(f"Unknown task type: {data['type']}")
                    
                    task = task_class(data['name'])
                    
                    # Execute task
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    result = loop.run_until_complete(task.run(**data.get('parameters', {})))
                    loop.close()
                    
                    # Send result
                    self.socketio.emit('task_completed', {
                        'name': data['name'],
                        'type': data['type'],
                        'success': result.success,
                        'result': result.data,
                        'error': result.error
                    })
                    
                except Exception as e:
                    self.socketio.emit('task_completed', {
                        'name': data['name'],
                        'type': data['type'],
                        'success': False,
                        'result': None,
                        'error': str(e)
                    })
            
            threading.Thread(target=task_worker, daemon=True).start()
        
        @self.socketio.on('execute_workflow')
        def handle_execute_workflow(data):
            if not self.is_framework_initialized:
                self.socketio.emit('error', {'message': 'Framework not initialized'})
                return
            
            def workflow_worker():
                try:
                    # Create default agent if none exist
                    if not self.agents:
                        agent = create_agent("default_agent", ["general_processing"])
                        self.agents["default_agent"] = agent
                    
                    agent_name = list(self.agents.keys())[0]
                    self.workflow_engine.register_agent(agent_name, self.agents[agent_name])
                    
                    # Create workflow
                    if data['type'] == 'simple':
                        workflow = create_simple_agent_workflow(
                            data['name'], agent_name, data['config'])
                    else:
                        workflow = create_workflow(data['name'], "Complex workflow")
                        for i, step_config in enumerate(data['config']):
                            workflow.add_agent_task(
                                step_config.get('name', f'Step {i+1}'),
                                agent_name,
                                step_config.get('parameters', {})
                            )
                        workflow = workflow.build()
                    
                    # Execute workflow
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    context = loop.run_until_complete(self.workflow_engine.execute_workflow(workflow))
                    loop.close()
                    
                    # Store workflow
                    self.active_workflows[data['name']] = {
                        'workflow': workflow,
                        'context': context,
                        'status': workflow.get_status()
                    }
                    
                    # Send results
                    workflows_data = []
                    for name, workflow_data in self.active_workflows.items():
                        status = workflow_data['status']
                        workflows_data.append({
                            'name': name,
                            'state': status.get('state', 'unknown'),
                            'completed_steps': status.get('completed_steps', 0),
                            'total_steps': status.get('total_steps', 0)
                        })
                    
                    self.socketio.emit('workflow_updated', {'workflows': workflows_data})
                    
                except Exception as e:
                    self.socketio.emit('error', {'message': f'Workflow execution failed: {str(e)}'})
            
            threading.Thread(target=workflow_worker, daemon=True).start()
        
        @self.socketio.on('get_config')
        def handle_get_config():
            if self.config_manager:
                try:
                    config_dict = {
                        'system': self.config_manager.get_system_config().__dict__,
                        'agent': self.config_manager.get_agent_config().__dict__,
                        'workflow': self.config_manager.get_workflow_config().__dict__
                    }
                    self.socketio.emit('config_updated', {'config': config_dict})
                except Exception as e:
                    self.socketio.emit('error', {'message': f'Failed to get configuration: {str(e)}'})
        
        @self.socketio.on('run_demo')
        def handle_run_demo():
            def demo_worker():
                try:
                    # Run the example script
                    import subprocess
                    import sys
                    
                    result = subprocess.run(
                        [sys.executable, "example.py"], 
                        cwd=os.path.dirname(__file__),
                        capture_output=True, 
                        text=True
                    )
                    
                    if result.returncode == 0:
                        logging.info("Demo completed successfully")
                    else:
                        logging.error(f"Demo failed: {result.stderr}")
                        
                except Exception as e:
                    logging.error(f"Demo execution failed: {str(e)}")
            
            threading.Thread(target=demo_worker, daemon=True).start()
    
    def setup_logging(self):
        """Setup logging to capture framework logs."""
        # Create custom handler for web GUI
        self.web_log_handler = WebGUIHandler(self.socketio)
        self.web_log_handler.setLevel(logging.INFO)
        formatter = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
        self.web_log_handler.setFormatter(formatter)
        
        # Add handler to root logger
        logging.getLogger().addHandler(self.web_log_handler)
        
        # Initialize framework in background
        self.initialize_framework()
    
    def initialize_framework(self):
        """Initialize the framework components."""
        def init_worker():
            try:
                logging.info("Initializing Agentic Framework...")
                
                # Initialize system
                self.config_manager = initialize_system()
                
                # Create workflow engine
                self.workflow_engine = WorkflowEngine()
                
                self.is_framework_initialized = True
                logging.info("Framework initialized successfully")
                
                # Notify clients
                self.socketio.emit('framework_status', {
                    'initialized': True,
                    'agents_count': len(self.agents),
                    'workflows_count': len(self.active_workflows)
                })
                
            except Exception as e:
                error_msg = f"Failed to initialize framework: {str(e)}"
                self.initialization_error = error_msg
                logging.error(error_msg)
                
                self.socketio.emit('framework_status', {
                    'initialized': False,
                    'error': error_msg
                })
        
        # Run initialization in background thread
        threading.Thread(target=init_worker, daemon=True).start()
    
    def run(self, host='localhost', port=5000, debug=False, open_browser=True):
        """Run the web application."""
        if open_browser:
            # Open browser after a short delay
            def open_browser_delayed():
                time.sleep(1.5)
                webbrowser.open(f'http://{host}:{port}')
            
            threading.Thread(target=open_browser_delayed, daemon=True).start()
        
        print(f"\nAgentic Model Framework Web GUI")
        print(f"==============================")
        print(f"Starting server on http://{host}:{port}")
        print(f"Press Ctrl+C to stop the server\n")
        
        try:
            self.socketio.run(self.app, host=host, port=port, debug=debug)
        except KeyboardInterrupt:
            print("\nShutting down gracefully...")
        except Exception as e:
            print(f"Server error: {e}")


def main():
    """Main entry point for the web GUI application."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Agentic Model Framework Web GUI')
    parser.add_argument('--host', default='localhost', help='Host to bind to')
    parser.add_argument('--port', type=int, default=5000, help='Port to bind to')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    parser.add_argument('--no-browser', action='store_true', help='Don\'t auto-open browser')
    
    args = parser.parse_args()
    
    # Create and run the web application
    app = AgenticFrameworkWebApp()
    app.run(
        host=args.host,
        port=args.port,
        debug=args.debug,
        open_browser=not args.no_browser
    )


if __name__ == "__main__":
    main()