#!/usr/bin/env python3
"""
Update CHANGELOG.md based on PR information and commit messages.
Features:
- Uses predefined categorization rules (no file reading)
- Handles multiple commits from a PR
- Prevents duplicate entries in same date section
- Groups by category in consistent order
"""

import re
import sys
import subprocess
from datetime import datetime

CATEGORY_KEYWORDS = {
    'Added': ['feat', 'feature', 'add', 'new'],
    'Fixed': ['fix', 'bug', 'issue', 'resolve'],
    'Security': ['security', 'cve', 'vulnerability', 'patch'],
    'Documentation': ['docs', 'documentation', 'readme'],
    'Deprecated': ['deprecat'],
    'Removed': ['remov'],
    'Changed': ['chore', 'refactor', 'perf', 'style', 'test'],
}

CATEGORY_ORDER = ['Security', 'Added', 'Fixed', 'Changed', 'Deprecated', 'Removed']

def categorize_commit(message):
    """Categorize a commit message based on keywords."""
    message_lower = message.lower()
    for category, keywords in CATEGORY_KEYWORDS.items():
        for keyword in keywords:
            if keyword.lower() in message_lower:
                return category
    return 'Changed'

def get_commits_from_pr(base_sha, head_sha):
    """Extract all commit messages from a PR."""
    commits = []
    try:
        cmd = ["git", "log", f"{base_sha}..{head_sha}", "--pretty=%B%n---END---"]
        result = subprocess.run(cmd, shell=False, capture_output=True, text=True)
        if result.returncode == 0:
            messages = result.stdout.split('---END---')
            for msg in messages:
                msg = msg.strip()
                if msg:
                    subject = msg.split('\n')[0].strip()
                    if subject:
                        commits.append(subject)
    except Exception as e:
        print(f"Error: {e}")
    return commits

def format_entry(title, pr_num, author, repo):
    """Format a changelog entry."""
    parts = repo.split('/')
    owner, name = parts if len(parts) == 2 else ('TundraSoft', repo)
    link = f"https://github.com/{owner}/{name}/pull/{pr_num}"
    return f"- {title} ([#{pr_num}]({link})) by @{author}"

def entry_exists(entry, existing):
    """Check if entry (by PR number) already exists."""
    match = re.search(r'\(#(\d+)\)', entry)
    if match:
        pr = match.group(1)
        return any(f"(#{pr})" in e for e in existing)
    return False

def update_changelog(path, entries_by_cat):
    """Update CHANGELOG.md with new entries, preventing duplicates."""
    today = datetime.now().strftime('%Y-%m-%d')
    date_hdr = f"## [{today}]"
    
    with open(path, 'r') as f:
        content = f.read()
    
    if date_hdr in content:
        # Today's section exists - merge entries carefully
        lines = content.split('\n')
        existing_by_cat = {}
        date_start = -1
        date_end = -1
        
        # Find today's section
        for i, line in enumerate(lines):
            if line.startswith(date_hdr):
                date_start = i
            elif date_start >= 0 and line.startswith('## ['):
                date_end = i
                break
        
        # Extract existing entries for today
        if date_start >= 0:
            end = date_end if date_end >= 0 else len(lines)
            current_cat = None
            for i in range(date_start + 1, end):
                if lines[i].startswith('### '):
                    current_cat = lines[i].replace('### ', '').strip()
                    existing_by_cat[current_cat] = []
                elif lines[i].startswith('- ') and current_cat:
                    existing_by_cat[current_cat].append(lines[i])
        
        # Build new section
        new_lines = []
        for i in range(0, date_start + 1):
            new_lines.append(lines[i])
        
        new_lines.append('')
        
        # Add all categories with deduplicated entries
        for cat in CATEGORY_ORDER:
            entries_to_add = []
            
            # Add existing entries first
            if cat in existing_by_cat:
                entries_to_add.extend(existing_by_cat[cat])
            
            # Add new entries (check for duplicates)
            if cat in entries_by_cat:
                for entry in entries_by_cat[cat]:
                    # Check if this exact entry exists
                    if entry not in entries_to_add:
                        # Also check by PR number to avoid same PR different commit message
                        pr_match = re.search(r'\(#(\d+)\)', entry)
                        if pr_match:
                            pr_num = pr_match.group(1)
                            is_dup = False
                            for existing in entries_to_add:
                                if f"(#{pr_num})" in existing:
                                    is_dup = True
                                    break
                            if not is_dup:
                                entries_to_add.append(entry)
                        else:
                            entries_to_add.append(entry)
            
            # Add category if has entries
            if entries_to_add:
                new_lines.append(f"### {cat}")
                new_lines.extend(entries_to_add)
                new_lines.append('')
        
        # Add rest of file (skip old today section)
        if date_end >= 0:
            new_lines.extend(lines[date_end:])
        
        content = '\n'.join(new_lines)
    else:
        # No today section - create it
        lines = content.split('\n')
        new_sec = f"{date_hdr}\n"
        
        for cat in CATEGORY_ORDER:
            if cat in entries_by_cat and entries_by_cat[cat]:
                new_sec += f"\n### {cat}\n"
                for entry in entries_by_cat[cat]:
                    new_sec += f"{entry}\n"
        
        new_sec += "\n---\n\n"
        
        insert_pos = 0
        for i, line in enumerate(lines):
            if line.startswith('## ['):
                insert_pos = i
                break
        
        if insert_pos > 0:
            content = '\n'.join(lines[:insert_pos]) + '\n' + new_sec + '\n'.join(lines[insert_pos:])
        else:
            content = content + '\n' + new_sec
    
    with open(path, 'w') as f:
        f.write(content)
    
    print(f"✅ Updated CHANGELOG.md for {today}")

def main():
    if len(sys.argv) < 4:
        print("Usage: update_changelog.py <path> <pr_title> <pr_num> <repo> [author] [base_sha] [head_sha]")
        sys.exit(1)
    
    path = sys.argv[1]
    pr_title = sys.argv[2]
    pr_num = int(sys.argv[3])
    repo = sys.argv[4]
    author = sys.argv[5] if len(sys.argv) > 5 else 'github-action'
    base_sha = sys.argv[6] if len(sys.argv) > 6 else None
    head_sha = sys.argv[7] if len(sys.argv) > 7 else None
    
    commits = [pr_title]
    if base_sha and head_sha:
        commits.extend(get_commits_from_pr(base_sha, head_sha))
    
    seen = set()
    unique = []
    for c in commits:
        if c not in seen:
            seen.add(c)
            unique.append(c)
    
    entries_by_cat = {}
    for msg in unique:
        cat = categorize_commit(msg)
        entry = format_entry(msg, pr_num, author, repo)
        entries_by_cat.setdefault(cat, []).append(entry)
    
    update_changelog(path, entries_by_cat)
    print(f"✅ Added {len(unique)} entry(ies) from PR #{pr_num}")

if __name__ == '__main__':
    main()
