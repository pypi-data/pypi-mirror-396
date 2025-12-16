# Homebrew Formula Automation Setup

This document explains the automated Homebrew formula update system.

## How It Works

When you create a GitHub Release in the main `tui-delta` repository:

1. **Release workflow triggers** (`.github/workflows/update-homebrew.yml`)
   - Extracts version from tag (e.g., `v0.2.0` → `0.2.0`)
   - Sends repository_dispatch event to `homebrew-tui-delta` repo

2. **Homebrew tap receives trigger** (`homebrew-tui-delta/.github/workflows/update-formula.yml`)
   - Waits for PyPI release (up to 10 minutes)
   - Fetches package URL and SHA256 from PyPI
   - Updates `Formula/tui-delta.rb` automatically
   - Creates a Pull Request for review

3. **You review and merge the PR**
   - Check that SHA256 matches PyPI
   - Optionally test locally
   - Merge when ready

4. **Users get the update**
   - `brew upgrade tui-delta` pulls the new version

## Setup Required

### 1. Configure Homebrew Repository Settings

Enable GitHub Actions to create pull requests:

1. Go to: https://github.com/JeffreyUrban/homebrew-tui-delta/settings/actions
2. Navigate to **Actions** → **General**
3. Scroll to **Workflow permissions**
4. Check ✅ **"Allow GitHub Actions to create and approve pull requests"**
5. Click **Save**

### 2. Create GitHub Personal Access Token (Fine-Grained)

You need to create a fine-grained Personal Access Token (PAT) to allow the main repo to trigger the homebrew repo.

#### Creating the Token:

1. Go to: https://github.com/settings/personal-access-tokens/new
2. **Token name**: "Homebrew formula updater"
3. **Expiration**: 1 year (recommended - set calendar reminder to renew)
4. **Repository access**: Select "Only select repositories"
   - Choose: `JeffreyUrban/homebrew-tui-delta`
5. **Permissions** → **Repository permissions**:
   - **Contents**: Read and write
   - **Metadata**: Read-only (automatically selected)
   - **Pull requests**: Read and write
   - **Workflows**: Read and write
6. Click **Generate token**
7. **Copy the token immediately** (you won't see it again)

#### Adding the Token as a Secret:

1. Go to the main tui-delta repo: https://github.com/JeffreyUrban/tui-delta/settings/secrets/actions
2. Click **New repository secret**
3. **Name**: `HOMEBREW_UPDATE_TOKEN`
4. **Secret**: Paste the token you just created
5. Click **Add secret**

## Testing the Workflow

### Dry Run (Without Actually Releasing)

You can manually trigger the homebrew update workflow:

1. Go to: https://github.com/JeffreyUrban/homebrew-tui-delta/actions/workflows/update-formula.yml
2. Click "Run workflow"
3. Enter the version to test (e.g., `0.1.1`)
4. Click "Run workflow"

This will create a test PR without needing a full release.

### Full Release Flow

1. **Prepare release**:
   - Update CHANGELOG.md
   - Commit changes
   - Push to main

2. **Create GitHub Release**:
   - Go to: https://github.com/JeffreyUrban/tui-delta/releases/new
   - Tag: `v0.2.0` (or next version)
   - Title: `v0.2.0`
   - Description: Copy from CHANGELOG.md
   - Click "Publish release"

3. **Automated steps happen**:
   - Release workflow publishes to PyPI
   - Update-homebrew workflow triggers
   - Homebrew tap waits for PyPI
   - PR is created in homebrew-tui-delta

4. **Review and merge**:
   - Check the PR in homebrew-tui-delta
   - Test if desired: `brew install --build-from-source jeffreyurban/JeffreyUrban/tui-delta`
   - Merge the PR

## Workflow Files

### Main Repo (`tui-delta`)
- `.github/workflows/update-homebrew.yml` - Triggers on release, sends dispatch to tap

### Homebrew Tap (`homebrew-tui-delta`)
- `.github/workflows/update-formula.yml` - Receives trigger, updates formula, creates PR

## Troubleshooting

### "Workflow not found" error

The `update-homebrew.yml` workflow references a secret. Make sure:
1. The secret `HOMEBREW_UPDATE_TOKEN` exists in the main repo
2. The token has the correct permissions:
   - Contents: Read and write
   - Metadata: Read-only
   - Pull requests: Read and write
   - Workflows: Read and write
3. The token hasn't expired
4. The token has access to the `homebrew-tui-delta` repository

### "PyPI timeout" error

The workflow waits 10 minutes for PyPI. If your PyPI release is slow:
1. Check that the release actually completed
2. The workflow will fail gracefully with an error message
3. You can manually re-run the workflow once PyPI is ready

### PR not created

Check the Actions tab in homebrew-tui-delta:
1. https://github.com/JeffreyUrban/homebrew-tui-delta/actions
2. Look for failed runs
3. Check the logs for errors

Common causes:
- **Missing permission**: Ensure "Allow GitHub Actions to create and approve pull requests" is enabled in the homebrew repo settings (see Setup step 1)
- **Token permissions**: Verify the token has Pull requests: Read and write permission
- **Formula syntax error**: Check that the formula file has valid Ruby syntax

## Manual Fallback

If automation fails, you can always update manually:

```bash
# Get new SHA256
curl -s https://pypi.org/pypi/tui-delta/json | jq -r '.releases["0.2.0"][] | select(.packagetype=="sdist")'

# Edit Formula/tui-delta.rb
# - Update url
# - Update sha256
# - Update version in test

# Test
brew install --build-from-source ./Formula/tui-delta.rb
brew test tui-delta

# Commit and push
git add Formula/tui-delta.rb
git commit -m "chore: Update tui-delta to v0.2.0"
git push
```

## Benefits

✅ **Automated**: Formula updates automatically on release
✅ **Safe**: Creates PR for review, not direct merge
✅ **Verified**: Waits for PyPI confirmation before proceeding
✅ **Traceable**: Clear audit trail via PRs
✅ **No manual SHA256**: Fetched directly from PyPI
