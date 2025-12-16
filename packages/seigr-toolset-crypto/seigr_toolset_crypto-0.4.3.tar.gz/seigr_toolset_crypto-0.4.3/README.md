# Seigr Toolset Crypto (STC)

[![Sponsor Seigr-lab](https://img.shields.io/badge/Sponsor-Seigr--lab-forestgreen?style=flat&logo=github)](https://github.com/sponsors/Seigr-lab)
[![PyPI](https://img.shields.io/pypi/v/seigr-toolset-crypto)](https://pypi.org/project/seigr-toolset-crypto/)
[![License](https://img.shields.io/badge/license-ANTI--CAPITALIST-red)](LICENSE)
[![Coverage](https://img.shields.io/badge/coverage-91.42%25-brightgreen)](htmlcov/index.html)
[![Tests](https://img.shields.io/badge/tests-246%20passing-brightgreen)](docs/testing.md)

**Post-classical cryptographic engine with automated security profiles**

---

## What is STC?

Post-classical cryptographic system using lattice-based entropy, probabilistic hashing, and tensor operations. No XOR, no block ciphers.

**Key Features:**

- **19+ Security Profiles** - Auto-detects file types and optimizes parameters
- **Real-Time Streaming** - 132.9 FPS, 7.52ms latency for P2P applications  
- **Large Files** - >100GB support with constant 7MB memory
- **Production Ready** - 91.42% test coverage, zero vulnerabilities

---

## Quick Start

```bash
# Install
pip install seigr-toolset-crypto

# Encrypt file (auto-detects type and profile)
stc-cli encrypt --input document.pdf --password "my_password"

# Decrypt
stc-cli decrypt --input document.pdf.enc --password "my_password"
```

**Python API:**

```python
from interfaces.api.stc_api import STCContext

ctx = STCContext('my-seed')
encrypted, metadata = ctx.encrypt("Secret data", password="password123")
decrypted = ctx.decrypt(encrypted, metadata, password="password123")
```

**→ [Complete Usage Guide](docs/USAGE.md)** - CLI commands, API examples, streaming

---

## Documentation

### Getting Started

- **[Installation](docs/DISTRIBUTION_GUIDE.md)** - PyPI, source, dependencies
- **[Usage Guide](docs/USAGE.md)** - CLI interface, Python API, examples
- **[Security Profiles](docs/usage-guide.md#security-profiles)** - Auto-detection, optimization

### Technical

- **[Architecture](docs/architecture.md)** - System design, cryptographic components
- **[Core Modules](docs/core-modules.md)** - CEL, PHE, CKE, DSF, PCF explained
- **[API Reference](docs/api-reference.md)** - Complete API documentation
- **[Performance](docs/PERFORMANCE.md)** - Benchmarks, optimization

### Security & Quality

- **[Security Guide](docs/security-guide.md)** - Threat model, best practices
- **[Security Audit](docs/SECURITY_AUDIT.md)** - Grade A+ (Bandit, pip-audit, Safety)
- **[Testing](docs/testing.md)** - 91.42% coverage, 246 tests
- **[Production Readiness](docs/PRODUCTION_READINESS.md)** - Deployment guide

### Development

- **[Changelog](docs/CHANGELOG.md)** - Version history
- **[Migration Guide](docs/migration-guide.md)** - Upgrading versions

---

## How It Works

**Post-classical cryptographic primitives:**

1. **CEL** - Continuous Entropy Lattice (lattice-based entropy)
2. **PHE** - Probabilistic Hashing Engine (multi-path hashing)
3. **CKE** - Contextual Key Emergence (key derivation)
4. **DSF** - Data-State Folding (tensor transformation)
5. **PCF** - Polymorphic Cryptographic Flow (adaptive parameters)

**→ [Architecture Deep Dive](docs/architecture.md)**

---

## Use Cases

### File Encryption

Auto-selected profiles based on file type:

- Documents, Media, Credentials
- Financial (tax, banking), Medical (HIPAA), Legal (contracts)
- Government, Technical, Backup

**→ [Profile System Guide](docs/usage-guide.md#security-profiles)**

### Real-Time Streaming

Optimized for P2P:

- Video/audio streaming (132.9 FPS)
- Live data feeds (7.52ms latency)
- Game state sync, IoT sensors

**→ [Streaming Performance](docs/PERFORMANCE.md#streaming-context)**

### Large Files

Enterprise-grade:

- Files >100GB, 7MB constant memory
- 50-100 MB/s throughput

**→ [Performance Benchmarks](docs/PERFORMANCE.md)**

---

## Performance

| Use Case | Metric | Performance |
|----------|--------|-------------|
| Streaming | Latency | 7.52ms |
| Streaming | FPS | 132.9 sustained |
| File (Document) | Speed | ~0.8s |
| File (Media) | Speed | ~0.5s |
| Large Files | Memory | 7MB constant |
| Large Files | Throughput | 50-100 MB/s |

**→ [Full Performance Report](docs/PERFORMANCE.md)**

---

## Security

- **Zero Vulnerabilities** - Bandit, pip-audit, Safety (grade A+)
- **91.42% Coverage** - 246 passing tests
- **Post-Classical** - Lattice-based, no XOR/block ciphers
- **Compliance Ready** - HIPAA, GDPR, SOX configurations

**→ [Security Audit](docs/SECURITY_AUDIT.md)** | **[Best Practices](docs/security-guide.md)**

---

## Contributing

Part of the **Seigr Ecosystem** - a self-sovereign decentralized network.

**For Contributors:**

- All code requires test coverage (91%+ target)
- Follow post-classical principles (no XOR, no legacy crypto)
- See [Testing Guide](docs/testing.md) and [Architecture](docs/architecture.md)

**For Security Researchers:**

- Security analysis welcome
- Submit via GitHub Issues with technical details

---

## License

**ANTI-CAPITALIST SOFTWARE LICENSE (v 1.4)** - See [LICENSE](LICENSE)

---

## Citation

```bibtex
@software{seigr_toolset_crypto,
  title = {Seigr Toolset Crypto: Post-Classical Cryptographic Engine},
  author = {Seigr-lab},
  year = {2025},
  version = {0.4.2},
  url = {https://github.com/Seigr-lab/SeigrToolsetCrypto}
}
```

---

**[PyPI Package](https://pypi.org/project/seigr-toolset-crypto/)** • **[Documentation](docs/)** • **[Sponsor](https://github.com/sponsors/Seigr-lab)**
