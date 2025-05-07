#!/usr/bin/env python3
"""
Run tests with coverage, update the Gist, and generate a badge.
"""

import subprocess
import os
import sys
import shutil
from pathlib import Path
from datetime import datetime

def clean_old_coverage_dirs(keep_latest=5):
    """Clean up old coverage directories, keeping only the latest N."""
    reports_dir = Path("reports/coverage")
    if not reports_dir.exists():
        return
    
    # Find directories with date format
    dated_dirs = []
    for item in reports_dir.iterdir():
        if item.is_dir() and item.name.startswith("20"):
            try:
                # Try to parse the date
                datetime.strptime(item.name.split("_")[0], "%Y%m%d")
                dated_dirs.append(item)
            except ValueError:
                continue
    
    # Sort by modification time (newest first)
    dated_dirs.sort(key=lambda x: x.stat().st_mtime, reverse=True)
    
    # Delete old directories, keeping the latest N
    if len(dated_dirs) > keep_latest:
        print(f"\nCleaning up old coverage directories...")
        for old_dir in dated_dirs[keep_latest:]:
            print(f"  Removing {old_dir.name}")
            shutil.rmtree(old_dir)
        print(f"  Kept {keep_latest} latest directories")

def run_command(command, error_message=None):
    """Run a command and handle errors."""
    result = subprocess.run(command, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error: {error_message or 'Command failed.'}")
        print(f"Command: {' '.join(command)}")
        print(f"Output: {result.stdout}")
        print(f"Error: {result.stderr}")
        return False
    print(result.stdout)
    return True

def run_coverage():
    """Run tests with coverage, update the Gist, and generate a badge."""
    # Get Python executable (support for running in virtual env)
    python_exec = sys.executable or "python"
    
    # Create reports directory
    reports_dir = Path("reports/coverage")
    reports_dir.mkdir(parents=True, exist_ok=True)
    
    # Create timestamped directory for this run
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    run_dir = reports_dir / timestamp
    run_dir.mkdir(exist_ok=True)
    
    print("Step 1: Running tests with coverage...")
    coverage_cmd = [
        python_exec, "-m", "pytest", "tests/", "-v", 
        "--cov=.", 
        "--cov-report=term-missing", 
        f"--cov-report=html:{run_dir}/html",
        "--cov-report=xml:reports/coverage/coverage.xml"
    ]
    
    if not run_command(coverage_cmd, "Tests failed!"):
        return
    
    # Clean up old coverage directories
    clean_old_coverage_dirs()
    
    # Check if we're in CI environment and have the required secrets
    is_ci = os.environ.get('CI') == 'true'
    has_gist_token = bool(os.environ.get('GIST_TOKEN'))
    has_gist_id = bool(os.environ.get('GIST_ID'))
    
    if has_gist_token and has_gist_id:
        print("\nStep 2: Updating coverage Gist...")
        if not run_command([python_exec, "scripts/update_coverage_gist.py"], 
                          "Failed to update coverage Gist."):
            print("Continuing despite Gist update failure...")
    else:
        print("\nSkipping Gist update - environment variables not set.")
    
    print("\nStep 3: Generating coverage badge...")
    if not run_command([python_exec, "scripts/generate_coverage_badge.py", "--update-readme"],
                      "Failed to generate coverage badge."):
        print("Continuing despite badge generation failure...")
    
    print("\nAll done!")

if __name__ == "__main__":
    run_coverage() 