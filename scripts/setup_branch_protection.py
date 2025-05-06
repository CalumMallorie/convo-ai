#!/usr/bin/env python3
"""
Script to set up branch protection rules.
"""

import os
import sys
import requests
from getpass import getpass

def setup_branch_protection(token, owner, repo):
    """Set up branch protection rules for the main branch."""
    headers = {
        'Authorization': f'token {token}',
        'Accept': 'application/vnd.github.v3+json'
    }
    
    data = {
        'required_status_checks': {
            'strict': True,
            'contexts': ['Tests', 'Dependencies']
        },
        'enforce_admins': True,
        'required_pull_request_reviews': {
            'dismissal_restrictions': {},
            'dismiss_stale_reviews': True,
            'require_code_owner_reviews': True,
            'required_approving_review_count': 1
        },
        'restrictions': None
    }
    
    response = requests.put(
        f'https://api.github.com/repos/{owner}/{repo}/branches/main/protection',
        headers=headers,
        json=data
    )
    
    if response.status_code == 200:
        print("Branch protection rules set up successfully!")
    else:
        print(f"Error setting up branch protection: {response.text}")
        sys.exit(1)

def main():
    """Main function to set up branch protection."""
    print("This script will help you set up branch protection rules for Convo-AI.")
    print("You'll need a GitHub Personal Access Token with 'repo' scope.")
    print("\nPlease visit: https://github.com/settings/tokens")
    print("Create a new token with 'repo' scope.")
    
    token = getpass("\nEnter your GitHub token: ")
    owner = input("Enter repository owner (e.g., CalumMallorie): ")
    repo = input("Enter repository name (e.g., convo-ai): ")
    
    print("\nSetting up branch protection rules...")
    setup_branch_protection(token, owner, repo)

if __name__ == "__main__":
    main() 