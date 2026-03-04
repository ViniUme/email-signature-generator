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

    print("      Installing Playwright Chromium...")
    subprocess.check_call([sys.executable, "-m", "playwright", "install", "chromium"])

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
        "--hidden-import", "playwright",
        "--hidden-import", "playwright.sync_api",
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

    # Localiza o Chromium — Playwright pode instalá-lo em locais diferentes
    print("      Locating Playwright Chromium...")

    browsers_src = None
    candidates = []

    import playwright
    playwright_pkg = Path(playwright.__file__).parent

    # 1. Dentro do pacote do Playwright (menos comum)
    candidates.append(playwright_pkg / "driver" / "package" / ".local-browsers")

    # 2. Pasta padrão do sistema (onde 'playwright install' coloca por padrão)
    if sys.platform == "win32":
        candidates.append(Path(os.environ.get("LOCALAPPDATA", "")) / "ms-playwright")
        candidates.append(Path(os.environ.get("USERPROFILE", "")) / "AppData" / "Local" / "ms-playwright")
    elif sys.platform == "darwin":
        candidates.append(Path.home() / "Library" / "Caches" / "ms-playwright")
    else:
        candidates.append(Path.home() / ".cache" / "ms-playwright")

    # 3. Variável de ambiente customizada (se o usuário tiver definido)
    env_path = os.environ.get("PLAYWRIGHT_BROWSERS_PATH")
    if env_path:
        candidates.insert(0, Path(env_path))

    for candidate in candidates:
        print(f"      Checking: {candidate}")
        if candidate.exists() and any(candidate.iterdir()):
            browsers_src = candidate
            print(f"      Found at: {browsers_src}")
            break

    if not browsers_src:
        print("[WARNING] Chromium not found in any known location.")
        print("          Run 'playwright install chromium' and try again.")
    else:
        # Copia apenas a pasta do chromium_headless_shell, ignorando outros browsers
        chromium_folders = [
            d for d in browsers_src.iterdir()
            if d.is_dir() and "chromium" in d.name.lower()
        ]

        if not chromium_folders:
            print(f"[WARNING] No Chromium folder found inside: {browsers_src}")
        else:
            browsers_dst = package / "chromium"
            if browsers_dst.exists():
                shutil.rmtree(browsers_dst)
            browsers_dst.mkdir()

            for folder in chromium_folders:
                dst_folder = browsers_dst / folder.name
                print(f"      Copying {folder.name}...")
                shutil.copytree(folder, dst_folder)

            print(f"      Chromium copied to: {browsers_dst}")

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
