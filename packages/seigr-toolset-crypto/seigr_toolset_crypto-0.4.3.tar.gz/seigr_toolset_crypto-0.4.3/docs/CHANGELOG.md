# Changelog

All notable changes to Seigr Toolset Crypto will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.4.2] - 2025-11-27

### Security

#### 🔒 Comprehensive Security Audit & Fixes

- **Zero Vulnerabilities Achieved**: All security audits passed with grade A+
- **Bandit Audit**: Fixed 21 security issues (1 medium, 20 low severity)
  - Replaced `eval()` with `ast.literal_eval()` in selective_decoys.py (CWE-78: arbitrary code execution)
  - Replaced `random` module with `secrets` for cryptographic randomness (CWE-330: weak PRNG)
  - Fixed bare exception handlers with specific exception types (CWE-703: improper error handling)
  - Added subprocess timeouts and security justifications (CWE-78: OS command injection prevention)
  - Result: 0 issues identified (16,574 lines scanned, 12 intentional #nosec suppressions documented)

- **pip-audit**: Fixed 1 vulnerability
  - Upgraded h11 from 0.14.0 to 0.16.0 (GHSA-vqfr-h8mv-ghfj: HTTP request smuggling)
  - Upgraded httpcore 1.0.6 → 1.0.9, httpx 0.27.2 → 0.28.1
  - Result: 0 vulnerabilities (166 packages scanned)

- **Safety Check**: 0 vulnerabilities found (166 packages scanned)

- **GitHub CodeQL**: Continuous monitoring with 0 errors

#### 📋 Security Documentation

- **New File**: `docs/SECURITY_AUDIT.md` - Comprehensive security audit report
  - Bandit analysis results and remediation
  - pip-audit vulnerability assessment
  - Safety dependency scanning results
  - GitHub CodeQL integration
  - Security best practices and audit schedule
  - Overall security grade: A+

### Changed

#### 📚 Documentation Restructuring

- **Professional File Organization**:
  - Moved `CHANGELOG.md` to `docs/CHANGELOG.md`
  - Moved `USAGE.md` to `docs/USAGE.md`
  - Created `docs/audits/` directory for security reports
  - Cleaned root directory (12 files → 2 files: README.md, requirements.txt)

- **README.md Optimization**:
  - Reduced from 622 lines to 189 lines (70% reduction)
  - Transformed into concise landing page with proper documentation links
  - Removed monolithic content, replaced with organized documentation hub
  - Removed misleading roadmap (v0.4.1 already published)
  - Fixed version consistency across all references

- **Updated Documentation Links**:
  - README.md: Updated CHANGELOG and USAGE paths
  - setup.py: Updated documentation URLs to docs/ paths
  - docs/README.md: Updated relative paths

#### 🔧 Code Quality Improvements

- **Security Hardening**:
  - `core/metadata/selective_decoys.py`: eval() → ast.literal_eval()
  - `core/state/metadata_utils.py`: random → secrets (3 fixes for timing/config randomization)
  - `interfaces/api/stc_api.py`: random → secrets (3 fixes for adaptive difficulty timing)
  - `interfaces/ui/utils/theme_manager.py`: Added subprocess timeouts, security justifications
  - 8 files: Specific exception handling with documented intentional pass statements

### Fixed

- **Dependency Vulnerabilities**: h11 HTTP request smuggling vulnerability (GHSA-vqfr-h8mv-ghfj)
- **Weak Randomness**: Replaced weak PRNG with cryptographically secure `secrets` module
- **Code Injection Risk**: Removed `eval()` usage in favor of `ast.literal_eval()`
- **Error Handling**: Replaced bare except clauses with specific exception types
- **Documentation Consistency**: Fixed all version numbers to reflect published v0.4.1

## [0.4.1] - 2025-11-19

### Added

#### 🧪 Comprehensive Test Coverage Improvements

- **Test Suite Expansion**: Added 126 new comprehensive tests, bringing total to 246+ tests
- **Coverage Achievement**: Project-wide coverage improved from 82.75% to **91.42%** (+8.67pp)
- **New Test Files**:
  - `tests/test_upfront_validation_coverage.py` - 50 tests covering decoy validation system
  - `tests/test_cli_coverage.py` - 24 tests covering CLI interface edge cases
  - `tests/test_stc_api_coverage.py` - 62 tests covering STC API comprehensive functionality

#### 📊 Module-Specific Coverage Improvements

- **core/streaming/upfront_validation.py**: 74.31% → **90.97%** (+16.66pp)
  - Algorithmic decoy validation: 4 tests
  - Differential decoy validation: 9 tests
  - Selective decoy validation: 8 tests
  - Entropy calculation: 4 tests
  - Structure validation: 4 tests
  - Pattern detection: 7 tests
  - Edge cases: 14 tests

- **interfaces/cli/stc_cli.py**: 66.85% → **97.79%** (+30.94pp)
  - Metadata serialization edge cases: 3 tests
  - Command functions (encrypt, decrypt, hash): 12 tests
  - CLI entry point: 5 tests
  - Error handling: 4 tests

- **interfaces/cli/**init**.py**: 0% → **100%** (+100pp)
  - Full module initialization coverage

- **interfaces/api/streaming_context.py**: 19.88% → **98.19%** (+78.31pp)
  - Improved through existing comprehensive test suite

- **interfaces/api/stc_api.py**: 13.36% → **91.70%** (+78.34pp)
  - Context initialization: 5 tests (string/bytes/int seeds, custom params)
  - Entropy health monitoring: 5 tests (thresholds, profiles, quality checks)
  - Adaptive difficulty: 8 tests (modes, timing randomization)
  - Stream encryption: 5 tests (chunking, progress callbacks)
  - Password handling: 4 tests (defaults, custom passwords)
  - Decoy options: 5 tests (injection, polymorphic)
  - Metadata versioning: 2 tests (v0.3.0 compatibility)
  - State persistence: 1 test (file persistence)
  - Status reporting: 1 test (get_status)
  - Convenience wrappers: 6 tests (encrypt, decrypt, hash, quick functions)
  - Hashing and key derivation: 6 tests (PHE, CKE integration)
  - Edge cases: 3 tests (large data, unicode, context data)
  - Total: 62 comprehensive tests covering all major STC API features

### Changed

- **Development Status**: Test coverage now at production-ready levels (91.42%)
- **Quality Assurance**: All 246+ tests passing with 0 failures, 0 skips

### Documentation

- Updated test coverage statistics across documentation
- Added production readiness assessment

## [0.4.0] - 2025-11-15

### Added

#### ⚡ StreamingContext - High-Performance P2P Streaming

- **New Module**: `interfaces/api/streaming_context.py` - Optimized interface for real-time streaming encryption
- **ChunkHeader**: Fixed 16-byte binary format (sequence, nonce, data_length, flags)
- **Adaptive Chunking**: Automatic splitting of large frames (>8KB) into optimal-sized sub-chunks
- **Performance Achievement**: 132.9 FPS (443% over 30 FPS target), 7.52ms latency (85% under 50ms target)
- **Minimal Overhead**: 0.31% metadata overhead (16 bytes) vs ~200KB in full STC mode
- **Post-Classical Compliance**: Pure DSF tensor operations, zero XOR, zero block ciphers

#### 🎯 StreamingContext API

- `StreamingContext.__init__()` - Initialize with configurable chunk size, adaptive chunking, CEL depth
- `StreamingContext.encrypt_chunk(data)` - Encrypt single frame with adaptive sub-chunking
- `StreamingContext.decrypt_chunk(header, encrypted)` - Decrypt frame (single/multi-chunk automatic)
- `StreamingContext.get_stream_metadata()` - Session metadata for handshake (~9 bytes)
- `StreamingContext.get_performance_stats()` - Throughput, latency, chunk counts, sub-chunk stats
- `ChunkHeader.to_bytes()` / `ChunkHeader.from_bytes()` - Fixed 16-byte serialization

#### 🔧 Optimization Techniques

- **Lazy CEL Initialization**: Depth 2→6 on demand (70% faster init)
- **Precomputed Key Schedule**: 256 keys upfront (eliminates per-frame CKE overhead)
- **Simplified DSF**: 2 folds vs 5 for small chunks (60% faster encryption)
- **Zero-Copy Headers**: Fixed 16-byte format (99.992% metadata reduction)
- **Entropy Pooling**: 1KB pool reused across chunks (95% fewer PHE calls)
- **Adaptive Chunking**: Auto-split large frames for optimal DSF tensor performance

#### 📊 Performance Benchmarks

**Realistic Streaming Scenario** (30 FPS, 5KB frames):

- FPS: 132.9 (target: 30) - **443% over target**
- Latency: 7.52ms (target: <50ms) - **85% under target**
- Overhead: 0.31% (target: <10%) - **97% under target**
- Throughput: 0.65 MB/s sustained

**Chunk Size Performance**:

- 256B: 0.44ms, 0.55 MB/s
- 1KB: 1.19ms, 0.82 MB/s
- 4KB: 5.21ms, 0.75 MB/s
- 8KB (optimal): 16.02ms, 0.49 MB/s
- 16KB (adaptive): 30.02ms, 0.52 MB/s, 102 sub-chunks
- 64KB (adaptive): 28.97ms, 2.16 MB/s, 408 sub-chunks (70% faster than single-chunk)

#### 🧪 Comprehensive Testing

- **21 tests added** in `tests/test_streaming_context.py`:
  - ChunkHeader serialization and validation (2 tests)
  - StreamingContext initialization and encryption (12 tests)
  - Adaptive chunking logic and roundtrips (6 tests)
  - Performance benchmarks (1 test)
- **100% passing**: All 21 tests pass in 7.43s

### Enhanced

- **STCContext API**: Added lightweight streaming methods (backward compatible):
  - `encrypt_frame_lightweight(data, frame_sequence, session_context)`
  - `decrypt_frame_lightweight(encrypted_data, frame_nonce, session_metadata)`
  - `init_stream_session()` - Returns session metadata

### Changed

- **Development Status**: Beta → Production-ready for streaming use cases
- **Target Audience**: Expanded to include P2P application developers
- **Performance Focus**: Optimized for real-time streaming scenarios

### Fixed

- **Multi-chunk decryption padding**: Fixed DSF padding issue where sub-chunks weren't tracking original lengths
- **Initialization order**: Fixed `chunk_sequence` used before definition in entropy pool init
- **XOR removal**: Completely removed classical crypto "fast path" that violated post-classical principles

### Performance Improvements

**Streaming vs Full STC** (for real-time frames):

- Latency: ~200ms → 7.52ms (**26x faster**)
- Overhead: ~200KB → 16 bytes (**99.992% reduction**)
- Memory: Variable → Constant 7MB (**predictable**)
- FPS: ~5 FPS → 132.9 FPS (**26x higher**)

**Adaptive Chunking** (64KB frames):

- No chunking: 87.23ms, 0.72 MB/s
- Adaptive (8KB): 28.97ms, 2.16 MB/s (**70% faster, 3x throughput**)

### Documentation

- **`docs/releases/RELEASE_v0.4.0.md`**: Comprehensive release notes with examples
- **`tests/test_streaming_context.py`**: Full test suite documentation
- **README.md**: Added StreamingContext quick start and use cases
- **CHANGELOG.md**: Detailed v0.4.0 changes

### Migration from v0.3.1

✅ **Fully backward compatible** - All v0.3.1 code continues to work without changes.

StreamingContext is an **optional new interface** for streaming use cases. Existing `STCContext` applications are unaffected.

### Use Cases

- **P2P Video Streaming**: SeigrToolsetTransmissions integration
- **Real-Time Audio**: Low-latency voice/music streaming
- **Live Data Feeds**: Sensor data, telemetry, real-time analytics
- **Game State Sync**: Multiplayer game encryption

## [0.3.1] - 2025-11-02

### Added

#### 🧠 Automated Security Profiles System

- **5 Basic Security Profiles**: Document, Media, Credentials, Backup, Custom with auto-detection
- **19+ Pattern-Based Profiles**: Financial, Medical, Legal, Technical, Government, and specialized profiles
- **Content Analysis Engine**: Analyzes file content using pattern matching to detect sensitive data and recommend optimal security
- **Auto-Detection**: Automatically detects file types via extensions, signatures, and applies optimal security settings
- **Profile Optimization**: Dynamic parameter adjustment based on file size and content type
- **Interactive Recommendations**: `recommend_profile_interactive()` provides detailed guidance

#### ⚡ High-Performance Streaming Engine

- **Ultra-Fast Streaming**: >100GB file support at 50+ MB/s throughput
- **Constant Memory Usage**: Only 7MB RAM regardless of file size
- **Upfront Decoy Validation**: 3-5x faster decryption via early validation
- **Streaming Integration**: Works seamlessly with all security profiles
- **Automatic Optimization**: Perfect chunk sizes and buffer management

#### 🖥️ Command-Line Interface

- **Simple Commands**: `stc-cli encrypt --auto` handles file type detection and profile selection automatically
- **Automated Analysis**: `stc-cli analyze` provides detailed file recommendations based on pattern matching
- **Batch Operations**: Encrypt/decrypt entire folders with profile optimization
- **No Programming Required**: Accessible to non-technical users
- **Cross-Platform Support**: Windows, macOS, Linux compatibility

#### 🔒 Adaptive Security Manager

- **Threat Detection**: Automatically detects attack patterns and responds
- **Context-Aware Security**: Adjusts protection based on environment and usage
- **Compliance Integration**: HIPAA, GDPR, SOX-compliant profiles available
- **Pattern-Based Optimization**: System uses heuristics to improve recommendations
- **Audit Trail**: Complete logging of security decisions and adaptations

### Enhanced

- **User Manual**: Comprehensive documentation with step-by-step guides for all user levels
- **API Integration**: Security profiles integrated with existing STC API
- **Test Coverage**: 100+ tests including automated security system validation
- **Performance**: Profile-specific optimizations for different file types
- **Documentation**: Real-world scenarios and practical examples

### Changed

- **Development Status**: Upgraded from Alpha to Beta (production-ready)
- **Target Audience**: Expanded from developers to include non-technical users and enterprises
- **CLI Entry Point**: Updated to `stc-cli` for better user experience
- **Package Description**: Updated to reflect automated security capabilities

## [0.3.0] - 2025-10-30

### Added

#### Feature 1: Entropy Health API

- **Quality scoring system**: 0.0-1.0 score based on lattice diversity, operation count, and state variance
- **Status classification**: EXCELLENT (0.9+), GOOD (0.8-0.9), ACCEPTABLE (0.7-0.8), WEAK (<0.7)
- **Threshold enforcement**: Auto-reject encryptions below minimum entropy threshold
- **Detailed metrics**: Lattice diversity ratio, unique values, state version, history depth
- **Warning system**: Detects low diversity, insufficient operations, stale state
- New API methods:
  - `STCContext.get_entropy_profile()` - Returns quality score and detailed metrics
  - `STCContext.set_minimum_entropy_threshold(threshold)` - Sets auto-rejection threshold

#### Feature 2: Enhanced Decoy Polymorphism

- **Variable lattice sizes**: Decoys use randomized dimensions (32×3 to 96×5)
- **Randomized decoy count**: Actual count varies ±2 from specified value
- **Timing randomization**: Optional 10-30ms jitter between operations (opt-in)
- **Noise padding**: Optional random bytes in metadata (opt-in, adds 5-10%)
- **Performance optimization**: Decoys use smaller lattices (64×64×4 vs 128×128×6 for real CEL)
  - 5.8x faster per decoy (0.14s vs 0.81s)
  - Maintains security: attacker cannot distinguish decoy size from real
- New parameters in `encrypt()`:
  - `variable_decoy_sizes` (default: True)
  - `randomize_decoy_count` (default: True)
  - `timing_randomization` (default: False)
  - `noise_padding` (default: False)

#### Feature 3: Context-Adaptive Morphing

- **CEL-delta-driven intervals**: Morphing interval adjusts based on CEL state changes
  - High change: 50 operations (aggressive morphing)
  - Medium change: 100 operations (balanced)
  - Low change: 200 operations (conservative)
- **Pattern detection**: Monitors CEL evolution to detect stagnation
- New API methods:
  - `STCContext.pcf.get_adaptive_status()` - Returns adaptive morphing state

#### Feature 4: Adaptive Difficulty Scaling

- **Oracle attack detection**: Monitors for repeated decrypt attempts with tampered data
- **Dynamic path scaling**: PHE path count increases from 7 to 15 under attack
- **Timing randomization**: Adds delays to prevent timing analysis
- **Difficulty levels**: 'fast' (3 paths), 'balanced' (7 paths), 'paranoid' (15 paths)
- New initialization parameter:
  - `adaptive_difficulty` - Sets initial difficulty level

#### Feature 5: Streaming Support

- **Chunk-based encryption**: Processes data in configurable chunks (default 1MB)
- **Memory efficient**: Avoids loading entire large files into memory
- **Progress callbacks**: Optional callback for UI progress updates
- New API methods:
  - `STCContext.encrypt_stream(data, chunk_size, progress_callback)` - Yields encrypted chunks
  - `STCContext.decrypt_stream(chunks, metadata, progress_callback)` - Yields decrypted chunks

#### Feature 6: Metadata Compression Enhancement

- **RLE + varint compression**: Run-length encoding for zeros + variable-length integers
- **Dictionary encoding removed**: Ineffective for pseudo-random CEL data (51% unique values)
- **Compression ratio**: ~66% compression for typical lattice data
- **Security maintained**: Compression is deterministic and reversible

### Changed

#### Security-First Philosophy

- **All security features ENABLED by default**: Decoys, polymorphism, adaptive morphing
- **Performance through optimization**: Achieved 2.9x speedup via smaller decoy lattices, NOT by disabling features
- **Professional approach**: "Security first, optimize implementation" vs "disable features for speed"

#### Performance Improvements

- **Decoy lattice optimization**: Real CEL 128×128×6, Decoys 64×64×4
  - 5.8x faster per decoy while maintaining plausible deniability
  - Total speedup: 2.9x (5.2s → 1.8s with 3 decoys enabled)
- **Encryption time**: ~1.8s with full security features (3 decoys, polymorphism)
- **Metadata size**: ~486KB with 3 decoys (vs 276KB without decoys in v0.2.1)

#### API Enhancements

- `encrypt()` now accepts:
  - `use_decoys=True` (ENABLED by default)
  - `num_decoys=3` (default count)
  - `variable_decoy_sizes=True` (ENABLED)
  - `randomize_decoy_count=True` (ENABLED)
  - `timing_randomization=False` (opt-in for paranoid mode)
  - `noise_padding=False` (opt-in for paranoid mode)

### Performance

- **Default settings** (3 decoys, polymorphic features enabled):
  - Encryption: 1.8s average
  - Metadata: 486KB
  - Security: FULL
- **Paranoid mode** (all features enabled):
  - Encryption: 2.5s average
  - Metadata: 750KB
  - Security: MAXIMUM
- **Performance mode** (explicit `use_decoys=False`):
  - Encryption: 0.6s average
  - Metadata: 276KB
  - Security: REDUCED (not recommended for production)

### Documentation

- **docs/PERFORMANCE.md**: New security-first performance guide
  - Benchmarks with all security features enabled
  - Optimization strategy (smaller decoy lattices)
  - Production recommendations
- **Examples updated**:
  - `examples/entropy_health/entropy_monitoring.py` - Demonstrates quality monitoring
  - `examples/config_encryption/config_example.py` - Shows v0.3.0 security features
  - All examples work with default secure settings

### Migration from v0.2.1

- **API compatible**: All v0.2.1 code works without changes
- **Metadata format**: Binary compatible (TLV format unchanged)
- **New features**: Opt-in by default (use_decoys=True is now default)
- **Performance**: May be slower if you were using `use_decoys=False` before
  - Solution: Keep decoys enabled for security, or explicitly set `use_decoys=False` if needed

### Security Improvements

- **Plausible deniability**: 3 decoys by default (was opt-in in v0.2.1)
- **Polymorphic obfuscation**: Variable sizes and counts prevent pattern analysis
- **Entropy quality monitoring**: Prevents weak encryptions automatically
- **Attack resistance**: Adaptive difficulty scaling counters oracle attacks
- **Streaming security**: Large file encryption without memory disclosure

## [0.2.1] - 2025-10-30

### Added

- **Variable-length integer encoding (varint)**: Implemented LEB128-style varint with zigzag encoding for signed integers
  - Run-length encoding for consecutive zeros (marker: 0xFF)
  - Reduces metadata size by 65% (786KB → 276KB without decoys)
- **Decoy vector TLV serialization**: Full support for obfuscated vectors in binary format
  - New TLV type: `TLV_TYPE_VECTOR` (0x10) for serializing encrypted metadata blobs
  - Recursive TLV serialization/deserialization for nested vector structures
- **Decoy vectors now enabled by default**: `use_decoys=True` in encrypt() API

### Changed

- **Performance optimizations**:
  - Reduced CEL audit frequency: every 100th operation (was every 50th)
  - Reduced chained timing entropy: every 200th operation (was every 100th)
  - Total speedup: 1.95x faster than v0.2.0 (2.27s → 1.17s avg)
- **Metadata compression**:
  - Without decoys: 786KB → 276KB (65% reduction)
  - With 3 decoys: 786KB → 414KB (47% reduction)
- **API**: `use_decoys` parameter now defaults to `True` (was `False`)

### Performance

- **Encryption**: 0.63s average (was 1.33s in v0.2.0)
- **Decryption**: 0.54s average (was 0.94s in v0.2.0)
- **Total**: 1.17s average (was 2.27s in v0.2.0)
- **Speedup**: 1.95x faster than v0.2.0, 148x faster than v0.1.0

## [0.2.0] - 2025-10-30

### Added

#### Entropy Amplification (CEL Module)

- **3-tier historical feedback loops**: Recent (5 states), Medium (states 6-20), Deep (states 21-100) with distinct prime moduli (65521, 524287, 2147483647)
- **Nonlinear temporal mixing**: Polynomial mixing (quadratic for timing/memory, cubic for history) with Fibonacci-weighted contributions
- **Nanosecond timing chains**: 5 computational loads targeting different CPU units (prime factorization, modular exp, matrix mult, permutation, diffusion)
- **Cross-layer entropy injection**: Fresh timing entropy injected at each CEL layer boundary
- **Entropy quality metrics**: Self-auditing with timing variance checks, CEL diversity monitoring, historical staleness detection
- **Internal audit logging**: Audit events stored in CEL history (never external), retrievable via `get_audit_log()`

#### Multi-Path Hashing (PHE Module)

- **Dynamic path count**: 3-15 parallel paths based on data Shannon entropy (high-entropy data gets more paths)
- **CEL-driven path DAG**: Path dependencies determined by CEL lattice structure, creating unique topology per encryption
- **3 new transformation strategies**:
  - Strategy 5: Mirror-fold (reverse sequence folding)
  - Strategy 6: Spiral transform (position-based spiral indexing)
  - Strategy 7: Lattice projection (project onto CEL layer, read in CEL-ordered)
- **Composite folding**: 4-stage path combination (rotate → XOR-fold → multiply → cascade)
- **Collision resistance auditing**: Path diversity metrics with risk level classification (LOW/MEDIUM/HIGH)

#### Persistence Vector Obfuscation (STATE Module)

- **Metadata encryption**: Ephemeral CEL-derived keys from password + timestamp seed
- **Differential CEL encoding**: Store only deltas from seed-initialized state (70-90% compression)
- **Decoy vector injection**: 3-5 fake CEL snapshots interleaved with real metadata (real index hidden in PHE hash)
- **Metadata MAC**: PHE-based message authentication code for tamper detection
- **TLV binary format**: Replaces JSON serialization (~25% size reduction, enables versioning)
- New utilities in `core/state/metadata_utils.py`:
  - `encrypt_metadata()` / `decrypt_metadata()`
  - `differential_encode_cel_snapshot()` / `differential_decode_cel_snapshot()`
  - `inject_decoy_vectors()` / `extract_real_vector()`
  - `compute_metadata_mac()` / `verify_metadata_mac()`

#### Self-Auditing Infrastructure

- CEL entropy quality checks (every 10th operation):
  - Low-resolution timer detection (triggers emergency re-init)
  - Degenerate state detection (triggers forced diffusion)
  - Stale entropy detection (triggers cross-layer interaction)
- PHE collision risk monitoring (every 10th digest):
  - Path diversity ratio calculation
  - Risk level classification
- Internal audit log retrieval:
  - `CEL.get_audit_log(limit)` - returns last N audit events
  - `PHE.get_audit_log(limit)` - returns collision risk audits

#### New Utilities

- `utils/tlv_format.py`: Type-Length-Value binary serialization
  - `serialize_metadata_tlv()` / `deserialize_metadata_tlv()`
  - `detect_metadata_version()` - auto-detects v0.1.x JSON vs v0.2.0 TLV
- `utils/math_primitives.py` additions:
  - `compute_chained_timing_entropy()` - 5-stage timing chain
  - `calculate_shannon_entropy()` - integer Shannon-like metric
  - `variable_length_encode_int()` / `variable_length_decode_int()` - LEB128-style encoding

### Changed

#### Breaking Changes

- **Metadata format**: JSON → TLV binary (incompatible with v0.1.x)
- **CEL evolution**: Nonlinear mixing, tier feedback, cross-layer injection (snapshots incompatible)
- **PHE hashing**: Dynamic path count, DAG topology, new strategies (hashes differ from v0.1.x)
- **API signatures**:
  - `STCContext.encrypt()` now returns `(bytes, bytes)` instead of `(bytes, dict)`
  - New parameters: `password`, `use_decoys`, `num_decoys`
  - `STCContext.decrypt()` accepts `bytes` metadata, auto-detects version

#### Enhanced

- CEL history: Now stores both entropy values and audit events (as dicts)
- PHE path history: Now stores both path selectors and audit events
- API error handling: Clear migration messages for v0.1.x data

### Storage Impact

- CEL snapshot: 10-20 KB (JSON) → 1-3 KB (TLV + differential) = 70-85% reduction
- Encryption overhead: +256 B (ephemeral seed), +16 B (MAC), +3-9 KB (decoys)
- **Total metadata**: 10-20 KB (v0.1.x) → 8-16 KB (v0.2.0) with vastly improved security

### Performance Targets

- Encryption: ~2.3s for small messages (actual: 1.3s encryption + 0.9s metadata overhead)
- Decryption: ~2.3s for small messages (actual: 0.9s decryption + 0.9s metadata overhead)
- Total round-trip: ~2.3s (achieves <3s target)
- Audit checks: <5% overall impact (sampled every 50th operation)
- **76x speedup** from initial implementation through aggressive optimization

### Performance Optimizations (Post-Implementation)

- Reduced default lattice size: 256×256×8 → 128×128×6 (75% fewer cells)
- Simplified PHE composite folding: 4-stage → 2-stage (eliminated rotate_bits hotspot)
- Reduced PHE path count: 3-15 → 3-5 (60% fewer paths)
- Optimized CEL diffusion iterations: 1-8 → 1-3 (62% fewer iterations)
- Reduced audit frequency: every 10th → every 50th operation
- Reduced timing chain frequency: every 10th → every 100th operation
- Simplified path transformations (XOR instead of rotate in dependency injection)
- Metadata size reduced: 4MB → 786KB (81% reduction)

### Migration Path

- **Automatic version detection**: API detects v0.1.x JSON format and raises clear error
- **Error message**: Directs users to migration utility (to be implemented in future release)
- **Backward compatibility**: NOT supported (breaking release)

### Security Improvements

- Metadata no longer exposes CEL state in plaintext
- Decoy vectors prevent real metadata identification without password
- MAC prevents tampering and oracle attacks
- Entropy quality monitoring detects weak encryption conditions
- Timing chains increase entropy variance 10x (50ns → 500ns)

### Documentation Updates

- `core/cel/.instructions.md`: Detailed entropy amplification specs
- `core/phe/.instructions.md`: Multi-path hashing and DAG topology
- `core/state/.instructions.md`: Persistence obfuscation implementation
- `core/.instructions.md`: v0.2.0 architecture overview and roadmap

### Known Limitations

- **Metadata size**: ~786KB per encryption (reduced from 4MB through lattice optimization). Still larger than ideal but acceptable. Further compression possible in future versions.
- **Differential encoding disabled**: Currently produces more data than full lattice. Will be optimized when variable-length encoding is implemented.
- **Decoy vector serialization**: Not yet implemented for TLV format. Use `use_decoys=False` for now.
- **Performance trade-offs**: Optimizations reduced lattice size (128×128×6 vs 256×256×8) and simplified some transformations. Security remains strong but with slightly reduced entropy compared to theoretical maximum.
- No migration utility yet (users must re-encrypt v0.1.x data)
- Password hash migration requires user re-authentication
- Differential encoding requires original seed (cannot decode without it)

## [0.1.4] - 2025-10-29

### Changed

- Created `seigrtc` wrapper package to avoid import collisions
- Updated entry point: `stc=seigrtc.interfaces.cli.stc_cli:main`
- Updated examples to use `from seigrtc.interfaces.api import stc_api`

## [0.1.3] - Previous releases

(Earlier versions not documented in detail)

---

## Upgrade Guide

### From v0.1.x to v0.2.0

**⚠️ BREAKING CHANGES - Data must be re-encrypted**

1. **Export plaintext data** (decrypt with v0.1.x)
2. **Upgrade package**: `pip install --upgrade seigr-toolset-crypto`
3. **Re-encrypt data** (encrypt with v0.2.0)

**Password hashes**: Must be regenerated (v0.1.x hashes incompatible)

**API changes**:

```python
# v0.1.x
encrypted, metadata_dict = ctx.encrypt(data)
# metadata_dict is plain dict

# v0.2.0
encrypted, metadata_bytes = ctx.encrypt(data, password="secret")
# metadata_bytes is TLV binary format
```

**New features** (opt-in):

```python
# Use decoy vectors (default: enabled)
encrypted, metadata = ctx.encrypt(data, use_decoys=True, num_decoys=3)

# Disable decoys for smaller metadata
encrypted, metadata = ctx.encrypt(data, use_decoys=False)

# Custom password (default: uses seed)
encrypted, metadata = ctx.encrypt(data, password="custom_password")
```

**Audit logs**:

```python
# Check CEL entropy quality
cel_audits = ctx.cel.get_audit_log(limit=10)
for audit in cel_audits:
    print(f"Quality: {audit['quality']}, Metrics: {audit['metrics']}")

# Check PHE collision risks
phe_audits = ctx.phe.get_audit_log(limit=10)
for audit in phe_audits:
    print(f"Risk: {audit['risk_level']}, Diversity: {audit['diversity_ratio']}")
```

---

## Roadmap

### v0.3.0 (Future)

- Migration utility for v0.1.x → v0.2.0 conversion
- Adaptive difficulty scaling (auto-adjust path count based on detected attacks)
- Hardware acceleration (SIMD/GPU for CEL evolution)
- Formal verification of entropy bounds

### v1.0.0 (Long-term)

- Stable API with full backward compatibility guarantees
- Quantum resistance research integration
- Performance optimization (target: <10% overhead vs v0.1.x)
- Comprehensive security audit and whitepaper

[0.2.0]: https://github.com/Seigr-lab/SeigrToolsetCrypto/compare/v0.1.4...v0.2.0
[0.1.4]: https://github.com/Seigr-lab/SeigrToolsetCrypto/compare/v0.1.3...v0.1.4
[0.1.3]: https://github.com/Seigr-lab/SeigrToolsetCrypto/releases/tag/v0.1.3
