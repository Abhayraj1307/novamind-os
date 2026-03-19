# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['desktop_main.py'],
    pathex=[],
    binaries=[],
    datas=[('app/static', 'app/static')],
    hiddenimports=['uvicorn.logging', 'uvicorn.loops', 'uvicorn.protocols', 'uvicorn.lifespan', 'engineio.async_drivers.threading'],
    hookspath=['hooks'],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='NovaMind',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='NovaMind',
)
app = BUNDLE(
    coll,
    name='NovaMind.app',
    icon=None,
    bundle_identifier=None,
)
