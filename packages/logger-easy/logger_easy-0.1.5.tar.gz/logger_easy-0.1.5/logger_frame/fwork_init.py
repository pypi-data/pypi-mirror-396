from pathlib import Path
from importlib.resources import files

def init_project(args=None):
    dst = Path.cwd() / "logger.py"
    dst2 = Path.cwd() / "log_guitest.py"

    src = files("logger_frame") / "logger.py"
    src2 = files("logger_frame") / "log_guitest.py"
    dst.write_bytes(src.read_bytes())
    dst2.write_bytes(src2.read_bytes())

    print("logger.py copied to current directory")
