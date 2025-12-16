# Seigr Toolset Crypto v0.4.2

**Release Date:** November 27, 2025

## 🔒 Security Hardening Release

This release focuses on comprehensive security improvements, achieving **zero vulnerabilities** across all security audits (Bandit, pip-audit, Safety, CodeQL) with an overall **grade A+**.

---

## 🛡️ Security Fixes

### Fixed 22 Security Issues

**Bandit Audit** - Fixed 21 issues (1 medium, 20 low):

- ✅ **Code Injection** - Replaced `eval()` with `ast.literal_eval()` (CWE-78)
- ✅ **Weak Randomness** - Replaced `random` with `secrets` module in 6 locations (CWE-330)
- ✅ **Error Handling** - Fixed bare exception handlers in 8 files (CWE-703)
- ✅ **Subprocess Security** - Added timeouts and security justifications

**pip-audit** - Fixed 1 vulnerability:

- ✅ **HTTP Request Smuggling** - Upgraded h11 0.14.0 → 0.16.0 (GHSA-vqfr-h8mv-ghfj)
- ✅ **Dependencies** - Upgraded httpcore 1.0.6 → 1.0.9, httpx 0.27.2 → 0.28.1

**Safety Check** - 0 vulnerabilities (166 packages scanned)

**GitHub CodeQL** - Continuous monitoring with 0 errors

**Result**: **Zero vulnerabilities**, **Grade A+**

---

## 📚 Documentation Improvements

### Professional Organization

- **Restructured Documentation**:
  - Moved `CHANGELOG.md` and `USAGE.md` to `docs/`
  - Created `docs/audits/` for security reports
  - Cleaned root directory (12 files → 2 files)

### Optimized README

- **70% Reduction**: 622 lines → 189 lines
- **Transformed**: Monolithic document → Concise landing page
- **Organized**: Added documentation hub with proper links
- **Fixed**: Version consistency and misleading roadmap

### New Security Documentation

- **docs/SECURITY_AUDIT.md** - Comprehensive security audit report
  - Complete audit methodology and results
  - Security best practices
  - Audit schedule and maintenance plan

---

## 🔧 Code Quality

### Security Hardening

- **selective_decoys.py**: `eval()` → `ast.literal_eval()`
- **metadata_utils.py**: 3 random → secrets conversions
- **stc_api.py**: 3 random → secrets conversions for timing randomization
- **theme_manager.py**: Added subprocess timeouts
- **8 modules**: Specific exception handling with documentation

---

## 📊 What's Included

- **91.42% Test Coverage** - 246 passing tests
- **Zero Vulnerabilities** - All security audits passed
- **Production Ready** - Comprehensive testing and documentation
- **Post-Classical Crypto** - Lattice-based, no XOR/block ciphers

---

## 📦 Installation

### PyPI (Recommended)

```bash
pip install seigr-toolset-crypto==0.4.2
```

### From GitHub Release

```bash
# Download from: https://github.com/Seigr-lab/SeigrToolsetCrypto/releases/tag/v0.4.2

# Install wheel (recommended)
pip install seigr_toolset_crypto-0.4.2-py3-none-any.whl

# Or install source tarball
pip install seigr_toolset_crypto-0.4.2.tar.gz
```

---

## 🔗 Links

- **PyPI Package**: <https://pypi.org/project/seigr-toolset-crypto/>
- **Documentation**: <https://github.com/Seigr-lab/SeigrToolsetCrypto/blob/main/docs/>
- **Security Audit**: <https://github.com/Seigr-lab/SeigrToolsetCrypto/blob/main/docs/SECURITY_AUDIT.md>
- **Changelog**: <https://github.com/Seigr-lab/SeigrToolsetCrypto/blob/main/docs/CHANGELOG.md>

---

## ⚠️ Breaking Changes

None - This is a security and documentation maintenance release.

---

## 📈 Upgrade Guide

### From v0.4.1

```bash
pip install --upgrade seigr-toolset-crypto
```

No API changes, fully backward compatible.

---

## 🙏 Acknowledgments

Thanks to the security tools that made this audit possible:

- **Bandit** - Python security linter
- **pip-audit** - PyPI vulnerability scanner
- **Safety** - Dependency security scanner
- **GitHub CodeQL** - Continuous security monitoring

---

**Full Changelog**: <https://github.com/Seigr-lab/SeigrToolsetCrypto/blob/main/docs/CHANGELOG.md>
