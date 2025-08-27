#!/bin/bash

echo "🚀 Quilt GitHub Repository Setup"
echo "================================"
echo ""

echo "📋 Files ready to push:"
git status --porcelain
echo ""

echo "🔗 To connect to GitHub:"
echo "1. Go to https://github.com/new"
echo "2. Create a new repository named 'quilt' or 'quilt-indexer'"
echo "3. Make it Public or Private (your choice)"
echo "4. DON'T initialize with README, .gitignore, or license"
echo "5. Click 'Create repository'"
echo ""

echo "📝 After creating the repository, run these commands:"
echo "git remote add origin https://github.com/YOUR_USERNAME/quilt.git"
echo "git push -u origin main"
echo ""

echo "💡 Replace YOUR_USERNAME with your actual GitHub username"
echo ""

echo "🎯 Then you can deploy to Railway:"
echo "1. Go to https://railway.app"
echo "2. Connect your GitHub account"
echo "3. Deploy from the quilt repository"
echo "4. Get public URLs for your GitHub App"
echo ""

echo "✅ Your Quilt code is ready to deploy!"
