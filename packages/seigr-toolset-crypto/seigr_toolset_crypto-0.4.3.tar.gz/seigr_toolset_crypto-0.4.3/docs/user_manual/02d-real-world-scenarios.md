# Chapter 2D: Real-World Scenarios

**🌍 Practical Examples for Common Use Cases**

This chapter shows you exactly how to use STC for real-world situations that anyone might encounter.

---

## 🏠 **Personal & Family Use**

### 📸 **Scenario**: Securing Family Photos

**The Problem**: You have thousands of family photos and want to back them up securely to cloud storage.

**The Solution**:

```bash
# Method 1: Command Line (Easiest)
# Encrypt entire photo folder with media-optimized settings
stc-cli encrypt-folder --input "Family Photos 2024" --profile media --password "family_memories_2024"

# Upload encrypted folder to cloud storage
# Photos are now secure even if cloud storage is breached!
```

**Python Version**:
```python
from pathlib import Path
from stc import STCContext
from core.profiles import get_profile_for_file, get_optimized_parameters

def secure_family_photos(photo_folder, password):
    """Encrypt all family photos for secure cloud backup"""
    
    photo_folder = Path(photo_folder)
    ctx = STCContext("family-photos")
    
    for photo_path in photo_folder.rglob("*.jpg"):
        # Auto-detect media profile
        profile = get_profile_for_file(str(photo_path))
        params = get_optimized_parameters(profile, file_size=photo_path.stat().st_size)
        
        # Encrypt with media-optimized settings (fast, efficient)
        encrypted, metadata = ctx.encrypt_file(
            str(photo_path),
            password,
            profile_params=params
        )
        
        print(f"✅ Secured {photo_path.name}")

# Usage
secure_family_photos("Family Photos 2024", "family_memories_2024")
```

**Why This Works**:
- **Media profile** optimizes for large image files
- **Fast processing** won't take hours for thousands of photos
- **Secure cloud storage** - photos encrypted before upload
- **Easy recovery** - decrypt entire folder when needed

---

### 📄 **Scenario**: Protecting Important Documents

**The Problem**: You need to secure tax returns, insurance documents, birth certificates, and other important papers.

**The Solution**:

```bash
# Analyze documents to get perfect recommendations
stc-cli analyze --input "2024_Tax_Return.pdf"
stc-cli analyze --input "Birth_Certificate.pdf"
stc-cli analyze --input "Insurance_Policy.pdf"

# Encrypt with intelligent analysis
stc-cli encrypt --input "2024_Tax_Return.pdf" --intelligent --password "tax_docs_2024"
stc-cli encrypt --input "Birth_Certificate.pdf" --intelligent --password "important_docs_2024"
stc-cli encrypt --input "Insurance_Policy.pdf" --intelligent --password "insurance_secure_2024"
```

**Python Version with Content Analysis**:
```python
from core.profiles import AdvancedProfileManager
from stc import STCContext

def secure_important_documents(document_paths, passwords):
    """Intelligently secure important personal documents"""
    
    for doc_path, password in zip(document_paths, passwords):
        # AI analyzes document content
        analysis = AdvancedProfileManager.analyze_and_recommend(
            file_path=doc_path
        )
        
        print(f"📄 Document: {doc_path}")
        print(f"🔍 Detected: {analysis['content_type']}")
        print(f"🎯 Profile: {analysis['recommended_profile']}")
        print(f"📊 Confidence: {analysis['confidence_score']:.2f}")
        
        # Apply intelligent security
        ctx = STCContext("personal-documents")
        encrypted, metadata = ctx.encrypt_file(
            doc_path,
            password,
            intelligent_profile=analysis['recommended_profile']
        )
        
        print(f"✅ Secured with {analysis['security_level']} security\n")

# Usage
documents = [
    "2024_Tax_Return.pdf",
    "Birth_Certificate.pdf", 
    "Insurance_Policy.pdf"
]
passwords = [
    "tax_docs_2024",
    "important_docs_2024",
    "insurance_secure_2024"
]

secure_important_documents(documents, passwords)
```

---

## 💼 **Business & Professional Use**

### 📊 **Scenario**: Securing Client Files

**The Problem**: You're a consultant with sensitive client data that needs different security levels based on confidentiality.

**The Solution**:

```python
from core.profiles import AdvancedProfileManager
from stc import STCContext
import os

def secure_client_files(client_folder, client_name, confidentiality_level):
    """Secure client files with appropriate security level"""
    
    ctx = STCContext(f"client-{client_name}")
    
    # Security levels map to different approaches
    security_map = {
        "public": "DOCUMENT",           # Standard documents
        "confidential": "CORPORATE_COMMUNICATIONS",  # Business sensitive
        "restricted": "FINANCIAL_DATA", # Financial/legal data
        "classified": "CLASSIFIED_DOCUMENTS"  # Maximum security
    }
    
    target_profile = security_map.get(confidentiality_level, "DOCUMENT")
    password = f"{client_name}_client_data_2024"
    
    for root, dirs, files in os.walk(client_folder):
        for file in files:
            file_path = os.path.join(root, file)
            
            # Get intelligent recommendation
            analysis = AdvancedProfileManager.analyze_and_recommend(
                file_path=file_path
            )
            
            # Use higher of target level or AI recommendation
            final_profile = max(target_profile, analysis['recommended_profile'], 
                              key=lambda x: get_security_level_score(x))
            
            # Encrypt with chosen security level
            encrypted, metadata = ctx.encrypt_file(
                file_path,
                password,
                intelligent_profile=final_profile,
                context={"client": client_name, "confidentiality": confidentiality_level}
            )
            
            print(f"🔒 {file}: {final_profile} security")

def get_security_level_score(profile):
    """Return numeric security level for comparison"""
    levels = {
        "DOCUMENT": 1,
        "CORPORATE_COMMUNICATIONS": 2,
        "FINANCIAL_DATA": 3,
        "CLASSIFIED_DOCUMENTS": 4
    }
    return levels.get(profile, 1)

# Usage examples
secure_client_files("Client_ABC_Files", "ABC_Corp", "confidential")
secure_client_files("Client_XYZ_Legal", "XYZ_Inc", "restricted")
```

---

### 🏥 **Scenario**: HIPAA-Compliant Medical Records

**The Problem**: Healthcare provider needs to secure patient records with HIPAA compliance.

**The Solution**:

```python
from core.profiles import AdvancedProfileManager
from stc import STCContext
from datetime import datetime

def secure_medical_records(patient_folder, provider_id):
    """HIPAA-compliant medical record encryption"""
    
    ctx = STCContext(f"medical-{provider_id}")
    
    for root, dirs, files in os.walk(patient_folder):
        for file in files:
            file_path = os.path.join(root, file)
            
            # AI detects medical content
            analysis = AdvancedProfileManager.analyze_and_recommend(
                file_path=file_path,
                compliance_requirements=["HIPAA"]
            )
            
            # Generate HIPAA-compliant password
            patient_id = os.path.basename(root)  # Folder name = patient ID
            password = f"medical_{provider_id}_{patient_id}_2024"
            
            # Encrypt with medical-grade security
            encrypted, metadata = ctx.encrypt_file(
                file_path,
                password,
                intelligent_profile="MEDICAL_RECORDS",
                context={
                    "provider": provider_id,
                    "patient": patient_id,
                    "compliance": "HIPAA",
                    "date": datetime.now().isoformat()
                }
            )
            
            # Log for HIPAA audit trail
            print(f"📋 HIPAA: {file} encrypted for patient {patient_id}")
            print(f"   Security: {analysis['security_level']}")
            print(f"   Compliance: {analysis['compliance_verified']}")

# Usage
secure_medical_records("Patient_Records", "Provider_12345")
```

---

## 🔐 **High-Security Scenarios**

### 🏛️ **Scenario**: Government/Legal Documents

**The Problem**: Law firm handling classified or legally privileged documents.

**The Solution**:

```bash
# Maximum security command-line approach
stc-cli encrypt --input "Classified_Case_File.pdf" \
    --profile CLASSIFIED_DOCUMENTS \
    --context "classification=secret,clearance=top_secret" \
    --password "legal_case_ultra_secure_2024"

# Verify encryption strength
stc-cli analyze --input "Classified_Case_File.pdf.enc" --security-audit
```

**Python Version**:
```python
from core.profiles import AdvancedProfileManager, AdaptiveSecurityManager
from stc import STCContext

def secure_classified_documents(document_path, classification_level, clearance_level):
    """Maximum security for classified/privileged documents"""
    
    # Enable maximum security context
    ctx = STCContext("classified-legal")
    adaptive_security = AdaptiveSecurityManager()
    
    # AI analysis with security focus
    analysis = AdvancedProfileManager.analyze_and_recommend(
        file_path=document_path,
        security_priority="maximum",
        compliance_requirements=["CLASSIFIED", "ATTORNEY_CLIENT_PRIVILEGE"]
    )
    
    # Generate government-grade password
    password = f"classified_{classification_level}_{clearance_level}_2024"
    
    # Apply maximum security profile
    encrypted, metadata = ctx.encrypt_file(
        document_path,
        password,
        intelligent_profile="CLASSIFIED_DOCUMENTS",
        context={
            "classification": classification_level,
            "clearance": clearance_level,
            "privilege": "attorney_client",
            "security_level": "maximum"
        }
    )
    
    # Enable threat monitoring
    adaptive_security.enable_threat_monitoring(
        file_path=f"{document_path}.enc",
        alert_level="immediate"
    )
    
    print(f"🏛️ CLASSIFIED: {document_path} secured")
    print(f"   Classification: {classification_level}")
    print(f"   Security Level: MAXIMUM")
    print(f"   Threat Monitoring: ACTIVE")

# Usage
secure_classified_documents(
    "Classified_Case_File.pdf", 
    "secret", 
    "top_secret"
)
```

---

## 💻 **Developer & Technical Use**

### 🔑 **Scenario**: Securing Source Code and API Keys

**The Problem**: Developer needs to secure source code, API keys, and development credentials.

**The Solution**:

```bash
# Secure entire codebase
stc-cli encrypt-folder --input "MyProject" --profile SOURCE_CODE --password "dev_project_2024"

# Secure API keys with maximum security
stc-cli encrypt --input ".env" --profile DEVELOPER_CREDENTIALS --password "api_keys_ultra_secure"

# Secure database backups
stc-cli encrypt --input "db_backup.sql" --profile DATABASE_FILES --password "database_backup_2024"
```

**Python Version**:
```python
from core.profiles import AdvancedProfileManager
from stc import STCContext
import os

def secure_development_environment(project_folder, project_name):
    """Secure entire development environment"""
    
    ctx = STCContext(f"dev-{project_name}")
    
    # Define security levels for different file types
    security_mapping = {
        '.env': 'DEVELOPER_CREDENTIALS',    # Maximum security for secrets
        '.key': 'DEVELOPER_CREDENTIALS',
        '.pem': 'DEVELOPER_CREDENTIALS',
        '.sql': 'DATABASE_FILES',           # Database files
        '.py': 'SOURCE_CODE',               # Source code
        '.js': 'SOURCE_CODE',
        '.java': 'SOURCE_CODE',
        '.config': 'SYSTEM_CONFIGURATIONS'  # Config files
    }
    
    for root, dirs, files in os.walk(project_folder):
        # Skip version control and build directories
        dirs[:] = [d for d in dirs if d not in ['.git', '.vscode', 'node_modules', '__pycache__']]
        
        for file in files:
            file_path = os.path.join(root, file)
            file_ext = os.path.splitext(file)[1]
            
            # Use intelligent analysis
            analysis = AdvancedProfileManager.analyze_and_recommend(
                file_path=file_path
            )
            
            # Override with security mapping if available
            profile = security_mapping.get(file_ext, analysis['recommended_profile'])
            
            # Generate file-type specific password
            password = f"{project_name}_{profile.lower()}_2024"
            
            # Encrypt with appropriate security
            encrypted, metadata = ctx.encrypt_file(
                file_path,
                password,
                intelligent_profile=profile,
                context={
                    "project": project_name,
                    "file_type": profile,
                    "developer": os.getenv('USER', 'developer')
                }
            )
            
            print(f"💻 {file}: {profile}")

# Usage
secure_development_environment("MyWebApp", "webapp_v2")
```

---

## 🔄 **Backup & Archival Scenarios**

### 💾 **Scenario**: Encrypted System Backups

**The Problem**: Regular system backups need to be encrypted before cloud storage.

**The Solution**:

```bash
#!/bin/bash
# automated_backup.sh - Daily encrypted backup script

# Create system backup
tar -czf system_backup_$(date +%Y%m%d).tar.gz /home/user/important_files

# Encrypt with backup-optimized profile (fastest)
stc-cli encrypt \
    --input "system_backup_$(date +%Y%m%d).tar.gz" \
    --profile backup \
    --password "system_backup_2024_secure" \
    --stream  # Use streaming for large files

# Upload encrypted backup to cloud
# Original backup file can be safely deleted
rm "system_backup_$(date +%Y%m%d).tar.gz"

echo "✅ Encrypted backup uploaded to cloud"
```

**Python Version**:
```python
import os
import shutil
import datetime
from stc import STCContext
from core.profiles import get_optimized_parameters

def automated_encrypted_backup(source_paths, backup_destination, cloud_upload_func):
    """Automated encrypted backup system"""
    
    date_str = datetime.datetime.now().strftime("%Y%m%d")
    backup_name = f"system_backup_{date_str}"
    
    # Create compressed backup
    backup_path = f"{backup_name}.tar.gz"
    shutil.make_archive(backup_name, 'gztar', root_dir='/', base_dir=source_paths)
    
    # Get backup-optimized parameters
    params = get_optimized_parameters("backup", file_size=os.path.getsize(backup_path))
    
    # Encrypt with streaming for large files
    ctx = STCContext("system-backup")
    encrypted_path = ctx.encrypt_stream(
        input_path=backup_path,
        output_path=f"{backup_path}.enc",
        password="system_backup_2024_secure",
        profile_params=params
    )
    
    # Upload encrypted backup to cloud
    cloud_upload_func(f"{backup_path}.enc")
    
    # Clean up unencrypted backup
    os.remove(backup_path)
    
    print(f"✅ Encrypted backup {backup_name} created and uploaded")
    print(f"   Size: {os.path.getsize(f'{backup_path}.enc') / 1024 / 1024:.1f} MB")
    print(f"   Security: BACKUP profile (optimized for speed)")

# Usage with your cloud provider
def upload_to_cloud(file_path):
    # Your cloud upload logic here
    print(f"📤 Uploading {file_path} to cloud storage...")

automated_encrypted_backup(
    source_paths="home/user/important_files",
    backup_destination="/backups",
    cloud_upload_func=upload_to_cloud
)
```

---

## 🚨 **Emergency Scenarios**

### 🔓 **Scenario**: Emergency Document Access

**The Problem**: You need to give emergency access to encrypted documents to family/colleagues.

**The Solution**:

```python
from stc import STCContext
from core.profiles import get_profile_for_file

def create_emergency_access(document_path, emergency_contact, emergency_instructions):
    """Create emergency access to encrypted documents"""
    
    # Create separate emergency context
    emergency_ctx = STCContext("emergency-access")
    
    # Use simpler password for emergency access
    emergency_password = f"emergency_{emergency_contact}_2024"
    
    # Get appropriate profile
    profile = get_profile_for_file(document_path)
    
    # Create emergency-accessible copy
    emergency_encrypted, emergency_metadata = emergency_ctx.encrypt_file(
        document_path,
        emergency_password,
        context={
            "purpose": "emergency_access",
            "authorized_contact": emergency_contact,
            "instructions": emergency_instructions
        }
    )
    
    # Create emergency instructions file
    instructions = f"""
EMERGENCY ACCESS INSTRUCTIONS
============================

Document: {document_path}
Emergency Contact: {emergency_contact}
Password: {emergency_password}

INSTRUCTIONS:
{emergency_instructions}

To decrypt:
1. Install STC: pip install seigr-toolset-crypto
2. Run: stc-cli decrypt --input {document_path}.emergency.enc --password {emergency_password}

This file was created on {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
    
    with open(f"{document_path}.emergency_instructions.txt", "w") as f:
        f.write(instructions)
    
    print(f"🚨 Emergency access created for {document_path}")
    print(f"   Emergency contact: {emergency_contact}")
    print(f"   Instructions saved to: {document_path}.emergency_instructions.txt")

# Usage
create_emergency_access(
    "Important_Will.pdf",
    "spouse_name",
    "This document contains my will and testament. Contact my lawyer John Smith at 555-0123."
)
```

---

## 📱 **Mobile & Cross-Platform**

### 🔄 **Scenario**: Sync Encrypted Files Across Devices

**The Problem**: You want to access encrypted files on multiple devices (phone, tablet, laptop).

**The Solution**:

```python
import json
from stc import STCContext
from core.profiles import get_profile_for_file

def create_cross_platform_sync(file_path, sync_password, device_list):
    """Create encrypted files that sync across multiple devices"""
    
    # Use consistent context across all devices
    ctx = STCContext("cross-platform-sync")
    
    # Get profile for file
    profile = get_profile_for_file(file_path)
    
    # Create device-specific encryption
    sync_info = {
        "original_file": file_path,
        "profile": profile.value,
        "devices": device_list,
        "sync_password": sync_password,
        "created_date": datetime.datetime.now().isoformat()
    }
    
    # Encrypt for cross-platform access
    encrypted, metadata = ctx.encrypt_file(
        file_path,
        sync_password,
        context={
            "sync_enabled": True,
            "devices": device_list,
            "cross_platform": True
        }
    )
    
    # Create sync info file
    with open(f"{file_path}.sync_info.json", "w") as f:
        json.dump(sync_info, f, indent=2)
    
    print(f"🔄 Cross-platform sync enabled for {file_path}")
    print(f"   Devices: {', '.join(device_list)}")
    print(f"   Use same password '{sync_password}' on all devices")

# Usage
create_cross_platform_sync(
    "Important_Notes.pdf",
    "sync_password_2024",
    ["iPhone", "iPad", "Windows_Laptop", "Linux_Desktop"]
)
```

---

## 💡 **Tips for Real-World Usage**

### 🔑 **Password Management Strategy**

```python
# Good password patterns for different use cases:

# Personal files: descriptive + year
personal_password = "family_photos_2024"
tax_password = "tax_documents_2024"

# Business files: company + purpose + year  
client_password = f"{client_name}_project_files_2024"
financial_password = "company_financials_Q4_2024"

# High security: complex but memorable
classified_password = "ultra_secure_classified_docs_2024!"
```

### 📁 **File Organization Best Practices**

```bash
# Organize encrypted files clearly
Documents/
├── Personal/
│   ├── Tax_Returns.enc (tax_docs_2024)
│   ├── Birth_Certificate.enc (important_docs_2024)
│   └── Insurance.enc (insurance_2024)
├── Family/
│   ├── Photos_2024.enc (family_memories_2024)
│   └── Videos.enc (family_memories_2024)
└── Business/
    ├── Client_ABC.enc (client_abc_2024)
    └── Financial_Records.enc (business_finance_2024)
```

### ⚡ **Performance Optimization**

```python
# Choose the right profile for performance:

# Large media files (>100MB): Use MEDIA or BACKUP profile
# Small sensitive files (<10MB): Use CREDENTIALS profile  
# Office documents (1-100MB): Use DOCUMENT profile
# Bulk archives (>1GB): Use BACKUP profile with streaming

# Example:
if file_size > 100 * 1024 * 1024:  # >100MB
    profile = "MEDIA"  # Fast processing
elif file_size < 10 * 1024 * 1024:  # <10MB
    profile = "CREDENTIALS"  # Maximum security
else:
    profile = "DOCUMENT"  # Balanced
```

---

## Next Steps

Now that you've seen real-world scenarios:

1. **[Try Your Own Use Case](02b-command-line.md)** - Adapt these examples to your needs
2. **[Learn Advanced Security](03-security-features.md)** - Understand the security behind these examples
3. **[Build Complete Solutions](04-advanced-usage.md)** - Create automated systems

**Remember**: These scenarios show STC's flexibility. Adapt the patterns to your specific needs - STC makes it easy to secure anything!

---

**💡 Pro Tip**: Start with the simplest approach (command line with `--intelligent`), then customize as needed. STC's intelligent analysis handles most decisions automatically!