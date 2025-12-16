"""
Algorithmic Decoy System v0.3.1

Generates decoys on-demand instead of storing full CEL snapshots.
Used for files <1MB where storage efficiency is critical.
"""

import hashlib
import hmac
import struct
from typing import List, Dict, Any, Tuple
from dataclasses import dataclass
import numpy as np
@dataclass
class AlgorithmicDecoyMetadata:
    """Self-sovereign binary metadata for algorithmic decoys"""
    def __init__(self, decoy_count: int, decoy_seeds: List[bytes], 
                 lattice_size: int, depth: int, salt_rounds: int = 10000):
        self.decoy_count = decoy_count
        self.decoy_seeds = decoy_seeds
        self.lattice_size = lattice_size
        self.depth = depth
        self.salt_rounds = salt_rounds
    
    def serialize(self) -> bytes:
        """Serialize to compact binary format"""
        # Header: 4-byte magic + version + counts + parameters
        header = struct.pack('!4sBBHHHI', 
                           b'STCA',  # Seigr Toolset Crypto Algorithmic
                           1,        # Version
                           self.decoy_count,
                           self.lattice_size,
                           self.depth,
                           len(self.decoy_seeds[0]) if self.decoy_seeds else 32,
                           self.salt_rounds)
        
        # Pack all seeds sequentially (much more compact than hex)
        seeds_data = b''.join(self.decoy_seeds)
        
        return header + seeds_data
    
    @classmethod 
    def deserialize(cls, data: bytes) -> 'AlgorithmicDecoyMetadata':
        """Deserialize from binary format"""
        if len(data) < 16:
            raise ValueError("Invalid algorithmic decoy metadata")
        
        # Unpack header
        magic, version, decoy_count, lattice_size, depth, seed_length, salt_rounds = \
            struct.unpack('!4sBBHHHI', data[:16])
        
        if magic != b'STCA':
            raise ValueError("Invalid magic number")
        if version != 1:
            raise ValueError(f"Unsupported version: {version}")
        
        # Extract seeds
        seeds_data = data[16:]
        expected_seeds_size = decoy_count * seed_length
        if len(seeds_data) != expected_seeds_size:
            raise ValueError("Invalid seeds data size")
        
        decoy_seeds = []
        for i in range(decoy_count):
            start = i * seed_length
            end = start + seed_length
            decoy_seeds.append(seeds_data[start:end])
        
        return cls(decoy_count, decoy_seeds, lattice_size, depth, salt_rounds)
    
    def __getitem__(self, key):
        """Compatibility layer for existing code"""
        if key == 'decoy_count' or key == 'c':
            return self.decoy_count
        elif key == 'decoy_seeds' or key == 's':
            return [seed.hex() for seed in self.decoy_seeds]  # Return hex for compatibility
        elif key == 'generation_params' or key == 'p':
            return {
                'lattice_size': self.lattice_size,
                'depth': self.depth,
                'salt_rounds': self.salt_rounds,
                'method': 'hmac_kdf'
            }
        elif isinstance(key, int):
            # Handle integer access for compatibility
            if key == 0:
                return self.decoy_count
            elif key == 1:
                return [seed.hex() for seed in self.decoy_seeds]
            else:
                raise IndexError(f"Index {key} out of range")
        else:
            raise KeyError(f"Unknown key: {key}")
    
    def get(self, key, default=None):
        try:
            return self[key]
        except KeyError:
            return default
    
    def keys(self):
        return ['decoy_count', 'decoy_seeds', 'generation_params']

@dataclass
class AlgorithmicDecoyParams:
    """Parameters for algorithmic decoy generation"""
    decoy_seeds: List[bytes]      # Derived seeds for each decoy
    generation_method: str        # 'hmac_kdf', 'hash_chain', 'xor_stream'
    salt_rounds: int             # Number of derivation rounds
    lattice_size: int            # Target lattice dimensions
    depth: int                   # Target lattice depth
    
class AlgorithmicDecoyGenerator:
    """Generates cryptographically indistinguishable decoys on-demand"""
    
    def __init__(self, real_cel_seed: bytes, lattice_size: int = 128, depth: int = 6):
        self.real_cel_seed = real_cel_seed
        self.lattice_size = lattice_size
        self.depth = depth
        
        # Derive master decoy key from real CEL seed
        self.master_key = self._derive_master_key(real_cel_seed)
    
    def _derive_master_key(self, seed: bytes) -> bytes:
        """Derive master key for decoy generation"""
        # Use domain separation to ensure decoy keys don't interfere with real keys
        domain = b"STC_v0.3.1_ALGORITHMIC_DECOYS"
        return hashlib.pbkdf2_hmac('sha256', seed, domain, 10000, 32)
    
    def generate_decoy_seeds(self, decoy_count: int) -> List[bytes]:
        """Generate deterministic seeds for each decoy"""
        seeds = []
        
        for i in range(decoy_count):
            # Create unique seed for each decoy
            counter = struct.pack('!I', i)
            seed = hmac.new(self.master_key, counter, hashlib.sha256).digest()
            seeds.append(seed)
        
        return seeds
    
    def generate_decoy_cel(self, decoy_seed: bytes) -> np.ndarray:
        """Generate a full CEL from decoy seed (computationally expensive)"""
        
        # Initialize random state with decoy seed
        rng = np.random.RandomState(seed=int.from_bytes(decoy_seed[:4], 'big'))
        
        # Generate decoy lattice with same dimensions as real CEL
        lattice = rng.randint(-2147483648, 2147483647, 
                             size=(self.lattice_size, self.lattice_size, self.depth),
                             dtype=np.int32)
        
        # Apply transforms to make it look realistic
        lattice = self._apply_realistic_transforms(lattice, decoy_seed)
        
        return lattice
    
    def _apply_realistic_transforms(self, lattice: np.ndarray, seed: bytes) -> np.ndarray:
        """Apply transforms to make decoy look like real CEL evolution"""
        
        # Simulate entropy evolution patterns
        rng = np.random.RandomState(seed=int.from_bytes(seed[4:8], 'big'))
        
        # Add realistic entropy patterns
        for _ in range(3):  # Simulate 3 evolution rounds
            # Add noise based on position
            noise = rng.normal(0, 1000, lattice.shape).astype(np.int32)
            
            # Safely add noise and clip to prevent overflow
            lattice_int64 = lattice.astype(np.int64) + noise.astype(np.int64)
            lattice = np.clip(lattice_int64, -2147483648, 2147483647).astype(np.int32)
            
            # Apply rotation and permutation (simplified)
            lattice = np.roll(lattice, rng.randint(-10, 10), axis=0)
            lattice = np.roll(lattice, rng.randint(-10, 10), axis=1)
        
        return lattice
    
    def validate_decoy_quality(self, real_cel: np.ndarray, decoy_cel: np.ndarray) -> float:
        """Validate that decoy is indistinguishable from real CEL"""
        
        # Statistical tests for indistinguishability
        tests = []
        
        # 1. Mean and variance similarity
        real_mean, real_var = np.mean(real_cel), np.var(real_cel)
        decoy_mean, decoy_var = np.mean(decoy_cel), np.var(decoy_cel)
        
        mean_diff = abs(real_mean - decoy_mean) / max(abs(real_mean), 1)
        var_diff = abs(real_var - decoy_var) / max(real_var, 1)
        tests.extend([1.0 - min(mean_diff, 1.0), 1.0 - min(var_diff, 1.0)])
        
        # 2. Distribution shape similarity (simplified KS test)
        real_flat = real_cel.flatten()
        decoy_flat = decoy_cel.flatten()
        
        # Sample subset for performance
        sample_size = min(10000, len(real_flat))
        real_sample = np.random.choice(real_flat, sample_size, replace=False)
        decoy_sample = np.random.choice(decoy_flat, sample_size, replace=False)
        
        # Compare sorted distributions
        real_sorted = np.sort(real_sample)
        decoy_sorted = np.sort(decoy_sample)
        max_diff = np.max(np.abs(real_sorted - decoy_sorted)) / (2**31)
        tests.append(1.0 - min(max_diff, 1.0))
        
        # 3. Entropy similarity
        real_entropy = self._calculate_entropy(real_sample)
        decoy_entropy = self._calculate_entropy(decoy_sample)
        entropy_diff = abs(real_entropy - decoy_entropy) / max(real_entropy, 1)
        tests.append(1.0 - min(entropy_diff, 1.0))
        
        # Return average quality score (0.0 = terrible, 1.0 = perfect)
        return sum(tests) / len(tests)
    
    def _calculate_entropy(self, data: np.ndarray) -> float:
        """Calculate approximate Shannon entropy"""
        # Handle edge case of uniform data
        if len(np.unique(data)) == 1:
            return 0.0
        
        # For int32 data with large range, use percentile-based binning
        # This avoids numpy histogram indexing issues with extreme values
        data_flat = data.flatten() if data.ndim > 1 else data
        
        # Use 256 bins based on data quantiles, not absolute values
        # This handles any data range safely
        try:
            # Create bin edges based on data distribution
            percentiles = np.linspace(0, 100, 257)
            bin_edges = np.percentile(data_flat, percentiles)
            
            # Remove duplicate edges (can happen with repeated values)
            bin_edges = np.unique(bin_edges)
            
            if len(bin_edges) < 2:
                return 0.0
            
            # Compute histogram with safe bin edges
            hist, _ = np.histogram(data_flat, bins=bin_edges)
            hist = hist[hist > 0]  # Remove empty bins
            
            if len(hist) == 0:
                return 0.0
            
            # Calculate probabilities
            probs = hist / np.sum(hist)
            
            # Shannon entropy
            return -np.sum(probs * np.log2(probs))
        except Exception:
            # Fallback: use value counts for discrete entropy
            unique, counts = np.unique(data_flat, return_counts=True)
            probs = counts / np.sum(counts)
            return -np.sum(probs * np.log2(probs))

class AlgorithmicDecoySystem:
    """Complete algorithmic decoy system for metadata storage and retrieval"""
    
    def __init__(self):
        self.generator = None
        self._current_metadata = None
    
    def create_decoy_metadata(self, real_cel_seed: bytes, decoy_count: int,
                            lattice_size: int = 128, depth: int = 6) -> Dict[str, Any]:
        """Create metadata for algorithmic decoys (minimal storage)"""
        
        self.generator = AlgorithmicDecoyGenerator(real_cel_seed, lattice_size, depth)
        decoy_seeds = self.generator.generate_decoy_seeds(decoy_count)
        
        metadata = AlgorithmicDecoyMetadata(decoy_count, decoy_seeds, lattice_size, depth)
        self._current_metadata = metadata  # Store for validation
        return metadata
    
    def load_decoy_metadata(self, metadata, real_cel_seed: bytes) -> 'AlgorithmicDecoySystem':
        """Load decoy system from metadata"""
        
        # Handle both old and new format for compatibility
        if 'generation_params' in metadata:
            params = metadata['generation_params']
            lattice_size = params['lattice_size']
            depth = params['depth']
        elif hasattr(metadata, 'lattice_size'):
            # New binary format
            lattice_size = metadata.lattice_size
            depth = metadata.depth
        else:
            # Legacy format
            params = metadata.get('p', {})
            lattice_size = params.get('l', 128)
            depth = params.get('d', 6)
            
        self.generator = AlgorithmicDecoyGenerator(
            real_cel_seed, 
            lattice_size, 
            depth
        )
        
        return self
    
    def generate_all_decoys(self, metadata) -> List[np.ndarray]:
        """Generate all decoy CELs (expensive - use sparingly)"""
        
        if not self.generator:
            raise ValueError("Decoy system not initialized")
        
        decoys = []
        
        # Handle both old and new format for compatibility
        if hasattr(metadata, 'decoy_seeds'):
            # New binary format - seeds are already bytes
            decoy_seeds = metadata.decoy_seeds
        else:
            # Legacy format - seeds are hex strings
            decoy_seeds = [bytes.fromhex(seed_hex) for seed_hex in metadata['decoy_seeds']]
        
        for seed in decoy_seeds:
            decoy_cel = self.generator.generate_decoy_cel(seed)
            decoys.append(decoy_cel)
        
        return decoys
    
    def generate_decoy_on_demand(self, decoy_index: int, metadata: Dict[str, Any]) -> np.ndarray:
        """Generate single decoy on-demand (more efficient)"""
        
        if not self.generator:
            raise ValueError("Decoy system not initialized")
        
        if decoy_index >= len(metadata['decoy_seeds']):
            raise ValueError(f"Invalid decoy index: {decoy_index}")
        
        decoy_seed = bytes.fromhex(metadata['decoy_seeds'][decoy_index])
        return self.generator.generate_decoy_cel(decoy_seed)
    
    def validate_decoy_security(self, real_cel: np.ndarray, metadata: Dict[str, Any]) -> Dict[str, float]:
        """Validate security properties of all decoys"""
        
        if not self.generator:
            raise ValueError("Decoy system not initialized")
        
        results = {}
        decoy_seeds = [bytes.fromhex(seed_hex) for seed_hex in metadata['decoy_seeds']]
        
        for i, seed in enumerate(decoy_seeds):
            decoy_cel = self.generator.generate_decoy_cel(seed)
            quality = self.generator.validate_decoy_quality(real_cel, decoy_cel)
            results[f'decoy_{i}'] = quality
        
        # Overall security score
        results['overall_quality'] = sum(results.values()) / len(decoy_seeds)
        
        return results
    
    def estimate_generation_time(self, decoy_count: int, lattice_size: int, depth: int) -> float:
        """Estimate time to generate all decoys (for performance planning)"""
        
        # Rough estimates based on lattice complexity
        base_time_per_decoy = 0.1  # 100ms base time
        size_factor = (lattice_size / 128) ** 2  # Quadratic scaling with size
        depth_factor = depth / 6  # Linear scaling with depth
        
        per_decoy_time = base_time_per_decoy * size_factor * depth_factor
        total_time = per_decoy_time * decoy_count
        
        return total_time
    
    def get_storage_size(self, metadata: Dict[str, Any]) -> int:
        """Calculate storage size of algorithmic decoy metadata"""
        
        # Count bytes in metadata
        storage_size = 0
        
        # Base parameters
        storage_size += 4  # decoy_count (int)
        
        # Decoy seeds (32 bytes each)
        storage_size += len(metadata['decoy_seeds']) * 32
        
        # Generation parameters (small overhead)
        storage_size += 200  # Conservative estimate for metadata overhead
        
        return storage_size
    
    def generate_decoys(self, file_size: int, cel_seed: bytes, decoy_count: int) -> List[bytes]:
        """Generate decoys based on file size and CEL seed"""
        # Determine lattice parameters from file size
        if file_size < 1024:
            lattice_size, depth = 32, 4
        elif file_size < 10240:
            lattice_size, depth = 64, 4
        elif file_size < 102400:
            lattice_size, depth = 96, 5
        else:
            lattice_size, depth = 128, 6
        
        # Create metadata
        metadata = self.create_decoy_metadata(cel_seed, decoy_count, lattice_size, depth)
        self.load_decoy_metadata(metadata, cel_seed)
        
        # Generate all decoys
        decoys = self.generate_all_decoys(metadata)
        
        # Convert to bytes (serialize each decoy)
        decoy_bytes = []
        for decoy in decoys:
            decoy_bytes.append(decoy.tobytes())
        
        return decoy_bytes
    
    def reconstruct_decoys(self, file_size: int, cel_seed_hash: bytes, decoy_count: int) -> List[bytes]:
        """Reconstruct decoys from file characteristics"""
        
        # Generate decoys using the same logic as generation
        return self.generate_decoys(file_size, cel_seed_hash, decoy_count)
    
    def reconstruct_single_decoy(self, file_size: int, cel_seed_hash: bytes, decoy_count: int, decoy_index: int) -> bytes:
        """Reconstruct ONLY the specified decoy (optimized for streaming)"""
        
        if decoy_index >= decoy_count:
            raise ValueError(f"Invalid decoy index {decoy_index} for {decoy_count} decoys")
        
        # Determine lattice parameters from file size (same logic as generate_decoys)
        if file_size < 1024:
            lattice_size, depth = 32, 4
        elif file_size < 10240:
            lattice_size, depth = 64, 4
        elif file_size < 102400:
            lattice_size, depth = 96, 5
        else:
            lattice_size, depth = 128, 6
        
        # Create generator (lightweight - just stores parameters)
        self.generator = AlgorithmicDecoyGenerator(cel_seed_hash, lattice_size, depth)
        
        # Generate ONLY the specific decoy seed we need
        decoy_seeds = self.generator.generate_decoy_seeds(decoy_count)
        target_seed = decoy_seeds[decoy_index]
        
        # Generate only this one CEL
        decoy_cel = self.generator.generate_decoy_cel(target_seed)
        
        # Convert to bytes
        return decoy_cel.tobytes()
    
    def validate_metadata(self, file_size: int = None, cel_seed: bytes = None, decoy_count: int = None, metadata = None) -> bool:
        """Validate decoy metadata structure and parameters"""
        
        # Handle different call patterns for compatibility
        if metadata is None:
            # Called with file_size, cel_seed, decoy_count - validate against stored metadata
            if file_size is None or cel_seed is None or decoy_count is None:
                return False
            if not hasattr(self, '_current_metadata') or self._current_metadata is None:
                return False
                
            try:
                # Store current metadata before test
                original_metadata = self._current_metadata
                
                # Check if this seed would generate the same metadata  
                # Create a temporary generator without overwriting our state
                temp_generator = AlgorithmicDecoyGenerator(cel_seed, original_metadata.lattice_size, original_metadata.depth)
                test_seeds = temp_generator.generate_decoy_seeds(decoy_count)
                
                # Restore current metadata
                self._current_metadata = original_metadata
                
                # Compare the generated seeds
                return test_seeds == original_metadata.decoy_seeds
            except Exception:
                return False
        else:
            # Called with metadata object
            return self._validate_metadata_object(metadata)
    
    def _validate_metadata_object(self, metadata) -> bool:
        """Internal validation logic"""
        try:
            # Check basic structure
            if not hasattr(metadata, 'decoy_count') or not hasattr(metadata, 'decoy_seeds'):
                return False
            
            # Check decoy count matches seeds
            if len(metadata.decoy_seeds) != metadata.decoy_count:
                return False
            
            # Validate ranges
            if not (1 <= metadata.decoy_count <= 50):
                return False
            
            if not (16 <= metadata.lattice_size <= 512):
                return False
            
            if not (2 <= metadata.depth <= 16):
                return False
            
            return True
        except Exception:
            return False

def create_test_decoy_system(decoy_count: int = 3) -> Tuple[AlgorithmicDecoySystem, Dict[str, Any]]:
    """Create test decoy system for validation"""
    
    # Generate test real CEL seed
    real_seed = hashlib.sha256(b"test_cel_seed_v0.3.1").digest()
    
    # Create decoy system
    system = AlgorithmicDecoySystem()
    metadata = system.create_decoy_metadata(real_seed, decoy_count)
    system.load_decoy_metadata(metadata, real_seed)
    
    return system, metadata

def benchmark_decoy_generation(decoy_counts: List[int], lattice_sizes: List[int]) -> Dict[str, float]:
    """Benchmark decoy generation performance"""
    
    import time
    results = {}
    
    for decoy_count in decoy_counts:
        for lattice_size in lattice_sizes:
            key = f"{decoy_count}decoys_{lattice_size}size"
            
            # Create test system
            system, metadata = create_test_decoy_system(decoy_count)
            system.generator.lattice_size = lattice_size
            
            # Benchmark generation
            start_time = time.time()
            decoys = system.generate_all_decoys(metadata)
            elapsed = time.time() - start_time
            
            results[key] = {'time': elapsed, 'count': len(decoys)}
    
    return results

# Convenience functions for integration
def create_algorithmic_decoys(file_size: int, cel_seed: bytes, decoy_count: int = 3) -> Tuple[List[bytes], bytes]:
    """Create algorithmic decoys and return serialized metadata"""
    system = AlgorithmicDecoySystem()
    decoys = system.generate_decoys(file_size, cel_seed, decoy_count)
    metadata = system.create_decoy_metadata(cel_seed, decoy_count)
    return decoys, metadata.serialize()

def reconstruct_algorithmic_decoys(file_size: int, cel_seed: bytes, decoy_count: int = 3) -> List[bytes]:
    """Reconstruct algorithmic decoys from parameters"""
    system = AlgorithmicDecoySystem()
    return system.generate_decoys(file_size, cel_seed, decoy_count)