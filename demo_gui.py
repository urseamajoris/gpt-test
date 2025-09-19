#!/usr/bin/env python3
"""
Quick demo script for the Agentic Model Framework GUI.

This script demonstrates how to quickly test the GUI application.
"""

import subprocess
import sys
import os
import time
import webbrowser

def main():
    """Run a quick demo of the GUI application."""
    print("Agentic Model Framework GUI - Quick Demo")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not os.path.exists('web_gui.py'):
        print("Error: Please run this script from the framework directory.")
        sys.exit(1)
    
    print("1. Testing launcher...")
    try:
        result = subprocess.run([sys.executable, 'launcher.py', '--help'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print("   ✓ Launcher is working")
        else:
            print("   ✗ Launcher failed")
            return
    except Exception as e:
        print(f"   ✗ Launcher test failed: {e}")
        return
    
    print("2. Testing framework import...")
    try:
        result = subprocess.run([sys.executable, '-c', 
                               'import agent, workflow, config, tasks; print("OK")'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0 and 'OK' in result.stdout:
            print("   ✓ Framework modules import successfully")
        else:
            print("   ✗ Framework import failed")
            return
    except Exception as e:
        print(f"   ✗ Framework test failed: {e}")
        return
    
    print("3. Testing dependencies...")
    try:
        result = subprocess.run([sys.executable, '-c', 
                               'import flask, flask_socketio; print("OK")'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0 and 'OK' in result.stdout:
            print("   ✓ GUI dependencies are available")
        else:
            print("   ✗ GUI dependencies missing")
            print("   Run: pip install -r requirements.txt")
            return
    except Exception as e:
        print(f"   ✗ Dependency test failed: {e}")
        return
    
    print("\n✓ All tests passed!")
    print("\nTo start the GUI application:")
    print("  python launcher.py")
    print("\nOr directly:")
    print("  python web_gui.py")
    print("\nThe GUI will open in your web browser at http://localhost:5000")
    
    # Ask if user wants to start the GUI now
    try:
        response = input("\nStart the GUI now? (y/N): ").strip().lower()
        if response in ['y', 'yes']:
            print("\nStarting GUI application...")
            subprocess.run([sys.executable, 'launcher.py'])
    except KeyboardInterrupt:
        print("\nDemo completed.")

if __name__ == "__main__":
    main()