from setuptools import setup
from setuptools.command.install import install
import subprocess

class PostInstallCommand(install):
    """Post-installation for installation mode."""
    def run(self):
        install.run(self)
        # Execute the shell commands here
        subprocess.run(["echo", "Hello, World!"])
        subprocess.run(["touch", "/tmp/mypackage_installed"])

setup(
    name='s3torchconnector',
    version='0.1.0',
    packages=['s3torchconnector'],
    cmdclass={
        'install': PostInstallCommand,
    },
)
