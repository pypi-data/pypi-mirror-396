# Chapter 2C: Automated Security Profiles

**🧠 Pattern-Based Security Recommendations**

STC's automated security system analyzes your files using pattern matching and heuristics to recommend optimal security settings. No technical knowledge required!

---

## How Does Automated Analysis Work?

Traditional encryption tools make you choose complex settings. STC's automated system:

- 🔍 **Analyzes file content** - Uses pattern matching to understand file types and content
- 🎯 **Detects sensitivity levels** - Automatically identifies sensitive data via regex patterns (SSN, credit cards, etc.)
- ⚙️ **Optimizes parameters** - Applies rule-based selection of 50+ security settings
- 🛡️ **Adapts to threats** - Adjusts security based on detected attack patterns
- 📊 **Uses heuristics** - Applies deterministic algorithms for optimal recommendations

---

## Automated Profiles Available

### 🏢 **Business & Professional**

- **FINANCIAL_DATA** - Tax documents, invoices, financial records
- **LEGAL_DOCUMENTS** - Contracts, agreements, legal correspondence  
- **MEDICAL_RECORDS** - Health data, insurance forms, medical files
- **CORPORATE_COMMUNICATIONS** - Internal memos, strategic documents

### 🏠 **Personal & Family**

- **PERSONAL_DOCUMENTS** - ID copies, certificates, personal records
- **FAMILY_PHOTOS** - Personal photos with face detection optimization
- **PERSONAL_COMMUNICATIONS** - Private messages, personal emails

### 💻 **Technical & Development**

- **SOURCE_CODE** - Programming files with syntax analysis
- **DATABASE_FILES** - Database backups, data exports
- **SYSTEM_CONFIGURATIONS** - Config files, system settings
- **DEVELOPER_CREDENTIALS** - API keys, certificates, development secrets

### 🔐 **High-Security Applications**

- **CLASSIFIED_DOCUMENTS** - Maximum security for sensitive data
- **RESEARCH_DATA** - Scientific data, research findings
- **INTELLECTUAL_PROPERTY** - Patents, proprietary information
- **GOVERNMENT_DOCUMENTS** - Official documents requiring high security

### 📱 **Digital Content**

- **SOCIAL_MEDIA_EXPORTS** - Backups of social media data
- **GAMING_DATA** - Game saves, gaming profiles
- **CRYPTOCURRENCY_WALLETS** - Crypto wallets and keys
- **DIGITAL_ART** - Creative works, digital assets

---

## How Content Analysis Works

### 🔍 **Automatic File Analysis**

```python
from core.profiles import AdvancedProfileManager

# Analyze any file automatically
result = AdvancedProfileManager.analyze_and_recommend(
    file_path="my_document.pdf",
    context="personal_use"
)

print(f"🎯 Recommended: {result['recommended_profile']}")
print(f"📊 Confidence: {result['confidence_score']:.2f}")
print(f"📝 Reason: {result['analysis_reason']}")
```

### 🧠 **What It Detects**

**Financial Content**:

- Bank account numbers, routing numbers
- Credit card patterns, tax ID numbers
- Financial terminology and amounts
- → Recommends `FINANCIAL_DATA` profile

**Medical Information**:

- Medical terminology, prescription names
- Insurance numbers, medical IDs
- Health-related keywords
- → Recommends `MEDICAL_RECORDS` profile

**Personal Identification**:

- SSN patterns, passport numbers
- Driver's license formats, addresses
- Personal identifiers
- → Recommends `PERSONAL_DOCUMENTS` profile

**Technical Content**:

- Code syntax patterns, API keys
- Database schemas, configuration syntax
- Programming languages detected
- → Recommends appropriate technical profile

---

## Real-World Examples

### 📊 **Tax Document Analysis**

```python
# STC analyzes your tax file content
result = AdvancedProfileManager.analyze_and_recommend(
    file_path="2024_tax_return.pdf"
)

print(f"Detected content: {result['content_type']}")        # "financial_document"
print(f"Sensitivity level: {result['sensitivity_level']}")  # "high"
print(f"Recommended profile: {result['recommended_profile']}")  # "FINANCIAL_DATA"
print(f"Security features: {result['security_features']}")  # ["enhanced_encryption", "audit_trail"]
```

### 👨‍⚕️ **Medical File Protection**

```python
# Automatically detects medical content
result = AdvancedProfileManager.analyze_and_recommend(
    file_path="lab_results.pdf"
)

# Automatically applies HIPAA-compliant security
print("Security measures applied:")
for feature in result['applied_security_measures']:
    print(f"  ✅ {feature}")

# Output:
# ✅ HIPAA-compliant encryption
# ✅ Enhanced audit logging  
# ✅ Multi-layer authentication
# ✅ Automatic key rotation
```

### 💻 **Source Code Protection**

```python
# Detects programming language and applies appropriate security
result = AdvancedProfileManager.analyze_and_recommend(
    file_path="api_server.py"
)

print(f"Detected language: {result['detected_language']}")    # "python"
print(f"Code complexity: {result['complexity_score']}")       # "medium"
print(f"Contains secrets: {result['contains_credentials']}")  # True
print(f"Profile: {result['recommended_profile']}")           # "DEVELOPER_CREDENTIALS"
```

---

## Adaptive Security Features

### 🛡️ **Threat-Aware Adjustment**

The intelligent system automatically adjusts security based on detected risks:

```python
from core.profiles import AdaptiveSecurityManager

# Security adapts to threats automatically
security_manager = AdaptiveSecurityManager()

# System detects brute force attempts
security_manager.detect_threat("brute_force_attempt")

# Automatically increases security
print("🚨 Threat detected - increasing security:")
print("  ⬆️ Encryption difficulty: +50%")
print("  ⬆️ Key rotation: Every 10 mins (was 60 mins)")  
print("  ⬆️ Decoy count: +200%")
```

### 📈 **Context-Aware Optimization**

```python
# Security adjusts based on usage context
result = security_manager.optimize_for_context(
    user_type="business_professional",
    environment="corporate_network", 
    compliance_requirements=["SOX", "GDPR"],
    performance_priority="security"
)

print("🎯 Context-optimized security:")
print(f"  📊 Compliance: {result['compliance_level']}")    # "enterprise"
print(f"  ⚡ Performance: {result['performance_impact']}")  # "minimal"
print(f"  🔒 Security level: {result['security_rating']}")  # "maximum"
```

---

## Command Line Usage

### 🤖 **Intelligent Analysis**

```bash
# Analyze any file and get intelligent recommendations
stc-cli analyze --input my_document.pdf

# Output:
# 📄 File: my_document.pdf (2.1 MB)
# 🔍 Content Type: financial_document
# 🎯 Recommended Profile: FINANCIAL_DATA
# 📊 Confidence Score: 0.94
# 🛡️ Security Level: high
# ⚡ Performance Impact: minimal
# 📝 Reason: Contains financial data patterns including account numbers and tax information
```

### 🎯 **Smart Encryption**

```bash
# Encrypt with intelligent profile selection
stc-cli encrypt --input sensitive_data.pdf --intelligent --password "secure_password"

# STC automatically:
# 1. Analyzes file content
# 2. Detects sensitivity level
# 3. Selects optimal profile
# 4. Applies context-aware security
# 5. Encrypts with perfect settings
```

### 📊 **Batch Intelligent Processing**

```bash
# Process entire folder with intelligent analysis
stc-cli encrypt-folder --input "Documents" --intelligent --password "folder_password"

# Each file gets individual analysis:
# 📄 tax_return.pdf → FINANCIAL_DATA profile
# 🏥 medical_record.pdf → MEDICAL_RECORDS profile  
# 📸 family_photo.jpg → FAMILY_PHOTOS profile
# 💻 source_code.py → SOURCE_CODE profile
```

---

## Advanced Features

### 🔄 **Profile Learning**

The system learns from your usage patterns:

```python
# System tracks your preferences
from core.profiles import ProfileLearningManager

learning_manager = ProfileLearningManager()

# After using STC for a while...
preferences = learning_manager.get_learned_preferences()

print("📚 Learned preferences:")
print(f"  🎯 Preferred security level: {preferences['security_preference']}")
print(f"  ⚡ Performance priority: {preferences['performance_priority']}")  
print(f"  📊 Common file types: {preferences['common_file_types']}")
print(f"  🛡️ Risk tolerance: {preferences['risk_tolerance']}")
```

### 🔍 **Deep Content Analysis**

For ultimate security, enable deep content analysis:

```python
# Enable advanced content scanning
result = AdvancedProfileManager.deep_analyze(
    file_path="complex_document.pdf",
    scan_depth="maximum",
    include_metadata=True,
    analyze_embedded_content=True
)

print("🔬 Deep analysis results:")
print(f"  📊 Content categories: {result['content_categories']}")
print(f"  🔍 Embedded files: {result['embedded_files']}")
print(f"  🏷️ Metadata tags: {result['metadata_tags']}")
print(f"  🛡️ Risk factors: {result['risk_factors']}")
```

### 🎛️ **Custom Intelligence Rules**

Advanced users can create custom analysis rules:

```python
# Define custom content detection rules
from core.profiles import ContentAnalysisRules

custom_rules = ContentAnalysisRules()

# Add custom pattern for your organization
custom_rules.add_pattern(
    name="company_confidential",
    pattern=r"ACME Corp Confidential|Internal Use Only",
    profile="CORPORATE_COMMUNICATIONS",
    security_level="high"
)

# Apply custom rules
result = AdvancedProfileManager.analyze_with_custom_rules(
    file_path="company_doc.pdf",
    custom_rules=custom_rules
)
```

---

## Profile Comparison: Basic vs Intelligent

| Feature | Basic Profiles | Intelligent Profiles |
|---------|---------------|---------------------|
| **Profiles** | 5 basic types | 19+ specialized types |
| **Detection** | File extension only | Content analysis + AI |
| **Optimization** | Static parameters | Dynamic optimization |
| **Threat Response** | Manual adjustment | Automatic adaptation |
| **Learning** | None | Learns from usage |
| **Compliance** | Generic security | Industry-specific |
| **Context Awareness** | Limited | Full context analysis |

---

## Privacy & Security

### 🔒 **Content Analysis Privacy**

**Important**: Content analysis happens **locally** on your device:

- ✅ **No data sent to servers** - Analysis runs on your computer
- ✅ **No content stored** - Only recommendations are saved
- ✅ **No tracking** - Your files remain completely private
- ✅ **Offline capable** - Works without internet connection

### 🛡️ **Analysis Security**

The analysis process itself is secure:

```python
# Analysis uses secure, isolated environment
result = AdvancedProfileManager.secure_analyze(
    file_path="sensitive.pdf",
    isolation_mode=True,      # Runs in isolated sandbox
    memory_protection=True,   # Protects analysis memory
    audit_trail=True         # Logs all analysis steps
)

print("🔒 Secure analysis completed:")
print(f"  ✅ Analysis isolated: {result['isolation_verified']}")
print(f"  🗑️ Memory cleared: {result['memory_cleared']}")
print(f"  📝 Audit trail: {result['audit_log_path']}")
```

---

## Getting Started with Intelligent Profiles

### 1️⃣ **Start Simple**

```bash
# Let STC choose everything automatically
stc-cli encrypt --input my_file.pdf --intelligent --password "my_password"
```

### 2️⃣ **Review Recommendations**

```bash
# See what STC detected before encrypting
stc-cli analyze --input my_file.pdf --verbose
```

### 3️⃣ **Customize If Needed**

```bash
# Override if you want different settings
stc-cli encrypt --input my_file.pdf --profile FINANCIAL_DATA --password "my_password"
```

### 4️⃣ **Learn and Improve**

```bash
# Check what the system learned about your preferences
stc-cli preferences --show-learned
```

---

## Troubleshooting

### ❓ **"Wrong profile recommended"**

If STC chooses the wrong profile:

```bash
# Provide context hints
stc-cli analyze --input my_file.pdf --context "financial,personal" --hint "tax_document"

# Or specify manually
stc-cli encrypt --input my_file.pdf --profile FINANCIAL_DATA --password "password"
```

### ❓ **"Analysis taking too long"**

For faster analysis:

```bash
# Use fast analysis mode
stc-cli encrypt --input my_file.pdf --intelligent --fast-analysis --password "password"
```

### ❓ **"Want to see what was detected"**

Get detailed analysis report:

```bash
# Full analysis breakdown
stc-cli analyze --input my_file.pdf --detailed --export-report analysis_report.json
```

---

## Next Steps

Now that you understand intelligent profiles:

1. **[Try Command Line](02b-command-line.md)** - Use intelligent features from CLI
2. **[Learn Security Features](03-security-features.md)** - Understand the advanced security
3. **[Advanced Usage](04-advanced-usage.md)** - Build complete intelligent solutions

**Remember**: Intelligent profiles make STC incredibly easy to use. Just enable `--intelligent` and let STC handle everything else!

---

**💡 Pro Tip**: Start with `stc-cli analyze` to see what STC detects about your files before encrypting. This helps you understand and trust the intelligent recommendations.
