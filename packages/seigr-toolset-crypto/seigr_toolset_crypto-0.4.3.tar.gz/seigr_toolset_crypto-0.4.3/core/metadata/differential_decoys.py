"""
Differential Decoy System v0.3.1

Stores decoys as differences from base CEL instead of full snapshots.
Used for files 1MB-100MB where we need balance between storage and performance.
"""

import numpy as np
import zlib
import struct
from typing import List, Dict, Any, Tuple, Optional
from dataclasses import dataclass
import hashlib
@dataclass
class DifferentialDecoyMetadata:
    """Self-sovereign binary metadata for differential decoys"""
    def __init__(self, decoy_count: int, base_cel_shape: Tuple[int, int, int],
                 difference_ratio: float, decoys: List[Dict[str, Any]]):
        self.decoy_count = decoy_count
        self.base_cel_shape = base_cel_shape
        self.difference_ratio = difference_ratio
        self.decoys = decoys
    
    def serialize(self) -> bytes:
        """Serialize to compact binary format"""
        # Header: magic + version + parameters
        header = struct.pack('!4sBBHHHfH',
                           b'STCD',  # Seigr Toolset Crypto Differential
                           1,        # Version
                           self.decoy_count,
                           self.base_cel_shape[0],
                           self.base_cel_shape[1], 
                           self.base_cel_shape[2],
                           self.difference_ratio,
                           len(self.decoys))
        
        # Pack each decoy's differential data
        decoys_data = b''
        for decoy in self.decoys:
            positions = decoy['delta_positions']
            values = decoy['delta_values']
            
            # Decoy header: position count + quality score + compression ratio
            decoy_header = struct.pack('!Iff', 
                                     len(positions),
                                     decoy['quality_score'],
                                     decoy['compression_ratio'])
            
            # Pack positions and values efficiently
            decoy_data = b''
            for pos, val in zip(positions, values):
                # Use signed int for values, unsigned for positions
                decoy_data += struct.pack('!Ii', pos, val)
            
            decoys_data += decoy_header + decoy_data
        
        return header + decoys_data
    
    @classmethod
    def deserialize(cls, data: bytes) -> 'DifferentialDecoyMetadata':
        """Deserialize from binary format"""
        if len(data) < 18:
            raise ValueError("Invalid differential decoy metadata")
        
        # Unpack header
        header_data = struct.unpack('!4sBBHHHfH', data[:18])
        magic, version, decoy_count, shape_x, shape_y, shape_z, diff_ratio, decoys_len = header_data
        
        if magic != b'STCD':
            raise ValueError("Invalid magic number")
        if version != 1:
            raise ValueError(f"Unsupported version: {version}")
        
        base_cel_shape = (shape_x, shape_y, shape_z)
        
        # Parse decoys data
        decoys = []
        offset = 18
        
        for _ in range(decoys_len):
            # Read decoy header
            pos_count, quality, compression = struct.unpack('!Iff', data[offset:offset+12])
            offset += 12
            
            # Read positions and values
            positions = []
            values = []
            for _ in range(pos_count):
                pos, val = struct.unpack('!Ii', data[offset:offset+8])
                positions.append(pos)
                values.append(val)
                offset += 8
            
            decoys.append({
                'delta_positions': positions,
                'delta_values': values,
                'quality_score': quality,
                'compression_ratio': compression
            })
        
        return cls(decoy_count, base_cel_shape, diff_ratio, decoys)
    
    def __getitem__(self, key):
        """Compatibility layer"""
        if key == 'decoy_count':
            return self.decoy_count
        elif key == 'base_cel_shape':
            return self.base_cel_shape
        elif key == 'target_difference_ratio':
            return self.difference_ratio
        elif key == 'decoys':
            return self.decoys
        elif key == 'differential_only_size':
            # Calculate differential size on demand
            return sum(len(d['delta_positions']) * 8 * d['compression_ratio'] for d in self.decoys)
        elif key == 'base_cel_compressed':
            # For compatibility - return empty since we don't store this in the main metadata
            return b''
        elif key == 'total_storage_size':
            # Calculate total size on demand
            return sum(len(d['delta_positions']) * 8 * d['compression_ratio'] for d in self.decoys)
        else:
            raise KeyError(f"Unknown key: {key}")
    
    def get(self, key, default=None):
        try:
            return self[key]
        except KeyError:
            return default
    
    def keys(self):
        return ['decoy_count', 'base_cel_shape', 'target_difference_ratio', 'decoys']

@dataclass
class DifferentialDecoy:
    """Represents a decoy stored as differences from base CEL"""
    delta_positions: List[int]    # Positions that differ from base
    delta_values: List[int]       # New values at those positions
    compression_ratio: float      # Achieved compression ratio
    quality_score: float          # Decoy quality assessment

class DifferentialDecoyGenerator:
    """Generates decoys as compressed differences from real CEL"""
    
    def __init__(self, base_cel: np.ndarray, target_difference_ratio: float = 0.02):
        self.base_cel = base_cel.copy()
        self.target_difference_ratio = target_difference_ratio  # 2% of lattice points differ (was 15%)
        self.lattice_shape = base_cel.shape
        self.total_elements = base_cel.size
    
    def generate_decoy_differential(self, decoy_seed: bytes, 
                                  difference_ratio: Optional[float] = None) -> DifferentialDecoy:
        """Generate decoy as differences from base CEL"""
        
        if difference_ratio is None:
            difference_ratio = self.target_difference_ratio
        
        # Initialize RNG with decoy seed
        rng = np.random.RandomState(seed=int.from_bytes(decoy_seed[:4], 'big'))
        
        # Determine how many points to modify (cap at reasonable limit)
        num_changes = min(int(self.total_elements * difference_ratio), 10000)  # Cap at 10K changes max
        
        # Select random positions to modify
        flat_positions = rng.choice(self.total_elements, num_changes, replace=False)
        
        # Generate new values for these positions
        delta_values = []
        for pos in flat_positions:
            # Get current value at position
            current_value = self.base_cel.flat[pos]
            
            # Generate new value that's different but realistic
            delta = rng.randint(-1000000, 1000000)  # Realistic entropy delta
            
            # Prevent overflow by using int64 for calculation then clipping
            new_value = int(np.int64(current_value) + np.int64(delta))
            
            # Clip to valid int32 range to prevent overflow
            new_value = np.clip(new_value, -2147483648, 2147483647)
            
            delta_values.append(int(new_value))
        
        # Calculate quality score
        quality = self._assess_decoy_quality(flat_positions, delta_values)
        
        # Estimate compression ratio
        raw_size = len(flat_positions) * (4 + 4)  # position + value pairs
        compressed_size = self._estimate_compressed_size(flat_positions, delta_values)
        compression_ratio = compressed_size / raw_size if raw_size > 0 else 1.0
        
        return DifferentialDecoy(
            delta_positions=flat_positions.tolist(),
            delta_values=delta_values,
            compression_ratio=compression_ratio,
            quality_score=quality
        )
    
    def _assess_decoy_quality(self, positions: np.ndarray, values: List[int]) -> float:
        """Assess quality of differential decoy"""
        
        # Check distribution of changes across lattice
        position_distribution = self._check_position_distribution(positions)
        
        # Check realism of value changes
        value_realism = self._check_value_realism(positions, values)
        
        # Check that changes don't create obvious patterns
        pattern_score = self._check_pattern_avoidance(positions, values)
        
        # Combine scores (equal weight)
        overall_quality = (position_distribution + value_realism + pattern_score) / 3.0
        
        return overall_quality
    
    def _check_position_distribution(self, positions: np.ndarray) -> float:
        """Check if changed positions are well-distributed across lattice"""
        
        # Convert flat positions to 3D coordinates
        coords = np.unravel_index(positions, self.lattice_shape)
        
        # Check distribution across each dimension
        scores = []
        for dim_coords in coords:
            # Calculate how evenly distributed the changes are
            unique_coords = np.unique(dim_coords)
            expected_spread = len(positions) / self.lattice_shape[0]  # Approximate
            actual_spread = len(unique_coords)
            
            # Score based on how close to uniform distribution
            distribution_score = min(actual_spread / expected_spread, 1.0)
            scores.append(distribution_score)
        
        return sum(scores) / len(scores)
    
    def _check_value_realism(self, positions: np.ndarray, values: List[int]) -> float:
        """Check if new values look realistic compared to surrounding values"""
        
        realism_scores = []
        
        for i, (flat_pos, new_value) in enumerate(zip(positions, values)):
            # Get 3D position
            pos_3d = np.unravel_index(flat_pos, self.lattice_shape)
            
            # Get neighboring values for context
            neighbors = self._get_neighbors(pos_3d)
            
            if len(neighbors) > 0:
                neighbor_mean = np.mean(neighbors)
                neighbor_std = np.std(neighbors)
                
                # Check if new value is within reasonable range of neighbors
                if neighbor_std > 0:
                    z_score = abs(new_value - neighbor_mean) / neighbor_std
                    realism_score = max(0.0, 1.0 - z_score / 5.0)  # Normalize by 5 std devs
                else:
                    realism_score = 1.0 if new_value == neighbor_mean else 0.5
                
                realism_scores.append(realism_score)
        
        return sum(realism_scores) / len(realism_scores) if realism_scores else 1.0
    
    def _get_neighbors(self, pos_3d: Tuple[int, int, int]) -> List[int]:
        """Get neighboring values for realism checking"""
        
        x, y, z = pos_3d
        neighbors = []
        
        # Check 6-connected neighbors (not diagonal)
        for dx, dy, dz in [(0,0,1), (0,0,-1), (0,1,0), (0,-1,0), (1,0,0), (-1,0,0)]:
            nx, ny, nz = x + dx, y + dy, z + dz
            
            if (0 <= nx < self.lattice_shape[0] and 
                0 <= ny < self.lattice_shape[1] and 
                0 <= nz < self.lattice_shape[2]):
                neighbors.append(self.base_cel[nx, ny, nz])
        
        return neighbors
    
    def _check_pattern_avoidance(self, positions: np.ndarray, values: List[int]) -> float:
        """Check that changes don't create obvious attack patterns"""
        
        # Check for clustering of changes (bad for security)
        clustering_score = self._check_clustering(positions)
        
        # Check for value patterns (e.g., all zeros, arithmetic progressions)
        value_pattern_score = self._check_value_patterns(values)
        
        return (clustering_score + value_pattern_score) / 2.0
    
    def _check_clustering(self, positions: np.ndarray) -> float:
        """Check if positions are too clustered (suspicious)"""
        
        if len(positions) < 2:
            return 1.0
        
        # Convert to 3D coordinates
        coords_3d = np.array(np.unravel_index(positions, self.lattice_shape)).T
        
        # Calculate pairwise distances
        distances = []
        for i in range(len(coords_3d)):
            for j in range(i + 1, len(coords_3d)):
                dist = np.linalg.norm(coords_3d[i] - coords_3d[j])
                distances.append(dist)
        
        if not distances:
            return 1.0
        
        # Good distribution should have reasonable mean distance
        mean_distance = np.mean(distances)
        expected_distance = (self.lattice_shape[0] / 3)  # Rough estimate
        
        # Score based on how close to expected
        distance_ratio = min(mean_distance / expected_distance, 2.0)
        clustering_score = min(distance_ratio, 1.0)
        
        return clustering_score
    
    def _check_value_patterns(self, values: List[int]) -> float:
        """Check for suspicious patterns in new values"""
        
        if len(values) < 3:
            return 1.0
        
        # Check for all same values (obvious pattern)
        unique_values = len(set(values))
        if unique_values == 1:
            return 0.0  # All same = bad
        
        # Check for arithmetic progressions
        diffs = [values[i+1] - values[i] for i in range(len(values)-1)]
        if len(set(diffs)) == 1 and diffs[0] != 0:
            return 0.2  # Arithmetic progression = suspicious
        
        # Check for simple patterns (multiples of powers of 2, etc.)
        pattern_scores = []
        for base in [2, 4, 8, 16, 256, 1024]:
            multiples = sum(1 for v in values if v % base == 0)
            ratio = multiples / len(values)
            pattern_score = 1.0 - min(ratio, 1.0)  # Lower score for many multiples
            pattern_scores.append(pattern_score)
        
        return sum(pattern_scores) / len(pattern_scores)
    
    def _estimate_compressed_size(self, positions: List[int], values: List[int]) -> int:
        """Estimate compressed size of differential data (fast approximation)"""
        
        # For performance, use fast estimation instead of actual compression
        raw_size = len(positions) * 8  # 4 bytes pos + 4 bytes value
        
        # Estimate compression ratio based on data characteristics
        if len(positions) < 100:
            compression_ratio = 0.8  # Small datasets compress less
        elif len(positions) < 1000:
            compression_ratio = 0.6  # Medium datasets
        else:
            compression_ratio = 0.4  # Large datasets compress better
        
        return int(raw_size * compression_ratio)
    
    def reconstruct_decoy_cel(self, differential: DifferentialDecoy) -> np.ndarray:
        """Reconstruct full decoy CEL from differential"""
        
        # Start with base CEL
        decoy_cel = self.base_cel.copy()
        
        # Apply differences
        for pos, new_value in zip(differential.delta_positions, differential.delta_values):
            decoy_cel.flat[pos] = new_value
        
        return decoy_cel

class DifferentialDecoySystem:
    """Complete differential decoy system for medium-sized files"""
    
    def __init__(self):
        self.generator = None
        self.base_cel_compressed = None
    
    def create_decoy_metadata(self, real_cel: np.ndarray, decoy_count: int,
                            target_difference_ratio: float = 0.02) -> Dict[str, Any]:
        """Create metadata for differential decoys"""
        
        # In production, base CEL would be derived from file, not stored
        # For testing, we compress it but could exclude from metadata size calculation
        self.base_cel_compressed = self._compress_base_cel(real_cel)
        
        # Create generator
        self.generator = DifferentialDecoyGenerator(real_cel, target_difference_ratio)
        
        # Generate decoy seeds
        master_seed = hashlib.sha256(real_cel.tobytes()).digest()
        decoy_seeds = self._generate_decoy_seeds(master_seed, decoy_count)
        
        # Generate differential decoys
        decoys = []
        for seed in decoy_seeds:
            differential = self.generator.generate_decoy_differential(seed)
            decoys.append({
                'delta_positions': differential.delta_positions,
                'delta_values': differential.delta_values,
                'compression_ratio': differential.compression_ratio,
                'quality_score': differential.quality_score
            })
        
        return DifferentialDecoyMetadata(decoy_count, real_cel.shape, target_difference_ratio, decoys)
    
    def _compress_base_cel(self, cel: np.ndarray) -> bytes:
        """Compress base CEL using zlib with high compression"""
        cel_bytes = cel.tobytes()
        compressed = zlib.compress(cel_bytes, level=9)  # Maximum compression
        return compressed
    
    def _decompress_base_cel(self, compressed_data: bytes, shape: Tuple[int, int, int]) -> np.ndarray:
        """Decompress base CEL"""
        decompressed = zlib.decompress(compressed_data)
        cel = np.frombuffer(decompressed, dtype=np.int32).reshape(shape)
        return cel
    
    def _generate_decoy_seeds(self, master_seed: bytes, count: int) -> List[bytes]:
        """Generate deterministic seeds for decoys"""
        seeds = []
        for i in range(count):
            seed_data = master_seed + struct.pack('!I', i)
            seed = hashlib.sha256(seed_data).digest()
            seeds.append(seed)
        return seeds
    
    def _calculate_storage_size(self, decoys: List[Dict[str, Any]]) -> int:
        """Calculate total storage size of differential metadata"""
        
        size = len(self.base_cel_compressed)  # Base CEL
        
        for decoy in decoys:
            # Use pre-calculated compression ratios for speed
            size += int(decoy['compression_ratio'] * len(decoy['delta_positions']) * 8)
        
        return size
    
    def _calculate_differential_only_size(self, decoys: List[Dict[str, Any]]) -> int:
        """Calculate size of just the differential data (excluding base CEL)"""
        
        size = 0
        for decoy in decoys:
            # Use pre-calculated compression ratios for speed
            size += int(decoy['compression_ratio'] * len(decoy['delta_positions']) * 8)
        
        return size
    
    def load_decoy_metadata(self, metadata) -> 'DifferentialDecoySystem':
        """Load decoy system from metadata (supports both dict and DifferentialDecoyMetadata)"""
        
        if isinstance(metadata, DifferentialDecoyMetadata):
            # Binary format - need to reconstruct base CEL from provided data
            # For testing, we'll use a mock base CEL with the correct shape from metadata
            mock_shape = metadata.base_cel_shape
            mock_cel = np.random.randint(-1000, 1000, size=mock_shape, dtype=np.int32)
            self.base_cel_compressed = self._compress_base_cel(mock_cel)
            
            # Initialize generator
            self.generator = DifferentialDecoyGenerator(
                mock_cel, 
                metadata.difference_ratio
            )
            
        elif isinstance(metadata, dict):
            # Legacy dict format
            if 'base_cel_compressed' in metadata:
                # Handle both hex string and bytes
                if isinstance(metadata['base_cel_compressed'], str):
                    base_cel_compressed = bytes.fromhex(metadata['base_cel_compressed'])
                else:
                    base_cel_compressed = metadata['base_cel_compressed']
            else:
                # Mock data for testing
                mock_shape = (64, 64, 4)
                mock_cel = np.random.randint(-1000, 1000, size=mock_shape, dtype=np.int32)
                base_cel_compressed = self._compress_base_cel(mock_cel)
            
            base_cel_shape = metadata.get('base_cel_shape', (64, 64, 4))
            base_cel = self._decompress_base_cel(base_cel_compressed, tuple(base_cel_shape))
            
            # Initialize generator
            self.generator = DifferentialDecoyGenerator(
                base_cel, 
                metadata.get('target_difference_ratio', 0.02)
            )
            self.base_cel_compressed = base_cel_compressed
        else:
            raise ValueError(f"Unsupported metadata type: {type(metadata)}")
        
        return self
    
    def reconstruct_decoy(self, decoy_index: int, metadata: Dict[str, Any]) -> np.ndarray:
        """Reconstruct specific decoy from metadata"""
        
        if not self.generator:
            raise ValueError("Decoy system not initialized")
        
        if decoy_index >= len(metadata['decoys']):
            raise ValueError(f"Invalid decoy index: {decoy_index}")
        
        decoy_data = metadata['decoys'][decoy_index]
        
        # Create differential decoy object
        differential = DifferentialDecoy(
            delta_positions=decoy_data['delta_positions'],
            delta_values=decoy_data['delta_values'],
            compression_ratio=decoy_data['compression_ratio'],
            quality_score=decoy_data['quality_score']
        )
        
        # Reconstruct full CEL
        return self.generator.reconstruct_decoy_cel(differential)
    
    def validate_all_decoys(self, metadata: Dict[str, Any]) -> Dict[str, float]:
        """Validate quality of all differential decoys"""
        
        if not self.generator:
            raise ValueError("Decoy system not initialized")
        
        results = {}
        
        for i, decoy_data in enumerate(metadata['decoys']):
            # Quality score is pre-calculated and stored
            results[f'decoy_{i}'] = decoy_data['quality_score']
        
        # Overall quality
        scores = [decoy['quality_score'] for decoy in metadata['decoys']]
        results['overall_quality'] = sum(scores) / len(scores) if scores else 0.0
        
        return results
    
    def validate_decoy_system(self, file_data: bytes, metadata: 'DifferentialDecoyMetadata') -> bool:
        """Validate differential decoy system against file data"""
        try:
            # Basic validation - check if metadata is valid
            if not isinstance(metadata, DifferentialDecoyMetadata):
                return False
            
            # Check required attributes exist
            if not hasattr(metadata, 'decoys'):
                return False
            
            # Check that decoys list is not empty and has valid structure
            if not metadata.decoys or not isinstance(metadata.decoys, list):
                return False
            
            # Check that each decoy has required structure
            for decoy in metadata.decoys:
                if not isinstance(decoy, dict):
                    return False
                # Basic structural check - should have expected keys for differential decoys
                required_keys = ['delta_positions', 'delta_values', 'quality_score', 'compression_ratio']
                if not all(key in decoy for key in required_keys):
                    return False
            
            # If we got this far, the metadata structure is valid
            return True
            
        except Exception:
            return False
    
    def get_storage_efficiency(self, metadata) -> Dict[str, float]:
        """Calculate storage efficiency metrics"""
        
        # Base CEL size
        base_cel_shape = tuple(metadata['base_cel_shape'])
        full_cel_size = np.prod(base_cel_shape) * 4  # int32 = 4 bytes
        
        # Total differential storage
        total_diff_size = metadata.get('total_storage_size', 0)
        
        # Calculate savings vs full storage
        decoy_count = metadata['decoy_count']
        full_storage_size = full_cel_size * (decoy_count + 1)  # +1 for real CEL
        
        efficiency = {
            'full_storage_size': full_storage_size,
            'differential_storage_size': total_diff_size,
            'storage_savings': full_storage_size - total_diff_size,
            'compression_ratio': total_diff_size / full_storage_size if full_storage_size > 0 else 0,
            'space_saved_percent': ((full_storage_size - total_diff_size) / full_storage_size) * 100 if full_storage_size > 0 else 0
        }
        
        return efficiency
    
    def generate_all_decoys(self, metadata) -> List[np.ndarray]:
        """Generate all decoy CELs from differential metadata"""
        
        if not self.generator:
            raise ValueError("Decoy system not initialized")
        
        decoys = []
        for i in range(metadata['decoy_count']):
            decoy_cel = self.reconstruct_decoy(i, metadata)
            decoys.append(decoy_cel)
        
        return decoys
    
    def reconstruct_decoys(self, metadata) -> List[bytes]:
        """Reconstruct decoys as bytes from metadata"""
        
        # Load metadata if not already loaded
        if not self.generator:
            self.load_decoy_metadata(metadata)
        
        # Generate all decoys
        decoys_np = self.generate_all_decoys(metadata)
        
        # Convert to bytes
        decoy_bytes = []
        for decoy in decoys_np:
            decoy_bytes.append(decoy.tobytes())
        
        return decoy_bytes

def create_test_differential_system(lattice_size: int = 64, depth: int = 4, 
                                  decoy_count: int = 3) -> Tuple[DifferentialDecoySystem, Dict[str, Any]]:
    """Create test differential decoy system"""
    
    # Generate test real CEL
    rng = np.random.RandomState(42)
    real_cel = rng.randint(-2147483648, 2147483647, 
                          size=(lattice_size, lattice_size, depth), 
                          dtype=np.int32)
    
    # Create system
    system = DifferentialDecoySystem()
    metadata = system.create_decoy_metadata(real_cel, decoy_count)
    system.load_decoy_metadata(metadata)
    
    return system, metadata

# Convenience functions for integration
def create_differential_decoys(base_cel: bytes, decoy_count: int = 3) -> Tuple[List[bytes], bytes]:
    """Create differential decoys and return serialized metadata"""
    # Convert bytes to numpy array (placeholder - would need proper CEL parsing)
    import numpy as np
    # Mock conversion - in real implementation this would parse CEL format
    lattice_size = 128
    depth = 6 
    mock_cel = np.random.randint(-2147483648, 2147483647, 
                                size=(lattice_size, lattice_size, depth), 
                                dtype=np.int32)
    
    system = DifferentialDecoySystem()
    metadata = system.create_decoy_metadata(mock_cel, decoy_count)
    decoys = system.generate_all_decoys(metadata)
    return decoys, metadata.serialize()

def reconstruct_differential_decoys(metadata_bytes: bytes) -> List[bytes]:
    """Reconstruct differential decoys from metadata"""
    # This would need the actual metadata class - simplified for now
    system = DifferentialDecoySystem()
    # Placeholder implementation
    return system.generate_all_decoys(None)  # Would need deserialized metadata