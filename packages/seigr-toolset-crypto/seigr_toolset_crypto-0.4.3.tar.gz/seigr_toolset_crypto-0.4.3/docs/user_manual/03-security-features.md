# Chapter 3: Security Features

Learn about STC's advanced security features in simple terms - no technical jargon required!

## What You'll Learn

- ✓ What are "decoys" and why they protect you
- ✓ How to check if your encryption is healthy
- ✓ What "adaptive security" means
- ✓ How to use security features effectively
- ✓ When to enable or disable features

---

## Understanding Decoys

### What Are Decoys?

Imagine you're hiding a treasure chest in a room. Instead of just hiding ONE chest, you create several FAKE chests that look identical. An attacker who finds the room can't tell which chest is real!

That's exactly what STC's decoys do with your encrypted data.

### How Decoys Protect You

```python
from stc import STCContext

ctx = STCContext('my-seed')

# When you encrypt with decoys (ON by default)
encrypted, metadata = ctx.encrypt(
    "My secret password is 12345",
    password="encryption_pw",
    use_decoys=True  # This is ON by default
)
```

**What happens behind the scenes:**

1. STC creates the REAL encrypted version of your data
2. STC creates 3-7 FAKE encrypted versions (decoys)
3. All versions look identical - impossible to tell which is real
4. An attacker must try ALL of them (like trying 7 different keys)

**Result:** Your data is hidden among fake data. Even if someone steals your encrypted file, they can't tell which version is real!

### Decoys in Action

```python
# Example: Let's see what decoys look like
from stc import STCContext

ctx = STCContext('demo-seed')

# Encrypt with decoys
encrypted, metadata = ctx.encrypt(
    "Secret message",
    password="pw",
    num_decoys=3  # Create 3 decoy copies (1-5 actual due to randomization)
)

# Check metadata to see decoy information
print(f"Number of CEL snapshots: {len(metadata['cel_snapshots'])}")
# Output: Could be 1-5 (randomized for security)

# One of these is REAL, the others are DECOYS
# Attacker cannot tell which is which!
```

### Should You Use Decoys?

**✓ YES - Use decoys if:**

- You're encrypting sensitive data (passwords, financial info)
- You want maximum security
- Storage size is not a major concern (~486 KB metadata per file)

**❌ MAYBE NOT - Disable decoys if:**

- You're encrypting millions of small files (metadata overhead adds up)
- You need the absolute fastest performance
- Your data is not highly sensitive

**How to disable (NOT recommended):**

```python
# Disable decoys (less secure!)
encrypted, metadata = ctx.encrypt(
    "Less important data",
    password="pw",
    use_decoys=False  # No decoys = faster but less secure
)
```

---

## Entropy Health Monitoring

### What Is "Entropy"?

Think of entropy as the "randomness quality" of your encryption. 

- **High entropy** = Very random = Strong encryption = Hard to crack
- **Low entropy** = Predictable = Weak encryption = Easier to crack

STC has a built-in "health checker" that tells you if your encryption is strong or weak.

### Checking Encryption Health

```python
from stc import STCContext

ctx = STCContext('my-seed')

# Check the health of your encryption
health = ctx.get_entropy_health()

print(f"Encryption Quality: {health['status']}")
print(f"Score: {health['quality_score']:.2f}")
```

**Example output:**

```
Encryption Quality: excellent
Score: 0.92
```

### What Do Health Scores Mean?

| Score Range | Status | What It Means | Action Needed? |
|------------|---------|---------------|----------------|
| 0.85 - 1.0 | **Excellent** | Encryption is very strong | No action needed |
| 0.70 - 0.84 | **Good** | Fine for normal use | ✓ No action needed |
| 0.50 - 0.69 | **Fair** | Getting weak, should refresh | ⚠️ Consider refreshing |
| 0.00 - 0.49 | **Poor** | Too weak - do not encrypt | Refresh immediately |

### Refreshing Entropy

If your health score is low, refresh it:

```python
# Check health
health = ctx.get_entropy_health()

if health['quality_score'] < 0.7:
    print("⚠️ Entropy is getting weak...")
    
    # Refresh entropy
    ctx.cel.update()
    
    # Check again
    health = ctx.get_entropy_health()
    print(f"✓ Refreshed! New score: {health['quality_score']:.2f}")
```

### When Should You Check Health?

```python
# Good practice: Check before important encryption
ctx = STCContext('my-seed')

# Check health BEFORE encrypting sensitive data
health = ctx.get_entropy_health()

if health['quality_score'] < 0.7:
    print("Refreshing entropy for optimal security...")
    ctx.cel.update()

# Now encrypt with confidence
encrypted, metadata = ctx.encrypt(
    "Very sensitive data",
    password="strong_password"
)
```

**Recommendation:** Check health every 50-100 encryption operations, or before encrypting critical data.

---

## Adaptive Security Features

### What Is "Adaptive Security"?

Adaptive security means STC automatically adjusts its protection based on what's happening. Like a smart alarm system that increases security when it detects suspicious activity!

### Feature 1: Adaptive Morphing

**What it does:** STC changes its encryption pattern based on how random the data is becoming.

```python
# Enabled by default
encrypted, metadata = ctx.encrypt(
    "Data",
    password="pw",
    adaptive_morphing=True  # Automatically adjusts security
)
```

**How it works (simplified):**

- If data is becoming very random: "Things are changing fast, let's morph more often!"
- If data is stable: "Things are steady, we can morph less frequently"

**Why you care:** You get optimal security without having to configure anything!

### Feature 2: Adaptive Difficulty

**What it does:** STC automatically makes encryption harder if it detects an attack.

```python
# Enabled by default
encrypted, metadata = ctx.encrypt(
    "Data",
    password="pw",
    adaptive_difficulty=True  # Auto-defends against attacks
)
```

**How it works (simplified):**

- Normal operation: Fast, efficient encryption
- Attack detected: "Uh oh! Someone is trying to crack this! Make it MUCH harder!"
- Difficulty automatically doubles

**Why you care:** Automatic protection against hackers trying to break your encryption.

### Feature 3: Variable Decoy Sizes

**What it does:** Makes decoys different sizes so attackers can't identify the real one by size.

```python
encrypted, metadata = ctx.encrypt(
    "Data",
    password="pw",
    variable_decoy_sizes=True  # Default: ON
)
```

**How it works:**

- Real encrypted data: 128×128×6 (large and strong)
- Decoy #1: 32×32×3 (tiny)
- Decoy #2: 64×64×4 (medium)
- Decoy #3: 96×96×5 (large)

**Why you care:** Attacker can't just "pick the big one" - they all look different!

### Feature 4: Randomized Decoy Count

**What it does:** Changes the number of decoys randomly.

```python
encrypted, metadata = ctx.encrypt(
    "Data",
    password="pw",
    num_decoys=3,  # Base number
    randomize_decoy_count=True  # Actual count: 1-5
)
```

**Why you care:** Attacker can't predict how many decoys there are. Could be 1, could be 7!

---

## Using Security Features Effectively

### Maximum Security Configuration

For your most sensitive data:

```python
from stc import STCContext

ctx = STCContext('ultra-secure-seed')

# Check health first
health = ctx.get_entropy_health()
if health['quality_score'] < 0.85:
    ctx.cel.update()

# Encrypt with maximum security
encrypted, metadata = ctx.encrypt(
    "Top secret data",
    password="very_strong_password_123!",
    use_decoys=True,              # Use decoys
    num_decoys=5,                 # More decoys (actual: 3-7)
    variable_decoy_sizes=True,    # Random sizes
    randomize_decoy_count=True,   # Random count
    adaptive_morphing=True,       # Auto-adjust morphing
    adaptive_difficulty=True,     # Auto-defend
    timing_randomization=True     # Hide timing patterns
)

print("✓ Data encrypted with MAXIMUM security!")
```

**Use for:**

- Passwords and credentials
- Financial information
- Personal identification
- Private communications

### Balanced Security Configuration (Default)

For normal everyday use:

```python
# This is what you get by default - just call encrypt!
encrypted, metadata = ctx.encrypt(
    "Normal data",
    password="password"
    # All security features enabled by default
)
```

**Use for:**

- Regular documents
- Photos and videos
- Work files
- Most everyday encryption needs

### Fast Configuration (Less Secure)

For non-sensitive data where speed matters:

```python
from stc import STCContext

# Smaller lattice = faster
ctx = STCContext('fast-seed', lattice_size=64, depth=4)

encrypted, metadata = ctx.encrypt(
    "Non-sensitive data",
    password="pw",
    use_decoys=False,          # Disable decoys
    adaptive_morphing=False,   # Disable adaptive features
    adaptive_difficulty=False
)

print("✓ Encrypted quickly (but less secure)")
```

**Use for:**

- Temporary files
- Non-sensitive backups
- Testing and development
- Data that's already public

---

## Real-World Security Examples

### Example 1: Protecting Passwords

```python
from stc import STCContext
import json

def secure_password_storage():
    """Maximum security for passwords"""
    ctx = STCContext('password-vault-seed')
    
    # Check entropy health
    health = ctx.get_entropy_health()
    print(f"Vault health: {health['status']}")
    
    if health['quality_score'] < 0.85:
        print("Refreshing vault entropy...")
        ctx.cel.update()
    
    # Store password with maximum security
    password_data = {
        'service': 'bank.com',
        'username': 'user123',
        'password': 'MyBankPassword123!'
    }
    
    encrypted, metadata = ctx.encrypt(
        json.dumps(password_data),
        password="master_password",
        num_decoys=5,  # Maximum decoys
        timing_randomization=True  # Extra protection
    )
    
    print("✓ Password stored with maximum security")
    return encrypted, metadata

# Use it
enc, meta = secure_password_storage()
```

### Example 2: Protecting Documents

```python
from stc import STCContext

def encrypt_document(filepath, password):
    """Balanced security for documents"""
    ctx = STCContext('document-encryption')
    
    # Read document
    with open(filepath, 'rb') as f:
        data = f.read()
    
    # Check health every time for important docs
    health = ctx.get_entropy_health()
    if health['quality_score'] < 0.7:
        ctx.cel.update()
    
    # Encrypt with default security (balanced)
    encrypted, metadata = ctx.encrypt(data, password=password)
    
    # Save encrypted version
    with open(f"{filepath}.encrypted", 'wb') as f:
        f.write(encrypted)
    
    import pickle
    with open(f"{filepath}.meta", 'wb') as f:
        pickle.dump(metadata, f)
    
    print(f"✓ Document encrypted: {filepath}")

# Use it
encrypt_document("important_contract.pdf", "strong_password")
```

### Example 3: Fast Encryption for Logs

```python
from stc import STCContext
import datetime

def encrypt_log_entry(log_message):
    """Fast encryption for less sensitive logs"""
    # Smaller lattice for speed
    ctx = STCContext('logs-seed', lattice_size=64, depth=4)
    
    # Add timestamp
    timestamped = f"[{datetime.datetime.now()}] {log_message}"
    
    # Fast encryption (decoys disabled)
    encrypted, metadata = ctx.encrypt(
        timestamped,
        password="log_password",
        use_decoys=False  # Speed over security for logs
    )
    
    return encrypted, metadata

# Use it
enc, meta = encrypt_log_entry("User logged in successfully")
print("✓ Log entry encrypted (fast mode)")
```

---

## Security Checklist

Before encrypting important data, verify:

- [ ] **Strong password?** At least 12 characters, mixed case, numbers, symbols
- [ ] **Unique seed?** Don't use "default" or common seeds
- [ ] **Health check?** Score above 0.7 for important data
- [ ] **Decoys enabled?** Yes for sensitive data
- [ ] **Metadata saved?** Can't decrypt without it
- [ ] **Test decrypt?** Verify you can decrypt before deleting original
- [ ] **File permissions?** Only you can read encrypted files (chmod 600)
- [ ] **Backup metadata?** Store metadata in safe place

---

## Common Questions

### Q: Do decoys slow down encryption?

**A:** Yes, slightly. With 3-5 decoys:

- Encryption: ~0.3s slower (creates extra fake copies)
- Decryption: ~0.1s slower (tries each copy until success)
- For most users: This is worth the extra security!

### Q: How often should I check entropy health?

**A:** 

- **Before important encryption:** Always check
- **Regular use:** Every 50-100 operations
- **Long-running programs:** Every hour or after 1000 operations

### Q: Can I see the health score in numbers?

**A:** Yes!

```python
health = ctx.get_entropy_health()

print(f"Quality Score: {health['quality_score']:.2f}")
print(f"Unique Ratio: {health['unique_ratio']:.2f}")
print(f"Distribution: {health['distribution_score']:.2f}")
print(f"Total Updates: {health['update_count']}")
```

### Q: What if I forget to check health?

**A:** STC will still work, but encryption might be slightly weaker. Best practice: check periodically!

### Q: Should I always use maximum security?

**A:** No! Use maximum security for:

- Passwords and credentials
- Financial data
- Personal identification

Use default security for:

- Regular documents
- Photos/videos
- Most everyday files

Use fast security for:

- Temporary files
- Non-sensitive data
- Already public information

---

## What's Next?

Now that you understand security features, continue to:

- **[Chapter 4: Advanced Usage](04-advanced-usage.md)** - Streaming, context data, performance tips
- **[Chapter 5: Troubleshooting](05-troubleshooting.md)** - Fix common problems

---

## Quick Security Reference

```python
# Maximum security
health = ctx.get_entropy_health()
if health['quality_score'] < 0.85:
    ctx.cel.update()

encrypted, metadata = ctx.encrypt(
    sensitive_data,
    password="strong_password",
    num_decoys=5,
    timing_randomization=True
)

# Balanced security (default)
encrypted, metadata = ctx.encrypt(data, password="pw")

# Fast mode (less secure)
ctx = STCContext('seed', lattice_size=64, depth=4)
encrypted, metadata = ctx.encrypt(data, password="pw", use_decoys=False)
```

Remember: When in doubt, use default settings. They provide excellent security for most use cases! 🔒
