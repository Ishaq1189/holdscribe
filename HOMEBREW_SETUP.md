# HoldScribe Homebrew Setup Guide

## 📦 Step-by-Step Homebrew Publication

### 1. Create GitHub Repository
```bash
# Navigate to your project
cd /Users/ishaq1189/Documents/mygithub/voice-transcribe

# Initialize git (if not already done)
git init
git add .
git commit -m "Initial commit: HoldScribe v1.0.0"

# Create repo on GitHub and push
git remote add origin https://github.com/ishaq1189/holdscribe.git
git branch -M main
git push -u origin main
```

### 2. Create Release
```bash
# Tag the release
git tag v1.0.0
git push origin v1.0.0
```

This will trigger the GitHub Actions workflow to create a release automatically.

### 3. Get SHA256 for Homebrew Formula
After the release is created, download the source tarball and calculate SHA256:
```bash
# The GitHub Actions workflow will output the SHA256
# Update homebrew-formula.rb with the correct SHA256
```

### 4. Update Homebrew Formula
Replace placeholders in `homebrew-formula.rb`:
- `ishaq1189` → your actual GitHub username
- `PLACEHOLDER_SHA256` → actual SHA256 from release

### 5. Create Homebrew Tap (Personal Tap)
```bash
# Create a new repository named 'homebrew-tap'
# on GitHub: ishaq1189/homebrew-tap

# Clone it locally
git clone https://github.com/ishaq1189/homebrew-tap.git
cd homebrew-tap

# Copy the formula
cp ../holdscribe/homebrew-formula.rb Formula/holdscribe.rb

# Commit and push
git add Formula/holdscribe.rb
git commit -m "Add holdscribe formula"
git push origin main
```

### 6. Test Installation
```bash
# Add your tap
brew tap ishaq1189/tap

# Install your formula
brew install holdscribe

# Test it works
holdscribe --help
```

### 7. Submit to Official Homebrew (Optional)
For inclusion in the main Homebrew repository:
```bash
# Fork homebrew-core
# Create PR with your formula in Formula/holdscribe.rb
```

## 🎯 Users Can Install With:

**From your personal tap:**
```bash
brew tap ishaq1189/tap
brew install holdscribe
```

**Or directly:**
```bash
brew install ishaq1189/tap/holdscribe
```

## 📋 Checklist
- [ ] Create GitHub repository
- [ ] Push code with all files
- [ ] Create v1.0.0 release
- [ ] Update homebrew-formula.rb with correct SHA256
- [ ] Create homebrew-tap repository
- [ ] Copy formula to tap
- [ ] Test installation
- [ ] Document usage

## 🚀 After Setup
Users can simply run:
```bash
brew install ishaq1189/tap/holdscribe
holdscribe  # Starts with Right Alt key
```

Hold Right Alt, speak, release to transcribe! 🎤