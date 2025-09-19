# -*- mode: python ; coding: utf-8 -*-
"""
Simple PyInstaller spec file for the Agentic Model Framework Web GUI.

This configuration builds a standalone executable that includes all necessary
components for the web-based interface.
"""

import sys
import os

# Block problematic paths and modules
block_cipher = None

# Hidden imports for the web application
hidden_imports = [
    'asyncio',
    'json', 
    'logging',
    'threading',
    'webbrowser',
    'datetime',
    'time',
    'socket',
    'urllib',
    'urllib.parse',
    'werkzeug.serving',
    'flask.json',
    'flask.helpers',
    'jinja2',
    'markupsafe',
    'itsdangerous',
    'blinker',
    'socketio',
    'engineio',
    'eventlet',
    'eventlet.wsgi',
    'dns.resolver',
    'dns.reversename'
]

# Add framework modules explicitly
framework_modules = ['agent', 'config', 'tasks', 'tasks.custom_tasks']
hidden_imports.extend(framework_modules)

# Include templates directory
datas = [
    ('templates', 'templates'),
]

# Analysis
a = Analysis(
    ['web_gui.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=hidden_imports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'matplotlib',
        'numpy', 
        'pandas',
        'scipy',
        'PyQt5',
        'PyQt6', 
        'PySide2',
        'PySide6',
        'tkinter',
        'turtle',
        '_tkinter',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

# Add our workflow module explicitly
a.pure.append(('workflow', 'workflow.py', 'PYMODULE'))

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='AgenticFrameworkGUI',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)