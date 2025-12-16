"""
Core Metadata Module v0.3.1

Provides the new layered metadata system for STC v0.3.1.
Replaces the fixed 486KB overhead with adaptive, scalable metadata.
"""

# Core metadata structures
from .layered_format import (
    LayeredMetadata,
    CoreMetadata,
    SecurityMetadata,
    ExtensionMetadata,
    MetadataFactory,
    SecurityProfile,
    DecoyStrategy
)

# Decoy systems
from .algorithmic_decoys import (
    AlgorithmicDecoySystem,
    create_algorithmic_decoys
)

from .differential_decoys import (
    DifferentialDecoySystem,
    create_differential_decoys
)

from .selective_decoys import (
    SelectiveDecoySystem,
    create_selective_decoys
)

# Integration layer - main interface
from .integration import (
    MetadataSystem,
    MetadataMigration,
    create_metadata_for_file,
    validate_file_metadata,
    get_decoys_for_file,
    estimate_metadata_overhead
)

__all__ = [
    # Core structures
    'LayeredMetadata',
    'CoreMetadata', 
    'SecurityMetadata',
    'ExtensionMetadata',
    'MetadataFactory',
    'SecurityProfile',
    'DecoyStrategy',
    
    # Decoy systems
    'AlgorithmicDecoySystem',
    'DifferentialDecoySystem', 
    'SelectiveDecoySystem',
    'create_algorithmic_decoys',
    'create_differential_decoys',
    'create_selective_decoys',
    
    # Integration layer
    'MetadataSystem',
    'MetadataMigration',
    'create_metadata_for_file',
    'validate_file_metadata',
    'get_decoys_for_file',
    'estimate_metadata_overhead'
]