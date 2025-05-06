#!/usr/bin/env python3
"""
Script to create and configure the coverage Gist.
"""

import os
import sys
import json
import requests
from getpass import getpass

def create_coverage_gist(token):
    """Create a new Gist for coverage data."""
    headers = {
        'Authorization': f'token {token}',
        'Accept': 'application/vnd.github.v3+json'
    }
    
    data = {
        'description': 'Convo-AI Coverage Data',
        'public': False,
        'files': {
            'coverage.json': {
                'content': json.dumps({
                    'schemaVersion': 1,
                    'label': 'coverage',
                    'message': '0%',
                    'color': 'red'
                })
            }
        }
    }
    
    response = requests.post(
        'https://api.github.com/gists',
        headers=headers,
        json=data
    )
    
    if response.status_code == 201:
        return response.json()['id']
    else:
        print(f"Error creating Gist: {response.text}")
        sys.exit(1)

def main():
    """Main function to set up coverage Gist."""
    print("This script will help you set up the coverage Gist for Convo-AI.")
    print("You'll need a GitHub Personal Access Token with 'gist' scope.")
    print("\nPlease visit: https://github.com/settings/tokens")
    print("Create a new token with 'gist' scope.")
    
    token = getpass("\nEnter your GitHub token: ")
    
    print("\nCreating coverage Gist...")
    gist_id = create_coverage_gist(token)
    
    print("\nSetup complete! Add these secrets to your GitHub repository:")
    print(f"GIST_SECRET: {token}")
    print(f"COVERAGE_GIST_ID: {gist_id}")
    print("\nTo add these secrets:")
    print("1. Go to your repository on GitHub")
    print("2. Click Settings > Secrets and variables > Actions")
    print("3. Click 'New repository secret'")
    print("4. Add each secret with its corresponding value")

if __name__ == "__main__":
    main() 