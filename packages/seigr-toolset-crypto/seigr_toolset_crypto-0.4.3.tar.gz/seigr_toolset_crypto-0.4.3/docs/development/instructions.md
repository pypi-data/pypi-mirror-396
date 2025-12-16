# **Seigr Toolset Crypto (STC) – Root Instructions**

## Current Status: v0.3.1 Development

**PHASE 1 COMPLETED ✅** - Metadata redesign with 99% size reduction achieved
**PHASE 2 IN PROGRESS** - Streaming performance optimization and upfront decoy validation

## Purpose

Seigr Toolset Crypto (STC) is a cryptographic foundation designed for **binary-world applications**.
It **rejects legacy symmetric/asymmetric paradigms**, avoids XOR and fixed algorithms, and instead employs **dynamic, entropy-regenerative, context-aware processes**.

STC v0.3.1 represents the final architecture redesign before v1.0.0 stable release, with **no backward compatibility** to v0.3.0.

## Core Architecture (v0.3.1)

### Metadata System (Phase 1 - COMPLETED)

* **Layered Metadata Format**: 3-tier system eliminating 486KB bloat
  * Core Layer: 8KB fixed (essential decryption parameters)
  * Security Layer: 2-50KB variable (adaptive decoy system)
  * Extension Layer: Future-proof hooks with nested dict/list serialization
* **Algorithmic Decoy System**: On-demand generation vs storage
  * <1MB files: Algorithmic decoys (seed-based, no storage)
  * 1-100MB files: Differential decoys (store differences only)
  * >100MB files: Selective decoys (critical sections with enhanced 7-point validation)
* **Self-Sovereign Binary Formats**: Complete JSON elimination using magic numbers (STCS, STCE, STCP, STCV, STCM, STCA, STCD)

### Core Directories

* `/core` — Fundamental cryptographic mechanisms: **CEL, PHE, CKE, DSF, PCF, STATE**.
  * `/core/metadata/` — v0.3.1 layered metadata system (IMPLEMENTED)
* `/utils` — Mathematical and operational utilities.
* `/interfaces` — CLI/API/bindings for integration.
* `/examples` — Reference use cases.
* `/tests` — Verification and entropy integrity checks.
* `/docs` — Research, design, and protocol documentation.
* `/internal` — Experimental and prototype workspaces.

## Phase 1 Achievements ✅

1. **Metadata Size Reduction**:
   * 1KB files: 8-12KB metadata (99% reduction from 486KB)
   * 1MB files: 15-25KB metadata (95% reduction)
   * 1GB files: 25-50KB metadata (90% reduction)

2. **Self-Sovereignty**: Complete elimination of JSON dependencies with binary formats

3. **Deterministic Decoy Generation**: Fixed all non-deterministic reconstruction issues

4. **Enhanced Validation**: 7-point file integrity checking for comprehensive modification detection

5. **Security Profile Integration**: Full mapping for all profile types (DOCUMENT, MEDIA, CREDENTIALS, BACKUP, CUSTOM)

## Current Guidelines

---

## Internal Directory

**Purpose:** Workspace for experiments, prototypes, and mathematical model testing.

**Guidelines:**

* Anything here can change or be discarded.
* No dependency on internal experimental code from core modules.
* Useful for rapid testing of new diffusion, folding, or entropy algorithms before stabilization.

**Note:** Once a concept matures, migrate it into `/core` or `/utils` with full documentation.

---

## Coding Assistant Role

You are the coding assistant for the **Seigr Toolset Crypto (STC) repository**.
STC is part of the larger Seigr Toolset — a collection of post-classical cryptographic and computational tools that **reject traditional symmetric/asymmetric paradigms**.

Your mission: implement all functional code **in full compliance** with the `.instructions.md` files located throughout the repository.

* Each `.instructions.md` is a **binding contract**.
* **Never use** pre-existing cryptographic libraries, hashing functions, or frameworks (AES, RSA, SHA, BLAKE, etc.).

---

## Operating Rules

1. **No legacy cryptography:** no XOR, no substitution-permutation networks, no block ciphers, no traditional key derivation.
2. **No randomness imports:** all entropy must come from **internal computation** (CEL-driven differentials, data deltas, temporal micro-variations).
3. **Deterministic yet context-sensitive:** identical seeds → identical outputs; operation chains → polymorphic behavior.
4. **Module isolation:** each component (CEL, PHE, CKE, DSF, PCF, STATE, etc.) must live in its designated directory with clear interfaces.
5. **Avoid wrappers:** write **native algorithms** that directly express blueprint concepts.
6. **Minimal dependencies:** use only core language features and lightweight math/numeric libraries when required.
7. **Document everything:** inline comments must explain each function in relation to the blueprint.
8. **Quick_decrypt support:** DSF must deterministically reconstruct CEL state from minimal snapshots, CKE keys, and metadata. This allows practical decryption without exposing the full entropy lattice.

---

## Development Sequence

### Phase 1: Metadata Redesign ✅ COMPLETED

1. ✅ Layered metadata architecture implementation
2. ✅ Algorithmic decoy systems (algorithmic, differential, selective)
3. ✅ Self-sovereign binary serialization (no JSON dependencies)
4. ✅ Enhanced validation with comprehensive file integrity checking
5. ✅ Comprehensive test coverage (246+ tests passing, 91.42% coverage)

### Phase 2: Streaming Performance ✅ COMPLETED

1. ✅ **Upfront Decoy Validation**: Fast 64KB chunk analysis identifies real decoy before streaming
2. ✅ **Memory Management**: Constant 7MB memory usage regardless of file size (supports >100GB files)
3. ✅ **Performance Optimization**: Streaming architecture eliminates trial-and-error decoy processing
4. ✅ **Real Decoy Identification**: Single-pass streaming decryption using validated real decoy
5. ✅ **Complete Integration**: Works with all decoy strategies and security profiles
6. ✅ **Test Coverage**: 50 tests for upfront validation (90.97% coverage)

### Phase 3: Security Profiles ✅ COMPLETED (v0.3.1)

1. ✅ **Enhanced Profile System**: 19+ specialized profiles (Document, Media, Credentials, Financial, Medical, Legal, Technical, Government, etc.)
2. ✅ **Intelligent Auto-Detection**: Algorithmic file type detection and smart security defaults
3. ✅ **Context-Aware Security**: Dynamic security level adjustment based on content sensitivity
4. ✅ **Profile-Specific Optimizations**: Custom encryption strategies per profile type
5. ✅ **Test Coverage**: 30+ tests for security profiles

### Phase 4: Interface & CLI ✅ COMPLETED (v0.4.1)

1. ✅ **Command-Line Interface**: User-friendly CLI for encryption without programming
2. ✅ **StreamingContext API**: High-performance P2P streaming (132.9 FPS, 7.52ms latency)
3. ✅ **API Coverage**: 24 tests for CLI (97.79% coverage), 21 tests for StreamingContext (98.19% coverage), 62 tests for STC API (91.70% coverage)
4. ✅ **Production-Ready**: 91.42% total code coverage across all modules

### Phase 5: Future-Proofing & v1.0 🔮 PLANNED  

1. **Extension Framework**: Plugin architecture for v1.x features
2. **API Stability**: Lock interfaces for v1.0.0 release
3. **Advanced Security Features**: Quantum-resistant algorithms preparation
4. **Performance Scaling**: Multi-threading and distributed processing
5. **Enterprise Features**: HSM integration, audit logging, compliance tools

### Core Cryptographic Engines (Foundational Systems)

* **CEL**: Continuous Entropy Lattice - The entropy foundation of the entire system

* **PHE**: Probabilistic hashing engine based on CEL state
* **CKE**: Contextual Key Emergence - Dynamic key generation system
* **DSF**: Data-State Folding - Non-XOR encryption core
* **PCF**: Polymorphic cryptographic flow controller
* **STATE**: Persistence and reconstruction system

These are the **fundamental pillars** that make Seigr Toolset Crypto unique!

---

## Development Tone

* Treat STC as a **research-grade cryptographic engine**, not a product demo.
* Prioritize **mathematical clarity and determinism**.
* Output **clean, modular, and internally consistent code** reflecting conceptual purity.
* You are **not building a traditional crypto library** — you are implementing the Seigr Toolset Crypto: a **new generation of post-legacy, entropy-regenerative cryptographic architecture**.

## Phase 2 Priorities

**IMMEDIATE FOCUS**: Streaming performance and memory optimization

* Implement upfront decoy validation using first 64KB chunk analysis
* Eliminate trial-and-error decoy processing during streaming
* Achieve constant 8MB memory usage regardless of file size
* Target 3-5x streaming decrypt performance improvement

**SUCCESS CRITERIA FOR PHASE 2**:

* [ ] Upfront decoy validation operational
* [ ] Memory usage capped at 8MB for all file sizes
* [ ] 3-5x streaming decrypt speed improvement
* [ ] Support for >100GB files without memory issues
* [ ] Elimination of memory leaks during decoy trials

## Critical Phase 1 Achievements

All Phase 1 objectives have been successfully completed:

* ✅ Metadata overhead reduced by 99% (486KB → <15KB for most files)
* ✅ Complete self-sovereignty achieved (zero JSON dependencies)
* ✅ Deterministic decoy reconstruction implemented
* ✅ Enhanced validation with 7-point file integrity checking
* ✅ All test suite passing (23/23 tests successful)
* ✅ Security profile integration completed
* ✅ Extension metadata supports nested dict/list serialization
