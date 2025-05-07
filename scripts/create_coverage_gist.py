#!/usr/bin/env python3
"""
Create initial coverage Gist and print its ID.
"""

import os
import json
import requests
from dotenv import load_dotenv

def create_coverage_gist():
    """Create a new Gist for coverage data and print its ID."""
    # Load environment variables
    load_dotenv()
    
    # Get Gist token from environment
    gist_token = os.getenv("GIST_TOKEN")
    if not gist_token:
        print("No GIST_TOKEN found in .env file!")
        return

    # Create Gist
    headers = {
        "Authorization": f"token {gist_token}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    data = {
        "description": "Convo-AI Test Coverage Report",
        "public": False,
        "files": {
            "coverage.xml": {
                "content": "<!-- Initial coverage file -->"
            }
        }
    }

    response = requests.post(
        "https://api.github.com/gists",
        headers=headers,
        json=data
    )

    if response.status_code == 201:
        gist_data = response.json()
        gist_id = gist_data["id"]
        print(f"\nGist created successfully!")
        print(f"Gist ID: {gist_id}")
        print(f"Gist URL: {gist_data['html_url']}")
        print("\nAdd this to your .env file:")
        print(f"GIST_ID={gist_id}")
    else:
        print(f"Failed to create Gist: {response.text}")

if __name__ == "__main__":
    create_coverage_gist() 