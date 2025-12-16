# Seigr Toolset Crypto v0.3.1

Release Date: November 2, 2025

## Changes

### Added

#### Security Profiles System

- 5 basic security profiles: Document, Media, Credentials, Backup, Custom
- 19 specialized profiles with predefined parameter sets for different file types
- File type detection using extensions, binary signatures, and keyword pattern matching
- Automated parameter selection based on detected file characteristics

#### Command-Line Interface

- `stc-cli` command with encrypt, decrypt, analyze, and batch operations
- File type auto-detection
- Folder batch processing capabilities
- Cross-platform support (Windows, macOS, Linux)

#### Streaming Engine

- Support for files >100GB
- Constant 7MB memory usage regardless of file size
- Throughput >50 MB/s
- 3-5x faster decryption through upfront decoy validation

#### Parameter Adjustment System

- Pattern-based security parameter modification
- File-content-aware parameter selection
- Predefined parameter sets for compliance requirements
- Execution logging and configuration tracking

### Enhanced

- Test coverage expanded to 100+ tests
- Complete user documentation with step-by-step guides
- API integration with security profiles
- Performance optimizations for profile-specific use cases

### Changed

- Development status: Alpha to Beta
- CLI entry point updated to `stc-cli`
- Package description updated to reflect intelligent security capabilities
- Target audience expanded beyond developers

### Performance

- Decryption speed improved 3-5x through upfront decoy validation
- Memory usage constant at 7MB regardless of file size
- Streaming throughput >50 MB/s sustained
- Dynamic parameter tuning for speed/security optimization

Performance benchmarks:

```
File Size    | Encryption Time | Memory Usage | Throughput
-------------|----------------|--------------|------------
1GB          | 20 seconds     | 7MB         | 50 MB/s
10GB         | 3.3 minutes    | 7MB         | 51 MB/s  
50GB         | 16 minutes     | 7MB         | 52 MB/s
100GB        | 32 minutes     | 7MB         | 52 MB/s
```

### Technical Details

#### Core Cryptographic Engine

- Enhanced CEL entropy health monitoring and quality scoring
- Optimized PHE path selection algorithms and collision resistance
- Streaming integration with all security profiles
- Constant memory usage regardless of file size or security level

#### API Changes

- Security profiles integrated with existing API
- Backward compatibility maintained with v0.3.0
- Enhanced error handling with clear messages
- Built-in performance monitoring and benchmarking

#### CLI Commands

```bash
# Basic operations
stc-cli encrypt document.pdf
stc-cli decrypt document.pdf.stc
stc-cli analyze financial_data.csv

# Batch operations
stc-cli encrypt-folder ./sensitive_documents/
```

## Installation

```bash
pip install seigr-toolset-crypto
```

Upgrade from previous versions:

```bash
pip install --upgrade seigr-toolset-crypto
```

Note: v0.3.1 is fully backward compatible with v0.3.0.

## Documentation

New user manual chapters:

- Chapter 2A: Security Profiles
- Chapter 2B: Command-Line Usage  
- Chapter 2C: Intelligent Profiles
- Chapter 2D: Real-World Scenarios

## Compatibility

- Backward compatible with v0.3.0
- All existing code and encrypted data works without changes
- Cross-platform support: Windows, macOS, Linux
