import os
import shutil

dst = "backup_pre_package_rename"
if os.path.exists(dst):
    shutil.rmtree(dst)
os.makedirs(dst, exist_ok=True)

items = [
    "anony", "tests", ".github",
    "config.py", "README.md", "NOTICE.md", ".env.example",
    "sample.env", "app.json", "pyproject.toml", "requirements.txt",
    "Dockerfile", "setup", "start", "heroku.yml", "Procfile",
    "LICENSE", ".dockerignore", ".gitignore", ".python-version"
]

for item in items:
    if os.path.isdir(item):
        shutil.copytree(item, os.path.join(dst, item), ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
    elif os.path.isfile(item):
        shutil.copy2(item, os.path.join(dst, item))

print(f"Pre-rename backup created successfully at {dst} with {len(items)} items.")
