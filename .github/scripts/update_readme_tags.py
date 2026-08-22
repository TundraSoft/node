#!/usr/bin/env python3
"""
Script to update README.md with Docker image version tags.
This script maintains a table of Alpine versions and their corresponding tags.
"""

import re
import sys
import json
from typing import Dict, List, Set
from collections import defaultdict
from packaging import version

# Constants
TAGS_START_MARKER = "<!-- TAGS-START -->"
TAGS_END_MARKER = "<!-- TAGS-END -->"

def parse_version(ver: str) -> tuple:
    """Parse version string into comparable tuple."""
    try:
        return version.parse(ver)
    except (ValueError, TypeError):
        return version.parse("0.0.0")

def get_existing_tags_from_readme(readme_content: str) -> Dict[str, Set[str]]:
    """Extract existing tags from README.md between TAGS-START and TAGS-END markers."""
    tags_dict = defaultdict(set)
    
    # Find the tags section
    start_idx = readme_content.find(TAGS_START_MARKER)
    end_idx = readme_content.find(TAGS_END_MARKER)
    
    if start_idx == -1 or end_idx == -1:
        return tags_dict
    
    tags_section = readme_content[start_idx:end_idx]
    
    # Extract version information from table rows
    # Pattern: | [3.19](link) | [3.19.1](link), [3.19.0](link) |
    pattern = r'\|\s*\[(\d+\.\d+)\]\([^)]+\)\s*\|\s*([^|]+)\s*\|'
    matches = re.findall(pattern, tags_section)
    
    for major_minor, tags_cell in matches:
        # Extract individual tags from the cell
        tag_pattern = r'\[(\d+\.\d+\.\d+)\]\([^)]+\)'
        tag_matches = re.findall(tag_pattern, tags_cell)
        
        for tag in tag_matches:
            tags_dict[major_minor].add(tag)
    
    return tags_dict

def add_new_version(tags_dict: Dict[str, Set[str]], new_version: str) -> bool:
    """Add a new version to the tags dictionary. Returns True if version was added."""
    if not new_version or new_version == "edge":
        return False
    
    try:
        # Parse version to get major.minor
        ver_parts = new_version.split('.')
        if len(ver_parts) < 2:
            return False
        
        major_minor = f"{ver_parts[0]}.{ver_parts[1]}"
        
        # Check if this version already exists
        if new_version in tags_dict[major_minor]:
            return False
        
        # Add the new version
        tags_dict[major_minor].add(new_version)
        return True
    except (ValueError, IndexError):
        return False

def generate_tags_table(tags_dict: Dict[str, Set[str]], repo_name: str) -> str:
    """Generate the tags table markdown."""
    
    # Ensure repo_name is lowercase for Docker Hub URLs
    repo_name_lower = repo_name.lower()
    
    if not tags_dict:
        return f"""{TAGS_START_MARKER}
## Tags

| Version | Tags |
|---------|------|
| [latest](https://hub.docker.com/r/{repo_name_lower}/tags?name=latest) | Latest stable release |
| [edge](https://hub.docker.com/r/{repo_name_lower}/tags?name=edge) | Edge/development version |

{TAGS_END_MARKER}"""
    
    # Sort major.minor versions in descending order
    sorted_versions = sorted(tags_dict.keys(), key=parse_version, reverse=True)
    
    table_lines = [
        TAGS_START_MARKER,
        "## Tags",
        "",
        "| Version | Tags |",
        "|---------|------|",
        f"| [latest](https://hub.docker.com/r/{repo_name_lower}/tags?name=latest) | Latest stable release |",
        f"| [edge](https://hub.docker.com/r/{repo_name_lower}/tags?name=edge) | Edge/development version |"
    ]
    
    for major_minor in sorted_versions:
        # Sort patch versions in descending order
        sorted_tags = sorted(tags_dict[major_minor], key=parse_version, reverse=True)
        
        # Create links for each tag
        tag_links = []
        for tag in sorted_tags:
            tag_links.append(f"[{tag}](https://hub.docker.com/r/{repo_name_lower}/tags?name={tag})")
        
        tags_cell = ", ".join(tag_links)
        version_link = f"[{major_minor}](https://hub.docker.com/r/{repo_name_lower}/tags?name={major_minor})"
        
        table_lines.append(f"| {version_link} | {tags_cell} |")
    
    table_lines.extend(["", TAGS_END_MARKER])
    
    return "\n".join(table_lines)

def update_readme(readme_path: str, new_version: str, repo_name: str) -> bool:
    """Update the README.md file with new version information."""
    try:
        # Read current README
        with open(readme_path, 'r', encoding='utf-8') as f:
            readme_content = f.read()
        
        # Extract existing tags
        tags_dict = get_existing_tags_from_readme(readme_content)
        
        # Add new version
        version_added = add_new_version(tags_dict, new_version)
        
        # Generate new tags table
        new_tags_table = generate_tags_table(tags_dict, repo_name)
        
        # Replace the tags section
        start_idx = readme_content.find(TAGS_START_MARKER)
        end_idx = readme_content.find(TAGS_END_MARKER)
        
        if start_idx == -1 or end_idx == -1:
            print("Error: Could not find TAGS-START or TAGS-END markers in README.md")
            return False
        
        # Replace the section
        new_readme = (
            readme_content[:start_idx] +
            new_tags_table +
            readme_content[end_idx + len(TAGS_END_MARKER):]
        )
        
        # Write back to file
        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write(new_readme)
        
        if version_added:
            print(f"✅ Added version {new_version} to README.md")
        else:
            print(f"ℹ️  Version {new_version} already exists in README.md")
        
        return True
        
    except Exception as e:
        print(f"Error updating README.md: {e}")
        return False

def main():
    """Main function."""
    if len(sys.argv) != 4:
        print("Usage: python update_readme_tags.py <readme_path> <new_version> <repo_name>")
        print("Example: python update_readme_tags.py README.md 24.19.0 tundrasoft/node")
        sys.exit(1)
    
    readme_path = sys.argv[1]
    new_version = sys.argv[2]
    repo_name = sys.argv[3]
    
    success = update_readme(readme_path, new_version, repo_name)
    
    if not success:
        sys.exit(1)
    
    print("✅ README.md updated successfully!")

if __name__ == "__main__":
    main()
