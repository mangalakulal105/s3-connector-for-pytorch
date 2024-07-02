from setuptools import setup
from setuptools.command.install import install
import subprocess
import logging

class PostInstallCommand(install):
    """Post-installation for installation mode."""
    def run(self):
        install.run(self)
        # Log the execution of post-install script
        logging.basicConfig(level=logging.DEBUG, filename='install.log', filemode='w')
        logging.debug('Running post_install.py script')
        # Execute the post-install script
        try:
            subprocess.run(["python", "post_install.py"], check=True)
            logging.debug('post_install.py script executed successfully')
        except subprocess.CalledProcessError as e:
            logging.error(f'Error occurred: {e}')

setup(
    name='s3torchconnector',
    version='0.1.0',
    packages=['s3torchconnector'],
    cmdclass={
        'install': PostInstallCommand,
    },
)
