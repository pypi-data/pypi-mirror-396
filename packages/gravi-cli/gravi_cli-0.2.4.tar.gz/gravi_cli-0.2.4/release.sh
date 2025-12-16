#!/bin/bash
set -e

# gravi-cli release script
# Triggers PyPI publishing via GitHub Actions
# Usage: ./release.sh [patch|minor|major]

BUMP_TYPE="${1:-patch}"

# Validate bump type
if [[ ! "$BUMP_TYPE" =~ ^(patch|minor|major)$ ]]; then
    echo "Error: Invalid bump type '$BUMP_TYPE'"
    echo "Usage: $0 [patch|minor|major]"
    echo ""
    echo "  patch - Bug fixes (0.1.0 -> 0.1.1)"
    echo "  minor - New features (0.1.0 -> 0.2.0)"
    echo "  major - Breaking changes (0.1.0 -> 1.0.0)"
    exit 1
fi

# Check if we're in a git repository
if ! git rev-parse --git-dir > /dev/null 2>&1; then
    echo "Error: Not in a git repository"
    exit 1
fi

# Check for uncommitted changes
if ! git diff-index --quiet HEAD --; then
    echo "Error: You have uncommitted changes. Please commit or stash them first."
    git status --short
    exit 1
fi

# Get current version
CURRENT_VERSION=$(grep '^version = ' pyproject.toml | grep -oP '\d+\.\d+\.\d+')
echo "Current version: $CURRENT_VERSION"
echo "Bump type: $BUMP_TYPE"
echo ""
echo "This will:"
echo "  1. Create and push a '$BUMP_TYPE' tag"
echo "  2. Trigger GitHub Actions to:"
echo "     - Bump the version"
echo "     - Build the package"
echo "     - Publish to PyPI"
echo "     - Create a version tag (e.g., gravi-cli-v0.1.1)"
echo ""
read -p "Continue? [y/N] " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Aborted."
    exit 1
fi

# Delete existing tag if it exists (both local and remote)
if git rev-parse "$BUMP_TYPE" >/dev/null 2>&1; then
    echo "Deleting existing local tag '$BUMP_TYPE'..."
    git tag -d "$BUMP_TYPE"
fi

if git ls-remote --tags origin | grep -q "refs/tags/$BUMP_TYPE$"; then
    echo "Deleting existing remote tag '$BUMP_TYPE'..."
    git push origin --delete "$BUMP_TYPE" 2>/dev/null || true
fi

# Create and push the trigger tag
echo "Creating and pushing '$BUMP_TYPE' tag..."
git tag "$BUMP_TYPE"
git push origin "$BUMP_TYPE"

echo ""
echo "✓ Tag pushed successfully!"
echo ""
echo "GitHub Actions is now building and publishing gravi-cli to PyPI."
echo "Monitor the progress at:"
echo "https://github.com/$(git remote get-url origin | sed 's/.*github.com[:/]\(.*\)\.git/\1/')/actions"
echo ""
echo "The '$BUMP_TYPE' tag will be automatically deleted after the release."
