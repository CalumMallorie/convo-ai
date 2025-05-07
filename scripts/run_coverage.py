#!/usr/bin/env python3
"""
Run tests with coverage, update the Gist, and generate a badge.
"""

import subprocess
from pathlib import Path

def run_coverage():
    """Run tests with coverage, update the Gist, and generate a badge."""
    # Create reports directory
    reports_dir = Path("reports/coverage")
    reports_dir.mkdir(parents=True, exist_ok=True)
    
    print("Step 1: Running tests with coverage...")
    result = subprocess.run(["python", "-m", "pytest", "tests/", "-v", "--cov=src", 
                           "--cov-report=term-missing", 
                           "--cov-report=html:reports/coverage/html",
                           "--cov-report=xml:reports/coverage/coverage.xml"])
    
    if result.returncode != 0:
        print("Tests failed! Not updating coverage Gist.")
        return
    
    print("\nStep 2: Updating coverage Gist...")
    subprocess.run(["python", "scripts/update_coverage_gist.py"])
    
    print("\nStep 3: Generating coverage badge...")
    subprocess.run(["python", "scripts/generate_coverage_badge.py"])
    
    print("\nAll done!")

if __name__ == "__main__":
    run_coverage() 