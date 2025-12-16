# Chapter 4: Advanced Usage

Learn advanced STC features including high-performance streaming, P2P encryption, context data, and performance optimization.

## What You'll Learn

- ✓ How to use StreamingContext for P2P applications
- ✓ How to encrypt large files efficiently
- ✓ What "context data" is and when to use it
- ✓ How to make encryption faster
- ✓ How to manage encryption state
- ✓ Performance tips and tricks

---

## StreamingContext for P2P Applications

### What is StreamingContext?

**StreamingContext** is a high-performance interface designed specifically for real-time streaming applications:

- **P2P Video/Audio**: SeigrToolsetTransmissions integration
- **Real-Time Data**: Live sensor data, telemetry, analytics
- **Game State Sync**: Multiplayer game encryption
- **Low-Latency Requirements**: <50ms encryption per frame

### Performance Characteristics

**Benchmark Results** (30 FPS, 5KB frames):
- **FPS**: 132.9 (443% over 30 FPS target)
- **Latency**: 7.52ms per frame (85% under 50ms target)
- **Overhead**: 0.31% (16 bytes per frame)
- **Throughput**: 0.65 MB/s sustained

### Basic Usage

```python
from interfaces.api.streaming_context import StreamingContext

# Initialize streaming context with shared seed
stream_ctx = StreamingContext('session_abc123')

# Encrypt streaming frame (video, audio, real-time data)
frame_data = b'...'  # Your frame data
header, encrypted = stream_ctx.encrypt_chunk(frame_data)

# Fixed 16-byte header for network transmission
header_bytes = header.to_bytes()

# Decrypt frame
decrypted = stream_ctx.decrypt_chunk(header, encrypted)
```

### Session Handshake Pattern

```python
# Server: Create session and share metadata
server_ctx = StreamingContext('shared_seed_abc123')
session_metadata = server_ctx.get_stream_metadata()  # 9 bytes
send_to_client(session_metadata)

# Client: Reconstruct session from same seed
client_ctx = StreamingContext('shared_seed_abc123')
# Server and client now use identical key schedules
# Encryption/decryption synchronized via chunk sequence numbers
```

### Adaptive Chunking

StreamingContext automatically optimizes performance based on frame size:

```python
# Small frames: Direct encryption (no splitting)
small_frame = b'X' * 4096  # 4KB
h1, e1 = stream_ctx.encrypt_chunk(small_frame)
print(h1.flags)  # 0x0000 (single chunk)

# Large frames: Automatic splitting into 8KB sub-chunks
large_frame = b'X' * 65536  # 64KB
h2, e2 = stream_ctx.encrypt_chunk(large_frame)
print(h2.flags)  # 0x0001 (multi-chunk flag)
print(f"Sub-chunks created: {stream_ctx.subchunks_created}")
```

### Performance Monitoring

```python
# Get performance statistics
stats = stream_ctx.get_performance_stats()

print(f"Chunks encrypted: {stats['chunks_encrypted']}")
print(f"Throughput: {stats['encrypt_throughput_mbps']:.2f} MB/s")
print(f"Avg latency: {stats['avg_encrypt_ms']:.2f}ms")
print(f"Sub-chunks: {stats['subchunks_created']}")
print(f"CEL depth: {stats['cel_depth']}")
```

### Configuration Options

```python
# Custom streaming context configuration
ctx = StreamingContext(
    seed='session_id',
    optimal_chunk_size=8192,           # 8KB optimal for DSF
    enable_adaptive_chunking=True,     # Auto-split large frames
    initial_depth=2,                   # Fast CEL init (depth 2)
    max_depth=6,                       # Security ceiling (depth 6)
    key_schedule_size=256,             # Precomputed keys
    entropy_pool_size=1024,            # 1KB entropy pool
    key_rotation_mb=10                 # Rotate keys after 10 MB
)
```

### P2P Streaming Example

```python
from interfaces.api.streaming_context import StreamingContext, ChunkHeader

# Sender: Encrypt and transmit video frames
sender_ctx = StreamingContext('video_session_2024')

for frame in video_stream:
    # Encrypt frame
    header, encrypted = sender_ctx.encrypt_chunk(frame.data)
    
    # Network transmission
    send_packet(header.to_bytes() + encrypted)

# Receiver: Decrypt video frames
receiver_ctx = StreamingContext('video_session_2024')

while receiving:
    # Receive packet
    packet = receive_packet()
    
    # Extract header (first 16 bytes)
    header = ChunkHeader.from_bytes(packet[:16])
    encrypted = packet[16:]
    
    # Decrypt frame
    frame_data = receiver_ctx.decrypt_chunk(header, encrypted)
    
    # Display frame
    display_video_frame(frame_data)
```

### When to Use StreamingContext vs STCContext

**Use StreamingContext if:**
- Real-time streaming (video, audio, live data)
- High-frequency encryption (30+ operations/second)
- Low-latency requirements (<50ms)
- Minimal overhead needed (<1% metadata)
- P2P network transmission

**Use STCContext if:**
- File encryption (documents, archives)
- Infrequent operations (manual user actions)
- Maximum security needed (decoys, full CEL depth)
- Backward compatibility required
- Password-based encryption

---

## High-Performance File Streaming (v0.3.1)

### Performance Improvements

STC v0.3.1 introduces **Phase 2 Streaming** for large files - a complete performance overhaul:

- **Upfront Decoy Validation**: Identifies the real decoy using only the first 64KB
- **Constant Memory Usage**: Only 7MB RAM regardless of file size (supports >100GB files)
- **3-5x Faster Decryption**: Eliminates trial-and-error processing
- **Streaming Architecture**: Purpose-built for large file efficiency

### The Problem with Previous Versions

Old approach (trial-and-error decoy processing):

```python
# Previous versions tried each decoy until one worked
for decoy in metadata.decoys:
    try:
        result = decrypt_with_decoy(data, decoy)  # Could fail multiple times
        if result: return result
    except: continue  # Try next decoy - SLOW!
```

**Problems:**
- Multiple decryption attempts wasted time
- Memory usage grew with file size
- Large files could exhaust system memory

### The Solution: Phase 2 Streaming

**Step 1: Upfront Validation** (NEW!)

```python
from core.streaming import validate_chunk_fast

# Analyze ONLY first 64KB to find real decoy
chunk = data[:65536]  # First 64KB only
real_decoy_index, validation_info = validate_chunk_fast(chunk, metadata)

print(f"✓ Real decoy identified: #{real_decoy_index}")
print(f"✓ Validation took: {validation_info['validation_time']:.2f}s")
```

**Step 2: High-Performance Streaming**

```python
from core.streaming import stream_decrypt_file

# Stream decrypt using ONLY the real decoy - no trial and error!
stats = stream_decrypt_file(
    input_file='large_video.mp4.enc',
    output_file='large_video.mp4',
    metadata=metadata,
    password="my_password"
)

print(f"✓ Decrypted at {stats['throughput_mbps']:.1f} MB/s")
print(f"✓ Peak memory usage: {stats['peak_memory_usage'] / 1024**2:.1f} MB")
print(f"✓ Processed {stats['chunks_processed']} chunks")
```

**Phase 2 Benefits:**

- ✅ **Constant 7MB Memory**: Same RAM usage for 1MB or 100GB files
- ✅ **3-5x Faster**: Upfront validation eliminates wasted decryption attempts  
- ✅ **No Trial-and-Error**: Direct decryption using identified real decoy
- ✅ **Unlimited File Size**: Successfully tested with >100GB files
- ✅ **Automatic Optimization**: Detects decoy strategy and optimizes accordingly
- ✅ **Real-time Stats**: Throughput, memory usage, and performance metrics

### Encrypting Large Files with Progress

```python
from stc import STCContext
import os

def encrypt_large_file(input_file, output_file, password):
    """Encrypt a large file with progress bar"""
    ctx = STCContext('large-file-seed')
    
    # Get file size
    file_size = os.path.getsize(input_file)
    print(f"Encrypting {file_size / 1024 / 1024:.2f} MB file...")
    
    # Progress callback function
    def show_progress(current_bytes, total_bytes):
        percent = (current_bytes / total_bytes) * 100
        mb_done = current_bytes / 1024 / 1024
        mb_total = total_bytes / 1024 / 1024
        print(f"Progress: {percent:.1f}% ({mb_done:.1f}/{mb_total:.1f} MB)", end='\r')
    
    # Encrypt with streaming
    metadata = ctx.encrypt_stream(
        input_path=input_file,
        output_path=output_file,
        password=password,
        chunk_size=1048576,  # 1 MB chunks
        progress_callback=show_progress
    )
    
    # Save metadata
    import pickle
    with open(f"{output_file}.meta", 'wb') as meta_file:
        pickle.dump(metadata, meta_file)
    
    print(f"\n✓ Encrypted: {output_file}")
    return metadata

# Example: Encrypt a 500 MB video file
encrypt_large_file('movie.mp4', 'movie_encrypted.bin', 'strong_password')
```

**Output:**

```
Encrypting 500.00 MB file...
Progress: 47.2% (236.0/500.0 MB)
```

### Decrypting Large Files

```python
import pickle
from stc import STCContext

def decrypt_large_file(encrypted_file, output_file, password):
    """Decrypt a large file with progress"""
    ctx = STCContext('large-file-seed')
    
    # Load metadata
    with open(f"{encrypted_file}.meta", 'rb') as meta_file:
        metadata = pickle.load(meta_file)
    
    # Progress callback
    def show_progress(current_bytes, total_bytes):
        percent = (current_bytes / total_bytes) * 100
        mb_done = current_bytes / 1024 / 1024
        mb_total = total_bytes / 1024 / 1024
        print(f"Progress: {percent:.1f}% ({mb_done:.1f}/{mb_total:.1f} MB)", end='\r')
    
    # Decrypt with streaming
    ctx.decrypt_stream(
        input_path=encrypted_file,
        metadata=metadata,
        output_path=output_file,
        password=password,
        chunk_size=1048576,
        progress_callback=show_progress
    )
    
    print(f"\n✓ Decrypted: {output_file}")

# Example: Decrypt the video file
decrypt_large_file('movie_encrypted.bin', 'movie_restored.mp4', 'strong_password')
```

### When to Use Streaming

| File Size | Recommendation |
|-----------|----------------|
| < 50 MB | Regular encryption (faster, simpler) |
| 50 MB - 500 MB | Either works (your choice) |
| > 500 MB | **Use streaming** (avoid memory issues) |

**Note:** Current version (v0.3.0) has a known issue with streaming decrypt for files >100 MB. Use regular decrypt for very large files until v0.3.1.

---

## Context Data

### What Is Context Data?

Context data is extra information you can attach to encryption. It makes the encrypted data UNIQUE even if the password and message are the same.

Think of it like adding a secret ingredient to a recipe - same recipe, different ingredient = different result!

### Basic Context Data Usage

```python
from stc import STCContext

ctx = STCContext('my-seed')

# Encrypt with context data
encrypted1, meta1 = ctx.encrypt(
    "Same message",
    password="same_password",
    context_data={"user": "alice"}
)

encrypted2, meta2 = ctx.encrypt(
    "Same message",
    password="same_password",
    context_data={"user": "bob"}
)

# Different encrypted results!
assert encrypted1 != encrypted2

print("✓ Same message + password = different encryption due to context!")
```

### Why Use Context Data?

**1. Multi-user systems:**

```python
# Each user gets different encryption for same data
def encrypt_for_user(data, password, user_id):
    ctx = STCContext('app-seed')
    
    encrypted, metadata = ctx.encrypt(
        data,
        password=password,
        context_data={'user_id': user_id}
    )
    
    return encrypted, metadata

# Alice's encryption
alice_enc, alice_meta = encrypt_for_user("shared data", "pw", "alice@example.com")

# Bob's encryption
bob_enc, bob_meta = encrypt_for_user("shared data", "pw", "bob@example.com")

# Different encrypted results even though message and password are same!
```

**2. Time-based encryption:**

```python
import time

def encrypt_with_timestamp(data, password):
    """Encryption includes timestamp"""
    ctx = STCContext('time-seed')
    
    timestamp = int(time.time())
    
    encrypted, metadata = ctx.encrypt(
        data,
        password=password,
        context_data={'timestamp': timestamp}
    )
    
    return encrypted, metadata, timestamp

# Each encryption is unique due to different timestamps
enc1, meta1, time1 = encrypt_with_timestamp("data", "pw")
time.sleep(1)  # Wait 1 second
enc2, meta2, time2 = encrypt_with_timestamp("data", "pw")

# Different encryptions!
assert enc1 != enc2
```

**3. Purpose-based encryption:**

```python
def encrypt_with_purpose(data, password, purpose):
    """Different encryption for different purposes"""
    ctx = STCContext('purpose-seed')
    
    encrypted, metadata = ctx.encrypt(
        data,
        password=password,
        context_data={'purpose': purpose}
    )
    
    return encrypted, metadata

# Same data, different purposes = different encryption
backup_enc, backup_meta = encrypt_with_purpose("data", "pw", "backup")
share_enc, share_meta = encrypt_with_purpose("data", "pw", "sharing")
archive_enc, archive_meta = encrypt_with_purpose("data", "pw", "archive")

# All different!
```

### Decrypting with Context Data

**IMPORTANT:** You MUST use the SAME context data to decrypt!

```python
# Encrypt with context
encrypted, metadata = ctx.encrypt(
    "Secret data",
    password="pw",
    context_data={'user': 'alice', 'role': 'admin'}
)

# ✓ Correct - same context
decrypted = ctx.decrypt(
    encrypted,
    metadata,
    password="pw",
    context_data={'user': 'alice', 'role': 'admin'}
)

# ❌ Wrong - different context (will fail or produce garbage!)
try:
    wrong_decrypt = ctx.decrypt(
        encrypted,
        metadata,
        password="pw",
        context_data={'user': 'bob', 'role': 'admin'}
    )
except Exception:
    print("❌ Wrong context - decryption failed!")
```

### Practical Context Data Examples

**Example: Session-based encryption**

```python
import uuid

def create_session_encryption():
    """Each session gets unique encryption"""
    session_id = str(uuid.uuid4())
    
    ctx = STCContext('session-seed')
    
    encrypted, metadata = ctx.encrypt(
        "Session data",
        password="session_pw",
        context_data={'session_id': session_id}
    )
    
    return encrypted, metadata, session_id

# Create session
enc, meta, session = create_session_encryption()

# Later, decrypt with session ID
decrypted = ctx.decrypt(enc, meta, password="session_pw", context_data={'session_id': session})
```

**Example: Role-based access**

```python
def encrypt_with_access_control(data, password, user_role):
    """Only users with matching role can decrypt"""
    ctx = STCContext('rbac-seed')
    
    encrypted, metadata = ctx.encrypt(
        data,
        password=password,
        context_data={'required_role': user_role}
    )
    
    return encrypted, metadata

# Encrypt for admins only
admin_enc, admin_meta = encrypt_with_access_control(
    "Admin-only data",
    password="admin_pw",
    user_role="admin"
)

# Admin can decrypt
decrypted = ctx.decrypt(admin_enc, admin_meta, password="admin_pw", context_data={'required_role': 'admin'})

# Regular user cannot decrypt (even with password!)
try:
    ctx.decrypt(admin_enc, admin_meta, password="admin_pw", context_data={'required_role': 'user'})
except:
    print("❌ Access denied - wrong role!")
```

---

## State Management

### What Is State?

STC's encryption changes over time. The "state" is a snapshot of where things are at any moment. Saving and loading state lets you:

- Pause and resume encryption
- Synchronize multiple processes
- Rollback to previous encryption state

### Saving State

```python
from stc import STCContext

ctx = STCContext('my-seed')

# Do some operations
ctx.hash("operation1")
ctx.hash("operation2")
encrypted, meta = ctx.encrypt("data", password="pw")

# Save complete state
state = ctx.save_state()

print(f"State keys: {list(state.keys())}")
# Output: ['cel_state', 'phe_state', 'pcf_state']
```

### Loading State

```python
# Create new context
ctx2 = STCContext('my-seed')

# Load saved state
ctx2.load_state(state)

# ctx2 now has IDENTICAL state to ctx!
# Same encryption behavior, same evolution
```

### Practical State Management

**Example: Checkpoint long process**

```python
import pickle

def encrypt_with_checkpoints(items, checkpoint_file):
    """Encrypt items with periodic checkpoints"""
    ctx = STCContext('checkpoint-seed')
    results = []
    
    for i, item in enumerate(items):
        # Encrypt item
        encrypted, metadata = ctx.encrypt(item, password="pw")
        results.append((encrypted, metadata))
        
        # Save checkpoint every 100 items
        if i % 100 == 0:
            state = ctx.save_state()
            with open(checkpoint_file, 'wb') as f:
                pickle.dump({'state': state, 'progress': i, 'results': results}, f)
            print(f"✓ Checkpoint saved at item {i}")
    
    return results

# Process 1000 items with checkpoints
items = [f"Item {i}" for i in range(1000)]
encrypt_with_checkpoints(items, 'checkpoint.dat')
```

**Example: Resume from checkpoint**

```python
import pickle

def resume_encryption(items, checkpoint_file):
    """Resume from saved checkpoint"""
    # Load checkpoint
    with open(checkpoint_file, 'rb') as f:
        checkpoint = pickle.load(f)
    
    # Create context and restore state
    ctx = STCContext('checkpoint-seed')
    ctx.load_state(checkpoint['state'])
    
    # Resume from where we left off
    progress = checkpoint['progress']
    results = checkpoint['results']
    
    print(f"Resuming from item {progress}...")
    
    for i in range(progress, len(items)):
        encrypted, metadata = ctx.encrypt(items[i], password="pw")
        results.append((encrypted, metadata))
    
    return results
```

---

## Performance Optimization

### 1. Reuse Context (Most Important!)

```python
# ❌ SLOW - Creates new context every time (very expensive!)
for item in items:
    ctx = STCContext('same-seed')  # DON'T DO THIS!
    encrypted, meta = ctx.encrypt(item, password="pw")

# ✓ FAST - Reuse context
ctx = STCContext('same-seed')  # Create ONCE
for item in items:
    encrypted, meta = ctx.encrypt(item, password="pw")
```

**Performance difference:** 10-100x faster!

### 2. Batch Similar Data

```python
import json

# ❌ SLOW - Encrypt each item separately
items = ["item1", "item2", "item3"]
for item in items:
    encrypted, meta = ctx.encrypt(item, password="pw")
    # 3 encryptions + 3 metadata (~1.4 MB total)

# ✓ FAST - Encrypt as batch
items_json = json.dumps(items)
encrypted, metadata = ctx.encrypt(items_json, password="pw")
# 1 encryption + 1 metadata (~486 KB total)

# Decrypt and unpack
decrypted_json = ctx.decrypt(encrypted, metadata, password="pw")
items_restored = json.loads(decrypted_json)
```

### 3. Choose Right Lattice Size

```python
# For speed (non-critical data)
ctx_fast = STCContext('seed', lattice_size=64, depth=4)
# Encryption: ~0.5s, Metadata: ~150 KB

# For balance (default)
ctx_normal = STCContext('seed')  # 128×128×6
# Encryption: ~1.8s, Metadata: ~486 KB

# For security (critical data)
ctx_secure = STCContext('seed', lattice_size=256, depth=8)
# Encryption: ~8s, Metadata: ~1.8 MB
```

### 4. Disable Decoys for Speed

```python
# ✓ If data is not sensitive, disable decoys for speed
encrypted, metadata = ctx.encrypt(
    non_sensitive_data,
    password="pw",
    use_decoys=False  # Faster encryption/decryption
)
```

### 5. Monitor and Refresh Entropy Wisely

```python
ctx = STCContext('my-seed')
operations = 0

for item in items:
    # Check health every 100 operations (not every time!)
    if operations % 100 == 0:
        health = ctx.get_entropy_health()
        if health['quality_score'] < 0.7:
            ctx.cel.update()
    
    encrypted, meta = ctx.encrypt(item, password="pw")
    operations += 1
```

### 6. Use Streaming for Large Files

```python
# ❌ SLOW - Loads entire file into memory
with open('large.bin', 'rb') as f:
    data = f.read()
encrypted, meta = ctx.encrypt(data, password="pw")

# ✓ FAST - Constant memory usage
metadata = ctx.encrypt_stream(
    input_path='large.bin',
    output_path='large.enc',
    password="pw"
)
```

---

## Performance Comparison

### Small Files (<1 MB)

| Method | Time | Memory | Metadata Size |
|--------|------|--------|---------------|
| Regular encrypt | 0.9s | 10 MB | 486 KB |
| Streaming encrypt | 1.2s | 8 MB | 486 KB |

**Recommendation:** Use regular encryption for small files.

### Large Files (500 MB)

| Method | Time | Memory | Metadata Size |
|--------|------|--------|---------------|
| Regular encrypt | 45s | 600 MB | 486 KB |
| Streaming encrypt | 50s | 8 MB | 486 KB |

**Recommendation:** Use streaming for large files to save memory!

### Batch vs Individual (100 items)

| Method | Total Time | Total Metadata |
|--------|-----------|----------------|
| Individual encrypt | 90s | 48 MB |
| Batch encrypt | 1.8s | 486 KB |

**Recommendation:** Batch similar data for huge speed gains!

---

## Practical Tips

### Tip 1: Profile Your Code

```python
import time

def encrypt_with_timing(data, password):
    """Measure encryption time"""
    start = time.time()
    
    encrypted, metadata = ctx.encrypt(data, password=password)
    
    elapsed = time.time() - start
    print(f"Encryption took {elapsed:.2f} seconds")
    
    return encrypted, metadata

# Use it
enc, meta = encrypt_with_timing("test data", "pw")
```

### Tip 2: Monitor Memory Usage

```python
import psutil
import os

def get_memory_usage():
    """Get current memory usage in MB"""
    process = psutil.Process(os.getpid())
    return process.memory_info().rss / 1024 / 1024

# Before encryption
mem_before = get_memory_usage()

# Encrypt
encrypted, metadata = ctx.encrypt(large_data, password="pw")

# After encryption
mem_after = get_memory_usage()

print(f"Memory used: {mem_after - mem_before:.2f} MB")
```

### Tip 3: Choose Right Chunk Size

```python
# For fast SSD/NVMe drives
metadata = ctx.encrypt_stream(
    input_path='file.bin',
    output_path='file.enc',
    password="pw",
    chunk_size=4194304  # 4 MB chunks (faster)
)

# For slow HDDs or network drives
metadata = ctx.encrypt_stream(
    input_path='file.bin',
    output_path='file.enc',
    password="pw",
    chunk_size=524288  # 512 KB chunks (more compatible)
)
```

---

## What's Next?

Continue to the final chapter:

- **[Chapter 5: Troubleshooting](05-troubleshooting.md)** - Fix common problems and errors

---

## Quick Reference

### Streaming Large Files

```python
# Encrypt
metadata = ctx.encrypt_stream(
    input_path='large.bin',
    output_path='large.enc',
    password="pw",
    chunk_size=1048576
)

# Decrypt
ctx.decrypt_stream(
    input_path='large.enc',
    metadata=metadata,
    output_path='large_restored.bin',
    password="pw"
)
```

### Context Data

```python
# Encrypt with context
encrypted, meta = ctx.encrypt(
    data,
    password="pw",
    context_data={'user': 'alice', 'purpose': 'backup'}
)

# Decrypt with SAME context
decrypted = ctx.decrypt(
    encrypted,
    meta,
    password="pw",
    context_data={'user': 'alice', 'purpose': 'backup'}
)
```

### State Management

```python
# Save state
state = ctx.save_state()

# Load state
ctx2 = STCContext('same-seed')
ctx2.load_state(state)
```

### Performance

```python
# Fast mode
ctx = STCContext('seed', lattice_size=64, depth=4)
encrypted, meta = ctx.encrypt(data, password="pw", use_decoys=False)

# Reuse context
ctx = STCContext('seed')  # Once!
for item in items:
    encrypted, meta = ctx.encrypt(item, password="pw")

# Batch data
import json
batch = json.dumps(items)
encrypted, meta = ctx.encrypt(batch, password="pw")
```

You now have comprehensive knowledge of STC advanced features.
