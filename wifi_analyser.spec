# wifi_analyser.spec
# PyInstaller spec file — builds macOS .app bundle
# Run with: pyinstaller wifi_analyser.spec

import os

block_cipher = None

BASE = os.path.abspath('.')

a = Analysis(
    ['launcher.py'],
    pathex=[BASE],
    binaries=[],
    datas=[
        ('templates', 'templates'),   # Include HTML templates
        ('static',    'static'),      # Include static files
    ],
    hiddenimports=[
        'flask',
        'scapy',
        'scapy.all',
        'scapy.layers.l2',
        'scapy.layers.inet',
        'engineio.async_drivers.threading',
        'jinja2',
        'werkzeug',
        'click',
        'itsdangerous',
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

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='WiFi Analyser',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,          # No terminal window
    disable_windowed_traceback=False,
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
    name='WiFi Analyser',
)

app = BUNDLE(
    coll,
    name='WiFi Analyser.app',
    icon=None,               # Add icon.icns here if you have one
    bundle_identifier='com.alexphilip.wifianalyser',
    info_plist={
        'NSPrincipalClass': 'NSApplication',
        'NSHighResolutionCapable': True,
        'CFBundleShortVersionString': '1.0.0',
        'CFBundleName': 'WiFi Analyser',
        'CFBundleDisplayName': 'WiFi Analyser',
        'NSRequiresAquaSystemAppearance': False,
    },
)
