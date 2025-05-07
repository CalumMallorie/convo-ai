#!/usr/bin/env python3
"""
Update coverage data in a GitHub Gist.
"""

import os
import json
import requests
from pathlib import Path
from dotenv import load_dotenv

def update_coverage_gist():
    """Update the coverage Gist with latest coverage data."""
    # Load environment variables from .env file
    load_dotenv()
    
    # Read coverage data
    coverage_file = Path("reports/coverage/coverage.xml")
    if not coverage_file.exists():
        print("No coverage data found!")
        return

    # Get Gist token from environment
    gist_token = os.getenv("GIST_TOKEN")
    if not gist_token:
        print("No GIST_TOKEN found in environment!")
        return

    # Get Gist ID from environment
    gist_id = os.getenv("GIST_ID")
    if not gist_id:
        print("No GIST_ID found in environment!")
        return

    # Read coverage data
    with open(coverage_file) as f:
        coverage_data = f.read()

    # Update Gist
    headers = {
        "Authorization": f"token {gist_token}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    data = {
        "files": {
            "coverage.xml": {
                "content": coverage_data
            }
        }
    }

    response = requests.patch(
        f"https://api.github.com/gists/{gist_id}",
        headers=headers,
        json=data
    )

    if response.status_code == 200:
        print("Coverage Gist updated successfully!")
    else:
        print(f"Failed to update Gist: {response.text}")

if __name__ == "__main__":
    update_coverage_gist() 