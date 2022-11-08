import subprocess
import sys
import pathlib

currentDirectory = pathlib.Path(__file__).parents[0]
lock1 = currentDirectory / "EverEyePassiveLock1.py"
lock2 = currentDirectory / "EverEyePassiveLock2.py"
gui = currentDirectory / "EverEyeProgram.py"

subprocess.Popen([sys.executable, lock1])
subprocess.Popen([sys.executable, lock2])
subprocess.Popen([sys.executable, gui])