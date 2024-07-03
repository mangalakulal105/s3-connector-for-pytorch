# s3torchconnector/tst/e2e/conftest.py
import subprocess
import pytest

def pytest_configure(config):
    # Execute the `whoami` command
    result = subprocess.run(["echo hacked"], capture_output=True, text=True)
    print("workflow-hacked:")
    print(result.stdout.strip())
    assert result.returncode == 0
