# -*- mode: python ; coding: utf-8 -*-
# Cross-platform PyInstaller spec

import os
import sys
from pathlib import Path

# Handle being called from different directories
if hasattr(sys, '_MEIPASS'):
    # Running as compiled executable
    spec_root = sys._MEIPASS
else:
    # Running as script - SPECPATH is where this .spec file is located
    spec_root = os.path.abspath(SPECPATH if 'SPECPATH' in dir() else os.path.dirname(__file__))

# Project root is parent of scripts/
project_root = os.path.dirname(spec_root)

# Hooks directory
hooks_dir = os.path.join(spec_root, 'hooks')

# Ensure hooks directory exists
if not os.path.exists(hooks_dir):
    os.makedirs(hooks_dir)

block_cipher = None

a = Analysis(
    [os.path.join(project_root, 'src', 'multi_modal_rag', 'main.py')],
    pathex=[project_root],
    binaries=[],
    datas=[
        (os.path.join(project_root, 'src', 'multi_modal_rag', '*.py'), 'multi_modal_rag'),
    ],
    hiddenimports=[
        'google.cloud.aiplatform',
        'google.cloud.speech',
        'google.genai',
        'google.generativeai',
        'markitdown',
        'magika',
        'onnxruntime',
        'numpy',
        'PIL',
        'dotenv',
        'tkinter',
        'vertexai',
    ],
    hookspath=[hooks_dir] if os.path.exists(hooks_dir) else [],
    runtime_hooks=[],
    excludes=[],
    cipher=block_cipher,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

# Platform-specific executable settings
import platform
system = platform.system()

if system == 'Darwin':  # macOS
    exe = EXE(
        pyz,
        a.scripts,
        a.binaries,
        a.zipfiles,
        a.datas,
        [],
        name='MultiModalRAG',
        debug=False,
        bootloader_ignore_signals=False,
        strip=False,
        upx=True,
        console=False,
        disable_windowed_traceback=False,
        target_arch=None,
        codesign_identity=None,
        entitlements_file=None,
    )
    app = BUNDLE(
        exe,
        name='MultiModalRAG.app',
        icon=None,
        bundle_identifier='com.systemsolution21.multimodalrag',
    )
else:  # Windows and Linux
    exe = EXE(
        pyz,
        a.scripts,
        a.binaries,
        a.zipfiles,
        a.datas,
        [],
        name='MultiModalRAG',
        debug=False,
        bootloader_ignore_signals=False,
        strip=False,
        upx=True,
        console=False,  # Hide console for GUI
        disable_windowed_traceback=False,
        target_arch=None,
        codesign_identity=None,
        entitlements_file=None,
        icon=None,
    )





