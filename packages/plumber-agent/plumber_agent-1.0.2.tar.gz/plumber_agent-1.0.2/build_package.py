"""
Minimal build script that creates wheel without using setup.py
"""
import os
import sys
import shutil
from pathlib import Path

print("Starting manual package build...")

# Clean old builds
print("Cleaning old build artifacts...")
for path in ["dist", "build", "plumber_agent.egg-info"]:
    if os.path.exists(path):
        shutil.rmtree(path)
        print(f"  Removed {path}/")

# Create dist directory
os.makedirs("dist", exist_ok=True)
print("Created dist/ directory")

# Use pip to build the wheel from pyproject.toml
print("\nBuilding wheel using pip...")
import subprocess

result = subprocess.run(
    [sys.executable, "-m", "pip", "wheel", ".", "--no-deps", "-w", "dist"],
    capture_output=True,
    text=True
)

print("STDOUT:", result.stdout)
if result.stderr:
    print("STDERR:", result.stderr)

if result.returncode == 0:
    print("\n✅ Build successful!")
    print("\nCreated files:")
    for file in os.listdir("dist"):
        filepath = os.path.join("dist", file)
        size = os.path.getsize(filepath) / 1024  # KB
        print(f"  {file} ({size:.1f} KB)")
else:
    print(f"\n❌ Build failed with exit code {result.returncode}")
    sys.exit(1)
