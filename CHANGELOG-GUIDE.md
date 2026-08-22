# Changelog Management Guide

## Overview

This project uses an automated changelog management system that maintains a comprehensive `CHANGELOG.md` file following the [Keep a Changelog](https://keepachangelog.com/) format.

## How It Works

### Automatic Updates

When a **PR is merged to `main`**, the `update-changelog.yml` workflow automatically:

1. **Extracts PR Information**
   - PR title
   - PR number
   - Merge author
   - Commit messages

2. **Categorizes the Change**
   - Analyzes PR title for keywords
   - Assigns to appropriate category (Added, Fixed, Security, etc.)
   - Falls back to "Changed" if uncertain

3. **Updates CHANGELOG.md**
   - Creates date section if needed (YYYY-MM-DD format)
   - Adds category section if needed
   - Appends entry with PR link and author
   - Prevents duplicate entries

4. **Commits and Pushes**
   - Uses bot account for commits
   - Adds `[skip ci]` to prevent rebuild
   - Auto-updates main branch

### Categorization Rules

The workflow automatically categorizes PRs based on title keywords:

| Keywords | Category | Example |
|----------|----------|---------|
| `feat`, `feature`, `add`, `new` | Added | "feat: Add custom service examples" |
| `fix`, `bug`, `issue` | Fixed | "fix: Correct timezone handling" |
| `security`, `cve`, `vulnerability` | Security | "security: Patch container vulnerability" |
| `docs`, `documentation`, `readme` | Documentation | "docs: Update README.md" |
| `chore`, `refactor`, `perf` | Changed | "chore: Refactor build process" |
| `deprecat` | Deprecated | "deprecate: Legacy API endpoint" |
| `remov` | Removed | "remove: Old build script" |

## Changelog Format

Each entry follows this structure:

```markdown
## [YYYY-MM-DD]

### Category
- PR Title ([#123](https://github.com/TundraSoft/node/pull/123)) by @author-username

### Category
- Another PR Title ([#124](https://github.com/TundraSoft/node/pull/124)) by @another-author
```

### Example Entry

```markdown
## [2025-12-17]

### Added
- Enhanced README with comprehensive S6 service documentation ([#42](https://github.com/TundraSoft/node/pull/42)) by @user1
- S6 Service Architecture documentation ([#43](https://github.com/TundraSoft/node/pull/43)) by @user2

### Fixed
- Correct timezone handling in init script ([#44](https://github.com/TundraSoft/node/pull/44)) by @user3

### Security
- Update Alpine base image for security patches ([#45](https://github.com/TundraSoft/node/pull/45)) by @user4

### Documentation
- Add troubleshooting guide ([#46](https://github.com/TundraSoft/node/pull/46)) by @user5
```

## Best Practices

### 1. Use Clear PR Titles

✅ **Good PR Titles** (categorized automatically)
- `feat: Add custom service examples to S6 overlay`
- `fix: Resolve cron job timing issue`
- `docs: Update README with troubleshooting guide`
- `security: Patch container vulnerability in Alpine`

❌ **Ambiguous PR Titles**
- `Update something`
- `WIP: Changes`
- `Random fixes`

→ These will default to "Changed" category

### 2. Link Issues in PR Descriptions

Include issue references in PR body for better traceability:

```
## Description
Fixes #123
Relates to #124, #125

## Changes
- Updated documentation
- Added examples
```

The workflow will link to the PR, which should link to the issues.

### 3. Write Descriptive PR Titles

The PR title becomes the changelog entry, so make it clear:

✅ **Good**
```
docs: Add comprehensive S6 service documentation and examples
```

❌ **Poor**
```
docs update
```

### 4. Use Conventional Commits

While not required, following [Conventional Commits](https://www.conventionalcommits.org/) helps:

```
feat(s6): Add health check support
fix(cron): Prevent duplicate job entries
docs(readme): Update service architecture diagram
security(alpine): Update base image
```

## Manual Changelog Updates

For significant releases or bulk updates, you can edit `CHANGELOG.md` directly:

1. Edit the file in your PR
2. Add entries under appropriate date/category
3. Follow the existing format
4. The automation won't duplicate if PR is already mentioned

### When to Manually Update

- Creating a **release branch** with curated changes
- **Summarizing multiple related PRs** into one entry
- **Adding historical changes** to the [Unreleased] section
- **Finalizing a release** with version tags

## Workflow Features

### Duplicate Detection

If a PR number is already in the changelog, the workflow:
- Skips adding the entry
- Issues a warning in the workflow run
- Prevents accidental duplicates

### Date-Based Organization

Entries are organized by merge date:
- New dates are added in reverse chronological order
- Multiple entries on same date are grouped together
- Makes it easy to find when changes were released

### Reversibility

To remove an entry:
1. Edit `CHANGELOG.md` directly
2. Commit with clear message explaining removal
3. PR gets merged normally

The automation won't re-add it since it checks for duplicates.

## Viewing Changelog History

### On GitHub

- **Repository Homepage**: Link to CHANGELOG.md in README
- **Releases Page**: `github.com/TundraSoft/node/releases`
- **Git History**: `git log --oneline CHANGELOG.md`

### Locally

```bash
# View entire changelog
cat CHANGELOG.md

# View changes since date
git log --since="2025-12-01" --oneline

# View commits affecting CHANGELOG
git log --follow CHANGELOG.md

# Check specific PR changes
git log --grep="123" --oneline
```

## Troubleshooting

### Workflow Failed to Update Changelog

**Check:**
1. PR was merged to `main` (not squashed from another branch)
2. PR title contains relevant keywords
3. No pre-existing entry for this PR number
4. CHANGELOG.md is not locked/edited elsewhere

**Review:**
- Check workflow run logs: `.github/workflows/update-changelog.yml`
- Look for error messages in the failed job

### Entry Didn't Get Categorized Correctly

**Solution:**
1. The workflow uses keyword matching on PR title
2. If categorization is wrong, manually edit CHANGELOG.md
3. Alternatively, rename the PR title (requires re-running workflow manually)

### Need to Re-run Workflow

```bash
# Remove the entry from changelog (if added)
# Edit CHANGELOG.md and remove the PR entry

# Push changes
git push

# Re-run workflow manually via GitHub UI
# Actions → Update Changelog → Run workflow
```

## Integration with Releases

When creating a GitHub Release:

1. **Go to Releases** → "Draft a new release"
2. **Select tag version** (e.g., `v1.0.0` - if versioning is adopted)
3. **Copy entries from CHANGELOG.md** for that date/version
4. **Publish release**

The changelog automatically keeps track of what changed between versions.

## Future Enhancements

Possible improvements:
- Generate release notes automatically from changelog
- Create GitHub Releases with changelog entries
- Version the changelog with semantic versioning
- Generate table of contents automatically
- Validate changelog format in PR checks

## References

- [Keep a Changelog](https://keepachangelog.com/)
- [Conventional Commits](https://www.conventionalcommits.org/)
- [Semantic Versioning](https://semver.org/)
- [GitHub Release Notes](https://docs.github.com/en/repositories/releasing-projects-on-github/about-releases)
