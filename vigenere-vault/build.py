#!/usr/bin/env python3
"""
Automated Build Script for Vigenère Vault.
Compiles the PySide6 application into a standalone double-clickable macOS application (.app)
or executable using PyInstaller.
"""

import os
from pathlib import Path
import platform
import shutil
import subprocess
import sys


def ensure_pyinstaller():
    try:
        import PyInstaller
        print("[✓] PyInstaller is installed and ready.")
    except ImportError:
        print("[*] PyInstaller not detected. Installing via pip...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
        print("[✓] PyInstaller installed successfully.")


def clean_previous_builds(base_dir: Path):
    dirs_to_clean = [
        base_dir / "build",
        base_dir / "dist",
    ]
    for d in dirs_to_clean:
        if d.exists() and d.is_dir():
            print(f"[*] Cleaning previous build artifacts in: {d.name}/")
            shutil.rmtree(d, ignore_errors=True)

    # Remove any leftover .spec files
    for spec_file in base_dir.glob("*.spec"):
        try:
            spec_file.unlink()
            print(f"[*] Removed previous spec file: {spec_file.name}")
        except Exception:
            pass


def build_app():
    script_dir = Path(__file__).resolve().parent
    os.chdir(script_dir)

    print("=" * 60)
    print("🚀 Building Standalone Vigenère Vault Application")
    print(f"   OS: {platform.system()} ({platform.machine()})")
    print(f"   Python: {sys.version.split()[0]} ({sys.executable})")
    print("=" * 60)

    ensure_pyinstaller()
    clean_previous_builds(script_dir)

    entry_point = script_dir / "gui.py"
    core_file = script_dir / "core.py"
    app_name = "VigenereVault"

    # PyInstaller arguments
    # On macOS, --add-data uses 'source:dest'
    sep = ":" if platform.system() != "Windows" else ";"
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--name", app_name,
        "--windowed",              # No terminal window on double-click
        "--noconfirm",             # Overwrite existing output
        "--clean",                 # Clean PyInstaller cache
        f"--add-data={core_file.name}{sep}.",
    ]

    # macOS specific options
    if platform.system() == "Darwin":
        cmd.extend([
            "--osx-bundle-identifier", "com.cypher.vigenerevault",
        ])

    cmd.append(str(entry_point.name))

    print(f"[*] Executing build command:\n    {' '.join(cmd)}\n")
    result = subprocess.run(cmd, cwd=script_dir)

    if result.returncode != 0:
        print("\n[✖] Build failed! Please inspect the logs above.")
        sys.exit(result.returncode)

    dist_dir = script_dir / "dist"
    app_path = dist_dir / f"{app_name}.app" if platform.system() == "Darwin" else dist_dir / app_name

    print("\n" + "=" * 60)
    print("🎉 BUILD SUCCESSFUL!")
    print("=" * 60)
    print(f"📦 Compiled App Path:")
    print(f"   {app_path}")
    print()

    if platform.system() == "Darwin" and app_path.exists():
        print("💡 您可以在 Finder 中直接對著它『點兩下』即可打開執行！")
        print("💡 若要在 Finder 中查看，請執行：")
        print(f"   open -R \"{app_path}\"")
        print()
        # If user passed --open flag, open Finder immediately
        if "--open" in sys.argv:
            subprocess.run(["open", "-R", str(app_path)])


if __name__ == "__main__":
    build_app()
