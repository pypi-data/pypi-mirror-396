"""
STC v0.3.1 Streaming Performance Module

Phase 2: Upfront Decoy Validation and Memory-Efficient Streaming

This module implements high-performance streaming decryption with:
- Upfront decoy validation using first 64KB chunk analysis
- Constant 8MB memory usage regardless of file size  
- 3-5x performance improvement through single-pass streaming
- Support for files >100GB without memory issues

Components:
- upfront_validation: Fast decoy identification
- optimized_decrypt: Memory-efficient streaming decryption
- integration: Complete Phase 2 streaming solution

Main Interfaces:
- fast_decrypt_file(): Recommended for file decryption
- stream_decrypt_data(): Recommended for data streaming
- StreamingIntegration: Complete Phase 2 solution class
"""

from .upfront_validation import UpfrontDecoyValidator, validate_chunk_fast
from .optimized_decrypt import OptimizedStreamingDecryptor, stream_decrypt_file
from .integration import StreamingIntegration, fast_decrypt_file, stream_decrypt_data

__all__ = [
    # Core classes
    'UpfrontDecoyValidator',
    'OptimizedStreamingDecryptor', 
    'StreamingIntegration',
    
    # Convenience functions
    'validate_chunk_fast',
    'stream_decrypt_file',
    'fast_decrypt_file',
    'stream_decrypt_data'
]