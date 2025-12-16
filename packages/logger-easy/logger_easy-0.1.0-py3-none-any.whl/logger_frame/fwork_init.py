from pathlib import Path
from importlib.resources import files

def init_project(args=None):
    dst = Path.cwd() / "logger.py"

    if dst.exists():
        print("logger.py already exists")
        return

    src = files("logger_frame") / "logger.py"
    dst.write_bytes(src.read_bytes())

    print("logger.py copied to current directory")