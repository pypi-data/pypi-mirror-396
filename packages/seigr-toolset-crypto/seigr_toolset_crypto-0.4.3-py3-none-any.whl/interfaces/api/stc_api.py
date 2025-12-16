"""
STC API - High-level interface for Seigr Toolset Crypto

Provides convenient functions for encryption, hashing, and key derivation
using the complete STC architecture (CEL, PHE, CKE, DSF, PCF, STATE).

v0.2.0 - Enhanced with entropy amplification, multi-path hashing,
         persistence vector obfuscation, and self-auditing
"""

from typing import Union, Optional, Dict, Any, Tuple

from core.cel import initialize_cel
from core.phe import create_phe
from core.cke import create_cke
from core.dsf import create_dsf
from core.pcf import create_pcf
from core.state import create_state_manager
from core.state.metadata_utils import (
    encrypt_metadata,
    decrypt_metadata,
    inject_decoy_vectors,
    extract_real_vector
)
from utils.tlv_format import (
    serialize_metadata_tlv,
    deserialize_metadata_tlv,
    detect_metadata_version,
    METADATA_VERSION_TLV
)

# Version constant
STC_VERSION = "0.2.0"

# Public API exports - only these functions should be used externally
__all__ = [
    'STCContext',
    'initialize', 
    'encrypt',
    'decrypt', 
    'hash_data',
    'quick_encrypt',
    'quick_decrypt',
    'STC_VERSION'
]


class STCContext:
    """
    Complete STC context managing all cryptographic components
    
    This is the main interface for using STC functionality.
    """
    
    def __init__(
        self,
        seed: Union[str, bytes, int],
        lattice_size: int = 128,  # Reduced from 256 for better performance
        depth: int = 6,  # Reduced from 8 for better performance
        morph_interval: int = 100,
        adaptive_difficulty: str = 'balanced',  # v0.3.0: 'paranoid', 'balanced', 'fast'
        adaptive_morphing: bool = True  # v0.3.0: Enable context-adaptive morphing
    ):
        """
        Initialize STC context (v0.3.0: Enhanced with adaptive features)
        
        Args:
            seed: Seed for deterministic initialization
            lattice_size: CEL lattice dimension (default 128, was 256)
            depth: CEL lattice depth (default 6, was 8)
            morph_interval: PCF morph interval (base interval for adaptive morphing)
            adaptive_difficulty: Sensitivity level for attack detection (v0.3.0)
                - 'paranoid': High sensitivity, aggressive scaling
                - 'balanced': Medium sensitivity (recommended)
                - 'fast': Low sensitivity, minimal overhead
            adaptive_morphing: Enable context-adaptive morphing intervals (v0.3.0)
        """
        self.seed = seed
        
        # Initialize all components
        self.cel = initialize_cel(seed, lattice_size, depth)
        self.phe = create_phe()
        self.cke = create_cke()
        self.dsf = create_dsf()
        self.pcf = create_pcf(morph_interval, adaptive_morphing)
        self.state_manager = create_state_manager()
        
        # Entropy health monitoring (v0.3.0)
        self.minimum_entropy_threshold = None  # None = no threshold enforcement
        
        # v0.3.0: Adaptive difficulty scaling
        self.adaptive_difficulty = adaptive_difficulty
        self.attack_detection_window = []  # Track suspicious operations
        self.base_phe_paths = 7  # Default PHE path count
        self.current_phe_paths = self.base_phe_paths
        self.failed_decryption_count = 0
        self.timing_attack_samples = []
        
        # Sync components
        self._sync_components()
        
    def _sync_components(self) -> None:
        """Synchronize all components"""
        # Get CEL snapshot
        cel_snapshot = self.cel.snapshot()
        
        # Bind to PHE and PCF
        self.phe.map_entropy(cel_snapshot)
        self.pcf.bind(cel_snapshot)
    
    def encrypt(
        self,
        data: Union[str, bytes],
        context_data: Optional[Dict[str, Any]] = None,
        password: Optional[str] = None,
        use_decoys: bool = True,  # v0.3.0: ENABLED by default for security (optimized performance)
        num_decoys: int = 3,  # v0.3.0: Default 3 decoys (uses optimized 64×64×4 lattices)
        # v0.3.0: Polymorphic decoy options (enabled by default for security)
        variable_decoy_sizes: bool = True,  # Uses 32×3 to 96×5 range (NOT 128×6)
        randomize_decoy_count: bool = True,  # Varies 3±2 decoys
        timing_randomization: bool = False,  # Optional: adds 10-30ms total (disabled for performance)
        noise_padding: bool = False  # Optional: adds metadata size
    ) -> Tuple[bytes, Union[bytes, Dict[str, Any]]]:
        """
        Encrypt data using complete STC pipeline (v0.3.0)
        
        SECURITY-FIRST with OPTIMIZED PERFORMANCE:
        - Decoys enabled by default (plausible deniability)
        - Polymorphic features enabled (obfuscation)
        - Performance optimized through smaller decoy lattices (64×64×4 vs 128×128×6)
        
        Args:
            data: Data to encrypt
            context_data: Optional additional context
            password: Password for metadata encryption (if None, uses seed)
            use_decoys: Enable decoy vectors for plausible deniability (default TRUE)
            num_decoys: Number of decoy snapshots (default 3, range 1-7)
            
            # v0.3.0: Polymorphic Decoy Options (ENABLED by default)
            variable_decoy_sizes: Use variable lattice sizes 32×3 to 96×5 (optimized, not 128×6)
            randomize_decoy_count: Randomize actual count ±2 from num_decoys
            timing_randomization: Add timing jitter (10ms total, optional for max security)
            noise_padding: Add random noise padding to decoys (increases metadata ~5-10%)
            
        Returns:
            Tuple of (encrypted_bytes, metadata_bytes)
            
        Raises:
            ValueError: If entropy quality is below minimum threshold (v0.3.0)
        """
        # Check entropy health before encrypting (v0.3.0)
        self._check_entropy_health()
        
        # Convert string to bytes
        if isinstance(data, str):
            data_bytes = data.encode('utf-8')
            original_length = len(data_bytes)
            was_string = True
        else:
            data_bytes = data
            original_length = len(data_bytes)
            was_string = False
        
        # Use seed as password if not provided
        if password is None:
            if isinstance(self.seed, str):
                password = self.seed
            elif isinstance(self.seed, bytes):
                password = self.seed.decode('utf-8', errors='replace')
            else:
                password = str(self.seed)
        
        # Update CEL with operation context
        operation_context = {
            'data': data_bytes,
            'operation': 'encrypt',
            'parameters': context_data or {}
        }
        self.cel.update(operation_context)
        
        # Get fresh CEL snapshot
        cel_snapshot = self.cel.snapshot()
        
        # Generate probabilistic hash of data
        phe_output = self.phe.digest(data_bytes, context_data)
        
        # Derive encryption key
        cke_context = {
            'cel_snapshot': cel_snapshot,
            'phe_output': phe_output,
            'operation': 'encrypt',
            'seed': self.seed,
            'data_size': len(data_bytes)
        }
        key_vector = self.cke.derive(cke_context)
        
        # Encrypt using DSF
        encrypted = self.dsf.fold(data_bytes, key_vector, cel_snapshot)
        
        # Cycle PCF
        self.pcf.cycle()
        
        # Discard ephemeral key
        self.cke.discard()
        
        # Prepare metadata with v0.2.0 enhancements
        metadata = {
            'original_length': original_length,
            'was_string': was_string,
            'phe_hash': phe_output,
            'cel_snapshot': cel_snapshot,
            'stc_version': STC_VERSION
        }
        
        # Encrypt metadata with differential encoding
        encrypted_metadata = encrypt_metadata(
            metadata,
            password,
            use_differential=False,  # Disabled: produces more data than full lattice
            seed=self.seed
        )
        
        # Inject polymorphic decoy vectors if requested (v0.3.0)
        if use_decoys:
            encrypted_metadata = inject_decoy_vectors(
                encrypted_metadata,
                password,
                num_decoys=num_decoys,
                variable_sizes=variable_decoy_sizes,
                randomize_count=randomize_decoy_count,
                timing_randomization=timing_randomization,
                noise_padding=noise_padding
            )
        
        # Serialize to TLV binary format
        if use_decoys:
            # Store obfuscated structure with polymorphic config (v0.3.0)
            metadata_dict = {
                'obfuscated': True,
                'vectors': encrypted_metadata['vectors'],
                'num_vectors': encrypted_metadata['num_vectors']
            }
            # Include polymorphic metadata if present
            if 'polymorphic' in encrypted_metadata:
                metadata_dict['polymorphic'] = encrypted_metadata['polymorphic']
            
            metadata_bytes = serialize_metadata_tlv(metadata_dict)
        else:
            metadata_bytes = serialize_metadata_tlv(encrypted_metadata)
        
        return encrypted, metadata_bytes
    
    def decrypt(
        self,
        encrypted_data: bytes,
        metadata: Union[Dict[str, Any], bytes],
        context_data: Optional[Dict[str, Any]] = None,
        password: Optional[str] = None
    ) -> Union[str, bytes]:
        """
        Decrypt data using STC pipeline (v0.3.0)
        Enhanced with adaptive difficulty and attack detection
        
        Args:
            encrypted_data: Encrypted bytes
            metadata: Metadata from encryption (dict or TLV bytes)
            context_data: Optional additional context
            password: Password for metadata decryption (if None, uses seed)
            
        Returns:
            Decrypted data (string or bytes based on metadata)
            
        Raises:
            ValueError: If metadata version is incompatible or attack detected
        """
        # v0.3.0: Detect potential oracle attacks
        if self._detect_oracle_attack():
            self._scale_difficulty()
        
        # v0.3.0: Add timing randomization if configured
        self._add_timing_randomization()
        
        try:
            # Use seed as password if not provided
            if password is None:
                if isinstance(self.seed, str):
                    password = self.seed
                elif isinstance(self.seed, bytes):
                    password = self.seed.decode('utf-8', errors='replace')
                else:
                    password = str(self.seed)
            
            # Detect and handle metadata version
            if isinstance(metadata, bytes):
                version = detect_metadata_version(metadata)
                
                if version != METADATA_VERSION_TLV:
                    # Only support self-sovereign TLV format for true self-sovereignty
                    raise ValueError(
                        "Unsupported metadata format. STC only supports self-sovereign TLV format."
                    )
                
                # Deserialize TLV
                metadata_dict = deserialize_metadata_tlv(metadata)
                
                # Check if obfuscated with decoys
                if metadata_dict.get('obfuscated'):
                    # Extract real vector from decoys
                    obfuscated_data = {
                        'vectors': metadata_dict['vectors'],
                        'num_vectors': metadata_dict['num_vectors']
                    }
                    encrypted_metadata = extract_real_vector(obfuscated_data, password)
                    # Decrypt metadata
                    metadata = decrypt_metadata(encrypted_metadata, password, seed=self.seed)
                elif 'encrypted_metadata' in metadata_dict:
                    # Metadata is encrypted (not obfuscated)
                    metadata = decrypt_metadata(metadata_dict, password, seed=self.seed)
                else:
                    # Metadata is already in plain form (backward compat or direct TLV)
                    metadata = metadata_dict
            
            elif isinstance(metadata, dict):
                # Check for v0.1.x plain dict (has 'phe_hash' as hex string)
                if isinstance(metadata.get('phe_hash'), str):
                    raise ValueError(
                        "This data was encrypted with STC v0.1.x. "
                        "Please use the migration utility to convert to v0.2.0 format."
                    )
                # Already decrypted metadata (v0.2.0) - no action needed
            
            # Reconstruct PHE hash
            phe_output = metadata['phe_hash']
            if isinstance(phe_output, str):
                phe_output = bytes.fromhex(phe_output)
            
            # Use embedded CEL snapshot from encryption for exact reconstruction
            cel_snapshot = metadata['cel_snapshot']
            
            # Derive decryption key (same process as encryption)
            cke_context = {
                'cel_snapshot': cel_snapshot,
                'phe_output': phe_output,
                'operation': 'encrypt',  # Use same operation for key derivation
                'seed': self.seed,
                'data_size': metadata['original_length']
            }
            key_vector = self.cke.derive(cke_context)
            
            # Decrypt using DSF
            decrypted = self.dsf.unfold(
                encrypted_data,
                key_vector,
                cel_snapshot,
                original_length=metadata['original_length']
            )
            
            # Discard ephemeral key
            self.cke.discard()
            
            # Convert back to string if original was string
            if metadata.get('was_string', False):
                return decrypted.decode('utf-8')
            
            return decrypted
            
        except Exception as e:
            # v0.3.0: Track failed decryption attempts for attack detection
            self.failed_decryption_count += 1
            raise e
    
    def hash(
        self,
        data: Union[str, bytes],
        context_data: Optional[Dict[str, Any]] = None
    ) -> bytes:
        """
        Generate probabilistic hash
        
        Args:
            data: Data to hash
            context_data: Optional context
            
        Returns:
            Hash bytes
        """
        # Update CEL
        if isinstance(data, str):
            data_bytes = data.encode('utf-8')
        else:
            data_bytes = data
        
        operation_context = {
            'data': data_bytes,
            'operation': 'hash',
            'parameters': context_data or {}
        }
        self.cel.update(operation_context)
        
        # Sync PHE
        cel_snapshot = self.cel.snapshot()
        self.phe.map_entropy(cel_snapshot)
        
        # Generate hash
        hash_result = self.phe.digest(data_bytes, context_data)
        
        # Cycle PCF
        self.pcf.cycle()
        
        return hash_result
    
    def derive_key(
        self,
        length: int = 32,
        context_data: Optional[Dict[str, Any]] = None
    ) -> bytes:
        """
        Derive ephemeral key
        
        Args:
            length: Key length in bytes
            context_data: Optional context
            
        Returns:
            Derived key bytes
        """
        # Update CEL
        operation_context = {
            'operation': 'derive_key',
            'parameters': context_data or {}
        }
        self.cel.update(operation_context)
        
        # Get CEL snapshot
        cel_snapshot = self.cel.snapshot()
        
        # Derive key
        cke_context = {
            'cel_snapshot': cel_snapshot,
            'operation': 'derive_key',
            'seed': self.seed,
        }
        if context_data:
            cke_context.update(context_data)
        
        key_vector = self.cke.derive(cke_context, key_length=length)
        key_bytes = bytes(key_vector)
        
        # Discard after extraction
        self.cke.discard()
        
        # Cycle PCF
        self.pcf.cycle()
        
        return key_bytes
    
    def encrypt_stream(
        self,
        data: Union[str, bytes],
        chunk_size: int = 1024 * 1024,  # 1MB chunks
        password: Optional[str] = None,
        use_decoys: bool = True,
        progress_callback: Optional[callable] = None
    ):
        """
        Encrypt large data in chunks with streaming support (v0.3.0)
        
        Yields encrypted chunks and provides final metadata.
        Useful for encrypting large files without loading entire content into memory.
        
        Args:
            data: Data to encrypt (string or bytes)
            chunk_size: Size of each chunk in bytes (default 1MB)
            password: Password for metadata encryption
            use_decoys: Whether to inject decoy vectors
            progress_callback: Optional callback(current_chunk, total_chunks)
            
        Yields:
            Tuples of (chunk_index, encrypted_chunk_bytes)
            
        Returns:
            Final metadata for all chunks
            
        Example:
            >>> ctx = STCContext('seed')
            >>> large_data = b"..." * 10_000_000  # 10MB
            >>> chunks = []
            >>> for idx, encrypted_chunk in ctx.encrypt_stream(large_data):
            ...     chunks.append(encrypted_chunk)
            >>> metadata = chunks[-1]  # Last item is metadata
        """
        # Convert to bytes
        if isinstance(data, str):
            data_bytes = data.encode('utf-8')
            was_string = True
        else:
            data_bytes = data
            was_string = False
        
        total_size = len(data_bytes)
        num_chunks = (total_size + chunk_size - 1) // chunk_size
        
        # Use seed as password if not provided
        if password is None:
            password = str(self.seed) if not isinstance(self.seed, str) else self.seed
        
        # Store chunk metadata
        chunk_metadata_list = []
        
        # Process each chunk
        for chunk_idx in range(num_chunks):
            start = chunk_idx * chunk_size
            end = min(start + chunk_size, total_size)
            chunk_data = data_bytes[start:end]
            
            # Update CEL incrementally
            self.cel.update({
                'operation': 'encrypt_stream',
                'chunk_index': chunk_idx,
                'chunk_size': len(chunk_data)
            })
            
            # Encrypt this chunk
            cel_snapshot = self.cel.snapshot()
            phe_output = self.phe.digest(chunk_data, {'chunk': chunk_idx})
            
            cke_context = {
                'cel_snapshot': cel_snapshot,
                'phe_output': phe_output,
                'operation': 'encrypt_stream',
                'seed': self.seed,
                'chunk_index': chunk_idx
            }
            key_vector = self.cke.derive(cke_context)
            
            # Encrypt chunk
            encrypted_chunk = self.dsf.fold(chunk_data, key_vector, cel_snapshot)
            self.cke.discard()
            
            # Store chunk metadata
            chunk_metadata_list.append({
                'chunk_index': chunk_idx,
                'original_size': len(chunk_data),
                'encrypted_size': len(encrypted_chunk),
                'cel_state_version': cel_snapshot['state_version'],
                'phe_hash': phe_output
            })
            
            # Yield encrypted chunk
            yield (chunk_idx, encrypted_chunk)
            
            # Progress callback
            if progress_callback:
                progress_callback(chunk_idx + 1, num_chunks)
        
        # Create final metadata
        final_metadata = {
            'stream_version': '0.3.0',
            'total_chunks': num_chunks,
            'chunk_size': chunk_size,
            'total_size': total_size,
            'was_string': was_string,
            'chunks': chunk_metadata_list,
            'cel_final_snapshot': self.cel.snapshot()
        }
        
        # Encrypt metadata
        from core.state.metadata_utils import encrypt_metadata
        encrypted_metadata = encrypt_metadata(final_metadata, password, seed=self.seed)
        
        # Optionally inject decoys
        if use_decoys:
            from core.state.metadata_utils import inject_decoy_vectors
            encrypted_metadata = inject_decoy_vectors(encrypted_metadata, password, num_decoys=3)
        
        # Serialize to TLV
        from utils.tlv_format import serialize_metadata_tlv
        if use_decoys:
            metadata_bytes = serialize_metadata_tlv({
                'obfuscated': True,
                'vectors': encrypted_metadata['vectors'],
                'num_vectors': encrypted_metadata['num_vectors']
            })
        else:
            metadata_bytes = serialize_metadata_tlv(encrypted_metadata)
        
        # Yield final metadata as special chunk
        yield ('metadata', metadata_bytes)
    
    def decrypt_stream(
        self,
        encrypted_chunks: list,
        metadata: Union[Dict[str, Any], bytes],
        password: Optional[str] = None,
        progress_callback: Optional[callable] = None
    ):
        """
        Decrypt stream of encrypted chunks (v0.3.0)
        
        Args:
            encrypted_chunks: List of (chunk_index, encrypted_bytes) tuples
            metadata: Stream metadata from encrypt_stream
            password: Password for metadata decryption
            progress_callback: Optional callback(current_chunk, total_chunks)
            
        Yields:
            Decrypted chunk bytes in order
            
        Example:
            >>> encrypted_chunks = list(ctx.encrypt_stream(data))
            >>> metadata = encrypted_chunks.pop()  # Remove metadata
            >>> decrypted_parts = []
            >>> for chunk in ctx.decrypt_stream(encrypted_chunks, metadata):
            ...     decrypted_parts.append(chunk)
            >>> original_data = b''.join(decrypted_parts)
        """
        # Use seed as password if not provided
        if password is None:
            password = str(self.seed) if not isinstance(self.seed, str) else self.seed
        
        # Decrypt metadata
        from core.state.metadata_utils import decrypt_metadata, extract_real_vector
        from utils.tlv_format import deserialize_metadata_tlv
        
        if isinstance(metadata, bytes):
            metadata_dict = deserialize_metadata_tlv(metadata)
            
            if metadata_dict.get('obfuscated'):
                obfuscated_data = {
                    'vectors': metadata_dict['vectors'],
                    'num_vectors': metadata_dict['num_vectors']
                }
                encrypted_meta = extract_real_vector(obfuscated_data, password)
                stream_metadata = decrypt_metadata(encrypted_meta, password, seed=self.seed)
            else:
                stream_metadata = decrypt_metadata(metadata_dict, password, seed=self.seed)
        else:
            stream_metadata = metadata
        
        # Sort chunks by index
        sorted_chunks = sorted(encrypted_chunks, key=lambda x: x[0])
        total_chunks = len(sorted_chunks)
        
        # Decrypt each chunk
        for chunk_idx, encrypted_chunk in sorted_chunks:
            chunk_meta = stream_metadata['chunks'][chunk_idx]
            
            # Reconstruct CEL state for this chunk
            # Note: For true streaming, we'd restore CEL state incrementally
            # For now, we use the stored metadata
            phe_output = chunk_meta['phe_hash']
            
            # Derive decryption key
            cke_context = {
                'cel_snapshot': stream_metadata['cel_final_snapshot'],
                'phe_output': phe_output,
                'operation': 'encrypt_stream',
                'seed': self.seed,
                'chunk_index': chunk_idx
            }
            key_vector = self.cke.derive(cke_context)
            
            # Decrypt chunk
            decrypted_chunk = self.dsf.unfold(
                encrypted_chunk,
                key_vector,
                stream_metadata['cel_final_snapshot'],
                original_length=chunk_meta['original_size']
            )
            self.cke.discard()
            
            yield decrypted_chunk
            
            # Progress callback
            if progress_callback:
                progress_callback(chunk_idx + 1, total_chunks)
    
    def save_state(self, filepath: Optional[str] = None) -> Dict[str, Any]:
        """
        Save complete context state
        
        Args:
            filepath: Optional file path to save to
            
        Returns:
            State dictionary
        """
        state = self.state_manager.save({
            'cel': self.cel,
            'pcf': self.pcf,
            'seed': self.seed,
            'metadata': {
                'lattice_size': self.cel.lattice_size,
                'depth': self.cel.depth,
                'morph_interval': self.pcf.morph_interval,
            }
        })
        
        if filepath:
            self.state_manager.save_to_file(state, filepath)
        
        return state
    
    def get_entropy_profile(self) -> Dict[str, Any]:
        """
        Get comprehensive entropy health profile (v0.3.0)
        
        Exposes internal entropy monitoring to allow users to validate
        encryption quality before use.
        
        Returns:
            Dictionary with:
                - quality_score: 0.0-1.0 overall entropy health
                - status: 'excellent', 'good', 'acceptable', 'weak', 'critical'
                - warnings: List of current issues
                - recommendations: List of suggested actions
                - metrics: Detailed measurements
                - recent_audits: Last 5 audit entries from CEL
        
        Example:
            >>> ctx = STCContext('my-seed')
            >>> profile = ctx.get_entropy_profile()
            >>> if profile['quality_score'] < 0.7:
            >>>     print(f"Warning: {profile['warnings']}")
            >>>     # Consider reinitializing or using different seed
        """
        return self.cel.get_entropy_profile()
    
    def set_minimum_entropy_threshold(self, threshold: Optional[float] = 0.7) -> None:
        """
        Set minimum entropy quality threshold for encryption (v0.3.0)
        
        When set, encrypt() will check entropy health before proceeding
        and raise ValueError if quality is below threshold.
        
        Args:
            threshold: Minimum quality score (0.0-1.0), None to disable
        
        Recommended thresholds:
            - 0.9: Paranoid (excellent entropy required)
            - 0.7: Balanced (good entropy required) [recommended]
            - 0.5: Permissive (acceptable entropy ok)
            - None: Disabled (no checking)
        
        Example:
            >>> ctx = STCContext('my-seed')
            >>> ctx.set_minimum_entropy_threshold(0.7)
            >>> # Now encrypt() will auto-check entropy quality
            >>> encrypted, metadata = ctx.encrypt("data", password="pw")
        """
        if threshold is not None and not (0.0 <= threshold <= 1.0):
            raise ValueError("Threshold must be between 0.0 and 1.0 or None")
        self.minimum_entropy_threshold = threshold
    
    def _check_entropy_health(self) -> None:
        """
        Internal method to check entropy health before encryption
        Raises ValueError if below threshold
        """
        if self.minimum_entropy_threshold is None:
            return  # No threshold set, skip check
        
        profile = self.get_entropy_profile()
        if profile['quality_score'] < self.minimum_entropy_threshold:
            warnings_str = '; '.join(profile['warnings'])
            recommendations_str = '; '.join(profile['recommendations'])
            raise ValueError(
                f"Entropy quality ({profile['quality_score']:.2f}) below minimum threshold "
                f"({self.minimum_entropy_threshold:.2f}). "
                f"Status: {profile['status']}. "
                f"Warnings: {warnings_str}. "
                f"Recommendations: {recommendations_str}"
            )
    
    def _detect_oracle_attack(self) -> bool:
        """
        Detect potential oracle attacks (v0.3.0)
        
        Oracle attacks involve repeated decryption attempts with variations
        to deduce information about the plaintext or key.
        
        Returns:
            True if attack pattern detected
        """
        import time
        
        # Track this operation
        current_time = time.time()
        self.attack_detection_window.append(current_time)
        
        # Keep window at 100 recent operations
        if len(self.attack_detection_window) > 100:
            self.attack_detection_window.pop(0)
        
        # Not enough data yet
        if len(self.attack_detection_window) < 20:
            return False
        
        # Calculate operation rate (ops/second)
        time_span = self.attack_detection_window[-1] - self.attack_detection_window[0]
        if time_span < 0.1:  # Avoid division by zero
            return False
        
        ops_per_second = len(self.attack_detection_window) / time_span
        
        # Set thresholds based on sensitivity
        if self.adaptive_difficulty == 'paranoid':
            rate_threshold = 10  # Very aggressive
            failed_threshold = 3
        elif self.adaptive_difficulty == 'balanced':
            rate_threshold = 50  # Moderate
            failed_threshold = 10
        else:  # 'fast'
            rate_threshold = 100  # Lenient
            failed_threshold = 20
        
        # Suspicious if high operation rate AND many failures
        high_rate = ops_per_second > rate_threshold
        many_failures = self.failed_decryption_count > failed_threshold
        
        return high_rate and many_failures
    
    def _scale_difficulty(self) -> None:
        """
        Scale up difficulty in response to detected attack (v0.3.0)
        """
        # Increase PHE paths
        if self.current_phe_paths < 15:  # Max 15 paths
            self.current_phe_paths += 1
            
            # Reinitialize PHE with more paths
            self.phe = create_phe()  # Note: Would need PHE factory update for path count
            
            # Re-sync components
            self._sync_components()
    
    def _add_timing_randomization(self) -> None:
        """
        Add random timing delays to prevent timing attacks (v0.3.0)
        """
        import time
        import random
        
        import secrets
        if self.adaptive_difficulty == 'paranoid':
            delay = 0.01 + secrets.randbelow(40000) / 1000000.0  # 10-50ms
        elif self.adaptive_difficulty == 'balanced':
            delay = 0.001 + secrets.randbelow(9000) / 1000000.0  # 1-10ms
        else:  # 'fast'
            delay = 0.0001 + secrets.randbelow(900) / 1000000.0  # 0.1-1ms
        
        time.sleep(delay)
    
    def get_adaptive_difficulty_status(self) -> Dict[str, Any]:
        """
        Get adaptive difficulty scaling status (v0.3.0)
        
        Returns:
            Dictionary with difficulty metrics
        """
        import time
        
        # Calculate current operation rate
        ops_per_second = 0.0
        if len(self.attack_detection_window) >= 2:
            time_span = self.attack_detection_window[-1] - self.attack_detection_window[0]
            if time_span > 0:
                ops_per_second = len(self.attack_detection_window) / time_span
        
        return {
            'sensitivity_level': self.adaptive_difficulty,
            'base_phe_paths': self.base_phe_paths,
            'current_phe_paths': self.current_phe_paths,
            'failed_decryptions': self.failed_decryption_count,
            'operation_rate': ops_per_second,
            'attack_detected': self._detect_oracle_attack() if len(self.attack_detection_window) >= 20 else False,
            'window_size': len(self.attack_detection_window)
        }
    
    def get_status(self) -> str:
        """
        Get human-readable status
        
        Returns:
            Status string
        """
        lines = [
            "=== STC Context Status ===",
            "",
            f"CEL Operation Count: {self.cel.operation_count}",
            f"CEL State Version: {self.cel.state_version}",
            f"PHE Operation Count: {self.phe.operation_count}",
            f"CKE Derivation Count: {self.cke.derivation_count}",
            f"DSF Operation Count: {self.dsf.operation_count}",
            "",
            "PCF Status:",
            self.pcf.describe(),
        ]
        
        return "\n".join(lines)


# Convenience functions

def initialize(
    seed: Union[str, bytes, int],
    lattice_size: int = 256,
    depth: int = 8,
    morph_interval: int = 100,
    adaptive_difficulty: str = 'balanced',
    adaptive_morphing: bool = True
) -> STCContext:
    """
    Initialize STC context (v0.3.0: Enhanced)
    
    Args:
        seed: Seed for initialization
        lattice_size: CEL lattice size
        depth: CEL depth
        morph_interval: PCF morph interval
        adaptive_difficulty: Attack detection sensitivity (v0.3.0)
        adaptive_morphing: Enable context-adaptive morphing (v0.3.0)
        
    Returns:
        Initialized STCContext
    """
    return STCContext(seed, lattice_size, depth, morph_interval, adaptive_difficulty, adaptive_morphing)


def encrypt(
    data: Union[str, bytes],
    context: STCContext,
    context_data: Optional[Dict[str, Any]] = None
) -> Tuple[bytes, Dict[str, Any]]:
    """
    Encrypt data
    
    Args:
        data: Data to encrypt
        context: STC context
        context_data: Optional additional context
        
    Returns:
        Tuple of (encrypted_bytes, metadata)
    """
    return context.encrypt(data, context_data)


def decrypt(
    encrypted_data: bytes,
    metadata: Dict[str, Any],
    context: STCContext,
    context_data: Optional[Dict[str, Any]] = None
) -> Union[str, bytes]:
    """
    Decrypt data
    
    Args:
        encrypted_data: Encrypted bytes
        metadata: Metadata from encryption
        context: STC context
        context_data: Optional additional context
        
    Returns:
        Decrypted data
    """
    return context.decrypt(encrypted_data, metadata, context_data)


def hash_data(
    data: Union[str, bytes],
    context: STCContext,
    context_data: Optional[Dict[str, Any]] = None
) -> bytes:
    """
    Generate probabilistic hash
    
    Args:
        data: Data to hash
        context: STC context
        context_data: Optional context
        
    Returns:
        Hash bytes
    """
    return context.hash(data, context_data)


def quick_encrypt(data: Union[str, bytes], seed: Union[str, bytes, int]) -> Tuple[bytes, Dict[str, Any], STCContext]:
    """
    Quick encryption with new context
    
    Args:
        data: Data to encrypt
        seed: Seed for context
        
    Returns:
        Tuple of (encrypted_bytes, metadata, context)
    """
    context = initialize(seed)
    encrypted, metadata = context.encrypt(data)
    return encrypted, metadata, context


def quick_decrypt(
    encrypted_data: bytes,
    metadata: Dict[str, Any],
    seed: Union[str, bytes, int]
) -> Union[str, bytes]:
    """
    Quick decryption with new context
    
    Reconstructs CEL state from embedded snapshot in metadata, enabling
    deterministic decryption without manual state tracking.
    
    Per DSF instructions: "quick_decrypt() must regenerate the CEL lattice 
    deterministically using CEL snapshot embedded in ciphertext"
    
    Args:
        encrypted_data: Encrypted bytes
        metadata: Metadata from encryption (includes cel_snapshot)
        seed: Seed (must match encryption seed)
        
    Returns:
        Decrypted data
    """
    context = initialize(seed)
    
    # The metadata now contains the full CEL snapshot from encryption
    # No need to fast-forward - we use the exact state from encryption
    # This ensures deterministic reconstruction per DSF requirements
    
    return context.decrypt(encrypted_data, metadata)
