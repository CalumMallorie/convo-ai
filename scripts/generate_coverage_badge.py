#!/usr/bin/env python3
"""
Generate a coverage badge Markdown for README.md based on the coverage report.
"""

import os
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from dotenv import load_dotenv

def generate_coverage_badge():
    """Generate a coverage badge Markdown based on the coverage report."""
    # Load environment variables from .env file
    load_dotenv()
    
    # Read coverage data
    coverage_file = Path("reports/coverage/coverage.xml")
    if not coverage_file.exists():
        print("No coverage data found! Run tests with coverage first.")
        print("Command: python -m pytest --cov=. --cov-report=xml:reports/coverage/coverage.xml")
        return
    
    try:
        # Parse coverage data
        tree = ET.parse(coverage_file)
        root = tree.getroot()
        
        # Get coverage percentage
        line_rate = float(root.get("line-rate", "0"))
        coverage_pct = int(line_rate * 100)
    except Exception as e:
        print(f"Error parsing coverage data: {e}")
        return
    
    # Determine badge color
    if coverage_pct >= 90:
        color = "brightgreen"
    elif coverage_pct >= 80:
        color = "green"
    elif coverage_pct >= 70:
        color = "yellowgreen"
    elif coverage_pct >= 60:
        color = "yellow"
    else:
        color = "red"
    
    # Generate badge URL
    badge_url = f"https://img.shields.io/badge/coverage-{coverage_pct}%25-{color}"
    
    # Get Gist ID
    gist_id = os.getenv("GIST_ID")
    
    # Generate Markdown
    if gist_id:
        markdown = f"[![Test Coverage]({badge_url})](https://gist.github.com/CalumMallorie/{gist_id})"
        print("\nCoverage Badge Markdown with Gist link:")
        print(markdown)
    else:
        markdown = f"![Test Coverage]({badge_url})"
        print("\nCoverage Badge Markdown:")
        print(markdown)
    
    # Also show plain badge URL for direct use
    print("\nBadge URL for direct use:")
    print(badge_url)
    
    # Update README.md automatically if requested
    if len(sys.argv) > 1 and sys.argv[1] == "--update-readme":
        try:
            update_readme_badge(badge_url)
            print("README.md updated successfully!")
        except Exception as e:
            print(f"Error updating README.md: {e}")
    else:
        print("\nCopy and paste one of these into your README.md to display the coverage badge.")
        print("Or run with --update-readme to update README.md automatically.")

def update_readme_badge(badge_url):
    """Update the coverage badge in README.md."""
    readme_path = Path("README.md")
    if not readme_path.exists():
        print("README.md not found!")
        return
    
    with open(readme_path, "r") as f:
        content = f.read()
    
    # Replace existing badge or add new badge
    if "![Coverage]" in content:
        new_content = content.replace(
            content[content.find("![Coverage]"):content.find(")", content.find("![Coverage]")) + 1],
            f"![Coverage]({badge_url})"
        )
    else:
        # Find a good place to add the badge, after the title or next to another badge
        if "![" in content and "](" in content:
            # Add after the first badge
            end_of_badge = content.find(")", content.find("](")) + 1
            new_content = content[:end_of_badge] + f" ![Coverage]({badge_url})" + content[end_of_badge:]
        else:
            # Add after the first heading
            first_heading_end = content.find("\n", content.find("#"))
            new_content = content[:first_heading_end] + f"\n\n![Coverage]({badge_url})" + content[first_heading_end:]
    
    with open(readme_path, "w") as f:
        f.write(new_content)

if __name__ == "__main__":
    generate_coverage_badge() 