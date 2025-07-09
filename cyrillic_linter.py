import os
import re

pattern = re.compile(r'[А-Яа-яЁё]')
excluded_dirs = {'.venv', }

for root, dirs, files in os.walk("."):
    dirs[:] = [d for d in dirs if d not in excluded_dirs]
    for name in files:
        if name.endswith(".py"):
            path = os.path.join(root, name)
            try:
                with open(path, encoding="utf-8", errors="ignore") as f:
                    for lineno, line in enumerate(f, 1):
                        if pattern.search(line):
                            print(f"{path}:{lineno}: {line.strip()}")
            except Exception as e:
                print(f"⚠️ Failed to read {path}: {e}")
