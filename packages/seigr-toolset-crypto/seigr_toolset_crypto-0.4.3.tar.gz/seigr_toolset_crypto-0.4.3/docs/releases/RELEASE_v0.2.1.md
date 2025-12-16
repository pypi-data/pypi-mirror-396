# STC v0.2.1 Release Notes

## Release Information

- **Version**: 0.2.1
- **Release Date**: October 30, 2025
- **Status**: Alpha (Production-Ready with Enhanced Performance)
- **PyPI**: https://pypi.org/project/seigr-toolset-crypto/
- **GitHub**: https://github.com/Seigr-lab/SeigrToolsetCrypto

## What's New in v0.2.1

### 🚀 Performance Improvements

- **2x Faster Encryption**: Reduced from 1.33s to 0.63s average
- **2x Faster Decryption**: Reduced from 0.94s to 0.54s average  
- **Total Speedup**: 1.95x faster (2.27s → 1.17s for encrypt+decrypt)
- **Overall Progress**: 148x faster than v0.1.0 (173s → 1.17s)

### 📦 Metadata Compression

- **65% Reduction**: 786KB → 276KB without decoys
- **47% Reduction**: 786KB → 414KB with 3 decoys
- **Variable-length integer encoding (varint)**: LEB128-style encoding with zigzag for signed integers
- **Run-length encoding**: Consecutive zeros compressed with RLE marker

### 🎭 Decoy Vector Support

- **Now Enabled by Default**: `use_decoys=True` in encrypt() API
- **Full TLV Serialization**: Decoy vectors properly serialized in binary format
- **Password-Derived Index**: Real vector position hidden in PHE hash
- **3 Decoy Vectors**: Default obfuscation with configurable count (3-5)

### ⚡ Optimization Details

1. **Varint Encoding**: 
   - LEB128-style variable-length integers
   - Zigzag encoding for signed values: `(n << 1) ^ (n >> 63)`
   - Run-length encoding for zero runs (3+ zeros)
   
2. **CEL Optimizations**:
   - Audit frequency: every 100th operation (was every 50th in v0.2.0)
   - Chained timing entropy: every 200th operation (was every 100th)
   
3. **TLV Enhancements**:
   - New `TLV_TYPE_VECTOR` (0x10) for nested encrypted metadata
   - Recursive TLV serialization/deserialization
   - Proper vector extraction in decryption path

## Performance Comparison

| Version | Encryption | Decryption | Total | Metadata | vs v0.1.0 |
|---------|-----------|------------|-------|----------|-----------|
| v0.1.0  | 90s       | 83s        | 173s  | 4MB      | 1x        |
| v0.2.0  | 1.33s     | 0.94s      | 2.27s | 786KB    | 76x       |
| **v0.2.1** | **0.63s** | **0.54s** | **1.17s** | **276KB** | **148x** |

## Installation

### From PyPI

```bash
pip install seigr-toolset-crypto==0.2.1
```

### From Source

```bash
git clone https://github.com/Seigr-lab/SeigrToolsetCrypto.git
cd SeigrToolsetCrypto
git checkout v0.2.1
pip install -e .
```

### From GitHub Release

Download the wheel or tarball from the [Releases page](https://github.com/Seigr-lab/SeigrToolsetCrypto/releases/tag/v0.2.1):

```bash
pip install seigr_toolset_crypto-0.2.1-py3-none-any.whl
```

## Quick Start

### With Decoys (Default in v0.2.1)

```python
from interfaces.api.stc_api import STCContext

# Create context
ctx = STCContext('my-seed')

# Encrypt with password and decoys (default)
encrypted, metadata = ctx.encrypt(
    "Secret message",
    password="strong_password"
    # use_decoys=True by default, num_decoys=3
)

# Decrypt (automatically extracts real vector from decoys)
decrypted = ctx.decrypt(encrypted, metadata, password="strong_password")

print(decrypted)  # "Secret message"
print(f"Metadata size: {len(metadata)//1024}KB")  # ~414KB with 3 decoys
```

### Without Decoys (Faster, Smaller)

```python
# Disable decoys for minimum metadata size
encrypted, metadata = ctx.encrypt(
    "Data",
    password="pw",
    use_decoys=False
)

print(f"Metadata size: {len(metadata)//1024}KB")  # ~276KB without decoys
```

## Migration from v0.2.0

### API Changes

**No breaking changes** - v0.2.1 is fully backward compatible with v0.2.0:

```python
# v0.2.0 code works unchanged
from interfaces.api.stc_api import STCContext
ctx = STCContext('seed')
encrypted, metadata = ctx.encrypt("data", password="pw")
decrypted = ctx.decrypt(encrypted, metadata, password="pw")
```

**New default behavior**:
- `use_decoys=True` by default (was `False` in v0.2.0)
- To match v0.2.0 behavior, explicitly set `use_decoys=False`

### Metadata Format

- **Fully compatible**: v0.2.1 can decrypt v0.2.0 metadata
- **Automatic detection**: TLV format version detected automatically
- **Varint encoding**: Applied automatically to all new encryptions

## Known Limitations

- **Metadata size**: Still ~276-414KB (better than v0.2.0's 786KB, but not yet <100KB)
- **No streaming**: Files must fit in memory
- **Research-grade**: Not formally audited for production security

## Roadmap

### v0.2.2 (Next Patch)

- Dictionary encoding for repeated patterns (target <200KB metadata)
- Additional varint optimizations
- Performance target: <1s total time

### v0.3.0 (Next Minor)

- Streaming support for large files
- Migration utility (v0.1.x → v0.2.x)
- Adaptive parameters based on data size
- Metadata size <100KB target

### v1.0.0 (Stable)

- Performance: <500ms encrypt+decrypt
- Full test coverage (>95%)
- Complete documentation
- Security audit

## What's Secure

- ✅ Password-based encryption with MAC verification
- ✅ Tamper detection via PHE-based MAC
- ✅ Wrong password rejection
- ✅ Metadata encryption with ephemeral keys
- ✅ Decoy vector obfuscation (password-derived index)
- ✅ Varint encoding (no security impact, compression only)

## What's Not Yet Secure

- ⚠️ No formal security audit
- ⚠️ Research-grade implementation
- ⚠️ No streaming (side-channel timing possible)
- ⚠️ Metadata size reveals data was encrypted with STC

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

This release achieves a 1.95x performance improvement over v0.2.0 and 148x over v0.1.0, with 65% smaller metadata thanks to varint compression. Decoy vectors are now fully functional and enabled by default for enhanced obfuscation.

We hope STC v0.2.1 serves your post-classical cryptographic needs well. Your feedback and contributions are always welcome!
