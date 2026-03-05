# PyInstaller spec for POS Scale App (PyQt6 + pywin32).
# Default: onedir (recommended for PyQt6 + printer). For onefile, use:
#   pyinstaller scale_app.spec --onefile
# Build: pyinstaller scale_app.spec

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[
        'PyQt6.QtCore',
        'PyQt6.QtGui',
        'PyQt6.QtWidgets',
        'serial',
        'serial.win32',
        'win32print',
        'win32ui',
        'win32con',
        'win32api',
    ],
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

# Onedir: EXE + COLLECT (default)
exe = EXE(
    pyz,
    a.scripts,
    exclude_binaries=True,
    name='ScaleApp',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements=None,
)

COLLECT = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='ScaleApp',
)
