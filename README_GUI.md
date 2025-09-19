# Agentic Model Framework - GUI Application

A cross-platform executable user interface for the Agentic Model Framework, designed to run on both Mac and Windows (and Linux).

## Overview

This GUI application provides an intuitive web-based interface for interacting with the Agentic Model Framework. It features:

- **Agent Management**: Create, configure, and monitor AI agents
- **Task Execution**: Define and run various types of tasks
- **Workflow Design**: Build and execute complex multi-step workflows
- **Real-time Monitoring**: Live logging and status updates
- **Cross-platform**: Runs on Windows, Mac, and Linux

## Quick Start

### Option 1: Run Directly (Recommended for Development)

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Start the GUI**:
   ```bash
   python launcher.py
   ```
   
   Or directly:
   ```bash
   python web_gui.py
   ```

3. **Open in Browser**: The application will automatically open in your web browser at `http://localhost:5000`

### Option 2: Build Executable (Recommended for Distribution)

#### On Windows:
1. Run `build.bat`
2. Find the executable in `dist/AgenticFrameworkGUI/`
3. Run `AgenticFrameworkGUI.exe`

#### On Mac/Linux:
1. Run `./build.sh`
2. Find the executable in `dist/AgenticFrameworkGUI/`
3. Run `./AgenticFrameworkGUI`

## Features

### 🤖 Agent Management
- Create agents with custom capabilities
- Monitor agent status and performance
- Configure agent behavior and settings
- View detailed agent information

### 📋 Task Execution
- Execute various task types:
  - Data Processing Tasks
  - Analysis Tasks
  - Communication Tasks
  - Decision Tasks
  - Model Training Tasks
  - Data Ingestion Tasks
  - Report Generation Tasks
- Configure task parameters with JSON
- View real-time task results

### 🔄 Workflow Management
- Design sequential workflows
- Execute complex multi-step processes
- Monitor workflow progress
- View detailed execution results

### 📊 Real-time Monitoring
- Live system logs
- Performance metrics
- Status indicators
- Error tracking

### ⚙️ Configuration Management
- Load/save configuration files
- Customize framework behavior
- Reset to default settings

## Usage Guide

### Creating an Agent

1. Go to the **Agents** tab
2. Click **Create Agent**
3. Enter agent name and select capabilities
4. Configure additional settings (JSON format)
5. Click **Create Agent**

### Running a Task

1. Go to the **Tasks** tab
2. Select task type from dropdown
3. Enter task name
4. Configure parameters in JSON format
5. Click **Execute Task**
6. View results in the Results section

### Building a Workflow

1. Go to the **Workflows** tab
2. Enter workflow name
3. Choose workflow type (Simple or Complex)
4. Configure workflow steps in JSON format
5. Click **Create & Execute Workflow**
6. Monitor progress in the Active Workflows section

### Example Task Configuration

```json
{
  "data": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
  "operations": ["filter", "sort"],
  "filter_criteria": {"value": 5}
}
```

### Example Workflow Configuration

```json
[
  {
    "name": "Data Processing",
    "task_type": "DataProcessingTask",
    "parameters": {
      "data": [1, 2, 3, 4, 5],
      "operations": ["filter"]
    }
  },
  {
    "name": "Analysis",
    "task_type": "AnalysisTask",
    "parameters": {
      "data": [1, 2, 3],
      "analysis_type": "statistical"
    }
  }
]
```

## Command Line Options

### Launcher Options
```bash
python launcher.py [options]

Options:
  --host HOST          Host to bind to (default: localhost)
  --port PORT          Port to bind to (default: 5000)
  --no-browser         Don't automatically open browser
  --debug              Enable debug mode
  --help               Show help message
```

### Web GUI Options
```bash
python web_gui.py [options]

Options:
  --host HOST          Host to bind to (default: localhost)
  --port PORT          Port to bind to (default: 5000)
  --debug              Enable debug mode
  --no-browser         Don't auto-open browser
```

## Building Executables

### Requirements for Building
- Python 3.7+
- PyInstaller
- All dependencies from requirements.txt

### Build Process

The build scripts automatically:
1. Install required dependencies
2. Create standalone executables
3. Package all necessary files
4. Generate distribution folder

### Distribution

The built executable includes:
- All Python dependencies
- Framework modules
- Web interface templates
- Configuration files

**Note**: The executable is self-contained and doesn't require Python to be installed on the target machine.

## Troubleshooting

### Common Issues

1. **Port already in use**:
   - Change port: `python launcher.py --port 8080`
   - Check for running instances

2. **Dependencies missing**:
   - Install: `pip install -r requirements.txt`
   - Check Python version (3.7+ required)

3. **Browser doesn't open**:
   - Manually navigate to `http://localhost:5000`
   - Use `--no-browser` flag and open manually

4. **Build fails**:
   - Ensure all dependencies are installed
   - Check Python and PyInstaller versions
   - Review error messages for missing modules

### Error Messages

- **"Framework not initialized"**: Wait for initialization to complete
- **"Invalid JSON"**: Check configuration syntax
- **"Agent creation failed"**: Verify agent configuration
- **"Task execution failed"**: Check task parameters

## System Requirements

### Minimum Requirements
- **Operating System**: Windows 10+, macOS 10.14+, or Linux
- **Python**: 3.7+ (for running from source)
- **Memory**: 512 MB RAM
- **Storage**: 100 MB free space
- **Network**: Available port (default: 5000)

### Recommended Requirements
- **Memory**: 1 GB RAM
- **Storage**: 500 MB free space
- **Browser**: Modern web browser (Chrome, Firefox, Safari, Edge)

## Development

### Project Structure
```
├── web_gui.py          # Main web application
├── launcher.py         # Simple launcher script
├── gui_app.py          # Tkinter GUI (fallback)
├── agentic_gui.spec    # PyInstaller configuration
├── build.sh            # Unix/Mac build script
├── build.bat           # Windows build script
├── requirements.txt    # Python dependencies
├── templates/          # Web interface templates
└── README_GUI.md       # This file
```

### Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This GUI application is part of the Agentic Model Framework project.

## Support

For issues and questions:
1. Check this README
2. Review the main project documentation
3. Create an issue in the project repository

---

**Note**: This GUI provides a user-friendly interface to the powerful Agentic Model Framework. For advanced usage and API details, refer to the main project documentation.