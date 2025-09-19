#!/usr/bin/env python3
"""
Simple launcher for the Agentic Model Framework GUI.

This script provides an easy way to start the GUI application
with common options and proper error handling.
"""

import sys
import os
import argparse
import subprocess

def main():
    """Main launcher function."""
    parser = argparse.ArgumentParser(
        description='Agentic Model Framework GUI Launcher',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python launcher.py              # Start with default settings
  python launcher.py --port 8080  # Start on custom port
  python launcher.py --no-browser # Start without opening browser
  python launcher.py --help       # Show this help
        """
    )
    
    parser.add_argument('--host', default='localhost', 
                       help='Host to bind to (default: localhost)')
    parser.add_argument('--port', type=int, default=5000,
                       help='Port to bind to (default: 5000)')
    parser.add_argument('--no-browser', action='store_true',
                       help='Don\'t automatically open browser')
    parser.add_argument('--debug', action='store_true',
                       help='Enable debug mode')
    
    args = parser.parse_args()
    
    # Check if required files exist
    required_files = ['web_gui.py', 'agent.py', 'workflow.py', 'config.py']
    missing_files = [f for f in required_files if not os.path.exists(f)]
    
    if missing_files:
        print("Error: Missing required files:")
        for file in missing_files:
            print(f"  - {file}")
        print("\nPlease ensure you're running this from the framework directory.")
        sys.exit(1)
    
    # Check Python version
    if sys.version_info < (3, 7):
        print("Error: Python 3.7 or higher is required.")
        print(f"Current version: {sys.version}")
        sys.exit(1)
    
    # Check dependencies
    try:
        import flask
        import flask_socketio
    except ImportError as e:
        print(f"Error: Missing required dependency: {e}")
        print("\nTo install dependencies, run:")
        print("  pip install -r requirements.txt")
        print("\nOr install manually:")
        print("  pip install flask flask-socketio")
        sys.exit(1)
    
    # Build command
    cmd = [sys.executable, 'web_gui.py']
    
    if args.host != 'localhost':
        cmd.extend(['--host', args.host])
    if args.port != 5000:
        cmd.extend(['--port', str(args.port)])
    if args.no_browser:
        cmd.append('--no-browser')
    if args.debug:
        cmd.append('--debug')
    
    print("Starting Agentic Model Framework GUI...")
    print(f"Server will start on http://{args.host}:{args.port}")
    print("Press Ctrl+C to stop the server\n")
    
    try:
        # Run the web GUI
        subprocess.run(cmd, check=True)
    except KeyboardInterrupt:
        print("\nStopping server...")
    except subprocess.CalledProcessError as e:
        print(f"\nError: Failed to start GUI application (exit code {e.returncode})")
        sys.exit(1)
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()