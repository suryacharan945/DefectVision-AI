# DefectVision AI — Publication Commands Preflight Review

**Document Version:** 1.0.0  
**Status:** DRAFT / PENDING EXPLICIT USER AUTHORIZATION  
**Execution Status:** **NO COMMANDS EXECUTED**  

---

## 1. Scope and Safety Declaration

This document specifies the exact sequence of commands required to initialize, verify, and publish the verified clean-room export of DefectVision AI.

> [!IMPORTANT]
> **Zero Remote Execution Notice:**  
> In compliance with the project governance mandate, no Git remote operations, no repository creations, and no network pushes have been or will be executed by the automated agent. All commands below are presented for human operator review and manual execution.

---

## 2. Phase 1: Local Clean Repository Initialization (Automated / Verified Locally)

The following commands are executed inside the isolated export directory `C:\Users\surya\Downloads\DefectVisionAI-CleanExport` to establish the new Git history:

```bash
# 1. Navigate to isolated clean export directory
cd "C:\Users\surya\Downloads\DefectVisionAI-CleanExport"

# 2. Initialize fresh, independent Git repository
git init

# 3. Configure local repository identity
git config user.name "DefectVision AI Release Team"
git config user.email "release@defectvision.local"

# 4. Stage all approved files (strict allowlist contents only)
git add .

# 5. Create initial clean release commit
git commit -m "feat: initial clean-room open-source release of DefectVision AI (v1.0.0-clean)"

# 6. Ensure default branch is named 'main'
git branch -M main
```

### Pre-Push Verification Checklist:
```bash
# Verify exactly 1 commit exists in history
git log --oneline
# Expected output: <clean-sha> feat: initial clean-room open-source release of DefectVision AI (v1.0.0-clean)

# Verify zero remote origins are configured
git remote -v
# Expected output: (empty)

# Verify clean working tree
git status
# Expected output: nothing to commit, working tree clean

# Verify zero dangling tags
git tag -l
# Expected output: (empty)
```

---

## 3. Phase 2: Remote Publication Options (Requires User Command)

When the user decides to publish the clean repository to GitHub, one of the following pathways should be chosen:

### Option 2A: Publish to Fresh GitHub Repository (Recommended)
This approach avoids colliding with the existing repository and allows safe migration:

```bash
# Using GitHub CLI (authenticated operator):
gh repo create DefectVisionAI-OpenSource --public --source=. --remote=origin --push

# OR Manual Setup via Web:
# 1. Create a new empty repository at https://github.com/new named 'DefectVisionAI-OpenSource'
# 2. Link and push:
git remote add origin https://github.com/suryacharan945/DefectVisionAI-OpenSource.git
git push -u origin main
```

### Option 2B: Replace Existing Repository (Requires Danger Zone Action)
If the user desires the exact URL `https://github.com/suryacharan945/DefectVision-AI`:

```bash
# Step 1: Human operator logs into GitHub web interface.
# Step 2: Navigate to https://github.com/suryacharan945/DefectVision-AI/settings
# Step 3: Danger Zone -> 'Rename repository' to 'DefectVision-AI-historical-private' -> 'Change visibility' to Private.
# Step 4: Create a new empty public repository named 'DefectVision-AI'.
# Step 5: Push the clean repository:
cd "C:\Users\surya\Downloads\DefectVisionAI-CleanExport"
git remote add origin https://github.com/suryacharan945/DefectVision-AI.git
git push -u origin main
```

---

## 4. Post-Publication Validation Commands

Once pushed to GitHub, verify public cloneability and zero-weight operation:

```bash
# 1. Clone into temporary test directory
git clone https://github.com/<owner>/<repo>.git test-clone
cd test-clone

# 2. Verify total clone size is lightweight (< 15 MB)
git count-objects -vH

# 3. Verify zero binary weights are present
find . -name "*.npy" -o -name "*.pt" -o -name "*.pth" -o -name "*.faiss"
# Expected output: (empty)

# 4. Start backend in zero-weight mode
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
python -m uvicorn DefectVisionAI.app:app --port 8000
# Expected: Server starts on port 8000, logs weights-pending info, zero crashes.
```
