# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller spec for the packaged Electron backend binary.

Produces a single-file executable named astrology-backend(.exe) under
backend/dist/. Kerykeion chart themes and templates are bundled as data.
Ephemeris files are resolved at runtime and are intentionally not bundled.
"""

from pathlib import Path

import certifi
import kerykeion


def _package_dir(module) -> Path:
    return Path(module.__file__).resolve().parent


KERYKEION_DIR = _package_dir(kerykeion)

a = Analysis(
    ["run_backend.py"],
    pathex=[],
    binaries=[
        (r'C:\Windows\System32\msvcp140.dll', '.'),
        (r'C:\Windows\System32\vcruntime140.dll', '.'),
        (r'C:\Windows\System32\vcruntime140_1.dll', '.'),
    ],
    datas=[
        (
            str(KERYKEION_DIR / "charts" / "themes"),
            "kerykeion/charts/themes",
        ),
        (
            str(KERYKEION_DIR / "charts" / "templates"),
            "kerykeion/charts/templates",
        ),
        (certifi.where(), "certifi"),
    ],
    hiddenimports=["kerykeion", "swisseph"],
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
    name="astrology-backend",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    # UPX can trigger false-positive AV hits on Windows installers.
    upx=False,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
