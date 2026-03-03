#!/usr/bin/env python3
"""
Build script — generates a standalone executable with PyInstaller.
Works on Windows and Linux.

Usage:
  python build.py           → Builds executable for the current OS
  python build.py --clean   → Cleans previous build before compiling
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path

BASE  = Path(__file__).parent
DIST  = BASE / "dist"
BUILD = BASE / "build"
SPEC  = BASE / "email_signature_generator.spec"


def install_pyinstaller():
    print("[1/4] Checking PyInstaller...")
    try:
        import PyInstaller
        print(f"      PyInstaller {PyInstaller.__version__} already installed.")
    except ImportError:
        print("      Installing PyInstaller and dependencies...")
        subprocess.check_call([
            sys.executable, "-m", "pip", "install",
            "pyinstaller", "openpyxl", "Pillow", "--quiet"
        ])
        print("      Done!")


def clean():
    for path in [DIST, BUILD, SPEC]:
        if path.exists():
            shutil.rmtree(path) if path.is_dir() else path.unlink()
    print("      Previous build removed.")


def build() -> bool:
    print("[2/4] Compiling executable...")
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",
        "--name", "EmailSignatureGenerator",
        "--clean",
        "--noconfirm",
        "--hidden-import", "openpyxl",
        "--hidden-import", "PIL",
        "--hidden-import", "PIL.Image",
        "--hidden-import", "PIL.ImageDraw",
        "--hidden-import", "PIL.ImageFont",
        "playwright", "install", "chromium",
        str(BASE / "main.py")
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print("[ERROR] Compilation failed:")
        print(result.stderr[-2000:])
        return False
    print("      Compilation successful!")
    return True


def copy_assets() -> bool:
    print("[3/4] Copying required files...")
    exe = DIST / ("EmailSignatureGenerator.exe" if sys.platform == "win32"
                  else "EmailSignatureGenerator")
    if not exe.exists():
        print(f"[ERROR] Executable not found at: {exe}")
        return False

    package = DIST / "EmailSignatureGenerator_package"
    package.mkdir(exist_ok=True)
    shutil.copy2(exe, package)

    for folder in ["templates", "data"]:
        src = BASE / folder
        dst = package / folder
        if src.exists():
            shutil.copytree(src, dst, dirs_exist_ok=True)
        else:
            dst.mkdir(exist_ok=True)

    (package / "output").mkdir(exist_ok=True)
    print(f"      Package created: {package}")
    return True


def show_result():
    print("[4/4] All done!")
    package = DIST / "EmailSignatureGenerator_package"
    print()
    print(f"  📦 Package location: {package}")
    print()
    print("  Package structure:")
    print("  ├── EmailSignatureGenerator(.exe)")
    print("  ├── templates/      ← Place your .html signature templates here")
    print("  ├── data/           ← Place one or more Excel files here")
    print("  └── output/         ← Generated signatures will appear here")
    print()
    print("  To distribute: zip the 'EmailSignatureGenerator_package' folder.")
    print("  No Python or dependency installation required on the target machine!")


def main():
    clean_flag = "--clean" in sys.argv
    print()
    print("=" * 55)
    print("   BUILD — Email Signature Generator")
    print("=" * 55)
    print()

    install_pyinstaller()

    if clean_flag:
        print("[*] Cleaning previous build...")
        clean()

    if not build():
        sys.exit(1)

    if not copy_assets():
        sys.exit(1)

    show_result()


if __name__ == "__main__":
    main()
