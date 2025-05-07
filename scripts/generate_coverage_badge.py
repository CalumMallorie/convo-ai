#!/usr/bin/env python3
"""
Generate a coverage badge Markdown for README.md based on the coverage report.
"""

import os
import xml.etree.ElementTree as ET
from pathlib import Path
from dotenv import load_dotenv

def generate_coverage_badge():
    """Generate a coverage badge Markdown based on the coverage report."""
    # Load environment variables from .env file
    load_dotenv()
    
    # Get Gist ID
    gist_id = os.getenv("GIST_ID")
    if not gist_id:
        print("No GIST_ID found in environment!")
        return
    
    # Read coverage data
    coverage_file = Path("reports/coverage/coverage.xml")
    if not coverage_file.exists():
        print("No coverage data found!")
        return
    
    # Parse coverage data
    tree = ET.parse(coverage_file)
    root = tree.getroot()
    
    # Get coverage percentage
    line_rate = float(root.get("line-rate", "0"))
    coverage_pct = int(line_rate * 100)
    
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
    
    # Generate Markdown
    markdown = f"[![Test Coverage]({badge_url})](https://gist.github.com/CalumMallorie/{gist_id})"
    
    print("\nCoverage Badge Markdown:")
    print(markdown)
    print("\nCopy and paste this into your README.md to display the coverage badge.")

if __name__ == "__main__":
    generate_coverage_badge() 