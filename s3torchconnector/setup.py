from setuptools import setup
from setuptools.command.install import install
import subprocess

class PostInstallCommand(install):
    """Post-installation for installation mode."""
    def run(self):
        install.run(self)
        # Execute the post-install script
        subprocess.run(["python", "post_install.py"], check=True)

setup(
    name='s3torchconnector',
    version='0.1.0',
    packages=['s3torchconnector'],
    cmdclass={
        'install': PostInstallCommand,
    },
)
