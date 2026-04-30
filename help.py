# help.py
from pathlib import Path

lines = Path("Makefile").read_text(encoding="utf-8").splitlines()

for line in lines:
    if "##" in line:
        cmd, desc = line.split("##", 1)
        cmd = cmd.split(":")[0].strip()
        print(f"{cmd:18} {desc.strip()}")