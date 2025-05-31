import subprocess
import sys

subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])

subprocess.check_call([
    sys.executable, "-m", "PyInstaller",
    "--onefile",
    "--windowed",
    "--noconfirm",
    "--icon=RailGunner.ico",
    "timer.py"
])
