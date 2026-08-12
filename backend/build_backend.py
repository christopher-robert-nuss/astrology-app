#!/usr/bin/env python3
"""Freeze the FastAPI backend with PyInstaller for Electron packaging.

Run on the same OS/arch as the target installer. PyInstaller does not
cross-compile, so a Windows NSIS build needs a Windows-built binary.
"""

from __future__ import annotations

import platform
import subprocess
import sys
from pathlib import Path


def _expected_binary_name() -> str:
    if platform.system() == "Windows":
        return "astrology-backend.exe"
    return "astrology-backend"


def main() -> int:
    backend_dir = Path(__file__).resolve().parent
    spec_path = backend_dir / "astrology-backend.spec"
    dist_dir = backend_dir / "dist"
    expected_binary = dist_dir / _expected_binary_name()

    if not spec_path.exists():
        raise FileNotFoundError(f"Missing PyInstaller spec: {spec_path}")

    try:
        import PyInstaller  # noqa: F401
    except ImportError as exc:
        raise SystemExit(
            "PyInstaller is required. Install it with:\n"
            "  pip install -r backend/requirements-dev.txt"
        ) from exc

    print(f"[build_backend] Freezing backend with {sys.executable}")
    print(f"[build_backend] Spec: {spec_path}")
    print(f"[build_backend] Target binary: {expected_binary.name}")

    subprocess.run(
        [sys.executable, "-m", "PyInstaller", "--noconfirm", "--clean", spec_path.name],
        cwd=backend_dir,
        check=True,
    )

    if not expected_binary.is_file():
        raise FileNotFoundError(
            f"PyInstaller finished but binary was not found at {expected_binary}"
        )

    size_mb = expected_binary.stat().st_size / (1024 * 1024)
    print(f"[build_backend] Wrote {expected_binary} ({size_mb:.1f} MiB)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
