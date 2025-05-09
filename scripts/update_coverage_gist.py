#!/usr/bin/env python3
"""
Update coverage data in a GitHub Gist.
"""

import os
import json
import sys
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
        print("Error: No coverage data found!")
        print("Run tests with coverage first using: python -m pytest --cov=. --cov-report=xml:reports/coverage/coverage.xml")
        return False

    # Get Gist token from environment
    gist_token = os.getenv("GIST_TOKEN")
    if not gist_token:
        print("Error: No GIST_TOKEN found in environment!")
        print("Set the GIST_TOKEN environment variable with your GitHub personal access token.")
        return False

    # Get Gist ID from environment
    gist_id = os.getenv("GIST_ID")
    if not gist_id:
        print("Error: No GIST_ID found in environment!")
        print("Set the GIST_ID environment variable with your Gist ID.")
        return False

    try:
        # Read coverage data
        with open(coverage_file) as f:
            coverage_data = f.read()

        # Get summary data for the description
        import xml.etree.ElementTree as ET
        tree = ET.parse(coverage_file)
        root = tree.getroot()
        line_rate = float(root.get("line-rate", "0"))
        coverage_pct = int(line_rate * 100)
        
        # Get timestamp for the description
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Update Gist
        headers = {
            "Authorization": f"token {gist_token}",
            "Accept": "application/vnd.github.v3+json"
        }
        
        data = {
            "description": f"Coverage Report ({coverage_pct}%) - Updated {timestamp}",
            "files": {
                "coverage.xml": {
                    "content": coverage_data
                },
                "summary.md": {
                    "content": f"# Coverage Summary\n\n- **Date**: {timestamp}\n- **Coverage**: {coverage_pct}%\n- **Status**: {'✅ Passed' if coverage_pct >= 70 else '❌ Failed'}\n\nThis report is automatically generated by the CI pipeline."
                }
            }
        }

        try:
            response = requests.patch(
                f"https://api.github.com/gists/{gist_id}",
                headers=headers,
                json=data,
                timeout=10  # 10 second timeout
            )

            if response.status_code == 200:
                print(f"✅ Coverage Gist updated successfully! Coverage: {coverage_pct}%")
                print(f"View at: https://gist.github.com/{gist_id}")
                return True
            else:
                print(f"❌ Failed to update Gist: HTTP {response.status_code}")
                print(f"Response: {response.text}")
                return False
        except requests.exceptions.RequestException as e:
            print(f"❌ Error making request to GitHub API: {e}")
            return False
            
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    success = update_coverage_gist()
    sys.exit(0 if success else 1) 