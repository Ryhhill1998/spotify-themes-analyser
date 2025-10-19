#!/usr/bin/env python3
"""Test runner script for the lambda function"""

import subprocess
import sys
from pathlib import Path


def run_command(cmd: list[str]) -> int:
    """Run a command and return the exit code"""
    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=Path(__file__).parent)
    return result.returncode


def main():
    """Main test runner"""
    if len(sys.argv) > 1:
        test_type = sys.argv[1]
    else:
        test_type = "all"

    base_cmd = ["uv", "run", "pytest"]

    if test_type == "unit":
        cmd = base_cmd + ["tests/unit/", "-m", "unit"]
    elif test_type == "integration":
        cmd = base_cmd + ["tests/integration/", "-m", "integration"]
    elif test_type == "e2e":
        cmd = base_cmd + ["tests/integration/test_end_to_end.py", "-m", "e2e"]
    elif test_type == "fast":
        cmd = base_cmd + ["-m", "not slow"]
    elif test_type == "all":
        cmd = base_cmd + ["tests/"]
    else:
        print(f"Unknown test type: {test_type}")
        print("Available types: unit, integration, e2e, fast, all")
        sys.exit(1)

    exit_code = run_command(cmd)
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
