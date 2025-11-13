#!/bin/bash

# Quick git commit and push script for OmniSync

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}📦 OmniSync Git Push Helper${NC}"
echo ""

# Check if we're in a git repo
if [ ! -d .git ]; then
    echo "❌ Not a git repository!"
    exit 1
fi

# Show status
echo "📋 Current changes:"
git status --short
echo ""

# Ask for commit message
if [ -z "$1" ]; then
    echo "Enter commit message (or press Enter for default):"
    read -r commit_msg
    if [ -z "$commit_msg" ]; then
        commit_msg="Update OmniSync code"
    fi
else
    commit_msg="$1"
fi

# Add all changes
echo ""
echo "➕ Adding all changes..."
git add -A

# Commit
echo "💾 Committing changes..."
git commit -m "$commit_msg"

# Push
echo "🚀 Pushing to GitHub..."
git push origin main

echo ""
echo -e "${GREEN}✅ Successfully pushed to GitHub!${NC}"
echo ""
echo "Repository: https://github.com/nithinyanna10/omnisync"

