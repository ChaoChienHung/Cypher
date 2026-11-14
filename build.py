#!/usr/bin/env python3
"""
Root build script for Cypher project.
Compiles vigenere-vault into a double-clickable standalone application.
"""

from pathlib import Path
import subprocess
import sys

if __name__ == "__main__":
    target_build = Path(__file__).resolve().parent / "vigenere-vault" / "build.py"
    cmd = [sys.executable, str(target_build)] + sys.argv[1:]
    sys.exit(subprocess.run(cmd).returncode)
