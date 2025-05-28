import os
import shutil
import subprocess
import sys
from pathlib import Path
import nicegui

APP_NAME = 'imxDiff'
ENTRY_FILE = 'guiApp.py'
DIST_DIR = Path('dist') / f'{APP_NAME}'
STATIC_SRC = Path(nicegui.__path__[0]) / 'static'
STATIC_DST = DIST_DIR / '_internal' / 'nicegui' / 'static'

def clean_build_dir():
    if DIST_DIR.exists():
        print(f'🧹 Cleaning old build at {DIST_DIR}...')
        shutil.rmtree(DIST_DIR)

def build_app():
    print(f'📦 Building NiceGUI app "{APP_NAME}"...')

    process = subprocess.Popen(
        ['nicegui-pack', '--name', APP_NAME, ENTRY_FILE],
        shell=True,
        env={**os.environ, 'NICEGUI_AUTOSTART': '0'},
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        universal_newlines=True,
    )

    for line in process.stdout:
        print(line, end='')

    process.wait()
    if process.returncode != 0:
        print(f'\n❌ Build failed with exit code {process.returncode}')
        sys.exit(1)

    print('✅ Build complete.')

def patch_static_assets():
    if not STATIC_SRC.exists():
        print(f'❌ Could not find NiceGUI static files at {STATIC_SRC}')
        sys.exit(1)
    print(f'🔧 Copying static files from {STATIC_SRC} to {STATIC_DST}')
    STATIC_DST.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(STATIC_SRC, STATIC_DST, dirs_exist_ok=True)
    print('✅ Static files copied.')

if __name__ == '__main__':
    clean_build_dir()
    build_app()
    patch_static_assets()
    print(f'🎉 App ready at {DIST_DIR}')
