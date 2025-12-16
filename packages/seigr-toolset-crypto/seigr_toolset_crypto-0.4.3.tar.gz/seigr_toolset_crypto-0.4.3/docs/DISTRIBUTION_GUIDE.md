# Distribution Guide - Seigr Toolset Crypto

This guide provides step-by-step instructions for creating and publishing new STC releases to PyPI and GitHub.

## Overview

The distribution process consists of:

1. **Pre-release preparation** - Update code, tests, and documentation
2. **Build distribution packages** - Create wheel and source distribution
3. **Publish to PyPI** - Upload packages to Python Package Index
4. **Create GitHub release** - Tag and publish on GitHub
5. **Post-release tasks** - Announcements and monitoring

## Step 1: Pre-Release Preparation

### 1.1 Update Version Number

Edit `setup.py` and update the version:

```python
setup(
    name="seigr-toolset-crypto",
    version="0.X.Y",  # Update this
    # ...
)
```

### 1.2 Update Documentation

**Required files to update**:

1. **CHANGELOG.md** - Add new version section:

   ```markdown
   ## [0.X.Y] - YYYY-MM-DD
   
   ### Added
   - New feature 1
   - New feature 2
   
   ### Changed
   - Changed behavior 1
   
   ### Fixed
   - Bug fix 1
   ```

2. **README.md** - Update:
   - Version badge: `[![Version](https://img.shields.io/badge/version-0.X.Y-blue)]`
   - Installation instructions: `pip install seigr-toolset-crypto==0.X.Y`
   - Performance numbers (if applicable)
   - Feature list (if new features added)

3. **RELEASE_v0.X.Y.md** - Create new release notes:

   ```bash
   # Copy from previous release and update
   cp RELEASE_v0.2.1.md RELEASE_v0.X.Y.md
   # Edit RELEASE_v0.X.Y.md with new version details
   ```

### 1.3 Update Examples and Tests

- Update examples to use new features (if applicable)
- Ensure all tests pass with new version
- Update test assertions for new behavior

### 1.4 Pre-Distribution Checklist

**Before building packages, verify**:

- [ ] Version bumped in `setup.py`
- [ ] CHANGELOG.md updated with version section
- [ ] README.md updated (version badge, installation, features)
- [ ] RELEASE_v0.X.Y.md created
- [ ] All tests passing: `python -m pytest tests/ -v`
- [ ] Examples working correctly
- [ ] No `use_decoys=False` or security-disabling code (unless intentional)
- [ ] Documentation reflects actual defaults and behavior

## Step 2: Build Distribution Packages

### 2.1 Clean Previous Builds

Remove old distribution files:

```bash
cd /e/SEIGR\ DEV/SeigrToolsetCrypto

# Remove old build artifacts
rm -rf build/
rm -rf dist/
rm -rf *.egg-info/
```

### 2.2 Install Build Tools

Ensure you have the latest build tools:

```bash
pip install --upgrade pip
pip install --upgrade build twine
```

### 2.3 Build Packages

Build wheel and source distribution:

```bash
# Build both wheel and source distribution
python -m build

# This creates:
# - dist/seigr_toolset_crypto-0.X.Y-py3-none-any.whl (wheel)
# - dist/seigr_toolset_crypto-0.X.Y.tar.gz (source distribution)
```

### 2.4 Verify Packages

Check packages are valid:

```bash
# Verify with twine
python -m twine check dist/*

# Should output:
# Checking dist/seigr_toolset_crypto-0.X.Y-py3-none-any.whl: PASSED
# Checking dist/seigr_toolset_crypto-0.X.Y.tar.gz: PASSED
```

### 2.5 Test Installation Locally

Test installing the wheel locally:

```bash
# Create test virtual environment
python -m venv test_env
source test_env/bin/activate  # On Windows: test_env\Scripts\activate

# Install from local wheel
pip install dist/seigr_toolset_crypto-0.X.Y-py3-none-any.whl

# Test import
python -c "from interfaces.api.stc_api import STCContext; print('OK')"

# Test basic functionality
python -c "
from interfaces.api.stc_api import STCContext
ctx = STCContext('test')
enc, meta = ctx.encrypt('test', password='pw')
dec = ctx.decrypt(enc, meta, password='pw')
assert dec == 'test'
print('Installation test PASSED')
"

# Deactivate and cleanup
deactivate
rm -rf test_env
```

### 2.6 Build Checklist

- [ ] Old build artifacts cleaned
- [ ] Build tools updated
- [ ] Packages built successfully
- [ ] `twine check` passed
- [ ] Local installation test passed
- [ ] Both wheel and tarball created in `dist/`

## Step 3: Publishing to PyPI

### 3.1 Setup PyPI Credentials

**Option A: API Token (Recommended)**

1. Go to <https://pypi.org/manage/account/token/>
2. Create new API token for the project
3. Save token securely (you'll only see it once)

**Option B: Username/Password**

Use your PyPI username and password (less secure, not recommended)

### 3.2 Test on TestPyPI First (Recommended)

Upload to TestPyPI before production:

```bash
# Upload to TestPyPI
python -m twine upload dist/*
python -m twine upload --repository testpypi dist/*

# You'll be prompted for credentials:
# username: __token__
# password: pypi-YOUR-TEST-API-TOKEN

# Test installation from TestPyPI
pip install --index-url https://test.pypi.org/simple/ --no-deps seigr-toolset-crypto==0.X.Y

# Test it works
python -c "from interfaces.api.stc_api import STCContext; print('TestPyPI install OK')"
```

### 3.3 Upload to Production PyPI

Once TestPyPI upload works, upload to production:

```bash
# Upload to PyPI with API token
python -m twine upload dist/* --username __token__ --password pypi-YOUR-API-TOKEN

# Or let it prompt you for credentials
python -m twine upload dist/*
```

### 3.4 Verify PyPI Upload

After successful upload, verify:

- [ ] Package appears at <https://pypi.org/project/seigr-toolset-crypto/>
- [ ] Version shows as 0.X.Y
- [ ] README renders correctly on PyPI page
- [ ] All project URLs work (Homepage, Documentation, Source, etc.)
- [ ] Installation works: `pip install seigr-toolset-crypto==0.X.Y`
- [ ] Metadata is correct (author, license, classifiers)

### 3.5 Test Installation from PyPI

Create fresh environment and test:

```bash
# Create clean test environment
python -m venv pypi_test
source pypi_test/bin/activate  # Windows: pypi_test\Scripts\activate

# Install from PyPI
pip install seigr-toolset-crypto==0.X.Y

# Verify installation
python -c "
from interfaces.api.stc_api import STCContext
ctx = STCContext('test')
enc, meta = ctx.encrypt('Hello', password='pw')
dec = ctx.decrypt(enc, meta, password='pw')
assert dec == 'Hello'
print('PyPI installation VERIFIED ✓')
"

# Cleanup
deactivate
rm -rf pypi_test
```

## Step 4: Publishing to GitHub

### 4.1 Commit All Changes

Commit all version-related changes:

```bash
cd /e/SEIGR\ DEV/SeigrToolsetCrypto

# Check what's changed
git status

# Add all updated files
git add .

# Commit with descriptive message
git commit -m "Release v0.X.Y: <Brief description>

<Detailed changes>
- Feature 1
- Feature 2
- Bug fix 1

See RELEASE_v0.X.Y.md for complete details."

# Push to main
git push origin main
```

### 4.2 Create Git Tag

Create annotated tag for the release:

```bash
# Create annotated tag
git tag -a v0.X.Y -m "STC v0.X.Y - <Release Title>

Major Features:
- Feature 1
- Feature 2

Performance:
- Metric 1
- Metric 2

See RELEASE_v0.X.Y.md for complete details."

# Push tag to GitHub
git push origin v0.X.Y
```

### 4.3 Create GitHub Release

**Navigate to**: <https://github.com/Seigr-lab/SeigrToolsetCrypto/releases/new>

**Fill in release form**:

- **Choose a tag**: v0.X.Y (select the tag you just pushed)
- **Release title**: STC v0.X.Y - <Release Title>
- **Description**: Use content from RELEASE_v0.X.Y.md or write summary

**Example description template**:

```markdown
## 🚀 STC v0.X.Y Released!

<Brief description of this release>

### Highlights

- 🎯 **Feature 1**: Description
- 🔐 **Feature 2**: Description
- ⚡ **Performance**: Numbers

### Installation

```bash
pip install seigr-toolset-crypto==0.X.Y
```

### Quick Start

```python
from interfaces.api.stc_api import STCContext

ctx = STCContext('my-seed')
encrypted, metadata = ctx.encrypt("Secret", password="pw")
decrypted = ctx.decrypt(encrypted, metadata, password="pw")
```

### What's New

- New feature 1 with details
- New feature 2 with details
- Performance improvements

### Breaking Changes (if any)

- Change 1
- Change 2

See [RELEASE_v0.X.Y.md](RELEASE_v0.X.Y.md) for complete release notes.

### Documentation

- [README](README.md) - Getting started
- [CHANGELOG](CHANGELOG.md) - Version history
- [Performance Guide](docs/PERFORMANCE.md) - Performance details

---

**Full Changelog**: <https://github.com/Seigr-lab/SeigrToolsetCrypto/blob/main/CHANGELOG.md>

```

**Attach Distribution Files**:
- [x] Upload `dist/seigr_toolset_crypto-0.X.Y-py3-none-any.whl`
- [x] Upload `dist/seigr_toolset_crypto-0.X.Y.tar.gz`

**Release Options**:
- [x] Set as the latest release (for stable releases)
- [ ] Set as a pre-release (for alpha/beta/rc versions)

Click **Publish release**

### 4.4 Verify GitHub Release

After publishing, verify:

- [ ] Release appears at https://github.com/Seigr-lab/SeigrToolsetCrypto/releases
- [ ] Tag v0.X.Y is visible in repository
- [ ] Release notes render correctly
- [ ] Distribution files are downloadable
- [ ] Links in release notes work

## Step 5: Post-Release Tasks

### 5.1 Update Project Documentation

If you have a separate documentation site or wiki, update it with the new version.

### 5.2 Announcements

**Example announcement for social media/forums**:

```

🚀 STC v0.X.Y Released!

Seigr Toolset Crypto <brief description>:

<emoji> Feature 1
<emoji> Feature 2
<emoji> Performance improvements

Install: pip install seigr-toolset-crypto==0.X.Y

<https://github.com/Seigr-lab/SeigrToolsetCrypto>
<https://pypi.org/project/seigr-toolset-crypto/>

# cryptography #python #security #opensource

```

### 5.3 Update Project Management

- [ ] Close issues resolved in this version
- [ ] Update project board/milestones
- [ ] Create milestone for next version
- [ ] Update roadmap in README or docs

### 5.4 Monitor for Issues

After release, monitor:
- GitHub issues for bug reports
- PyPI download stats
- User feedback
- Installation problems

### 5.5 Plan Next Release

Review roadmap and plan next version:
- What features for next minor version?
- What bugs need fixing for patch version?
- Update CHANGELOG.md with "Unreleased" section

## Rollback Procedure (Emergency)

If critical issues are discovered after release:

### PyPI Rollback

**Note**: You CANNOT delete releases from PyPI, but you can "yank" them:

```bash
# Yank the problematic version (makes it hidden but still installable if explicitly requested)
pip install twine
twine yank seigr-toolset-crypto 0.X.Y -r pypi --reason "Critical bug: <description>"
```

Then release a patch version (0.X.Y+1) with the fix.

### GitHub Rollback

```bash
# Delete the GitHub release (via web UI)
# Go to: https://github.com/Seigr-lab/SeigrToolsetCrypto/releases
# Click on release → Edit → Delete release

# Delete the tag locally and remotely
git tag -d v0.X.Y
git push origin :refs/tags/v0.X.Y

# If you need to revert commits
git revert <commit-hash>
git push origin main
```

## Complete Distribution Checklist

Use this checklist for each release:

### Pre-Release

- [ ] Version bumped in setup.py
- [ ] CHANGELOG.md updated
- [ ] README.md updated (version badge, installation)
- [ ] RELEASE_v0.X.Y.md created
- [ ] All tests passing
- [ ] Examples working
- [ ] Security features enabled (not bypassed)

### Build Packages

- [ ] Old build artifacts cleaned
- [ ] Build tools updated (`pip install --upgrade build twine`)
- [ ] Packages built: `python -m build`
- [ ] Twine check passed: `python -m twine check dist/*`
- [ ] Local installation test passed
- [ ] Both wheel (.whl) and tarball (.tar.gz) created

### PyPI Distribution

- [ ] TestPyPI upload successful (optional but recommended)
- [ ] Production PyPI upload successful
- [ ] Package visible on pypi.org
- [ ] Installation from PyPI works
- [ ] README renders correctly on PyPI

### GitHub Distribution  

- [ ] All changes committed and pushed
- [ ] Git tag created and pushed
- [ ] GitHub release created
- [ ] Distribution files attached to release
- [ ] Release notes complete and accurate

### Post-Release

- [ ] GitHub release verified
- [ ] PyPI package verified
- [ ] Announcements posted (if applicable)
- [ ] Issues/milestones updated
- [ ] Next version planned

## Troubleshooting

### Common Issues

**Build fails with "No module named 'build'"**:

```bash
pip install --upgrade build
```

**Twine upload fails with authentication error**:

- Verify your API token is correct
- Ensure token has upload permissions
- Check you're using `__token__` as username

**Package appears on PyPI but won't install**:

- Check package name spelling
- Verify version number
- Try: `pip install --upgrade --force-reinstall seigr-toolset-crypto==0.X.Y`

**GitHub release tag not appearing**:

```bash
# Verify tag exists locally
git tag -l

# Push tag explicitly
git push origin v0.X.Y
```

## Reference Links

For more information:

1. Check twine documentation: <https://twine.readthedocs.io/>
2. Python packaging guide: <https://packaging.python.org/>
3. GitHub releases: <https://docs.github.com/en/repositories/releasing-projects-on-github>
4. PyPI help: <https://pypi.org/help/>

---

## Quick Reference: Full Release Process

```bash
# 1. Update version in setup.py, docs, CHANGELOG.md, create RELEASE_v0.X.Y.md

# 2. Clean and build
rm -rf build/ dist/ *.egg-info/
python -m build
python -m twine check dist/*

# 3. Test locally
pip install dist/*.whl
python -c "from interfaces.api.stc_api import STCContext; print('OK')"

# 4. Upload to PyPI
python -m twine upload dist/* --username __token__ --password pypi-YOUR-TOKEN

# 5. Git commit, tag, and push
git add .
git commit -m "Release v0.X.Y: Description"
git push origin main
git tag -a v0.X.Y -m "Release notes"
git push origin v0.X.Y

# 6. Create GitHub release at:
# https://github.com/Seigr-lab/SeigrToolsetCrypto/releases/new
# - Select tag v0.X.Y
# - Add release notes
# - Attach dist/*.whl and dist/*.tar.gz
# - Publish
```

---

**You're ready to distribute new STC versions! 🎉**
