#!/usr/bin/env python3
"""
Run tests with coverage reporting.
"""

import os
import sys
import subprocess
from datetime import datetime
from pathlib import Path

def run_tests():
    """Run tests with coverage reporting."""
    # Create reports directory
    reports_dir = Path("reports/coverage")
    reports_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Run tests with coverage
    cmd = [
        "python", "-m", "pytest",
        "tests/",
        "-v",
        "--cov=src",
        "--cov-report=term-missing",
        f"--cov-report=html:reports/coverage/{timestamp}",
        "--cov-report=xml:reports/coverage/coverage.xml"
    ]
    
    print("Running tests with coverage...")
    result = subprocess.run(cmd)
    
    if result.returncode == 0:
        print("\nTests passed successfully!")
        print(f"Coverage report generated in reports/coverage/{timestamp}")
    else:
        print("\nTests failed!")
        sys.exit(1)

if __name__ == "__main__":
    run_tests() 