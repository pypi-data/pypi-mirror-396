# Testing

Test suite documentation and validation procedures for STC v0.4.0+

## Test Structure

```
tests/
├── __init__.py
├── test_cel.py                           # CEL unit tests
├── test_phe.py                           # PHE unit tests
├── test_integration.py                   # End-to-end tests
├── test_streaming_context.py             # StreamingContext tests (v0.4.0)
├── test_security_profiles.py             # Security profile tests (v0.3.1)
├── test_upfront_validation_coverage.py   # Upfront validation tests (v0.4.0+)
├── test_cli_coverage.py                  # CLI coverage tests (v0.4.0+)
└── ... (additional test modules)
```

## Running Tests

### All Tests

```bash
cd /path/to/SeigrToolsetCrypto
python tests/test_integration.py
```

Output:
```
................
----------------------------------------------------------------------
Ran 16 tests in 183.957s

OK
```

### Individual Test Files

```bash
python tests/test_cel.py      # CEL tests only
python tests/test_phe.py      # PHE tests only
```

### Demo Script

```bash
python demo.py
```

Expected output:
```
============================================================
Seigr Toolset Crypto - Demonstration
============================================================

=== STC Basic Encryption Demo ===
...
✓ PASS: Basic Encryption
✓ PASS: Probabilistic Hashing
✓ PASS: Key Derivation

Total: 3/3 demos passed
```

## Integration Tests (test_integration.py)

### Test Coverage

Total: **16 tests**

**Encryption/Decryption:**
1. `test_string_encryption` - String data round-trip
2. `test_bytes_encryption` - Binary data round-trip
3. `test_empty_string_encryption` - Edge case: empty input
4. `test_large_data_encryption` - 10 KB data
5. `test_unicode_encryption` - Unicode characters

**Context:**
6. `test_context_influence` - Context affects encryption
7. `test_context_aware_encryption` - Different contexts → different ciphertexts
8. `test_context_mismatch` - Wrong context fails decryption

**Hashing:**
9. `test_probabilistic_hashing` - Same input → different hashes over time
10. `test_hash_consistency` - Same CEL state → same hash

**Determinism:**
11. `test_seed_determinism` - Same seed → different initial outputs (timing entropy)
12. `test_reproducibility` - Non-deterministic due to timing

**Error Handling:**
13. `test_invalid_input_types` - TypeError on invalid inputs
14. `test_metadata_integrity` - Required metadata fields

**API:**
15. `test_quick_api` - quick_encrypt/quick_decrypt
16. `test_convenience_functions` - stc_api.encrypt/decrypt wrapper functions

### Test Details

#### test_string_encryption
```python
def test_string_encryption(self):
    data = "Hello, STC!"
    encrypted, metadata = self.context.encrypt(data)
    decrypted = self.context.decrypt(encrypted, metadata)
    self.assertEqual(decrypted, data)
```

**Validates:**
- String → bytes conversion
- DSF fold/unfold symmetry
- Metadata preservation

#### test_context_aware_encryption
```python
def test_context_aware_encryption(self):
    data = "sensitive"
    ctx1 = {"user": "alice"}
    ctx2 = {"user": "bob"}
    
    enc1, meta1 = self.context.encrypt(data, ctx1)
    enc2, meta2 = self.context.encrypt(data, ctx2)
    
    self.assertNotEqual(enc1, enc2)
```

**Validates:**
- Context influences CKE key derivation
- Same plaintext + different context = different ciphertext

#### test_probabilistic_hashing
```python
def test_probabilistic_hashing(self):
    data = "test data"
    hash1 = self.context.hash(data)
    hash2 = self.context.hash(data)
    
    self.assertNotEqual(hash1, hash2)
    self.assertEqual(len(hash1), 32)
    self.assertEqual(len(hash2), 32)
```

**Validates:**
- CEL evolution affects hash output
- Hash length consistency
- Non-deterministic behavior

#### test_reproducibility
```python
def test_reproducibility(self):
    ctx1 = STCContext(seed="test-seed")
    ctx2 = STCContext(seed="test-seed")
    
    enc1, _ = ctx1.encrypt("data")
    enc2, _ = ctx2.encrypt("data")
    
    # Not equal due to timing entropy
    self.assertNotEqual(enc1, enc2)
```

**Validates:**
- CEL uses timing deltas
- Same seed ≠ identical output (by design)
- Timing entropy working

#### test_quick_api
```python
def test_quick_api(self):
    data = "quick test"
    seed = "quick-seed"
    
    encrypted, metadata, ctx = stc_api.quick_encrypt(data, seed)
    decrypted = stc_api.quick_decrypt(encrypted, metadata, seed)
    
    self.assertEqual(decrypted, data)
```

**Validates:**
- CEL reconstruction from metadata
- One-shot encryption/decryption
- State persistence

## CEL Tests (test_cel.py)

### Test Coverage

**Initialization:**
1. `test_initialization` - CEL creates valid lattice
2. `test_seed_types` - Handles string, bytes, int seeds
3. `test_lattice_dimensions` - Correct shape and size

**State Evolution:**
4. `test_entropy_generation` - get_entropy() returns correct size
5. `test_state_updates` - update() changes lattice
6. `test_timing_influence` - Timing affects updates

**Snapshots:**
7. `test_snapshot_restore` - Round-trip state preservation

### Example Test

```python
def test_state_updates(self):
    cel = ContinuousEntropyLattice(seed="test", size=64, depth=4)
    initial_state = cel.lattice.copy()
    
    import time
    time.sleep(0.001)
    cel.update()
    
    updated_state = cel.lattice
    
    # State should change
    self.assertFalse(np.array_equal(initial_state, updated_state))
```

## PHE Tests (test_phe.py)

### Test Coverage

**Hashing:**
1. `test_hash_length` - Always 32 bytes
2. `test_hash_variability` - Different over time
3. `test_context_hashing` - Context affects output
4. `test_different_inputs` - Different inputs → different hashes

### Example Test

```python
def test_hash_variability(self):
    cel = ContinuousEntropyLattice(seed="test")
    phe = ProbabilisticHashingEngine(cel)
    
    hash1 = phe.hash("data")
    hash2 = phe.hash("data")
    
    self.assertNotEqual(hash1, hash2)  # CEL evolved
```

## Test Results Summary

### Status: ✅ All Passing

**Project-Wide Coverage: 91.42%** (246+ tests)

```
Test Module                          | Tests | Coverage | Status
-------------------------------------|-------|----------|--------
test_integration.py                  |  16   |  High    |   ✓
test_cel.py                          |   7   |  High    |   ✓
test_phe.py                          |   4   |  High    |   ✓
test_streaming_context.py            |  21   |  98.19%  |   ✓
test_security_profiles.py (v0.3.1)   |  30+  |  High    |   ✓
test_upfront_validation_coverage.py  |  50   |  90.97%  |   ✓
test_cli_coverage.py                 |  24   |  97.79%  |   ✓
test_stc_api_coverage.py             |  62   |  91.70%  |   ✓
... (additional modules)             |  42+  |  Varies  |   ✓
-------------------------------------|-------|----------|--------
Total                                | 246+  |  89.58%  |   ✓
```

### Module-Specific Coverage

**Core Modules:**
- `core/streaming/upfront_validation.py`: **90.97%** (50 tests)
- `core/streaming/integration.py`: **99.15%** (existing tests)
- `core/metadata/differential_decoys.py`: **95.71%** (existing tests)
- `core/metadata/layered_format.py`: **80.20%** (existing tests)

**Interface Modules:**
- `interfaces/cli/stc_cli.py`: **97.79%** (24 tests)
- `interfaces/cli/__init__.py`: **100%** (comprehensive coverage)
- `interfaces/api/streaming_context.py`: **98.19%** (21 tests)
- `interfaces/api/stc_api.py`: **91.70%** (62 comprehensive tests)

**Test Suite Highlights:**
- 126 new tests added for comprehensive coverage (upfront validation + CLI + STC API)
- 0 failing tests, 0 skipped tests
- Coverage improved from 82.75% → 91.42% (+8.67pp)
- Production-ready coverage levels achieved
- STC API coverage: 50.54% → 91.70% (+41.16pp) with 62 comprehensive tests

### Execution Time

- Integration tests: ~184 seconds
- CEL tests: ~5 seconds
- PHE tests: ~2 seconds
- Demo: ~1 second

**Total**: ~192 seconds

## Manual Testing Procedures

### 1. Basic Functionality

```bash
# Test encryption
python -c "
from interfaces.api import stc_api
enc, meta, ctx = stc_api.quick_encrypt('test', seed='s')
dec = stc_api.quick_decrypt(enc, meta, seed='s')
assert dec == 'test'
print('✓ Basic encryption works')
"
```

### 2. Large Data

```bash
python -c "
from interfaces.api import stc_api
data = 'x' * 1000000  # 1 MB
enc, meta, ctx = stc_api.quick_encrypt(data, seed='test')
dec = stc_api.quick_decrypt(enc, meta, seed='test')
assert dec == data
print('✓ Large data works')
"
```

### 3. Unicode

```bash
python -c "
from interfaces.api import stc_api
data = '你好世界 🌍'
enc, meta, ctx = stc_api.quick_encrypt(data, seed='test')
dec = stc_api.quick_decrypt(enc, meta, seed='test')
assert dec == data
print('✓ Unicode works')
"
```

### 4. Examples

```bash
cd examples/password_manager
python password_manager.py
# Should complete without errors

cd ../config_encryption
python config_example.py
# Should complete without errors
```

## Known Issues (v0.1.0)

### Non-Issues (Expected Behavior)

1. **Non-deterministic encryption**: Same seed + same data → different ciphertext
   - **Cause**: Timing entropy in CEL updates
   - **Not a bug**: This is by design
   - **Decryption still works**: CEL state embedded in metadata

2. **Different hashes for same input**: PHE produces different hashes over time
   - **Cause**: CEL state evolution
   - **Not a bug**: This is "probabilistic" hashing
   - **For deterministic hashing**: Freeze CEL state before hashing

### Actual Issues

None known in v0.1.0.

## Performance Benchmarks

### Encryption Speed

```python
import time
from interfaces.api import stc_api

data_sizes = [100, 1000, 10000, 100000]  # bytes

for size in data_sizes:
    data = 'x' * size
    context = stc_api.initialize(seed="bench")
    
    start = time.time()
    encrypted, metadata = context.encrypt(data)
    encrypt_time = time.time() - start
    
    start = time.time()
    decrypted = context.decrypt(encrypted, metadata)
    decrypt_time = time.time() - start
    
    print(f"{size:6d} bytes: encrypt={encrypt_time*1000:6.2f}ms, decrypt={decrypt_time*1000:6.2f}ms")
```

Expected results (approximate):
```
   100 bytes: encrypt= 52.31ms, decrypt= 48.12ms
  1000 bytes: encrypt= 56.78ms, decrypt= 51.23ms
 10000 bytes: encrypt=125.45ms, decrypt=118.67ms
100000 bytes: encrypt=890.12ms, decrypt=845.34ms
```

### Memory Usage

```python
import tracemalloc
from interfaces.api import stc_api

tracemalloc.start()

context = stc_api.initialize(seed="test")
snapshot1 = tracemalloc.take_snapshot()

encrypted, metadata = context.encrypt("test data" * 1000)
snapshot2 = tracemalloc.take_snapshot()

stats = snapshot2.compare_to(snapshot1, 'lineno')
total = sum(stat.size_diff for stat in stats)
print(f"Memory used: {total / 1024 / 1024:.2f} MB")
```

Expected: ~2-4 MB for typical operations

## Continuous Integration

### GitHub Actions (Recommended)

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - uses: actions/setup-python@v2
      with:
        python-version: '3.9'
    - run: pip install numpy>=1.24.0
    - run: python tests/test_integration.py
    - run: python tests/test_cel.py
    - run: python tests/test_phe.py
    - run: python demo.py
```

## Adding New Tests

### Template for Integration Test

```python
def test_new_feature(self):
    """Test description"""
    # Setup
    data = "test data"
    
    # Execute
    encrypted, metadata = self.context.encrypt(data)
    decrypted = self.context.decrypt(encrypted, metadata)
    
    # Verify
    self.assertEqual(decrypted, data)
    self.assertIsInstance(encrypted, bytes)
    self.assertIn('cel_snapshot', metadata)
```

### Template for Module Test

```python
import unittest
from core.new_module import NewModule

class TestNewModule(unittest.TestCase):
    def setUp(self):
        self.module = NewModule()
    
    def test_basic_functionality(self):
        result = self.module.do_something()
        self.assertIsNotNone(result)

if __name__ == '__main__':
    unittest.main()
```

## Test Data

No external test data files required. All tests use programmatically generated data.

## Coverage Analysis

To measure test coverage:

```bash
pip install coverage
coverage run tests/test_integration.py
coverage report -m
```

Expected coverage: ~85-90% for core modules (v0.1.0)

## Regression Testing

Before each release:

1. Run all test suites
2. Run demo.py
3. Test both examples
4. Build and install package
5. Test installed package

```bash
# Full regression test
python tests/test_integration.py && \
python tests/test_cel.py && \
python tests/test_phe.py && \
python demo.py && \
cd examples/password_manager && python password_manager.py && \
cd ../config_encryption && python config_example.py && \
echo "✓ All regression tests passed"
```
