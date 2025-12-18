"""Build and install ginsapy inside an isolated virtual environment."""
import os
import sys
import subprocess
import venv

base_dir = os.path.dirname(os.path.abspath(__file__))
venv_dir = os.path.join(base_dir, ".venv")

# 1. Create virtual environment if not existing
if not os.path.exists(venv_dir):
    print("* Creating isolated environment...")
    venv.EnvBuilder(with_pip=True).create(venv_dir)

# 2. Determine venv executables
if os.name == "nt":
    python_exe = os.path.join(venv_dir, "Scripts", "python.exe")
else:
    python_exe = os.path.join(venv_dir, "bin", "python")

# 3. Ensure build is installed in that environment
subprocess.check_call([python_exe, "-m", "pip", "install", "--upgrade", "pip", "build"])

# 4. Build wheel (in ./dist)
subprocess.check_call([python_exe, "-m", "build"], cwd=base_dir)

# 5. Install built wheel into the venv
dist_dir = os.path.join(base_dir, "dist")
wheel_files = [f for f in os.listdir(dist_dir) if f.endswith(".whl")]
if not wheel_files:
    raise FileNotFoundError("No wheel file found in dist/")
wheel_path = os.path.join(dist_dir, wheel_files[0])

subprocess.check_call([python_exe, "-m", "pip", "install", wheel_path])

print(f"\n* Done. Activate environment with:\n  {venv_dir}\\Scripts\\activate" if os.name == "nt"
      else f"\n* Done. Activate environment with:\n  source {venv_dir}/bin/activate")
