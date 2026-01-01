#!/bin/bash
# Script to push project to GitHub
# Replace YOUR_USERNAME with your actual GitHub username

echo "======================================"
echo "Pushing to GitHub"
echo "======================================"
echo ""

# Step 1: Create the repository on GitHub first!
# Go to: https://github.com/new
echo "STEP 1: Create a new repository on GitHub"
echo "  1. Go to https://github.com/new"
echo "  2. Repository name: personal-collection-helper"
echo "  3. Description: A helper tool for managing Emby and Booklore media libraries"
echo "  4. Choose Public or Private"
echo "  5. DO NOT initialize with README/.gitignore/license"
echo "  6. Click Create repository"
echo ""
read -p "Press Enter after you've created the repository..."

# Step 2: Replace YOUR_USERNAME below with your GitHub username
REPO_URL="https://github.com/YOUR_USERNAME/personal-collection-helper.git"

echo ""
echo "STEP 2: Pushing to GitHub..."
echo ""

# Add remote
git remote add origin $REPO_URL

# Rename branch to main (optional, but recommended)
git branch -M main

# Push to GitHub
git push -u origin main

echo ""
echo "✓ Done! Your code is now on GitHub"
echo "  View at: $REPO_URL"
