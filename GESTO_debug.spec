# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[('modelo_lsc.p', '.'), ('recursos', 'recursos'), ('modulos', 'modulos'), ('config.py', '.'), ('progreso.py', '.'), ('C:\\Users\\dosor\\OneDrive\\Desktop\\Gesto\\lsc_env\\lib\\site-packages\\mediapipe', 'mediapipe'), ('C:\\Users\\dosor\\OneDrive\\Desktop\\Gesto\\lsc_env\\lib\\site-packages\\customtkinter', 'customtkinter'), ('C:\\Users\\dosor\\OneDrive\\Desktop\\Gesto\\lsc_env\\lib\\site-packages\\sklearn', 'sklearn')],
    hiddenimports=['sklearn', 'sklearn.ensemble', 'sklearn.tree', 'joblib'],
    hookspath=[],
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
    a.binaries,
    a.datas,
    [],
    name='GESTO_debug',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
