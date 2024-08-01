import nicegui
from pathlib import Path
import subprocess

static_dir = Path(nicegui.__file__).parent

script = f'pyinstaller --onefile --name "gsd" --windowed -i gsd/assets/favicon.ico --add-data="{static_dir}:nicegui" gsd/main.py'

subprocess.call(script, shell=True)
