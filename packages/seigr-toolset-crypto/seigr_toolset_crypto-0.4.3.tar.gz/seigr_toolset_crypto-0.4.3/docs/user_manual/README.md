# Seigr Toolset Crypto - User Manual

A guide to encrypting and protecting data using STC

---

## Welcome

This manual is designed for users with no cryptography background required. It covers how to use Seigr Toolset Crypto (STC) to protect passwords, files, and sensitive data.

### What You'll Learn

By the end of this manual, you'll be able to:

- ✅ Install and set up STC
- ✅ Encrypt and decrypt text, passwords, and files
- ✅ Understand how STC protects your data
- ✅ Use advanced features like streaming encryption
- ✅ Troubleshoot common issues

### No Previous Experience Needed

If you can copy and paste code, you can use STC. We'll explain everything in plain English, with lots of examples.

---

## Table of Contents

### [Chapter 1: Getting Started](01-getting-started.md)

Learn the basics: what is STC, how to install it, and your first encryption.

**Topics**:

- What is encryption and why do you need it?
- Installing STC on Windows, Mac, and Linux
- Your first encryption in 3 lines of code
- Understanding passwords and seeds
- When to use STC

**Time to complete**: 15 minutes

---

### [Chapter 2A: Security Profiles - Easy Mode](02a-security-profiles.md)

Automated parameter selection - STC detects file types and selects appropriate settings.

**Topics**:

- Understanding security profiles (Document, Media, Credentials, Backup)
- Automatic file type detection and recommendations
- Real-world examples for every file type
- "What should I use?" interactive recommendations
- Performance vs security trade-offs explained

**Time to complete**: 20 minutes

---

### [Chapter 2B: Command Line Usage](02b-command-line.md)

Use STC from terminal/command prompt without programming.

**Topics**:

- Installing and using the STC CLI
- Encrypting files with simple commands
- Batch operations for folders
- Getting profile recommendations
- Real-world command-line workflows

**Time to complete**: 25 minutes

---

### [Chapter 2C: Specialized Security Profiles](02c-intelligent-profiles.md)

**ADVANCED!** Pattern-based content analysis and automated security optimization.

**Topics**:

- 19+ specialized profiles (Financial, Medical, Legal, Technical)
- Automatic content analysis via pattern matching and threat detection
- Adaptive security that responds to attacks
- Context-aware optimization using heuristics
- Privacy-preserving local analysis

**Time to complete**: 35 minutes

---

### [Chapter 2D: Real-World Scenarios](02d-real-world-scenarios.md)

**PRACTICAL!** Complete examples for common use cases.

**Topics**:

- Family photos and personal documents
- Business and professional files
- High-security government/legal documents
- Developer credentials and source code
- Emergency access and cross-platform sync

**Time to complete**: 30 minutes

---

### [Chapter 2: Basic Encryption](02-basic-encryption.md)

Programming examples for developers and power users.

**Topics**:

- Python API usage and integration
- Custom encryption workflows
- Advanced parameter customization
- Building STC into applications
- Error handling and edge cases

**Time to complete**: 30 minutes

---

### [Chapter 3: Security Features](03-security-features.md)

Understanding STC's unique security features in plain English.

**Topics**:

- What are "decoys" and why they protect you
- Entropy health: ensuring strong encryption
- Context data: adding extra protection
- How STC detects attacks automatically
- Timing randomization explained
- Understanding metadata

**Time to complete**: 25 minutes

---

### [Chapter 4: Advanced Usage](04-advanced-usage.md)

Power user features for serious security needs.

**Topics**:

- Streaming encryption for large files (GB+)
- Building a password manager with STC
- Encrypting configuration files
- Using context data effectively
- Performance optimization tips
- Thread safety and multi-user scenarios

**Time to complete**: 40 minutes

---

### [Chapter 5: Troubleshooting](05-troubleshooting.md)

Solving common problems and understanding error messages.

**Topics**:

- Common error messages explained
- "Wrong password" vs "corrupted data" - how to tell
- Recovering from entropy quality warnings
- Performance issues and solutions
- Frequently Asked Questions (FAQ)
- Where to get help

**Time to complete**: 20 minutes

---

## How to Use This Manual

### If You Just Want to Encrypt Files (No Programming)

1. **Chapter 1**: Install STC
2. **Chapter 2A**: Learn security profiles (easiest way!)
3. **Chapter 2B**: Use command-line tools
4. **Chapter 5**: Troubleshooting if needed

### If You Want Automated Features

1. **Chapter 1**: Install STC
2. **Chapter 2A**: Basic security profiles
3. **Chapter 2C**: Specialized profiles with content analysis
4. **Chapter 3**: Understand advanced security features

### If You're a Developer

1. **Chapter 1**: Installation and concepts
2. **Chapter 2**: Programming API and integration
3. **Chapter 3**: Security model deep-dive
4. **Chapter 4**: Production deployment patterns

- **Also see**: [API Reference](../api-reference.md) and [Architecture](../architecture.md)

### If You Have Some Experience

1. Skim **Chapter 1** for installation
2. **Chapter 2A** for easy profiles OR **Chapter 2B** for CLI OR **Chapter 2** for programming
3. **Chapter 3** to understand security features
4. **Chapter 4** for advanced topics

---

## Key Concepts (Simple Explanations)

### Encryption

**What it is**: Scrambling data so only people with the password can read it.

**Example**: "Hello World" → `b'\x9a\x12\xef...'` (encrypted) → "Hello World" (decrypted with password)

### Password

**What it is**: The secret key you use to encrypt/decrypt data.

**Best practice**: Use long, random passwords. Never reuse passwords.

### Seed

**What it is**: A starting point for STC's internal randomness.

**Best practice**: Use unique seeds for different applications. Think of it like a "namespace".

### Context Data

**What it is**: Extra information that must be present to decrypt (like a second password).

**Example**: `{'user': 'alice', 'app': 'myapp'}` - data can only be decrypted with this exact context.

### Metadata

**What it is**: Technical information STC needs to decrypt your data.

**Important**: Keep metadata files as secret as your encrypted data!

### Decoys

**What it is**: Fake encryption keys that look real but aren't.

**Why it matters**: Attackers can't tell which key is real, making your data safer.

---

## What Makes STC Special?

Unlike traditional encryption tools, STC provides:

1. **Automatic Attack Detection**
   - STC notices when someone is trying to crack your encryption
   - Automatically makes encryption stronger in response

2. **Quality Monitoring**
   - STC checks if encryption is strong enough
   - Warns you if quality degrades (rare, but important!)

3. **Decoy Obfuscation**
   - Creates fake keys alongside real ones
   - Attackers must try all keys (very expensive!)

4. **High-Performance Streaming** (v0.3.1)
   - Ultra-fast streaming for files of any size (>100GB supported)
   - Constant 7MB memory usage regardless of file size
   - Upfront decoy validation eliminates trial-and-error processing
   - 3-5x performance improvement over previous versions

5. **Context Awareness**
   - Tie encryption to specific users, apps, or purposes
   - Add extra protection beyond passwords

---

## Quick Reference

### 🚀 **Easiest Way** (Command Line with Auto-Detection)

```bash
# STC automatically detects file type and selects appropriate settings
stc-cli encrypt --input my_document.pdf --password "my_password"
stc-cli decrypt --input my_document.pdf.enc --password "my_password"

# Get profile recommendations
stc-cli analyze --input my_file.pdf
```

### Profile Detection (Python)

```python
from core.profiles import get_profile_for_file, get_optimized_parameters
from stc import STCContext

# Detect appropriate profile for file type
profile = get_profile_for_file("tax_documents.pdf")  # Returns "document"
params = get_optimized_parameters(profile, file_size=2048000)

# Encrypt with profile-specific parameters
ctx = STCContext("my-app")
encrypted, metadata = ctx.encrypt_file("tax_documents.pdf", "password", profile_params=params)
```

### Content Analysis (Advanced)

```python
from core.profiles import SecurityProfileManager

# Pattern matching analyzes content and recommends security settings
result = SecurityProfileManager.analyze_and_recommend(
    file_path="sensitive_data.pdf"
)
print(f"Recommended: {result['recommended_profile']}")  # e.g., "FINANCIAL_DATA"
print(f"Reason: {result['analysis_reason']}")
```

### 🛠️ **Traditional Programming** (Full Control)

```python
from stc import STCContext

# Manual approach for developers
ctx = STCContext("my-app")
encrypted, metadata = ctx.encrypt(b"secret message", password="strong_password")
decrypted = ctx.decrypt(encrypted, metadata, password="strong_password")
```

### ✅ **Check Encryption Quality**

```python
health = ctx.get_entropy_health()
print(f"Quality: {health['status']}")  # excellent/good/fair/poor
```

---

## Getting Help

### Resources

- **This Manual**: Start here for all basics
- **[Usage Guide](../usage-guide.md)**: More advanced examples
- **[API Reference](../api-reference.md)**: Complete technical documentation
- **[GitHub Issues](https://github.com/Seigr-lab/SeigrToolsetCrypto/issues)**: Report bugs or ask questions

### Community

- **GitHub Discussions**: Ask questions and share tips
- **Examples**: See [examples/](../../examples/) for complete working code

### Before You Ask for Help

1. Check **[Chapter 5: Troubleshooting](05-troubleshooting.md)** for common issues
2. Read error messages carefully - they often explain the problem
3. Try the simplest possible example first
4. Include your code and error message when asking for help

---

## Safety Tips

⚠️ **Critical Security Advice**:

1. **Never hardcode passwords** - Always load from secure storage
2. **Protect metadata files** - They're as sensitive as encrypted data
3. **Use strong passwords** - At least 12 characters, random is best
4. **Backup your data** - Keep copies before encryption experiments
5. **Test decryption** - Always verify you can decrypt before deleting originals

✅ **Good Habits**:

- Use unique seeds for each application
- Include context data for extra security
- Check entropy health periodically
- Keep STC updated to latest version
- Store encrypted files and metadata separately

---

## Example Projects

Want to see STC in action? Check out these complete examples:

1. **[Password Manager](../../examples/password_manager/)** - Store passwords securely
2. **[Configuration Encryption](../../examples/config_encryption/)** - Protect API keys and secrets
3. **[Validation Examples](../../examples/validation/)** - Test STC features

Each example includes:

- Complete working code
- Explanations of how it works
- Common pitfalls to avoid

---

## Let's Get Started!

Ready to learn? Head to **[Chapter 1: Getting Started](01-getting-started.md)** to begin your journey.

If you get stuck, remember:

- **Errors are normal** - use Chapter 5 to understand them
- **Start simple** - try basic examples before complex ones
- **Ask for help** - we're here to support you

This concludes the user manual.

---

---

**Last Updated**: November 19, 2025  
**Test Coverage**: 91.42% (246+ tests passing)
