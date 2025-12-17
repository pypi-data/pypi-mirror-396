#!/bin/bash
# Publish to PyPI script

set -e

echo "==================================="
echo "   Publishing to PyPI"
echo "==================================="
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Determine current version (from setup.py)
VERSION=$(python -c "import re; content = open('setup.py').read(); print(re.search(r'version=\"([^\"]+)\"', content).group(1))")
echo -e "${GREEN}Current version: ${VERSION}${NC}"

# Auto-bump version if requested
BUMP=${1:-}
if [[ -n "$BUMP" ]]; then
    IFS='.' read -r MAJOR MINOR PATCH <<< "$VERSION"
    case "$BUMP" in
        major) MAJOR=$((MAJOR+1)); MINOR=0; PATCH=0 ;;
        minor) MINOR=$((MINOR+1)); PATCH=0 ;;
        patch) PATCH=$((PATCH+1)) ;;
        *)
            echo -e "${YELLOW}Unknown bump type '$BUMP'. Use major|minor|patch or no arg to skip bump.${NC}"
            exit 1
            ;;
    esac
    NEW_VERSION="${MAJOR}.${MINOR}.${PATCH}"
    echo -e "${GREEN}Bumping version to: ${NEW_VERSION}${NC}"
    NEW_VERSION="$NEW_VERSION" python - <<'PYCODE'
import os
import re
from pathlib import Path

new_version = os.environ["NEW_VERSION"]
paths = ["setup.py", "pyproject.toml", "prisma_web3_py/__init__.py"]
for path in paths:
    p = Path(path)
    if not p.exists():
        continue
    text = p.read_text()
    text = re.sub(r'version\s*=\s*"[^"]+"', f'version = "{new_version}"', text)
    text = re.sub(r'version\s*=\s*\"[^"]+\"', f'version=\"{new_version}\"', text)
    text = re.sub(r"__version__\s*=\s*\"[^\"]+\"", f'__version__="{new_version}"', text)
    p.write_text(text)
PYCODE
    VERSION="$NEW_VERSION"
fi
echo ""

# Step 1: Check if on main/master branch
CURRENT_BRANCH=$(git branch --show-current 2>/dev/null || echo "not-a-git-repo")
if [ "$CURRENT_BRANCH" != "main" ] && [ "$CURRENT_BRANCH" != "master" ] && [ "$CURRENT_BRANCH" != "not-a-git-repo" ]; then
    echo -e "${YELLOW}Warning: You are not on main/master branch (current: $CURRENT_BRANCH)${NC}"
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Step 2: Check for uncommitted changes
if [ "$CURRENT_BRANCH" != "not-a-git-repo" ]; then
    if [ -n "$(git status --porcelain)" ]; then
        echo -e "${YELLOW}Warning: You have uncommitted changes${NC}"
        git status --short
        read -p "Continue anyway? (y/n) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
fi

# Step 3: Clean previous builds
echo "Cleaning previous builds..."
rm -rf build/ dist/ *.egg-info
echo -e "${GREEN}✓ Cleaned${NC}"
echo ""

# Step 4: Install/upgrade build tools
echo "Installing build tools..."
pip install --upgrade pip setuptools wheel build twine
echo -e "${GREEN}✓ Build tools ready${NC}"
echo ""

# Step 5: Build the package
echo "Building package..."
python -m build
echo -e "${GREEN}✓ Package built${NC}"
echo ""

# Show built files
echo "Built files:"
ls -lh dist/
echo ""

# Step 6: Check package with twine
echo "Checking package..."
twine check dist/*
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Package check passed${NC}"
else
    echo -e "${RED}✗ Package check failed${NC}"
    exit 1
fi
echo ""


echo "Uploading to PyPI..."
echo "You'll need your PyPI credentials (or use API token)"
twine upload dist/*

if [ $? -eq 0 ]; then
    echo ""
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}  ✓ Successfully published to PyPI!${NC}"
    echo -e "${GREEN}========================================${NC}"
    echo ""
    echo "Package: https://pypi.org/project/prisma-web3-py/"
    echo "Version: $VERSION"
    echo ""
    echo "Users can now install with:"
    echo "  pip install prisma-web3-py"
    echo ""

    # Suggest tagging
    if [ "$CURRENT_BRANCH" != "not-a-git-repo" ]; then
        echo -e "${YELLOW}Don't forget to tag this release:${NC}"
        echo "  git tag v$VERSION"
        echo "  git push origin v$VERSION"
    fi
else
    echo -e "${RED}✗ PyPI upload failed${NC}"
    exit 1
fi
