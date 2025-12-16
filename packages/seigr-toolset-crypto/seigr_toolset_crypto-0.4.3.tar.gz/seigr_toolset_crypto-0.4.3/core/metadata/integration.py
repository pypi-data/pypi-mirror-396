"""
Metadata Integration Layer v0.3.1

Integrates all metadata components into a unified system.
Provides the main interface for STC v0.3.1 metadata operations.
"""

from typing import List, Dict, Any, Optional
import hashlib
import secrets

# Import all metadata components
from .layered_format import (
    LayeredMetadata, MetadataFactory, SecurityProfile, DecoyStrategy
)
from .algorithmic_decoys import AlgorithmicDecoySystem, create_algorithmic_decoys
from .differential_decoys import DifferentialDecoySystem, create_differential_decoys
from .selective_decoys import SelectiveDecoySystem, create_selective_decoys

class MetadataSystem:
    """Main interface for STC metadata system"""
    
    def __init__(self):
        self.algorithmic_system = AlgorithmicDecoySystem()
        self.differential_system = DifferentialDecoySystem()
        self.selective_system = SelectiveDecoySystem()
    
    def generate_metadata(self, file_data: bytes, 
                         security_profile: SecurityProfile = SecurityProfile.DOCUMENT,
                         custom_params: Optional[Dict[str, Any]] = None,
                         file_size: Optional[int] = None) -> LayeredMetadata:
        """Generate complete metadata for a file"""
        
        if file_size is None:
            file_size = len(file_data)
        
        # Generate CEL seed and hash
        cel_seed = secrets.token_bytes(32)
        cel_seed_hash = hashlib.sha256(cel_seed).digest()
        
        # Create base metadata structure
        metadata = MetadataFactory.create_metadata(
            file_size=file_size,
            cel_seed_hash=cel_seed_hash,
            security_profile=security_profile,
            custom_params=custom_params
        )
        
        # Generate decoys based on strategy
        decoy_strategy = MetadataFactory.select_decoy_strategy(
            file_size, metadata.security.decoy_count
        )
        
        if decoy_strategy == DecoyStrategy.ALGORITHMIC:
            decoys, decoy_metadata = create_algorithmic_decoys(
                file_size, cel_seed, metadata.security.decoy_count
            )
            
        elif decoy_strategy == DecoyStrategy.DIFFERENTIAL:
            # Create a base CEL for differential system
            base_cel = self._generate_base_cel(file_data, cel_seed)
            decoys, decoy_metadata = create_differential_decoys(
                base_cel, metadata.security.decoy_count
            )
            
        else:  # SELECTIVE
            decoys, decoy_metadata = create_selective_decoys(
                file_data, metadata.security.decoy_count
            )
        
        # Store decoy metadata in security layer
        metadata.security.decoy_metadata = decoy_metadata
        metadata.security.decoy_strategy = decoy_strategy.value
        
        # Store actual decoys (in real implementation, these would be stored separately)
        metadata._generated_decoys = decoys
        
        return metadata
    
    def reconstruct_decoys(self, file_data: bytes, metadata: LayeredMetadata) -> List[bytes]:
        """Reconstruct decoys from file and metadata"""
        
        strategy = DecoyStrategy(metadata.security.decoy_strategy)
        decoy_metadata = metadata.security.decoy_metadata
        
        if strategy == DecoyStrategy.ALGORITHMIC:
            # Reconstruct using algorithmic system
            return self.algorithmic_system.reconstruct_decoys(
                len(file_data), metadata.core.cel_seed_hash, 
                metadata.security.decoy_count
            )
            
        elif strategy == DecoyStrategy.DIFFERENTIAL:
            # Reconstruct using differential system
            from .differential_decoys import DifferentialDecoyMetadata
            diff_metadata = DifferentialDecoyMetadata.deserialize(decoy_metadata)
            return self.differential_system.reconstruct_decoys(diff_metadata)
            
        else:  # SELECTIVE
            # Reconstruct using selective system
            from .selective_decoys import SelectiveDecoyMetadata
            sel_metadata = SelectiveDecoyMetadata.deserialize(decoy_metadata)
            return self.selective_system.reconstruct_decoys(file_data, sel_metadata)
    
    def validate_metadata(self, file_data: bytes, metadata: LayeredMetadata) -> bool:
        """Validate metadata against file data"""
        
        # Basic validation
        if len(file_data) != metadata.core.original_file_size:
            return False
        
        # Strategy-specific validation
        strategy = DecoyStrategy(metadata.security.decoy_strategy)
        
        if strategy == DecoyStrategy.ALGORITHMIC:
            # Validate algorithmic metadata
            # Need to deserialize the algorithmic metadata first
            try:
                from .algorithmic_decoys import AlgorithmicDecoyMetadata
                alg_metadata = AlgorithmicDecoyMetadata.deserialize(
                    metadata.security.decoy_metadata
                )
                # Validate using the metadata object directly
                return self.algorithmic_system._validate_metadata_object(alg_metadata)
            except Exception:
                return False
            
        elif strategy == DecoyStrategy.DIFFERENTIAL:
            # Validate differential metadata
            try:
                from .differential_decoys import DifferentialDecoyMetadata
                diff_metadata = DifferentialDecoyMetadata.deserialize(
                    metadata.security.decoy_metadata
                )
                return self.differential_system.validate_decoy_system(file_data, diff_metadata)
            except Exception:
                return False
                
        else:  # SELECTIVE
            # Validate selective metadata
            try:
                from .selective_decoys import SelectiveDecoyMetadata
                sel_metadata = SelectiveDecoyMetadata.deserialize(
                    metadata.security.decoy_metadata
                )
                return self.selective_system.validate_decoy_system(file_data, sel_metadata)
            except Exception:
                return False
    
    def get_metadata_size(self, metadata: LayeredMetadata) -> int:
        """Get actual size of serialized metadata"""
        return len(metadata.serialize())
    
    def get_size_breakdown(self, metadata: LayeredMetadata) -> Dict[str, int]:
        """Get detailed breakdown of metadata sizes"""
        
        core_size = len(metadata.core.serialize())
        security_size = len(metadata.security.serialize())
        extension_size = len(metadata.extension.serialize())
        
        return {
            'core_layer': core_size,
            'security_layer': security_size, 
            'extension_layer': extension_size,
            'total_size': core_size + security_size + extension_size,
            'original_estimate': MetadataFactory.estimate_metadata_size(
                metadata.core.original_file_size, 
                SecurityProfile(metadata.core.security_profile)
            )
        }
    
    def optimize_for_streaming(self, metadata: LayeredMetadata) -> Dict[str, Any]:
        """Prepare metadata for streaming decryption optimization"""
        
        strategy = DecoyStrategy(metadata.security.decoy_strategy)
        
        # Create streaming optimization data
        streaming_data = {
            'decoy_strategy': strategy.value,
            'decoy_count': metadata.security.decoy_count,
            'quick_validation': None,
            'upfront_checks': []
        }
        
        if strategy == DecoyStrategy.ALGORITHMIC:
            # For algorithmic decoys, we can pre-validate seeds
            streaming_data['quick_validation'] = {
                'type': 'seed_validation',
                'cel_seed_hash': metadata.core.cel_seed_hash.hex(),
                'expected_patterns': self._get_algorithmic_patterns(
                    metadata.core.cel_seed_hash
                )
            }
            
        elif strategy == DecoyStrategy.SELECTIVE:
            # For selective decoys, we can validate file structure first
            from .selective_decoys import SelectiveDecoyMetadata
            sel_metadata = SelectiveDecoyMetadata.deserialize(
                metadata.security.decoy_metadata
            )
            
            streaming_data['upfront_checks'] = [
                {
                    'type': 'file_hash_check',
                    'validation_hash': sel_metadata.validation_hash.hex(),
                    'check_positions': [0, 1024]  # Check first 1KB
                },
                {
                    'type': 'segment_validation',
                    'segment_count': len(sel_metadata.selected_segments),
                    'first_segment_offset': sel_metadata.selected_segments[0].segment_offset if sel_metadata.selected_segments else 0
                }
            ]
        
        return streaming_data
    
    def _generate_base_cel(self, file_data: bytes, cel_seed: bytes) -> bytes:
        """Generate base CEL for differential decoys (placeholder)"""
        # This would integrate with actual CEL generation
        # For now, create a mock CEL
        cel_header = b'CEL_V031' + cel_seed[:24]
        cel_content = hashlib.sha256(file_data + cel_seed).digest() * 512  # Mock CEL content
        cel_footer = hashlib.sha256(cel_header + cel_content).digest()[:16]
        
        return cel_header + cel_content + cel_footer
    
    def _get_algorithmic_patterns(self, cel_seed_hash: bytes) -> List[str]:
        """Get expected patterns for algorithmic decoy validation"""
        # Generate predictable patterns from seed for quick validation
        patterns = []
        for i in range(3):
            pattern_seed = hashlib.sha256(cel_seed_hash + bytes([i])).digest()
            pattern = hashlib.sha256(pattern_seed).hexdigest()[:16]
            patterns.append(pattern)
        
        return patterns

# Migration utilities
class MetadataMigration:
    """Handles migration from v0.3.0 to v0.3.1 metadata format"""
    
    @staticmethod
    def is_v030_metadata(metadata_bytes: bytes) -> bool:
        """Check if metadata is v0.3.0 format"""
        # This would check for v0.3.0 specific markers
        # For now, simple heuristic based on size
        return len(metadata_bytes) > 400 * 1024  # >400KB likely v0.3.0
    
    @staticmethod
    def migrate_v030_to_v031(old_metadata_bytes: bytes, file_data: bytes) -> LayeredMetadata:
        """Migrate v0.3.0 metadata to current format"""
        
        # This would parse v0.3.0 metadata and extract key information
        # For now, create new metadata
        system = MetadataSystem()
        
        # Auto-detect security profile
        from ..profiles.security_profiles import SecurityProfileManager
        profile = SecurityProfileManager.detect_profile_from_content(
            file_data[:1024] if len(file_data) > 1024 else file_data
        )
        
        return system.generate_metadata(file_data, profile)
    
    @staticmethod
    def estimate_size_reduction(old_size: int, new_metadata: LayeredMetadata) -> Dict[str, Any]:
        """Estimate size reduction from migration"""
        
        new_size = len(new_metadata.serialize())
        reduction = old_size - new_size
        reduction_percent = (reduction / old_size) * 100 if old_size > 0 else 0
        
        return {
            'old_size_bytes': old_size,
            'new_size_bytes': new_size,
            'reduction_bytes': reduction,
            'reduction_percent': round(reduction_percent, 1),
            'size_ratio': round(new_size / old_size, 3) if old_size > 0 else 0
        }

# Convenience functions for common operations
def create_metadata_for_file(file_data: bytes, 
                           security_profile: SecurityProfile = SecurityProfile.DOCUMENT) -> LayeredMetadata:
    """Create metadata for a file with automatic optimization"""
    system = MetadataSystem()
    return system.generate_metadata(file_data, security_profile)

def validate_file_metadata(file_data: bytes, metadata: LayeredMetadata) -> bool:
    """Validate metadata against file"""
    system = MetadataSystem()
    return system.validate_metadata(file_data, metadata)

def get_decoys_for_file(file_data: bytes, metadata: LayeredMetadata) -> List[bytes]:
    """Get decoys for a file"""
    system = MetadataSystem()
    return system.reconstruct_decoys(file_data, metadata)

def estimate_metadata_overhead(file_size: int, 
                             security_profile: SecurityProfile = SecurityProfile.DOCUMENT) -> Dict[str, Any]:
    """Estimate metadata overhead for planning"""
    
    estimated_size = MetadataFactory.estimate_metadata_size(file_size, security_profile)
    overhead_percent = (estimated_size / file_size) * 100 if file_size > 0 else 0
    
    # Compare with v0.3.0
    v030_size = 486 * 1024  # 486KB fixed overhead
    v030_overhead = (v030_size / file_size) * 100 if file_size > 0 else 0
    
    improvement = v030_overhead - overhead_percent
    
    return {
        'file_size': file_size,
        'v031_metadata_size': estimated_size,
        'v031_overhead_percent': round(overhead_percent, 2),
        'v030_metadata_size': v030_size,
        'v030_overhead_percent': round(v030_overhead, 2),
        'improvement_percent': round(improvement, 2),
        'size_reduction_ratio': round(v030_size / estimated_size, 1) if estimated_size > 0 else float('inf')
    }