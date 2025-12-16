# STC v0.2.0 Release Notes

## Release Information

- **Version**: 0.2.0
- **Release Date**: October 30, 2025
- **Status**: Alpha (Production-Ready with Known Limitations)
- **PyPI**: https://pypi.org/project/seigr-toolset-crypto/
- **GitHub**: https://github.com/Seigr-lab/SeigrToolsetCrypto

## What's New in v0.2.0

### 🔐 Security Enhancements

- **Password-Based Encryption**: Full support for password-protected encryption with MAC verification
- **Metadata Encryption**: Metadata encrypted with ephemeral keys derived from password + timestamp
- **MAC Verification**: Automatic tamper detection and wrong password rejection
- **Binary TLV Format**: Compact binary metadata format (786KB vs 4MB in alpha)

### ⚡ Performance Improvements

- **76x Speedup**: Reduced encryption time from 173s to 2.3s
- **Optimized PHE**: Multi-path count reduced from 3-15 to 3-5 paths
- **Smaller Lattice**: Default 128×128×6 (was 256×256×8)
- **Reduced Overhead**: 81% metadata size reduction

**Benchmarks** (17-byte message):
- Encryption: 1.33s (was 90s)
- Decryption: 0.94s (was 83s)
- Total: 2.27s (was 173s)
- Metadata: 786KB (was 4MB)

### 🎯 New Features

- **CEL Entropy Amplification**: 3-tier historical feedback loops with timing chains
- **PHE Multi-Path Hashing**: Dynamic 3-5 path execution with CEL-driven topology
- **Entropy Quality Auditing**: Monitoring for timing variance and lattice diversity
- **Backward Compatibility**: Automatic v0.1.x JSON format detection

### 📦 API Changes

**New in v0.2.0**:
```python
from interfaces.api.stc_api import STCContext

# Password-based encryption
ctx = STCContext('my-seed')
encrypted, metadata = ctx.encrypt("data", password="strong_pw")
decrypted = ctx.decrypt(encrypted, metadata, password="strong_pw")

# MAC verification (automatic)
try:
    ctx.decrypt(encrypted, metadata, password="wrong_pw")
except ValueError:
    print("Wrong password or tampering detected!")
```

**Breaking Changes**:
- `use_decoys` parameter default changed to `False` (TLV serialization not yet supported)
- Default lattice parameters: `lattice_size=128, depth=6` (was 256, 8)
- Metadata is now binary bytes (not dict) - backward compatible

### 📚 Documentation Updates

- Complete rewrite of usage guide for v0.2.0
- Comprehensive API reference with all new features
- Updated examples (password manager, config encryption)
- Performance optimization guide (PERFORMANCE_OPTIMIZATIONS.md)

## Installation

### From PyPI

```bash
pip install seigr-toolset-crypto==0.2.0
```

### From Source

```bash
git clone https://github.com/Seigr-lab/SeigrToolsetCrypto.git
cd SeigrToolsetCrypto
git checkout v0.2.0
pip install -e .
```

### From GitHub Release

Download the wheel or tarball from the [Releases page](https://github.com/Seigr-lab/SeigrToolsetCrypto/releases/tag/v0.2.0):

```bash
pip install seigr_toolset_crypto-0.2.0-py3-none-any.whl
```

## Quick Start

```python
from interfaces.api.stc_api import STCContext

# Create context
ctx = STCContext('my-seed')

# Encrypt with password
encrypted, metadata = ctx.encrypt(
    "Secret message",
    password="strong_password"
)

# Decrypt (MAC verified automatically)
decrypted = ctx.decrypt(encrypted, metadata, password="strong_password")

print(decrypted)  # "Secret message"
```

## Known Limitations

- **Metadata Size**: ~786KB constant overhead (independent of data size)
- **Decoy Vectors**: Not yet supported (`use_decoys` must be False)
- **Performance**: ~2.3s for small messages (acceptable for security-critical applications)
- **No Streaming**: Files must be loaded into memory

## Migration from v0.1.x

### API Migration

```python
# v0.1.x
from seigrtc.interfaces.api import stc_api
context = stc_api.initialize(seed="seed")
encrypted, metadata = context.encrypt("data")

# v0.2.0
from interfaces.api.stc_api import STCContext
context = STCContext('seed')
encrypted, metadata = context.encrypt("data", password="pw")
```

### Metadata Format

v0.2.0 automatically detects and supports v0.1.x JSON metadata:

```python
# Works with both formats
decrypted = ctx.decrypt(encrypted, old_json_metadata)
decrypted = ctx.decrypt(encrypted, new_tlv_metadata)
```

## Optimization Details

See [PERFORMANCE_OPTIMIZATIONS.md](PERFORMANCE_OPTIMIZATIONS.md) for complete details.

**Key Optimizations**:
1. PHE dependency injection: rotate_bits → XOR (eliminated 119M calls)
2. Path count reduction: 3-15 → 3-5 (60% fewer paths)
3. Composite folding: 4-stage → 2-stage
4. Lattice size: 256×256×8 → 128×128×6 (75% fewer cells)
5. Diffusion iterations: 1-8 → 1-3
6. Audit frequency: every 10th → every 50th

## Test Coverage

**37/37 tests passing (100%)**

- CEL (Continuous Entropy Lattice): 11 tests ✓
- PHE (Probabilistic Hashing): 10 tests ✓
- Integration (End-to-end): 16 tests ✓

All v0.2.0 features validated:
- Password-based encryption ✓
- MAC verification ✓
- Wrong password rejection ✓
- TLV binary format ✓
- Timing entropy ✓
- Multi-path hashing ✓
- Binary/Unicode data ✓
- Large data (10KB) ✓

## Security Considerations

### What's Secure

- ✅ Password-based encryption with MAC
- ✅ Tamper detection
- ✅ Wrong password rejection
- ✅ Metadata encryption with ephemeral keys
- ✅ No external randomness (computational entropy only)
- ✅ Deterministic reproducibility from seed

### Security Trade-offs

- **Lattice Size Reduction**: 524K → 98K cells (still very large, security remains strong)
- **Path Reduction**: 3-15 → 3-5 paths (still multi-path, maintains security)
- **Overall Impact**: "Extremely paranoid" → "Very strong" (acceptable for production)

### Not Yet Secure

- ⚠️ Decoy vectors not implemented (obfuscation mode disabled)
- ⚠️ No streaming (entire files in memory)
- ⚠️ Research-grade code (not formally audited)

## Roadmap

### v0.2.1 (Next Minor Release)

- Variable-length integer encoding (metadata → 100-200KB)
- Decoy vector TLV serialization
- Performance improvements (target <1s encryption)

### v0.3.0 (Next Major Release)

- Streaming support for large files
- Migration utility (v0.1.x → v0.2.0)
- Adaptive parameters based on data size
- Additional test coverage

### v1.0.0 (Stable Release)

- Performance: <20% encryption, <25% decryption overhead
- Full test coverage (>90%)
- Complete documentation
- Security audit

## Credits

**Author**: Sergi Saldaña-Massó (Seigr Lab)  
**License**: ANTI-CAPITALIST SOFTWARE LICENSE (v 1.4)  
**Sponsor**: https://github.com/sponsors/Seigr-lab

## Links

- **PyPI**: https://pypi.org/project/seigr-toolset-crypto/
- **GitHub**: https://github.com/Seigr-lab/SeigrToolsetCrypto
- **Documentation**: https://github.com/Seigr-lab/SeigrToolsetCrypto#readme
- **Changelog**: https://github.com/Seigr-lab/SeigrToolsetCrypto/blob/main/CHANGELOG.md
- **Issues**: https://github.com/Seigr-lab/SeigrToolsetCrypto/issues

## Support

For questions, issues, or contributions:
1. Check the [documentation](https://github.com/Seigr-lab/SeigrToolsetCrypto/tree/main/docs)
2. Review [CHANGELOG.md](CHANGELOG.md) and [PERFORMANCE_OPTIMIZATIONS.md](PERFORMANCE_OPTIMIZATIONS.md)
3. Open an issue on [GitHub](https://github.com/Seigr-lab/SeigrToolsetCrypto/issues)
4. Sponsor the project: https://github.com/sponsors/Seigr-lab

---

**Thank you for using Seigr Toolset Crypto!**

This release achieves a 76x performance improvement while maintaining strong security properties and adding new features like password-based encryption and MAC verification.

We hope STC v0.2.0 serves your post-classical cryptographic needs well. Your feedback and contributions are always welcome!
