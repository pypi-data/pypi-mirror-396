# Chapter 1: Getting Started

Welcome to Seigr Toolset Crypto! This chapter will teach you the basics: what encryption is, how to install STC, and how to perform your first encryption. No previous experience required!

---

## What is Encryption?

### In Simple Terms

**Encryption** is like putting your data in a locked box. Only someone with the key (password) can open the box and read the data.

**Example**:
- **Plaintext** (readable): "My bank password is secret123"
- **Encrypted** (scrambled): `b'\x9a\x12\xef\x45\xab\xcd...'` (looks like random garbage)
- **Decrypted** (readable again): "My bank password is secret123"

### Why Do You Need It?

Imagine these scenarios:

1. **Storing passwords**: You want to save your passwords to a file, but don't want anyone reading the file to see them
2. **Cloud backups**: You upload files to Dropbox/Google Drive, but don't trust the cloud provider
3. **Sharing secrets**: You need to send API keys to a coworker via Slack
4. **Local protection**: You want to protect files on your laptop in case it gets stolen

**Without encryption**: Anyone with access sees your data  
**With encryption**: Only people with the password can read it

---

## What Makes STC Different?

There are many encryption tools available. Here's why STC is special:

### Traditional Encryption (AES, RSA, etc.)

```
Plaintext → Encrypt with password → Ciphertext
Ciphertext → Decrypt with password → Plaintext
```

**Problem**: If someone has the ciphertext, they can try billions of passwords per second.

### STC (Seigr Toolset Crypto)

```
Plaintext → Encrypt with password + randomness + decoys → Ciphertext
Ciphertext → Decrypt with password (tries real key + decoys) → Plaintext
```

**Benefits**:
- **Decoys**: Creates fake keys alongside the real one - attackers must try ALL keys
- **Quality monitoring**: Warns you if encryption quality degrades
- **Attack detection**: Automatically strengthens encryption when attacks are detected
- **Large files**: Can encrypt files of any size without memory issues

**Think of it like**:
- Traditional encryption: 1 locked box
- STC encryption: 4-6 identical locked boxes, only 1 contains the real data (attacker must try all!)

---

## Installing STC

### Requirements

- **Python**: Version 3.8 or later
- **pip**: Python package installer (included with Python)
- **Operating System**: Windows, macOS, or Linux

### Check If You Have Python

Open a terminal/command prompt and run:

```bash
python --version
```

You should see something like:

```
Python 3.10.5
```

If you see `Python 2.x` or an error, you need to install Python 3:

- **Windows**: Download from [python.org](https://www.python.org/downloads/)
- **macOS**: `brew install python3` (or download from python.org)
- **Linux**: `sudo apt install python3 python3-pip` (Ubuntu/Debian) or `sudo yum install python3 python3-pip` (CentOS/RHEL)

### Install STC

Once Python is installed, run:

```bash
pip install seigr-toolset-crypto
```

You should see output like:

```
Collecting seigr-toolset-crypto
  Downloading seigr_toolset_crypto-0.3.0-py3-none-any.whl
Installing collected packages: seigr-toolset-crypto
Successfully installed seigr-toolset-crypto-0.3.0
```

### Verify Installation

Test that STC is installed correctly:

```bash
python -c "import stc; print('STC version:', stc.__version__)"
```

You should see:

```
STC version: 0.3.0
```

STC is now installed.

---

## Your First Encryption (3 Lines of Code!)

Let's encrypt your first piece of data. Create a new file called `first_encryption.py`:

```python
from stc import STCContext

# Step 1: Create an encryption context
ctx = STCContext("my-first-app")

# Step 2: Encrypt some text
secret_message = b"Hello, this is my secret message!"
encrypted, metadata = ctx.encrypt(secret_message, password="my_strong_password")

# Step 3: Decrypt the text
decrypted = ctx.decrypt(encrypted, metadata, password="my_strong_password")

print("Original:", secret_message)
print("Encrypted:", encrypted[:50], "...")  # Show first 50 bytes
print("Decrypted:", decrypted)
print("\nSuccess! Your first encryption/decryption worked.")
```

**Run the code**:

```bash
python first_encryption.py
```

**Expected output**:

```
Original: b'Hello, this is my secret message!'
Encrypted: b'\x9a\x12\xef\x45\xab\xcd\x78\x23\x56...' ...
Decrypted: b'Hello, this is my secret message!'

Success! Your first encryption/decryption worked.
```

### What Just Happened?

Let's break down each part:

```python
from stc import STCContext
```

This imports the main STC class. Think of `STCContext` as your encryption workspace.

```python
ctx = STCContext("my-first-app")
```

Creates an encryption context with a **seed** (`"my-first-app"`). The seed is like a "namespace" - different apps should use different seeds.

```python
encrypted, metadata = ctx.encrypt(secret_message, password="my_strong_password")
```

Encrypts your message using the password. Returns two things:
- `encrypted`: The scrambled data (bytes)
- `metadata`: Information STC needs to decrypt (also secret!)

```python
decrypted = ctx.decrypt(encrypted, metadata, password="my_strong_password")
```

Decrypts the data back to the original message using the password and metadata.

---

## Understanding Key Concepts

### Passwords

**What they are**: The secret key you use to encrypt/decrypt data.

**Good passwords**:
- ✅ "Tr0ub4dor&3" (complex, long)
- ✅ "correct-horse-battery-staple" (long passphrase)
- ✅ "aB3$xYz9!Qw" (random characters)

**Bad passwords**:
- ❌ "password" (too common)
- ❌ "123456" (too simple)
- ❌ "myname" (too short)

**Best practice**: Use a password manager to generate random passwords.

### Seeds

**What they are**: A starting value for STC's internal randomness.

**Think of seeds like**:
- Apartment building (seed) vs apartment number (password)
- Everyone in building "my-first-app" has different apartments (passwords)
- Can't access apartment without knowing the building (seed) AND apartment number (password)

**Good seeds**:
- ✅ "password-manager-v1"
- ✅ "file-encryptor"
- ✅ "backup-tool-2024"

**Bad seeds**:
- ❌ "app" (too generic - same for all users!)
- ❌ "" (empty - weakens security)
- ❌ Your password (confuses seed with password)

**Best practice**: Use descriptive, unique seeds for each application.

### Metadata

**What it is**: Technical information STC needs to decrypt your data.

**Important facts**:
- Contains encryption parameters (but NOT your password)
- Required for decryption (lose this = can't decrypt!)
- Should be kept as secret as the encrypted data
- Much larger than encrypted data (in STC, due to decoys)

**Example sizes**:
- Encrypted data: 100 KB
- Metadata: ~1.5 MB (with 3 decoys in v0.3.0)

**Why so large?**: STC includes decoy keys in metadata to confuse attackers. This extra size is the price of stronger security.

### The `b` Prefix (Bytes vs Strings)

You may have noticed `b"Hello"` instead of `"Hello"`. What's the difference?

```python
# String (text)
text = "Hello"

# Bytes (binary data)
binary = b"Hello"
```

**Why STC uses bytes**:
- Encryption works on binary data (0s and 1s)
- Strings have encoding issues (UTF-8, ASCII, etc.)
- Bytes are universal

**Converting between them**:

```python
# String → Bytes
text = "Hello"
binary = text.encode()  # b"Hello"

# Bytes → String
binary = b"Hello"
text = binary.decode()  # "Hello"
```

**In practice**:

```python
# Encrypting text
secret_text = "My password is secret123"
encrypted, metadata = ctx.encrypt(secret_text.encode(), password="pw")

# Decrypting back to text
decrypted_bytes = ctx.decrypt(encrypted, metadata, password="pw")
decrypted_text = decrypted_bytes.decode()
print(decrypted_text)  # "My password is secret123"
```

---

## Saving Encrypted Data

Your first encryption worked, but the data disappeared when the program ended! Let's save it to files.

### Saving to Files

```python
import pickle
from stc import STCContext

ctx = STCContext("my-app")

# Encrypt
secret = b"Important data to save"
encrypted, metadata = ctx.encrypt(secret, password="strong_pw")

# Save encrypted data
with open("secret.enc", 'wb') as f:
    f.write(encrypted)

# Save metadata
with open("secret.enc.meta", 'wb') as f:
    pickle.dump(metadata, f)

print("Saved encrypted data to secret.enc")
print("Saved metadata to secret.enc.meta")
```

### Loading from Files

```python
import pickle
from stc import STCContext

ctx = STCContext("my-app")

# Load encrypted data
with open("secret.enc", 'rb') as f:
    encrypted = f.read()

# Load metadata
with open("secret.enc.meta", 'rb') as f:
    metadata = pickle.load(f)

# Decrypt
decrypted = ctx.decrypt(encrypted, metadata, password="strong_pw")
print("Decrypted:", decrypted.decode())
```

### Complete Example: Encrypt and Save

Create `save_secret.py`:

```python
import pickle
from stc import STCContext

# Create context
ctx = STCContext("my-app")

# Get secret from user
secret_text = input("Enter your secret: ")

# Encrypt
encrypted, metadata = ctx.encrypt(secret_text.encode(), password="my_password")

# Save both files
with open("secret.enc", 'wb') as f:
    f.write(encrypted)

with open("secret.enc.meta", 'wb') as f:
    pickle.dump(metadata, f)

print("\n✅ Secret encrypted and saved!")
print("   - Encrypted data: secret.enc")
print("   - Metadata: secret.enc.meta")
print("\nKeep both files safe!")
```

### Loading Your Secret

Create `load_secret.py`:

```python
import pickle
from stc import STCContext

# Create context (must use same seed!)
ctx = STCContext("my-app")

# Load files
with open("secret.enc", 'rb') as f:
    encrypted = f.read()

with open("secret.enc.meta", 'rb') as f:
    metadata = pickle.load(f)

# Decrypt
decrypted = ctx.decrypt(encrypted, metadata, password="my_password")

print("Your secret:", decrypted.decode())
```

**Try it**:

```bash
$ python save_secret.py
Enter your secret: This is my password: secret123
✅ Secret encrypted and saved!

$ python load_secret.py
Your secret: This is my password: secret123
```

---

## Common Mistakes (and How to Fix Them)

### Mistake 1: Wrong Password

```python
encrypted, metadata = ctx.encrypt(b"data", password="correct")
decrypted = ctx.decrypt(encrypted, metadata, password="wrong")
```

**Error**:

```
ValueError: MAC verification failed - incorrect password or corrupted data
```

**Fix**: Use the exact same password for encryption and decryption.

### Mistake 2: Different Seed

```python
# Encryption
ctx1 = STCContext("app-v1")
encrypted, metadata = ctx1.encrypt(b"data", password="pw")

# Decryption (WRONG SEED!)
ctx2 = STCContext("app-v2")
decrypted = ctx2.decrypt(encrypted, metadata, password="pw")
```

**Error**: Decryption will fail (wrong internal state).

**Fix**: Always use the same seed for encryption and decryption:

```python
SEED = "my-app"  # Define once

ctx1 = STCContext(SEED)
encrypted, metadata = ctx1.encrypt(b"data", password="pw")

ctx2 = STCContext(SEED)  # Same seed
decrypted = ctx2.decrypt(encrypted, metadata, password="pw")
```

### Mistake 3: Forgot Metadata

```python
encrypted, metadata = ctx.encrypt(b"data", password="pw")

# Later... (metadata lost!)
decrypted = ctx.decrypt(encrypted, ???, password="pw")
```

**Error**: Can't decrypt without metadata!

**Fix**: Always save metadata alongside encrypted data:

```python
# Save together
with open("data.enc", 'wb') as f:
    f.write(encrypted)
with open("data.enc.meta", 'wb') as f:
    pickle.dump(metadata, f)

# Load together
with open("data.enc", 'rb') as f:
    encrypted = f.read()
with open("data.enc.meta", 'rb') as f:
    metadata = pickle.load(f)
```

### Mistake 4: String Instead of Bytes

```python
encrypted, metadata = ctx.encrypt("Hello", password="pw")  # ❌ String!
```

**Error**:

```
TypeError: a bytes-like object is required, not 'str'
```

**Fix**: Use `.encode()` to convert string to bytes:

```python
encrypted, metadata = ctx.encrypt("Hello".encode(), password="pw")  # ✅ Bytes
```

---

## When Should You Use STC?

### ✅ Good Use Cases

1. **Password Storage**
   - Storing passwords in a file or database
   - Protecting API keys and credentials

2. **File Encryption**
   - Encrypting documents before cloud upload
   - Protecting sensitive files on disk

3. **Backup Protection**
   - Encrypting database backups
   - Protecting archive files

4. **Secure Communication**
   - Encrypting messages before transmission
   - Protecting data at rest

### ⚠️ Not Ideal For

1. **Real-time Communication**
   - Use TLS/SSL instead (STC is for data at rest)
   - STC is slower than symmetric encryption (due to extra security features)

2. **Extremely Resource-Constrained Devices**
   - STC metadata is large (~1.5 MB with decoys)
   - Consider traditional encryption (AES) if storage is very limited

3. **Public Key Cryptography Needs**
   - STC uses passwords (symmetric encryption)
   - For public/private key pairs, use RSA or ECC

---

## Next Steps

Congratulations! You've learned:

- ✅ What encryption is and why you need it
- ✅ How to install STC
- ✅ How to perform basic encryption/decryption
- ✅ How to save and load encrypted data
- ✅ Common mistakes and how to avoid them

### Ready to Continue?

Move on to **[Chapter 2: Basic Encryption](02-basic-encryption.md)** to learn:

- Encrypting files and documents
- Building a simple password manager
- Encrypting multiple items
- Best practices for everyday encryption

### Quick Reference

**Basic encryption**:

```python
from stc import STCContext

ctx = STCContext("my-app")
encrypted, metadata = ctx.encrypt(b"secret data", password="strong_password")
```

**Basic decryption**:

```python
decrypted = ctx.decrypt(encrypted, metadata, password="strong_password")
```

**Save to file**:

```python
import pickle

with open("data.enc", 'wb') as f:
    f.write(encrypted)
with open("data.enc.meta", 'wb') as f:
    pickle.dump(metadata, f)
```

---

**Next**: [Chapter 2: Basic Encryption →](02-basic-encryption.md)

**Up**: [User Manual Home](README.md)
