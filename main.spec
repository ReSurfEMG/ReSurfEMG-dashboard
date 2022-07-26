# -*- mode: python ; coding: utf-8 -*-
import sys
import mne
import trace_updater

block_cipher = None

mne_path = sys.modules.get('mne').__path__[0]
trace_updater_path = sys.modules.get('trace_updater').__path__[0]

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
    ('pages','pages'),
    ('resources','resources'),
    (mne_path,'mne'),
    (trace_updater_path,'trace_updater'),
    ],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='resurfemg_dashboard',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='main',
)
