# Chapter 2B: Command Line Usage

**🖥️ Using STC Without Programming**

Don't want to write code? Use STC directly from your terminal or command prompt with simple commands.

---

## Installation & Setup

### Install STC CLI
```bash
# Install STC (includes CLI)
pip install seigr-toolset-crypto

# Verify installation
stc-cli --version
```

### First-Time Setup
```bash
# Test with a simple file
echo "Hello World" > test.txt
stc-cli encrypt --input test.txt --password "my_test_password"
stc-cli decrypt --input test.txt.enc --password "my_test_password"
```

---

## Basic Commands

### 🔐 Encrypt a File

```bash
# Basic encryption (auto-detects profile)
stc-cli encrypt --input document.pdf --password "your_password"

# Specify output location
stc-cli encrypt --input document.pdf --output secure_document.enc --password "your_password"

# Use specific profile
stc-cli encrypt --input document.pdf --profile credentials --password "your_password"
```

### 🔓 Decrypt a File

```bash
# Basic decryption (auto-finds metadata)
stc-cli decrypt --input document.pdf.enc --password "your_password"

# Specify output location
stc-cli decrypt --input secure_document.enc --output document.pdf --password "your_password"

# Specify metadata file (if needed)
stc-cli decrypt --input document.pdf.enc --metadata document.pdf.meta --password "your_password"
```

### 🤔 Get Recommendations

```bash
# Ask STC what profile to use
stc-cli recommend --file my_document.pdf
stc-cli recommend --file family_photo.jpg
stc-cli recommend --file passwords.txt
```

**Example Output**:
```
📄 File: my_document.pdf (2.3 MB)
✅ Recommended Profile: document
📝 Reason: Balanced security and performance for office documents
⚡ Expected Speed: Medium
🔒 Security Level: Good
📦 Metadata Size: ~47 KB
```

---

## Real-World Examples

### 📄 Encrypting Work Documents

```bash
# Encrypt your resume
stc-cli encrypt --input resume.pdf --password "secure_resume_2024"

# Encrypt multiple documents
stc-cli encrypt --input contract.docx --password "business_docs"
stc-cli encrypt --input invoice.xlsx --password "business_docs"
stc-cli encrypt --input presentation.pptx --password "business_docs"
```

### 📸 Securing Personal Photos

```bash
# Single photo
stc-cli encrypt --input vacation_photo.jpg --password "family_memories"

# All photos in a folder (bash/Linux)
for file in *.jpg; do
    stc-cli encrypt --input "$file" --password "family_memories"
done

# All photos in a folder (Windows)
for %f in (*.jpg) do stc-cli encrypt --input "%f" --password "family_memories"
```

### 🔐 Protecting Sensitive Files

```bash
# Use maximum security for sensitive data
stc-cli encrypt --input tax_documents.pdf --profile credentials --password "ultra_secure_2024"

# Encrypt password database
stc-cli encrypt --input passwords.kdbx --profile credentials --password "master_password"
```

### 📦 Bulk Backup Encryption

```bash
# Fast encryption for large backups
stc-cli encrypt --input system_backup.zip --profile backup --password "backup_key_2024"

# Multiple backup files
stc-cli encrypt --input backup_part1.tar.gz --profile backup --password "backup_key"
stc-cli encrypt --input backup_part2.tar.gz --profile backup --password "backup_key"
```

---

## Folder Operations

### Encrypt Entire Folders

```bash
# Encrypt all files in a folder
stc-cli encrypt-folder --input "My Documents" --password "folder_password"

# Encrypt with specific profile
stc-cli encrypt-folder --input "Family Photos" --profile media --password "photo_password"

# Exclude certain file types
stc-cli encrypt-folder --input "Work Files" --exclude "*.tmp,*.log" --password "work_password"
```

### Decrypt Entire Folders

```bash
# Decrypt all encrypted files in folder
stc-cli decrypt-folder --input "My Documents" --password "folder_password"

# Decrypt to different location
stc-cli decrypt-folder --input "encrypted_folder" --output "decrypted_folder" --password "folder_password"
```

---

## Advanced Options

### Working with Seeds

```bash
# Use specific seed for application isolation
stc-cli encrypt --input data.txt --seed "my-app-v1" --password "password"

# Decrypt with same seed
stc-cli decrypt --input data.txt.enc --seed "my-app-v1" --password "password"
```

### Context Data (Extra Security)

```bash
# Add context for extra protection
stc-cli encrypt --input sensitive.doc --context "user=alice,dept=finance" --password "password"

# Must use same context to decrypt
stc-cli decrypt --input sensitive.doc.enc --context "user=alice,dept=finance" --password "password"
```

### Performance Options

```bash
# Use streaming for large files (>10MB)
stc-cli encrypt --input large_video.mp4 --stream --password "video_password"

# Check encryption quality
stc-cli encrypt --input document.pdf --check-quality --password "password"
```

---

## Helpful Commands

### 📊 Get File Information

```bash
# Analyze encrypted file
stc-cli info --input document.pdf.enc

# Check entropy health
stc-cli health --input document.pdf.enc --metadata document.pdf.meta
```

### 🔍 Verify Files

```bash
# Test if password is correct (without full decryption)
stc-cli verify --input document.pdf.enc --password "test_password"

# Verify file integrity
stc-cli integrity --input document.pdf.enc --metadata document.pdf.meta
```

### 🗂️ Batch Operations

```bash
# Encrypt all PDFs in current folder
stc-cli batch-encrypt --pattern "*.pdf" --password "pdf_password"

# Decrypt all encrypted files
stc-cli batch-decrypt --pattern "*.enc" --password "common_password"
```

---

## Common Usage Patterns

### Daily Document Security

```bash
#!/bin/bash
# encrypt_work.sh - Secure your work files

# Encrypt today's work
stc-cli encrypt-folder --input "Today's Work" --password "$WORK_PASSWORD"

# Quick backup
stc-cli encrypt --input important_notes.txt --profile credentials --password "$SECURE_PASSWORD"
```

### Photo Backup Routine

```bash
#!/bin/bash
# backup_photos.sh - Secure photo backup

# Fast encryption for photo collection
for folder in "2024-01" "2024-02" "2024-03"; do
    stc-cli encrypt-folder --input "$folder" --profile media --password "$PHOTO_PASSWORD"
done
```

### Secure File Sharing

```bash
# Prepare file for sharing
stc-cli encrypt --input shared_document.pdf --password "shared_password_2024"

# Recipient decrypts with same password
stc-cli decrypt --input shared_document.pdf.enc --password "shared_password_2024"
```

---

## Error Handling

### Common Issues

**Wrong password**:
```bash
stc-cli decrypt --input file.enc --password "wrong_password"
# Error: Authentication failed - incorrect password or corrupted data
```

**Missing metadata**:
```bash
stc-cli decrypt --input file.enc --password "correct_password"
# Error: Metadata file 'file.meta' not found
# Solution: Use --metadata to specify location
stc-cli decrypt --input file.enc --metadata "/path/to/file.meta" --password "correct_password"
```

**File not found**:
```bash
stc-cli encrypt --input nonexistent.txt --password "password"
# Error: Input file 'nonexistent.txt' not found
```

### Getting Help

```bash
# General help
stc-cli --help

# Command-specific help
stc-cli encrypt --help
stc-cli decrypt --help
stc-cli recommend --help
```

---

## Tips for Non-Technical Users

### 🔑 Password Management
- **Use strong passwords**: At least 12 characters, mix of letters/numbers/symbols
- **Don't reuse passwords**: Use different passwords for different files
- **Consider a password manager**: Let it generate strong passwords for you

### 📁 File Organization
- **Keep metadata safe**: Treat `.meta` files as secret as encrypted files
- **Backup before encrypting**: Always keep unencrypted backups until you verify decryption works
- **Test small files first**: Try encrypting/decrypting a test file before bulk operations

### ⚡ Performance Tips
- **Use correct profiles**: Let STC auto-detect or use recommendations
- **Stream large files**: Use `--stream` for files >10MB
- **Batch similar files**: Process files of same type together

### 🛡️ Security Best Practices
- **Use context data**: Add `--context` for extra security on sensitive files
- **Verify encryption**: Use `stc-cli verify` to test passwords
- **Monitor quality**: Use `--check-quality` for important files

---

## Windows Users

### PowerShell Examples

```powershell
# Encrypt all files in a folder
Get-ChildItem "*.pdf" | ForEach-Object { 
    stc-cli encrypt --input $_.Name --password "my_password" 
}

# Decrypt all encrypted files
Get-ChildItem "*.enc" | ForEach-Object { 
    stc-cli decrypt --input $_.Name --password "my_password" 
}
```

### Command Prompt Examples

```cmd
REM Encrypt multiple files
for %%f in (*.docx) do stc-cli encrypt --input "%%f" --password "office_docs"

REM Decrypt multiple files  
for %%f in (*.enc) do stc-cli decrypt --input "%%f" --password "office_docs"
```

---

## Next Steps

Now that you can use STC from command line:

1. **[Learn Security Features](03-security-features.md)** - Understand what makes your files secure
2. **[Try Advanced Usage](04-advanced-usage.md)** - Build complete solutions
3. **[Troubleshooting](05-troubleshooting.md)** - Solve common problems

**Remember**: The CLI makes STC accessible without programming. Start with simple commands and build up to more complex operations!

---

**💡 Pro Tips**:
- Use `stc-cli recommend` when unsure which profile to use
- Always test decryption before deleting originals
- Keep passwords secure - STC can't recover them if lost!