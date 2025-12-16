# Chapter 2: Basic Encryption

Learn how to encrypt and decrypt files, text, and passwords using STC v0.3.0.

## What You'll Learn

- ✓ How to encrypt text messages
- ✓ How to encrypt files
- ✓ How to store passwords safely
- ✓ How to manage encrypted data
- ✓ How to save and load encrypted files

---

## Encrypting Text Messages

### Your First Encryption

Let's encrypt a simple message:

```python
from stc import STCContext

# Create your encryption context
ctx = STCContext('my-personal-seed')

# Encrypt a message
message = "Hello, this is secret!"
password = "my_strong_password"

encrypted, metadata = ctx.encrypt(message, password=password)

print("✓ Message encrypted successfully!")
print(f"Encrypted size: {len(encrypted)} bytes")
```

**What just happened?**

1. Created an encryption context with your unique seed
2. STC took your message and password
3. Generated a secret encrypted version
4. Gave you back two things:
   - `encrypted`: The secret scrambled data
   - `metadata`: Information needed to unscramble it later

### Decrypting Your Message

Now let's get the message back:

```python
# Decrypt the message
decrypted_message = ctx.decrypt(encrypted, metadata, password=password)

print(decrypted_message)
# Output: "Hello, this is secret!"
```

**Important:** You need THREE things to decrypt:
1. The encrypted data
2. The metadata
3. The correct password

Missing any of these = cannot decrypt!

### What If I Use the Wrong Password?

```python
try:
    # Try with wrong password
    wrong_decrypt = ctx.decrypt(encrypted, metadata, password="wrong_password")
except ValueError:
    print("❌ Wrong password! Cannot decrypt.")
```

STC protects you by detecting wrong passwords automatically.

---

## Encrypting Files

### Encrypting a Text File

Let's encrypt a file on your computer:

```python
from stc import STCContext
import pickle

# Create context
ctx = STCContext('file-encryption-seed')

# Read the file you want to encrypt
with open('secret_document.txt', 'r') as f:
    file_content = f.read()

# Encrypt it
password = "my_file_password"
encrypted, metadata = ctx.encrypt(file_content, password=password)

# Save encrypted version
with open('secret_document.txt.encrypted', 'wb') as f:
    f.write(encrypted)

# Save metadata (needed for decryption)
with open('secret_document.txt.metadata', 'wb') as f:
    pickle.dump(metadata, f)

print("✓ File encrypted and saved!")
```

**What you get:**
- `secret_document.txt.encrypted` - The scrambled file
- `secret_document.txt.metadata` - The decryption information

### Decrypting a File

To get your file back:

```python
import pickle
from stc import STCContext

# Create context (same seed as encryption!)
ctx = STCContext('file-encryption-seed')

# Load encrypted data
with open('secret_document.txt.encrypted', 'rb') as f:
    encrypted = f.read()

# Load metadata
with open('secret_document.txt.metadata', 'rb') as f:
    metadata = pickle.load(f)

# Decrypt
password = "my_file_password"
decrypted_content = ctx.decrypt(encrypted, metadata, password=password)

# Save decrypted file
with open('secret_document_decrypted.txt', 'w') as f:
    f.write(decrypted_content)

print("✓ File decrypted successfully!")
```

### Encrypting Binary Files (Images, Videos, etc.)

Binary files work the same way:

```python
from stc import STCContext
import pickle

ctx = STCContext('binary-files-seed')

# Read binary file (image, video, PDF, etc.)
with open('photo.jpg', 'rb') as f:
    file_bytes = f.read()

# Encrypt
password = "photo_password"
encrypted, metadata = ctx.encrypt(file_bytes, password=password)

# Save encrypted file
with open('photo.jpg.encrypted', 'wb') as f:
    f.write(encrypted)

# Save metadata
with open('photo.jpg.metadata', 'wb') as f:
    pickle.dump(metadata, f)

print("✓ Photo encrypted!")
```

**Decrypt the same way:**

```python
import pickle
from stc import STCContext

ctx = STCContext('binary-files-seed')

# Load encrypted photo
with open('photo.jpg.encrypted', 'rb') as f:
    encrypted = f.read()

with open('photo.jpg.metadata', 'rb') as f:
    metadata = pickle.load(f)

# Decrypt
decrypted_photo = ctx.decrypt(encrypted, metadata, password="photo_password")

# Save original photo
with open('photo_decrypted.jpg', 'wb') as f:
    f.write(decrypted_photo)

print("✓ Photo decrypted!")
```

---

## Storing Passwords Safely

### Creating a Simple Password Manager

Let's build a basic password manager to store your passwords securely:

```python
from stc import STCContext
import json
import pickle

class SimplePasswordManager:
    def __init__(self, master_password):
        """Initialize with your master password"""
        self.ctx = STCContext(f"password-manager-{master_password}")
        self.master_password = master_password
        self.passwords = {}
    
    def save_password(self, website, username, password):
        """Save a password for a website"""
        # Create a record
        record = {
            'website': website,
            'username': username,
            'password': password
        }
        
        # Convert to JSON
        record_json = json.dumps(record)
        
        # Encrypt it
        encrypted, metadata = self.ctx.encrypt(
            record_json,
            password=self.master_password
        )
        
        # Store encrypted version
        self.passwords[website] = {
            'encrypted': encrypted,
            'metadata': metadata
        }
        
        print(f"✓ Password for {website} saved securely!")
    
    def get_password(self, website):
        """Retrieve a password for a website"""
        if website not in self.passwords:
            print(f"❌ No password saved for {website}")
            return None
        
        # Get encrypted data
        entry = self.passwords[website]
        
        # Decrypt
        decrypted_json = self.ctx.decrypt(
            entry['encrypted'],
            entry['metadata'],
            password=self.master_password
        )
        
        # Parse JSON
        record = json.loads(decrypted_json)
        return record
    
    def save_to_file(self, filename):
        """Save all passwords to encrypted file"""
        with open(filename, 'wb') as f:
            pickle.dump(self.passwords, f)
        print(f"✓ All passwords saved to {filename}")
    
    def load_from_file(self, filename):
        """Load passwords from encrypted file"""
        with open(filename, 'rb') as f:
            self.passwords = pickle.load(f)
        print(f"✓ Passwords loaded from {filename}")

# Usage example
manager = SimplePasswordManager("my_super_secret_master_password")

# Save some passwords
manager.save_password("gmail.com", "myemail@gmail.com", "gmail_password_123")
manager.save_password("github.com", "myusername", "github_token_abc")

# Retrieve a password
gmail_info = manager.get_password("gmail.com")
print(f"Gmail username: {gmail_info['username']}")
print(f"Gmail password: {gmail_info['password']}")

# Save to file
manager.save_to_file("my_passwords.dat")
```

### Loading Your Passwords Later

```python
# Later, load your passwords
manager2 = SimplePasswordManager("my_super_secret_master_password")
manager2.load_from_file("my_passwords.dat")

# Get your GitHub password
github_info = manager2.get_password("github.com")
print(f"GitHub username: {github_info['username']}")
```

---

## Managing Encrypted Data

### Organizing Multiple Encrypted Files

Here's a helper class to organize your encrypted files:

```python
import os
import pickle
from stc import STCContext

class EncryptedFileManager:
    def __init__(self, password, storage_dir="encrypted_files"):
        """Initialize with password and storage directory"""
        self.ctx = STCContext(f"file-manager-{password}")
        self.password = password
        self.storage_dir = storage_dir
        
        # Create storage directory if it doesn't exist
        os.makedirs(storage_dir, exist_ok=True)
    
    def encrypt_file(self, filepath, encrypted_name=None):
        """Encrypt a file and save it"""
        # Read original file
        with open(filepath, 'rb') as f:
            data = f.read()
        
        # Encrypt
        encrypted, metadata = self.ctx.encrypt(data, password=self.password)
        
        # Determine encrypted filename
        if encrypted_name is None:
            encrypted_name = os.path.basename(filepath) + ".enc"
        
        # Save encrypted file
        enc_path = os.path.join(self.storage_dir, encrypted_name)
        with open(enc_path, 'wb') as f:
            f.write(encrypted)
        
        # Save metadata
        meta_path = enc_path + ".meta"
        with open(meta_path, 'wb') as f:
            pickle.dump(metadata, f)
        
        print(f"✓ Encrypted: {filepath} → {enc_path}")
        return enc_path
    
    def decrypt_file(self, encrypted_name, output_path):
        """Decrypt a file"""
        # Load encrypted file
        enc_path = os.path.join(self.storage_dir, encrypted_name)
        with open(enc_path, 'rb') as f:
            encrypted = f.read()
        
        # Load metadata
        meta_path = enc_path + ".meta"
        with open(meta_path, 'rb') as f:
            metadata = pickle.load(f)
        
        # Decrypt
        decrypted = self.ctx.decrypt(encrypted, metadata, password=self.password)
        
        # Save decrypted file
        with open(output_path, 'wb') as f:
            f.write(decrypted)
        
        print(f"✓ Decrypted: {enc_path} → {output_path}")
    
    def list_encrypted_files(self):
        """List all encrypted files"""
        files = [f for f in os.listdir(self.storage_dir) if f.endswith('.enc')]
        print(f"\nEncrypted files in {self.storage_dir}:")
        for f in files:
            size = os.path.getsize(os.path.join(self.storage_dir, f))
            print(f"  - {f} ({size:,} bytes)")
        return files

# Usage
manager = EncryptedFileManager("my_encryption_password")

# Encrypt some files
manager.encrypt_file("important_document.pdf")
manager.encrypt_file("private_photo.jpg")
manager.encrypt_file("secret_notes.txt")

# List encrypted files
manager.list_encrypted_files()

# Decrypt a file
manager.decrypt_file("important_document.pdf.enc", "document_restored.pdf")
```

### Checking Encrypted File Sizes

```python
import os
import pickle

def check_encrypted_size(original_file, encrypted_file, metadata_file):
    """Compare sizes of original vs encrypted"""
    original_size = os.path.getsize(original_file)
    encrypted_size = os.path.getsize(encrypted_file)
    
    with open(metadata_file, 'rb') as f:
        metadata = pickle.load(f)
    metadata_size = len(pickle.dumps(metadata))
    
    total_encrypted = encrypted_size + metadata_size
    
    print(f"Original file:  {original_size:,} bytes")
    print(f"Encrypted file: {encrypted_size:,} bytes")
    print(f"Metadata:       {metadata_size:,} bytes (~486 KB)")
    print(f"Total:          {total_encrypted:,} bytes")
    print(f"Overhead:       +{total_encrypted - original_size:,} bytes")

# Example
check_encrypted_size(
    "document.pdf",
    "document.pdf.encrypted",
    "document.pdf.metadata"
)
```

**Typical overhead:** ~486 KB metadata + small encryption overhead per file.

---

## Practical Tips

### 1. Always Save Both Encrypted Data AND Metadata

```python
# ✓ CORRECT - Save both
with open('file.enc', 'wb') as f:
    f.write(encrypted)

with open('file.enc.meta', 'wb') as f:
    pickle.dump(metadata, f)

# ❌ WRONG - Only save encrypted data
with open('file.enc', 'wb') as f:
    f.write(encrypted)
# Without metadata, you CANNOT decrypt!
```

### 2. Use Strong Passwords

```python
# ✓ GOOD passwords
"MyStr0ng!Pass_2024"
"correct-horse-battery-staple"
"P@ssw0rd_with_Numb3rs!"

# ❌ BAD passwords
"password"
"12345678"
"qwerty"
```

### 3. Keep Your Seed Secret

```python
# ✓ GOOD - Unique seed
ctx = STCContext('my-unique-personal-seed-xyz123')

# ❌ BAD - Generic seed
ctx = STCContext('default')  # Everyone using this is insecure!
```

### 4. Test Decryption Before Deleting Original

```python
# Encrypt file
encrypted, metadata = ctx.encrypt(data, password="pw")

# Save encrypted version
with open('file.enc', 'wb') as f:
    f.write(encrypted)
with open('file.enc.meta', 'wb') as f:
    pickle.dump(metadata, f)

# ✓ Test decryption FIRST
test_decrypted = ctx.decrypt(encrypted, metadata, password="pw")
assert test_decrypted == data
print("✓ Decryption verified!")

# NOW it's safe to delete original
os.remove('original_file.txt')
```

### 5. Organize Your Encrypted Files

```python
# Good folder structure:
encrypted_files/
    documents/
        contract.pdf.enc
        contract.pdf.enc.meta
        invoice.pdf.enc
        invoice.pdf.enc.meta
    photos/
        vacation.jpg.enc
        vacation.jpg.enc.meta
    passwords/
        passwords.dat
```

---

## Common Mistakes to Avoid

### ❌ Mistake 1: Losing Metadata

```python
# Wrong - metadata gets lost
encrypted, metadata = ctx.encrypt("secret", password="pw")
# ... metadata is never saved ...
# Later: Cannot decrypt because metadata is gone!
```

**Solution:** Always save metadata to a file!

### ❌ Mistake 2: Using Different Seeds

```python
# Encrypt with one seed
ctx1 = STCContext('seed-A')
encrypted, metadata = ctx1.encrypt("data", password="pw")

# Try to decrypt with different seed - FAILS!
ctx2 = STCContext('seed-B')
decrypted = ctx2.decrypt(encrypted, metadata, password="pw")
# This will produce garbage or fail!
```

**Solution:** Use the SAME seed for encryption and decryption!

### ❌ Mistake 3: Forgetting Password

```python
# No way to recover if you forget password!
encrypted, metadata = ctx.encrypt("important", password="?????")
# Password forgotten = data lost forever
```

**Solution:** Use a password manager or write it down in a safe place!

### ❌ Mistake 4: Not Checking File Permissions

```python
# Wrong - anyone can read your encrypted files
os.chmod("secret.enc", 0o644)  # World-readable!

# Correct - only you can read
os.chmod("secret.enc", 0o600)  # Owner only
```

---

## Quick Reference

### Encrypt Text

```python
ctx = STCContext('seed')
encrypted, metadata = ctx.encrypt("text", password="pw")
```

### Decrypt Text

```python
decrypted = ctx.decrypt(encrypted, metadata, password="pw")
```

### Encrypt File

```python
with open('file.txt', 'rb') as f:
    data = f.read()
encrypted, metadata = ctx.encrypt(data, password="pw")

with open('file.enc', 'wb') as f:
    f.write(encrypted)
import pickle
with open('file.enc.meta', 'wb') as f:
    pickle.dump(metadata, f)
```

### Decrypt File

```python
import pickle
with open('file.enc', 'rb') as f:
    encrypted = f.read()
with open('file.enc.meta', 'rb') as f:
    metadata = pickle.load(f)

decrypted = ctx.decrypt(encrypted, metadata, password="pw")
with open('file_restored.txt', 'wb') as f:
    f.write(decrypted)
```

---

## What's Next?

Now that you know basic encryption, continue to:

- **[Chapter 3: Security Features](03-security-features.md)** - Learn about decoys, entropy health, and advanced security
- **[Chapter 4: Advanced Usage](04-advanced-usage.md)** - Streaming, context data, performance optimization
- **[Chapter 5: Troubleshooting](05-troubleshooting.md)** - Fix common problems

---

## Practice Exercise

Try this on your own:

1. Create a text file with a secret message
2. Encrypt it using STC
3. Delete the original file
4. Decrypt it to verify you get the message back
5. Use the `SimplePasswordManager` to store 3 passwords

**Solution code:**

```python
from stc import STCContext
import pickle
import os

# 1. Create text file
with open('secret_message.txt', 'w') as f:
    f.write("This is my secret message!")

# 2. Encrypt it
ctx = STCContext('practice-seed')
with open('secret_message.txt', 'r') as f:
    data = f.read()

encrypted, metadata = ctx.encrypt(data, password="practice123")

with open('secret_message.enc', 'wb') as f:
    f.write(encrypted)

with open('secret_message.enc.meta', 'wb') as f:
    pickle.dump(metadata, f)

# 3. Delete original
os.remove('secret_message.txt')
print("✓ Original deleted")

# 4. Decrypt to verify
with open('secret_message.enc', 'rb') as f:
    encrypted = f.read()

with open('secret_message.enc.meta', 'rb') as f:
    metadata = pickle.load(f)

decrypted = ctx.decrypt(encrypted, metadata, password="practice123")
print(f"✓ Decrypted: {decrypted}")

# 5. Password manager
from user_manual.examples import SimplePasswordManager
manager = SimplePasswordManager("master_pw")
manager.save_password("email.com", "user@email.com", "email_pass")
manager.save_password("bank.com", "user123", "bank_pass")
manager.save_password("social.com", "username", "social_pass")
print("✓ 3 passwords stored!")
```

This completes the basic encryption tutorial.
