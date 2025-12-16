# Understanding STC Core Modules

This chapter explains how STC cryptographic components work together.

## Overview

STC uses five core modules:

- **CEL** - Continuous Entropy Lattice (entropy generation)
- **PHE** - Probabilistic Hashing Engine (multi-path hashing)
- **CKE** - Contextual Key Emergence (key derivation)
- **DSF** - Data-State Folding (tensor transformation)
- **PCF** - Polymorphic Cryptographic Flow (adaptive parameters)

## CEL - Continuous Entropy Lattice

**What it does**: Generates entropy without external randomness.

**User benefit**: Your encryption doesn't depend on weak system randomness.

## PHE - Probabilistic Hashing Engine

**What it does**: Hashes using multiple parallel paths (3-15 paths).

**User benefit**: Stronger protection against hash-based attacks.

## CKE - Contextual Key Emergence

**What it does**: Derives keys from current lattice state + password.

**User benefit**: Keys are unique to context and timing.

## DSF - Data-State Folding

**What it does**: Transforms data using tensor operations (no XOR).

**User benefit**: Post-classical approach resistant to quantum attacks.

## PCF - Polymorphic Cryptographic Flow

**What it does**: Adapts encryption parameters during operation.

**User benefit**: Dynamic security that responds to usage patterns.

## Security Profiles

Different profiles adjust core module parameters:

| Profile | CEL Size | PHE Paths | DSF Folds |
|---------|----------|-----------|-----------|
| Fast | 128×128×6 | 3 | 3 |
| Document | 256×256×8 | 5 | 5 |
| Credentials | 384×384×10 | 9 | 7 |
| Financial | 512×512×12 | 12 | 9 |

See [Security Profiles Guide](02a-security-profiles.md) for details.

## Next Steps

- [Basic Encryption](02-basic-encryption.md)
- [Security Features](03-security-features.md)
- [Advanced Usage](04-advanced-usage.md)
