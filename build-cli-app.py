import subprocess
import os
import platform
from pathlib import Path
import re
import sys


def extract_version():
    init_path = Path("imxCli/__init__.py")
    content = init_path.read_text()
    match = re.search(r'__version__\s*=\s*"([^"]+)"', content)
    if not match:
        raise ValueError("Version not found in imxCli/__init__.py")
    return match.group(1)


def build_cli_app():
    script_path = Path("imxCli/cliApp/cliApp.py")
    data_path = Path("data")

    if not script_path.exists():
        raise FileNotFoundError(f"Script not found: {script_path}")
    if not data_path.exists():
        raise FileNotFoundError(f"Data folder not found: {data_path}")

    version = extract_version()
    system = platform.system().lower()
    exe_name = f"imxCli-{version}-{system}"

    sep = ';' if os.name == 'nt' else ':'

    command = [
        "pyinstaller",
        str(script_path),
        "--noconfirm",
        "--clean",
        "--onefile",
        "--distpath", "dist",
        "--name", exe_name,
        "--add-data", f"{data_path}{sep}data",
    ]

    print("📦 Running:", " ".join(command))
    try:
        subprocess.run(command, check=True)
        print(f"\n✅ Built: dist/{exe_name}{'.exe' if os.name == 'nt' else ''}")
    except subprocess.CalledProcessError as e:
        print(f"\n❌ PyInstaller failed: {e}")
        sys.exit(e.returncode)


if __name__ == "__main__":
    build_cli_app()
