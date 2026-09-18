from pathlib import Path
import os
import runpy

PROJECT_DIR = Path(__file__).resolve().parent / "grimslash"
os.chdir(PROJECT_DIR)
runpy.run_path(str(PROJECT_DIR / "main.py"), run_name="__main__")
