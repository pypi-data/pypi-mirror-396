# API Reference

Complete API documentation for STC.

## Quick Start

```python
import stc

# Encrypt
encrypted, metadata = stc.encrypt(b"secret", password="pass")

# Decrypt
data = stc.decrypt(encrypted, metadata, password="pass")
```

## File Encryption

```python
# Encrypt file
stc.encrypt_file("doc.pdf", "doc.enc", password="pass")
# Creates: doc.enc + doc.enc.meta

# Decrypt file
stc.decrypt_file("doc.enc", "output.pdf", password="pass")
```

## STCContext API

```python
from interfaces.api.stc_api import STCContext

# Initialize
ctx = STCContext('my-seed')

# Custom parameters
ctx = STCContext(
    seed="my-seed",
    lattice_size=256,
    depth=8,
    adaptive_difficulty='balanced'  # 'fast', 'balanced', 'paranoid'
)

# Encrypt
encrypted, metadata = ctx.encrypt(data, password="pass")

# Decrypt
data = ctx.decrypt(encrypted, metadata, password="pass")

# Hash
hash_value = ctx.hash(data)

# Derive key
key = ctx.derive_key(length=32)
```

## Security Profiles

```python
from core.profiles import get_profile_for_file

# Auto-detect profile
profile = get_profile_for_file("taxes.pdf")  # Returns: "financial"

# Use profile
ctx = STCContext("app", profile="credentials")
```

## CLI Commands

```bash
# Encrypt
stc-cli encrypt --input file.pdf --password "pass"

# Decrypt
stc-cli decrypt --input file.pdf.enc --password "pass"
```

## Next Steps

- [Getting Started](01-getting-started.md)
- [Advanced Usage](04-advanced-usage.md)
