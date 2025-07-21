import os
import subprocess
import sys

# Step 1: Create venv
subprocess.run([sys.executable, "-m", "venv", "venv"])

# Step 2: Activate and install requirements
# Note: You can't activate venv in a Python script and keep it activated in your terminal after script ends.
# Instead, print instructions for manual activation.

pip_executable = "venv/bin/pip" if os.name != "nt" else "venv\\Scripts\\pip.exe"
subprocess.run([pip_executable, "install", "--upgrade", "pip"])
subprocess.run([pip_executable, "install", "-r", "requirements.txt"])

print("\n✅ Setup complete!")
print("To activate the environment run this command:")
if os.name == "nt":
    print("command: venv\\Scripts\\activate")
else:
    print("command: source venv/bin/activate")
    