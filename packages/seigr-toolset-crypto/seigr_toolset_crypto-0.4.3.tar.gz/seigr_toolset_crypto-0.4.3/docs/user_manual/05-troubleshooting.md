# Chapter 5: Troubleshooting

Common problems, error messages, and solutions for STC v0.3.0.

## What You'll Learn

- ✓ How to fix common errors
- ✓ Understanding error messages
- ✓ Debugging tips
- ✓ Frequently asked questions
- ✓ When to ask for help

---

## Common Errors and Solutions

### Error: "MAC verification failed"

**What it looks like:**

```python
>>> decrypted = ctx.decrypt(encrypted, metadata, password="wrong_pw")
ValueError: MAC verification failed
```

**What it means:** Either the password is wrong OR the data has been tampered with.

**Solutions:**

1. **Check your password:**

```python
# Try again with correct password
try:
    decrypted = ctx.decrypt(encrypted, metadata, password="correct_password")
    print("✓ Decryption successful!")
except ValueError:
    print("❌ Password is still wrong")
```

2. **Check if data is corrupted:**

```python
import hashlib

# Check file integrity
with open('encrypted_file.enc', 'rb') as f:
    data = f.read()
    file_hash = hashlib.sha256(data).hexdigest()
    print(f"File hash: {file_hash}")

# If hash changes between reads, file is corrupted
```

3. **Verify metadata is correct:**

```python
import pickle

# Load and inspect metadata
with open('file.enc.meta', 'rb') as f:
    metadata = pickle.load(f)
    
# Check metadata structure
print(f"Metadata keys: {list(metadata.keys())}")
# Should have: cel_snapshots, phe_state, pcf_state, etc.
```

---

### Error: "No such file or directory"

**What it looks like:**

```python
>>> with open('file.enc', 'rb') as f:
FileNotFoundError: [Errno 2] No such file or directory: 'file.enc'
```

**Solutions:**

1. **Check file path:**

```python
import os

# Check if file exists
if os.path.exists('file.enc'):
    print("✓ File exists")
else:
    print("❌ File not found")
    print(f"Current directory: {os.getcwd()}")
    print(f"Files here: {os.listdir('.')}")
```

2. **Use absolute paths:**

```python
# Instead of relative path
with open('file.enc', 'rb') as f:
    data = f.read()

# Use absolute path
import os
file_path = os.path.abspath('file.enc')
with open(file_path, 'rb') as f:
    data = f.read()
```

3. **List files to find it:**

```python
import os

# Search for .enc files
for root, dirs, files in os.walk('.'):
    for file in files:
        if file.endswith('.enc'):
            print(f"Found: {os.path.join(root, file)}")
```

---

### Error: "Entropy quality too low"

**What it looks like:**

```python
>>> encrypted, metadata = ctx.encrypt("data", password="pw")
ValueError: Entropy quality too low for encryption
```

**Solution:**

```python
# Check entropy health
health = ctx.get_entropy_health()
print(f"Quality score: {health['quality_score']:.2f}")
print(f"Status: {health['status']}")

# Refresh entropy
ctx.cel.update()
print("✓ Entropy refreshed")

# Now try encrypting again
encrypted, metadata = ctx.encrypt("data", password="pw")
print("✓ Encryption successful!")
```

---

### Error: "Context mismatch"

**What it looks like:**

```python
# Encrypted with context
encrypted, metadata = ctx.encrypt(
    "data",
    password="pw",
    context_data={'user': 'alice'}
)

# Decrypt without context - produces garbage or fails
decrypted = ctx.decrypt(encrypted, metadata, password="pw")
# Result: gibberish or exception
```

**Solution:**

```python
# MUST use same context for decryption
decrypted = ctx.decrypt(
    encrypted,
    metadata,
    password="pw",
    context_data={'user': 'alice'}  # Same context!
)
print("✓ Decryption successful!")
```

**How to avoid:**

```python
# Save context data with metadata
import pickle

context_data = {'user': 'alice', 'role': 'admin'}

encrypted, metadata = ctx.encrypt(
    "data",
    password="pw",
    context_data=context_data
)

# Save both metadata AND context data
with open('file.enc.meta', 'wb') as f:
    pickle.dump({
        'metadata': metadata,
        'context': context_data  # Save context too!
    }, f)

# Load both when decrypting
with open('file.enc.meta', 'rb') as f:
    saved = pickle.load(f)
    metadata = saved['metadata']
    context_data = saved['context']

decrypted = ctx.decrypt(encrypted, metadata, password="pw", context_data=context_data)
```

---

### Error: "Seed mismatch"

**What it looks like:**

```python
# Encrypt with one seed
ctx1 = STCContext('seed-A')
encrypted, metadata = ctx1.encrypt("data", password="pw")

# Decrypt with different seed - produces garbage!
ctx2 = STCContext('seed-B')
decrypted = ctx2.decrypt(encrypted, metadata, password="pw")
# Result: gibberish or exception
```

**Solution:**

```python
# Use SAME seed for encryption and decryption!
ctx = STCContext('seed-A')  # Same seed as encryption

decrypted = ctx.decrypt(encrypted, metadata, password="pw")
print("✓ Decryption successful!")
```

**How to avoid:**

```python
# Save seed identifier with metadata (NOT the actual seed!)
import pickle
import hashlib

seed = 'my-unique-seed'
seed_hash = hashlib.sha256(seed.encode()).hexdigest()[:16]

ctx = STCContext(seed)
encrypted, metadata = ctx.encrypt("data", password="pw")

# Save seed hash (not seed itself!) with metadata
with open('file.enc.meta', 'wb') as f:
    pickle.dump({
        'metadata': metadata,
        'seed_hash': seed_hash  # Identifier only
    }, f)

# When decrypting, verify seed
with open('file.enc.meta', 'rb') as f:
    saved = pickle.load(f)
    expected_hash = saved['seed_hash']
    
current_hash = hashlib.sha256(seed.encode()).hexdigest()[:16]

if current_hash != expected_hash:
    print("❌ Wrong seed!")
else:
    ctx = STCContext(seed)
    decrypted = ctx.decrypt(saved['metadata'], encrypted, password="pw")
```

---

### Error: "Memory Error"

**What it looks like:**

```python
>>> with open('huge_file.bin', 'rb') as f:
>>>     data = f.read()
MemoryError
```

**Solution: Use streaming**

```python
# Instead of loading entire file
with open('huge_file.bin', 'rb') as f:
    data = f.read()  # Memory error if file is too large!

encrypted, metadata = ctx.encrypt(data, password="pw")

# Use streaming for large files
metadata = ctx.encrypt_stream(
    input_path='huge_file.bin',
    output_path='huge_file.enc',
    password="pw",
    chunk_size=1048576  # 1 MB chunks
)
print("✓ Large file encrypted with constant memory!")
```

---

### Error: "Pickle Error"

**What it looks like:**

```python
>>> with open('file.enc.meta', 'rb') as f:
>>>     metadata = pickle.load(f)
pickle.UnpicklingError: invalid load key, '\x00'
```

**Solutions:**

1. **Metadata file is corrupted:**

```python
import os

# Check file size
size = os.path.getsize('file.enc.meta')
if size == 0:
    print("❌ Metadata file is empty!")
elif size < 1000:
    print("⚠️ Metadata file is suspiciously small")
else:
    print(f"✓ Metadata file size: {size} bytes")
```

2. **Wrong file mode:**

```python
# ❌ Wrong - text mode
with open('file.enc.meta', 'r') as f:  # Wrong!
    metadata = pickle.load(f)

# ✓ Correct - binary mode
with open('file.enc.meta', 'rb') as f:  # Correct!
    metadata = pickle.load(f)
```

3. **File was not saved with pickle:**

```python
# If you accidentally saved as text or JSON
import json

try:
    # Try pickle first
    with open('file.enc.meta', 'rb') as f:
        metadata = pickle.load(f)
except:
    # Try JSON
    with open('file.enc.meta', 'r') as f:
        metadata = json.load(f)
```

---

## Debugging Tips

### Tip 1: Enable Verbose Logging

```python
import logging

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)

# Now you'll see detailed logs
ctx = STCContext('seed')
encrypted, metadata = ctx.encrypt("data", password="pw")
```

### Tip 2: Inspect Metadata

```python
import pickle

# Load metadata and inspect
with open('file.enc.meta', 'rb') as f:
    metadata = pickle.load(f)

# Check structure
print("Metadata keys:", list(metadata.keys()))
print("CEL snapshots:", len(metadata.get('cel_snapshots', [])))
print("Metadata size:", len(pickle.dumps(metadata)), "bytes")

# Check for required fields
required_fields = ['cel_snapshots', 'phe_state', 'pcf_state']
for field in required_fields:
    if field not in metadata:
        print(f"❌ Missing required field: {field}")
    else:
        print(f"✓ Has {field}")
```

### Tip 3: Test with Known Data

```python
# Create a test with known input/output
def test_roundtrip():
    """Test encryption/decryption works"""
    ctx = STCContext('test-seed')
    
    test_data = "test message 12345"
    password = "test_password"
    
    # Encrypt
    encrypted, metadata = ctx.encrypt(test_data, password=password)
    
    # Decrypt
    decrypted = ctx.decrypt(encrypted, metadata, password=password)
    
    # Verify
    if decrypted == test_data:
        print("✓ Round-trip test PASSED")
        return True
    else:
        print(f"❌ Round-trip test FAILED")
        print(f"Expected: {test_data}")
        print(f"Got: {decrypted}")
        return False

# Run test
test_roundtrip()
```

### Tip 4: Compare File Hashes

```python
import hashlib

def hash_file(filepath):
    """Calculate SHA-256 hash of file"""
    sha256 = hashlib.sha256()
    with open(filepath, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b''):
            sha256.update(chunk)
    return sha256.hexdigest()

# Hash original file
original_hash = hash_file('original.txt')
print(f"Original: {original_hash}")

# Encrypt then decrypt
# ... encryption and decryption code ...

# Hash decrypted file
decrypted_hash = hash_file('decrypted.txt')
print(f"Decrypted: {decrypted_hash}")

# Verify
if original_hash == decrypted_hash:
    print("✓ Files match")
else:
    print("❌ Files differ - something went wrong!")
```

### Tip 5: Check Entropy Health

```python
def diagnose_entropy(ctx):
    """Diagnose entropy health issues"""
    health = ctx.get_entropy_health()
    
    print(f"=== Entropy Health Report ===")
    print(f"Status: {health['status']}")
    print(f"Quality Score: {health['quality_score']:.2f}")
    print(f"Unique Ratio: {health['unique_ratio']:.2f}")
    print(f"Distribution: {health['distribution_score']:.2f}")
    print(f"Update Count: {health['update_count']}")
    
    if health['recommendations']:
        print("\nRecommendations:")
        for rec in health['recommendations']:
            print(f"  - {rec}")
    
    # Advice
    if health['quality_score'] < 0.5:
        print("\n⚠️ CRITICAL: Quality too low - do not encrypt")
        print("Action: Run ctx.cel.update() immediately")
    elif health['quality_score'] < 0.7:
        print("\n⚠️ WARNING: Quality is marginal")
        print("Action: Consider running ctx.cel.update()")
    else:
        print("\n✓ Entropy health is good")

# Use it
ctx = STCContext('my-seed')
diagnose_entropy(ctx)
```

---

## Frequently Asked Questions

### Q: Can I change my password after encrypting?

**A:** No, you must decrypt with the original password, then re-encrypt with the new password:

```python
# Decrypt with old password
decrypted = ctx.decrypt(encrypted, metadata, password="old_password")

# Re-encrypt with new password
new_encrypted, new_metadata = ctx.encrypt(decrypted, password="new_password")
```

### Q: Can I recover data if I forget the password?

**A:** No. The password is essential for decryption. There is NO way to recover data without it.

**Best practices:**

- Use a password manager
- Write password in a safe physical location
- Create encrypted backup with different password

### Q: Why is my encrypted file larger than the original?

**A:** Encrypted files are usually similar in size, but metadata adds ~486 KB overhead:

```python
import os

original_size = os.path.getsize('original.txt')
encrypted_size = os.path.getsize('encrypted.enc')
metadata_size = os.path.getsize('encrypted.enc.meta')

print(f"Original:  {original_size:,} bytes")
print(f"Encrypted: {encrypted_size:,} bytes")
print(f"Metadata:  {metadata_size:,} bytes (~486 KB)")
print(f"Total:     {encrypted_size + metadata_size:,} bytes")
print(f"Overhead:  +{(encrypted_size + metadata_size) - original_size:,} bytes")
```

### Q: Can I encrypt files of any type?

**A:** Yes! STC works with ANY file type:

- Documents (PDF, Word, Excel)
- Images (JPG, PNG, GIF)
- Videos (MP4, AVI, MKV)
- Archives (ZIP, RAR, 7Z)
- Executables (EXE, APP)
- Databases (SQLite, etc.)

```python
# Works for ANY binary data
with open('any_file.xyz', 'rb') as f:
    data = f.read()

encrypted, metadata = ctx.encrypt(data, password="pw")
```

### Q: How do I encrypt multiple files?

**A:** Either encrypt each separately or combine into archive first:

**Option 1: Separate encryption**

```python
import os
import pickle

files = ['doc1.pdf', 'photo.jpg', 'video.mp4']
ctx = STCContext('multi-file-seed')

for filepath in files:
    with open(filepath, 'rb') as f:
        data = f.read()
    
    encrypted, metadata = ctx.encrypt(data, password="pw")
    
    # Save encrypted file
    with open(f"{filepath}.enc", 'wb') as f:
        f.write(encrypted)
    
    # Save metadata
    with open(f"{filepath}.enc.meta", 'wb') as f:
        pickle.dump(metadata, f)
    
    print(f"✓ Encrypted: {filepath}")
```

**Option 2: Archive first, then encrypt**

```python
import zipfile

# Create ZIP archive
with zipfile.ZipFile('archive.zip', 'w') as zipf:
    zipf.write('doc1.pdf')
    zipf.write('photo.jpg')
    zipf.write('video.mp4')

# Encrypt the archive
with open('archive.zip', 'rb') as f:
    data = f.read()

encrypted, metadata = ctx.encrypt(data, password="pw")

# Save encrypted archive
with open('archive.zip.enc', 'wb') as f:
    f.write(encrypted)

import pickle
with open('archive.zip.enc.meta', 'wb') as f:
    pickle.dump(metadata, f)

print("✓ All files encrypted in archive")
```

### Q: Is STC quantum-resistant?

**A:** Partially. STC uses some quantum-resistant techniques (lattice-based operations), but is not fully quantum-proof. For maximum quantum resistance, use larger lattice sizes:

```python
# Maximum quantum resistance (slower)
ctx = STCContext('seed', lattice_size=256, depth=8)
```

### Q: Can I use STC in production?

**A:** Yes, STC v0.3.0 is production-ready for most use cases. See [security-guide.md](../security-guide.md) for threat model and limitations.

**Production checklist:**

- [ ] Use strong passwords (12+ characters)
- [ ] Use unique seeds per user/application
- [ ] Monitor entropy health
- [ ] Enable all security features
- [ ] Backup metadata securely
- [ ] Test encryption/decryption before deploying
- [ ] Have disaster recovery plan

### Q: How long does encryption take?

**A:** Depends on data size and settings:

| Data Size | Settings | Time |
|-----------|----------|------|
| 1 KB | Default | ~0.9s |
| 1 MB | Default | ~1.2s |
| 100 MB | Default | ~45s |
| 100 MB | Streaming | ~50s |
| 1 GB | Streaming | ~8 min |

**Faster settings (less secure):**

```python
ctx = STCContext('seed', lattice_size=64, depth=4)
# ~3x faster
```

### Q: Why does decryption fail sometimes?

**Common reasons:**

1. Wrong password
2. Wrong seed
3. Missing context data
4. Corrupted encrypted data
5. Corrupted metadata
6. Metadata from different encryption

**Debugging:**

```python
import traceback

try:
    decrypted = ctx.decrypt(encrypted, metadata, password="pw")
except Exception as e:
    print(f"Decryption failed: {e}")
    traceback.print_exc()
```

---

## When to Ask for Help

Ask for help if:

- ✓ You've tried troubleshooting steps but still have errors
- ✓ You found a potential security issue
- ✓ STC behaves unexpectedly
- ✓ You need clarification on features

**Where to get help:**

- GitHub Issues: [github.com/Seigr-lab/SeigrToolsetCrypto/issues](https://github.com/Seigr-lab/SeigrToolsetCrypto/issues)
- Email: support@seigr.example.com
- Documentation: [Full docs](../README.md)

**When reporting issues, include:**

1. STC version (`stc.__version__`)
2. Python version
3. Operating system
4. Minimal code that reproduces the issue
5. Full error message and traceback
6. What you expected vs what happened

**Example bug report:**

```
Title: Decryption fails with "MAC verification failed"

STC version: 0.3.0
Python: 3.11.5
OS: Windows 11

Steps to reproduce:
1. Create context: ctx = STCContext('test-seed')
2. Encrypt: encrypted, metadata = ctx.encrypt("test", password="pw")
3. Decrypt: decrypted = ctx.decrypt(encrypted, metadata, password="pw")

Expected: "test"
Actual: ValueError: MAC verification failed

Full traceback:
[paste full traceback here]
```

---

## Quick Troubleshooting Checklist

When something goes wrong, check:

- [ ] **Password correct?** Try again carefully
- [ ] **Same seed?** Encryption and decryption must use same seed
- [ ] **Metadata saved?** Can't decrypt without it
- [ ] **Context data matches?** Same context for encrypt/decrypt
- [ ] **Entropy healthy?** Run `ctx.get_entropy_health()`
- [ ] **Files not corrupted?** Check file sizes and hashes
- [ ] **Correct file mode?** Use `'rb'` for reading encrypted data
- [ ] **Enough memory?** Use streaming for large files
- [ ] **Latest version?** Update to latest STC version

---

## Conclusion

You've completed the STC User Manual! You now know how to:

✅ Install and use STC  
✅ Encrypt and decrypt files  
✅ Use security features effectively  
✅ Optimize performance  
✅ Troubleshoot common problems

For more advanced topics, see:

- **[Usage Guide](../usage-guide.md)** - Comprehensive technical guide
- **[API Reference](../api-reference.md)** - Complete API documentation
- **[Security Guide](../security-guide.md)** - Threat model and best practices
- **[Architecture](../architecture.md)** - How STC works internally

Happy encrypting! 🔐
