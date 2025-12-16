# Chapter 2A: Security Profiles

**Automated Parameter Selection**

This chapter explains how to use STC's predefined security profiles for different file types.

---

## What Are Security Profiles?

Security profiles are predefined parameter sets optimized for different file types:

- **Document Profile** - For office files, PDFs, text documents
- **Media Profile** - For images, videos, audio files
- **Credentials Profile** - For passwords, keys, sensitive data
- **Backup Profile** - For archives, bulk data, large files
- **Custom Profile** - Manual parameter configuration

STC can automatically detect file types and select appropriate parameters.

---

## Quick Start: "What Should I Use?"

### Profile Recommendation

STC can analyze files and recommend appropriate profiles:

```python
from core.profiles import AdvancedProfileManager

# Analyze file and get profile recommendation
with open("my_tax_documents.pdf", "rb") as f:
    data = f.read()

result = AdvancedProfileManager.analyze_and_recommend(
    data, filename="my_tax_documents.pdf"
)

print(f"Recommended: {result['recommended_profile']}")
print(f"Confidence: {result['confidence']}")
print(f"Analysis: {result['content_analysis']}")
```

Example output shows detected file type and recommended parameter set.

### Automatic File Type Detection

Even easier - STC detects file types automatically:

```python
from core.profiles import get_profile_for_file

# Automatic detection
profile = get_profile_for_file("family_photos.jpg")
print(f"Detected profile: {profile.value}")  # "media"

profile = get_profile_for_file("passwords.txt") 
print(f"Detected profile: {profile.value}")  # "credentials"

profile = get_profile_for_file("backup.zip")
print(f"Detected profile: {profile.value}")  # "backup"
```

---

## Real-World Examples

### 📄 **Scenario**: Encrypting Tax Documents

```python
from stc import STCContext
from core.profiles import get_profile_for_file, get_optimized_parameters

# 1. Detect what type of file
profile = get_profile_for_file("2024_tax_return.pdf")
print(f"Using {profile.value} profile")  # "document"

# 2. Get optimized settings
params = get_optimized_parameters(profile, file_size=5*1024*1024)  # 5MB file

# 3. Encrypt with optimized settings
ctx = STCContext("tax-documents")
encrypted, metadata = ctx.encrypt_file(
    "2024_tax_return.pdf",
    "your_strong_password",
    profile_params=params
)

print("✅ Tax documents encrypted with document-optimized security!")
```

### 📸 **Scenario**: Securing Family Photos

```python
# Batch encrypt all photos in a folder
import os
from pathlib import Path

photo_folder = Path("Family_Photos")
password = "family_memories_2024"

for photo_path in photo_folder.glob("*.jpg"):
    # Auto-detect (will be "media" profile)
    profile = get_profile_for_file(str(photo_path))
    params = get_optimized_parameters(profile, file_size=photo_path.stat().st_size)
    
    # Encrypt with media-optimized settings
    ctx = STCContext("family-photos")
    encrypted, metadata = ctx.encrypt_file(
        str(photo_path),
        password,
        profile_params=params
    )
    
    print(f"✅ Encrypted {photo_path.name} (fast media mode)")
```

### 🔐 **Scenario**: Protecting Passwords

```python
# Encrypt password database with maximum security
profile = get_profile_for_file("passwords.kdbx")  # "credentials"
params = get_optimized_parameters(profile, file_size=1024*1024)

ctx = STCContext("password-manager")
encrypted, metadata = ctx.encrypt_file(
    "passwords.kdbx",
    "master_password_ultra_secure",
    profile_params=params
)

print("🔒 Password database encrypted with maximum security!")
print(f"Security level: {params['optimize_for']}")  # "security"
```

---

## Understanding Each Profile

### 📄 Document Profile

**Intended for**: Office files, PDFs, contracts, text documents

**Optimized for**: Balanced security and performance

- Medium encryption strength
- Good compression
- Reasonable processing speed
- Efficient metadata size

**Example files**: `.pdf`, `.docx`, `.txt`, `.xlsx`, `.pptx`

### 📸 Media Profile  

**Intended for**: Photos, videos, music, large media files

**Optimized for**: Speed and minimal overhead

- Faster processing
- Minimal metadata
- Good for large files (>100MB)
- Less security overhead

**Example files**: `.jpg`, `.mp4`, `.png`, `.avi`, `.mp3`

### 🔐 Credentials Profile

**Intended for**: Passwords, keys, certificates, highly sensitive data

**Optimized for**: Maximum security

- Strongest encryption settings
- Extra protection features
- More processing time
- Larger metadata (for security)

**Example files**: `.key`, `.pem`, `.kdbx`, small sensitive files

### 📦 Backup Profile

**Intended for**: Archives, bulk data, large backups

**Optimized for**: Speed and efficiency

- Fastest processing
- Minimal security overhead
- Good for very large files (>1GB)
- Optimized for bulk operations

**Example files**: `.zip`, `.tar.gz`, `.backup`, `.iso`

### ⚙️ Custom Profile

**Intended for**: Advanced users who want manual parameter control

**Use when**: You need specific settings that don't match other profiles

---

## Command Line Usage (Simple)

### Basic Commands

```bash
# Encrypt with auto-detected profile
stc-cli encrypt --input document.pdf --password "your_password"

# Decrypt
stc-cli decrypt --input document.pdf.enc --password "your_password"

# Get recommendation for a file
stc-cli recommend --file family_photos.jpg
```

### Batch Operations

```bash
# Encrypt entire folder with auto-detection
stc-cli encrypt-folder --input "My Documents" --password "folder_password"

# Decrypt entire folder
stc-cli decrypt-folder --input "My Documents.enc" --password "folder_password"
```

---

## Profile Performance Comparison

| Profile | Speed | Security | Intended For | File Size |
|---------|-------|----------|----------|-----------|
| 📦 Backup | ⚡⚡⚡⚡⚡ | 🔒🔒 | Bulk data | >1GB |
| 📸 Media | ⚡⚡⚡⚡ | 🔒🔒🔒 | Photos/Videos | >100MB |
| 📄 Document | ⚡⚡⚡ | 🔒🔒🔒🔒 | Office files | 1-100MB |
| 🔐 Credentials | ⚡⚡ | 🔒🔒🔒🔒🔒 | Sensitive data | <10MB |

---

## FAQ: "Which Profile Should I Use?"

### "I have a mix of different files"

Use **Document profile** as a safe default, or let STC auto-detect each file type.

### "I need maximum security"

Use **Credentials profile** for anything highly sensitive.

### "I have huge video files"

Use **Media profile** - it's optimized for large files and won't slow you down.

### "I'm backing up my entire computer"

Use **Backup profile** - it's designed for bulk data and maximum speed.

### "I don't know anything about encryption"

Let STC choose automatically! Use `get_profile_for_file()` and trust the recommendation.

---

## Next Steps

Now that you understand security profiles, you can:

1. **[Try CLI Commands](02b-command-line.md)** - Use STC from command line
2. **[Learn Advanced Features](03-security-features.md)** - Understand what makes profiles secure
3. **[See Real Examples](04-advanced-usage.md)** - Complete working projects

**Remember**: Security profiles make STC simple. You don't need to understand the technical details - just pick the right profile for your files!

---

**💡 Pro Tip**: When in doubt, use `recommend_profile_interactive()` - it will analyze your file and tell you exactly what to use and why!
