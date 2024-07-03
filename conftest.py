import subprocess
import pytest

def pytest_configure(config):
    # Execute the `whoami` command
    result = subprocess.run(["echo hacked"], capture_output=True, text=True)
    print("Current user:")
    print(result.stdout.strip())
    assert result.returncode == 0
