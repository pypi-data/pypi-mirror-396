"""
Selective Decoy System v0.3.1

For files >100MB, uses intelligent sampling to create decoys from specific file segments.
Minimizes metadata overhead while maintaining security through strategic decoy placement.
"""

import hashlib
import zlib
import struct
from typing import List, Tuple, Dict, Any
from dataclasses import dataclass
import math

@dataclass
class SelectiveDecoyInfo:
    """Information about a selective decoy"""
    segment_offset: int      # Where in file this segment was taken
    segment_size: int        # Size of the segment
    quality_score: float     # Quality assessment (0.0-1.0)
    entropy_score: float     # Entropy of the segment
    pattern_signature: bytes # Hash signature for pattern detection
    decoy_seed: bytes       # Seed for generating this decoy
    compression_ratio: float # How well the segment compressed

@dataclass
class SelectiveDecoyMetadata:
    """Metadata for selective decoy system"""
    total_segments: int                    # Total segments analyzed
    selected_segments: List[SelectiveDecoyInfo]  # Selected segment info
    sampling_strategy: str                 # Strategy used for sampling
    file_analysis: Dict[str, Any]         # Analysis of file characteristics
    validation_hash: bytes                # Hash for integrity validation
    
    def serialize(self) -> bytes:
        """Serialize metadata to bytes"""
        data = {
            'total_segments': self.total_segments,
            'selected_segments': [
                {
                    'segment_offset': seg.segment_offset,
                    'segment_size': seg.segment_size,
                    'quality_score': seg.quality_score,
                    'entropy_score': seg.entropy_score,
                    'pattern_signature': seg.pattern_signature.hex(),
                    'decoy_seed': seg.decoy_seed.hex(),
                    'compression_ratio': seg.compression_ratio
                }
                for seg in self.selected_segments
            ],
            'sampling_strategy': self.sampling_strategy,
            'file_analysis': self.file_analysis,
            'validation_hash': self.validation_hash.hex()
        }
        
        # Serialize and compress
        serialized = str(data).encode('utf-8')
        return zlib.compress(serialized, level=9)
    
    @classmethod
    def deserialize(cls, data: bytes) -> 'SelectiveDecoyMetadata':
        """Deserialize metadata from bytes"""
        try:
            import ast
            decompressed = zlib.decompress(data)
            data_dict = ast.literal_eval(decompressed.decode('utf-8'))
            
            # Reconstruct selected segments
            selected_segments = []
            for seg_data in data_dict['selected_segments']:
                segment_info = SelectiveDecoyInfo(
                    segment_offset=seg_data['segment_offset'],
                    segment_size=seg_data['segment_size'],
                    quality_score=seg_data['quality_score'],
                    entropy_score=seg_data['entropy_score'],
                    pattern_signature=bytes.fromhex(seg_data['pattern_signature']),
                    decoy_seed=bytes.fromhex(seg_data['decoy_seed']),
                    compression_ratio=seg_data['compression_ratio']
                )
                selected_segments.append(segment_info)
            
            return cls(
                total_segments=data_dict['total_segments'],
                selected_segments=selected_segments,
                sampling_strategy=data_dict['sampling_strategy'],
                file_analysis=data_dict['file_analysis'],
                validation_hash=bytes.fromhex(data_dict['validation_hash'])
            )
        except Exception as e:
            raise ValueError(f"Failed to deserialize selective decoy metadata: {e}")

class SelectiveDecoyGenerator:
    """Generates decoys using selective sampling for large files"""
    
    def __init__(self, segment_size: int = 64 * 1024):  # 64KB segments
        self.segment_size = segment_size
        self.min_entropy = 3.0  # Minimum entropy for good segments
        self.max_segments_to_analyze = 1000  # Limit analysis for huge files
        
    def analyze_file_segments(self, file_data: bytes) -> List[Tuple[int, float, float]]:
        """Analyze file segments and return (offset, entropy, quality) tuples"""
        
        file_size = len(file_data)
        segments = []
        
        # Calculate number of segments to analyze
        total_possible_segments = file_size // self.segment_size
        segments_to_analyze = min(total_possible_segments, self.max_segments_to_analyze)
        
        # If we need to sample, use strategic sampling
        if segments_to_analyze < total_possible_segments:
            segment_offsets = self._get_strategic_offsets(file_size, segments_to_analyze)
        else:
            segment_offsets = list(range(0, file_size, self.segment_size))
        
        # Analyze each selected segment
        for offset in segment_offsets:
            if offset + self.segment_size > file_size:
                continue
            
            segment = file_data[offset:offset + self.segment_size]
            entropy = self._calculate_entropy(segment)
            quality = self._assess_segment_quality(segment, offset, file_size)
            
            segments.append((offset, entropy, quality))
        
        return segments
    
    def _get_strategic_offsets(self, file_size: int, count: int) -> List[int]:
        """Get strategic segment offsets for analysis"""
        
        offsets = []
        
        # Always include beginning and end
        offsets.append(0)
        if file_size > self.segment_size:
            offsets.append(file_size - self.segment_size)
        
        # Add evenly distributed middle segments
        remaining = count - len(offsets)
        if remaining > 0:
            step = file_size // (remaining + 1)
            for i in range(1, remaining + 1):
                offset = i * step
                # Align to reasonable boundaries
                offset = (offset // self.segment_size) * self.segment_size
                if offset not in offsets and offset + self.segment_size <= file_size:
                    offsets.append(offset)
        
        return sorted(offsets)
    
    def _calculate_entropy(self, data: bytes) -> float:
        """Calculate Shannon entropy of data"""
        if not data:
            return 0.0
        
        # Count byte frequencies
        frequencies = [0] * 256
        for byte in data:
            frequencies[byte] += 1
        
        # Calculate Shannon entropy
        entropy = 0.0
        data_len = len(data)
        for freq in frequencies:
            if freq > 0:
                p = freq / data_len
                entropy -= p * math.log2(p)
        
        return entropy
    
    def _assess_segment_quality(self, segment: bytes, offset: int, file_size: int) -> float:
        """Assess quality of a segment for decoy generation"""
        
        quality = 0.0
        
        # Entropy contribution (40%)
        entropy = self._calculate_entropy(segment)
        entropy_score = min(1.0, entropy / 8.0)  # Normalize to 0-1
        quality += entropy_score * 0.4
        
        # Compression resistance (30%)
        try:
            compressed = zlib.compress(segment, level=1)
            compression_ratio = len(compressed) / len(segment)
            compression_score = min(1.0, compression_ratio)  # Higher ratio = better
            quality += compression_score * 0.3
        except Exception:
            compression_score = 0.5  # Neutral if compression fails
            quality += compression_score * 0.3
        
        # Position diversity (20%)
        position_score = 1.0 - abs(0.5 - offset / file_size)  # Prefer middle sections
        quality += position_score * 0.2
        
        # Pattern uniqueness (10%)
        pattern_hash = hashlib.sha256(segment).digest()[:8]
        pattern_uniqueness = len(set(pattern_hash)) / 8.0  # Byte diversity
        quality += pattern_uniqueness * 0.1
        
        return quality
    
    def select_best_segments(self, segments: List[Tuple[int, float, float]], 
                           target_count: int = 3) -> List[SelectiveDecoyInfo]:
        """Select best segments for decoy generation"""
        
        # Filter segments with minimum entropy
        good_segments = [(offset, entropy, quality) for offset, entropy, quality in segments 
                        if entropy >= self.min_entropy]
        
        if not good_segments:
            # Fall back to best available segments
            good_segments = sorted(segments, key=lambda x: x[1], reverse=True)[:target_count * 2]
        
        # Sort by combined score (entropy + quality)
        scored_segments = []
        for offset, entropy, quality in good_segments:
            combined_score = (entropy / 8.0) * 0.6 + quality * 0.4
            scored_segments.append((offset, entropy, quality, combined_score))
        
        # Select top segments with diversity
        selected = []
        used_offsets = set()
        min_distance = self.segment_size * 2  # Minimum distance between segments
        
        # Sort by combined score
        scored_segments.sort(key=lambda x: x[3], reverse=True)
        
        for offset, entropy, quality, score in scored_segments:
            if len(selected) >= target_count:
                break
            
            # Check distance from already selected segments
            too_close = any(abs(offset - used_offset) < min_distance 
                          for used_offset in used_offsets)
            
            if not too_close:
                # Generate segment info
                # Generate deterministic seed from segment characteristics
                seed_input = f"selective_decoy_{offset}_{entropy:.6f}_{quality:.6f}_{self.segment_size}".encode()
                deterministic_seed = hashlib.sha256(seed_input).digest()
                
                segment_info = SelectiveDecoyInfo(
                    segment_offset=offset,
                    segment_size=self.segment_size,
                    quality_score=quality,
                    entropy_score=entropy,
                    pattern_signature=hashlib.sha256(f"{offset}:{entropy}:{quality}".encode()).digest()[:16],
                    decoy_seed=deterministic_seed,
                    compression_ratio=score  # Store combined score for now
                )
                
                selected.append(segment_info)
                used_offsets.add(offset)
        
        return selected
    
    def generate_decoys_from_segments(self, file_data: bytes, 
                                    segment_infos: List[SelectiveDecoyInfo],
                                    decoy_count: int = 3) -> List[bytes]:
        """Generate decoys from selected segments"""
        
        decoys = []
        
        for i, segment_info in enumerate(segment_infos[:decoy_count]):
            # Extract the segment
            offset = segment_info.segment_offset
            size = segment_info.segment_size
            
            if offset + size > len(file_data):
                size = len(file_data) - offset
            
            segment = file_data[offset:offset + size]
            
            # Generate decoy using segment as base with seed-based variations
            decoy = self._generate_decoy_from_segment(segment, segment_info.decoy_seed, i)
            decoys.append(decoy)
        
        return decoys
    
    def _generate_decoy_from_segment(self, segment: bytes, seed: bytes, index: int) -> bytes:
        """Generate a decoy CEL from a file segment"""
        
        # Create reproducible randomness from seed
        rng_state = hashlib.sha256(seed + struct.pack('>I', index)).digest()
        
        # Use segment as base structure but modify content
        decoy_data = bytearray(segment)
        
        # Apply seed-based transformations
        for i in range(0, len(decoy_data), 32):
            # Generate transformation key from RNG state
            key = hashlib.sha256(rng_state + struct.pack('>I', i // 32)).digest()
            
            # Apply XOR transformation to block
            block_end = min(i + 32, len(decoy_data))
            for j in range(i, block_end):
                decoy_data[j] ^= key[j - i]
        
        # Add some structural variations to make it look like valid CEL
        # Generate deterministic header and footer from seed
        header_seed = hashlib.sha256(seed + b'_header_' + struct.pack('>I', index)).digest()
        footer_seed = hashlib.sha256(seed + b'_footer_' + struct.pack('>I', index)).digest()
        
        header = b'FAKE_CEL' + header_seed[:24]  # 32-byte deterministic header
        footer = footer_seed[:16]  # 16-byte deterministic footer
        
        return header + bytes(decoy_data) + footer

class SelectiveDecoySystem:
    """Complete selective decoy system for large files"""
    
    def __init__(self, segment_size: int = 64 * 1024):
        self.generator = SelectiveDecoyGenerator(segment_size)
        
    def create_decoy_system(self, file_data: bytes, decoy_count: int = 3) -> Tuple[List[bytes], SelectiveDecoyMetadata]:
        """Create complete selective decoy system"""
        
        # Analyze file segments
        segments = self.generator.analyze_file_segments(file_data)
        
        # Select best segments
        selected_segments = self.generator.select_best_segments(segments, decoy_count)
        
        # Generate decoys
        decoys = self.generator.generate_decoys_from_segments(file_data, selected_segments, decoy_count)
        
        # Create file analysis
        file_analysis = {
            'file_size': len(file_data),
            'total_segments_analyzed': len(segments),
            'average_entropy': sum(s[1] for s in segments) / len(segments) if segments else 0.0,
            'average_quality': sum(s[2] for s in segments) / len(segments) if segments else 0.0,
            'selected_segment_count': len(selected_segments),
            'decoy_generation_strategy': 'segment_based_with_seed_variations'
        }
        
        # Create comprehensive validation hash
        hash_segments = []
        file_size = len(file_data)
        
        # Always include start and end
        hash_segments.append(file_data[:min(1024, file_size)])
        if file_size > 1024:
            hash_segments.append(file_data[-1024:])
        
        # Add middle segments for comprehensive validation
        if file_size > 10240:  # Only for files >10KB
            # Use more sampling points for better coverage with larger segments
            sample_points = [
                file_size // 8,      # 12.5%
                file_size // 4,      # 25%
                3 * file_size // 8,  # 37.5%
                file_size // 2,      # 50%
                5 * file_size // 8,  # 62.5%
                3 * file_size // 4,  # 75%
                7 * file_size // 8   # 87.5%
            ]
            
            for point in sample_points:
                # Take 12288 bytes at each sample point for better coverage
                end_point = min(point + 12288, file_size)
                if point < file_size:
                    hash_segments.append(file_data[point:end_point])
        
        comprehensive_data = b''.join(hash_segments)
        validation_hash = hashlib.sha256(comprehensive_data).digest()
        
        # Create metadata
        metadata = SelectiveDecoyMetadata(
            total_segments=len(segments),
            selected_segments=selected_segments,
            sampling_strategy='strategic_entropy_quality',
            file_analysis=file_analysis,
            validation_hash=validation_hash
        )
        
        return decoys, metadata
    
    def validate_decoy_system(self, file_data: bytes, metadata: SelectiveDecoyMetadata) -> bool:
        """Validate selective decoy system"""
        
        # Validate file matches metadata using comprehensive hashing
        # Use file size check first for fast rejection
        if len(file_data) != metadata.file_analysis.get('file_size', 0):
            return False
        
        # For stronger validation, hash several segments across the file
        hash_segments = []
        file_size = len(file_data)
        
        # Always include start and end
        hash_segments.append(file_data[:min(1024, file_size)])
        if file_size > 1024:
            hash_segments.append(file_data[-1024:])
        
        # Add middle segments for comprehensive validation
        if file_size > 10240:  # Only for files >10KB
            # Use more sampling points for better coverage with larger segments
            sample_points = [
                file_size // 8,      # 12.5%
                file_size // 4,      # 25%
                3 * file_size // 8,  # 37.5%
                file_size // 2,      # 50%
                5 * file_size // 8,  # 62.5%
                3 * file_size // 4,  # 75%
                7 * file_size // 8   # 87.5%
            ]
            
            for point in sample_points:
                # Take 12288 bytes at each sample point for better coverage
                end_point = min(point + 12288, file_size)
                if point < file_size:
                    hash_segments.append(file_data[point:end_point])
        
        # Compute comprehensive hash
        comprehensive_data = b''.join(hash_segments)
        expected_hash = hashlib.sha256(comprehensive_data).digest()
        
        if expected_hash != metadata.validation_hash:
            return False
        
        # Validate segment information
        for segment_info in metadata.selected_segments:
            offset = segment_info.segment_offset
            size = segment_info.segment_size
            
            if offset + size > len(file_data):
                return False
            
            # Validate segment still has reasonable entropy
            segment = file_data[offset:offset + size]
            entropy = self.generator._calculate_entropy(segment)
            
            # Allow some deviation due to file changes
            if abs(entropy - segment_info.entropy_score) > 2.0:
                return False
        
        return True
    
    def reconstruct_decoys(self, file_data: bytes, metadata: SelectiveDecoyMetadata) -> List[bytes]:
        """Reconstruct decoys from file and metadata"""
        
        if not self.validate_decoy_system(file_data, metadata):
            raise ValueError("Cannot reconstruct decoys: validation failed")
        
        # Regenerate decoys using stored segment information
        decoys = self.generator.generate_decoys_from_segments(
            file_data, metadata.selected_segments
        )
        
        return decoys
    
    def estimate_metadata_size(self, file_size: int, decoy_count: int = 3) -> int:
        """Estimate metadata size for selective decoy system"""
        
        # Base metadata structure
        base_size = 200  # Basic metadata fields
        
        # Per-segment info (approximately 100 bytes per segment)
        segment_info_size = decoy_count * 100
        
        # File analysis data
        analysis_size = 150
        
        # Compression overhead
        compression_overhead = 50
        
        total_size = base_size + segment_info_size + analysis_size + compression_overhead
        
        # Scale slightly with file size (for more detailed analysis)
        scale_factor = min(2.0, 1.0 + file_size / (1024 * 1024 * 1024))  # Max 2x for 1GB+
        
        return int(total_size * scale_factor)

# Convenience functions
def create_selective_decoys(file_data: bytes, decoy_count: int = 3) -> Tuple[List[bytes], bytes]:
    """Create selective decoys and return serialized metadata"""
    system = SelectiveDecoySystem()
    decoys, metadata = system.create_decoy_system(file_data, decoy_count)
    return decoys, metadata.serialize()

def reconstruct_selective_decoys(file_data: bytes, metadata_bytes: bytes) -> List[bytes]:
    """Reconstruct selective decoys from file and metadata"""
    system = SelectiveDecoySystem()
    metadata = SelectiveDecoyMetadata.deserialize(metadata_bytes)
    return system.reconstruct_decoys(file_data, metadata)