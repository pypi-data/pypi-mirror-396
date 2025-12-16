"""
Contextual Key Emergence (CKE)
Ephemeral key reconstruction from context and CEL state

Keys are mathematical intersections - not stored entities.
They emerge from the combination of CEL snapshot, PHE output,
context vector, and optional user seed.

Key principles:
- No persistent keys on disk
- Keys exist only during operation
- Full context required for reconstruction
- Stateless after operation completion
"""

import numpy as np
from typing import Dict, Any, Optional, Union

from utils.math_primitives import (
    data_fingerprint_entropy
)


class ContextualKeyEmergence:
    """
    CKE - Ephemeral key emergence from context intersections
    
    Reconstructs keys from CEL state, PHE output, and context
    without ever storing the key material persistently.
    """
    
    def __init__(self):
        """Initialize CKE"""
        self.ephemeral_key: Optional[np.ndarray] = None
        self.key_length: int = 32  # Default key length in bytes
        self.derivation_count: int = 0
        
    def derive(
        self, 
        context: Dict[str, Any],
        key_length: Optional[int] = None
    ) -> np.ndarray:
        """
        Reconstruct key vector from context
        
        Per CKE contract: CKE.derive(context) → reconstruct key vector
        
        Args:
            context: Context dictionary containing:
                    - 'cel_snapshot': CEL snapshot
                    - 'phe_output': PHE hash output (optional)
                    - 'operation': operation type string
                    - 'seed': user seed or passphrase (optional)
                    - 'data_size': size of data to encrypt (optional)
                    - 'timestamp': timestamp or version (optional)
            key_length: Desired key length in bytes (default: 32)
            
        Returns:
            Ephemeral key vector as numpy array
        """
        if key_length is None:
            key_length = self.key_length
        
        # Validate context has minimum required fields
        if 'cel_snapshot' not in context:
            raise ValueError("Context must contain 'cel_snapshot'")
        
        # Extract context components
        cel_snapshot = context['cel_snapshot']
        phe_output = context.get('phe_output')
        operation = context.get('operation', 'default')
        seed = context.get('seed')
        data_size = context.get('data_size', 0)
        timestamp = context.get('timestamp', 0)
        
        # Combine sources to derive key
        key_vector = self._combine_sources(
            cel_snapshot=cel_snapshot,
            phe_output=phe_output,
            operation=operation,
            seed=seed,
            data_size=data_size,
            timestamp=timestamp,
            key_length=key_length
        )
        
        # Store ephemeral key temporarily
        self.ephemeral_key = key_vector
        self.derivation_count += 1
        
        # Return a COPY so that discard() doesn't affect the caller's key
        return key_vector.copy()
    
    def _combine_sources(
        self,
        cel_snapshot: Dict[str, Any],
        phe_output: Optional[bytes],
        operation: str,
        seed: Optional[Union[str, bytes]],
        data_size: int,
        timestamp: int,
        key_length: int
    ) -> np.ndarray:
        """
        Combine all entropy sources into key vector
        
        Args:
            cel_snapshot: CEL state snapshot
            phe_output: Optional PHE hash
            operation: Operation type
            seed: Optional user seed
            data_size: Size of data
            timestamp: Timestamp or version
            key_length: Desired key length
            
        Returns:
            Combined key vector
        """
        # Initialize key vector
        key_vector = np.zeros(key_length, dtype=np.uint8)
        
        # Extract CEL entropy
        cel_entropy = self._extract_cel_entropy(cel_snapshot, key_length)
        
        # Extract PHE entropy if available
        phe_entropy = self._extract_phe_entropy(phe_output, key_length) if phe_output else np.zeros(key_length, dtype=np.uint8)
        
        # Extract operation entropy
        operation_entropy = self._extract_operation_entropy(operation, key_length)
        
        # Extract seed entropy if provided
        seed_entropy = self._extract_seed_entropy(seed, key_length) if seed else np.zeros(key_length, dtype=np.uint8)
        
        # Extract context entropy
        context_entropy = self._extract_context_entropy(data_size, timestamp, key_length)
        
        # Combine all entropy sources using non-linear mixing
        for i in range(key_length):
            # Multi-source mixing with proper type handling
            value = (
                int(cel_entropy[i]) * 7919 +
                int(phe_entropy[i]) * 6547 +
                int(operation_entropy[i]) * 5381 +
                int(seed_entropy[i]) * 4093 +
                int(context_entropy[i]) * 3037
            ) % 256
            
            key_vector[i] = value
        
        # Apply additional diffusion
        key_vector = self._diffuse_key_vector(key_vector)
        
        return key_vector
    
    def _extract_cel_entropy(self, cel_snapshot: Dict[str, Any], length: int) -> np.ndarray:
        """
        Extract entropy from CEL snapshot
        
        Args:
            cel_snapshot: CEL snapshot dictionary
            length: Desired entropy length
            
        Returns:
            Entropy array
        """
        entropy = np.zeros(length, dtype=np.int32)  # Use int32 for intermediate calculations
        
        # Extract from lattice if available
        if 'lattice' in cel_snapshot:
            lattice = cel_snapshot['lattice']
            # Convert to numpy array if it's a list
            if isinstance(lattice, list):
                lattice = np.array(lattice)
            flat_lattice = lattice.flatten()
            
            for i in range(length):
                idx = (i * 7919) % len(flat_lattice)
                entropy[i] = int(flat_lattice[idx]) % 256
        
        # Mix with other CEL state components
        seed_fp = cel_snapshot.get('seed_fingerprint', 0)
        op_count = cel_snapshot.get('operation_count', 0)
        state_ver = cel_snapshot.get('state_version', 0)
        
        for i in range(length):
            entropy[i] = (entropy[i] + 
                         (seed_fp >> (i * 8)) % 256 +
                         (op_count * i) % 256 +
                         (state_ver * (i + 1)) % 256) % 256
        
        return entropy.astype(np.uint8)
    
    def _extract_phe_entropy(self, phe_output: bytes, length: int) -> np.ndarray:
        """
        Extract entropy from PHE output
        
        Args:
            phe_output: PHE hash bytes
            length: Desired entropy length
            
        Returns:
            Entropy array
        """
        entropy = np.zeros(length, dtype=np.int32)
        
        # Expand PHE output to desired length
        for i in range(length):
            idx = i % len(phe_output)
            entropy[i] = phe_output[idx]
            
            # Mix with position
            entropy[i] = (entropy[i] + i * 7919) % 256
        
        return entropy.astype(np.uint8)
    
    def _extract_operation_entropy(self, operation: str, length: int) -> np.ndarray:
        """
        Extract entropy from operation type
        
        Args:
            operation: Operation type string
            length: Desired entropy length
            
        Returns:
            Entropy array
        """
        op_bytes = operation.encode('utf-8')
        op_fingerprint = data_fingerprint_entropy(op_bytes)
        
        entropy = np.zeros(length, dtype=np.int32)
        for i in range(length):
            entropy[i] = ((op_fingerprint >> (i * 8)) + i * 6547) % 256
        
        return entropy.astype(np.uint8)
    
    def _extract_seed_entropy(self, seed: Union[str, bytes], length: int) -> np.ndarray:
        """
        Extract entropy from user seed
        
        Args:
            seed: User seed or passphrase
            length: Desired entropy length
            
        Returns:
            Entropy array
        """
        if isinstance(seed, str):
            seed_bytes = seed.encode('utf-8')
        else:
            seed_bytes = seed
        
        seed_fingerprint = data_fingerprint_entropy(seed_bytes)
        
        entropy = np.zeros(length, dtype=np.int32)
        
        # Expand seed across key length
        for i in range(length):
            byte_idx = i % len(seed_bytes)
            entropy[i] = (seed_bytes[byte_idx] + 
                         (seed_fingerprint >> (i * 8)) % 256 +
                         i * 5381) % 256
        
        return entropy.astype(np.uint8)
    
    def _extract_context_entropy(self, data_size: int, timestamp: int, length: int) -> np.ndarray:
        """
        Extract entropy from context parameters
        
        Args:
            data_size: Size of data
            timestamp: Timestamp or version
            length: Desired entropy length
            
        Returns:
            Entropy array
        """
        entropy = np.zeros(length, dtype=np.int32)
        
        for i in range(length):
            entropy[i] = ((data_size * (i + 1)) + (timestamp * i * 7919)) % 256
        
        return entropy.astype(np.uint8)
    
    def _diffuse_key_vector(self, key_vector: np.ndarray) -> np.ndarray:
        """
        Apply additional diffusion to key vector
        
        Args:
            key_vector: Input key vector
            
        Returns:
            Diffused key vector
        """
        result = key_vector.astype(np.int32)  # Use int32 for calculations
        length = len(result)
        
        # Multiple diffusion rounds
        for round_idx in range(3):
            # Forward pass
            for i in range(1, length):
                result[i] = (result[i] + result[i-1] * (round_idx + 1)) % 256
            
            # Backward pass
            for i in range(length - 2, -1, -1):
                result[i] = (result[i] + result[i+1] * (round_idx + 2)) % 256
        
        return result.astype(np.uint8)
    
    def combine(self, cel_snapshot: Dict[str, Any], phe_output: bytes) -> np.ndarray:
        """
        Blend CEL and PHE sources directly
        
        Per CKE contract: CKE.combine(CEL, PHE) → blend sources
        
        Args:
            cel_snapshot: CEL snapshot
            phe_output: PHE hash output
            
        Returns:
            Combined key vector
        """
        context = {
            'cel_snapshot': cel_snapshot,
            'phe_output': phe_output,
            'operation': 'combine'
        }
        
        return self.derive(context)
    
    def discard(self) -> None:
        """
        Clear ephemeral data immediately after use
        
        Per CKE contract: CKE.discard() → clear ephemeral data
        """
        # Overwrite ephemeral key with zeros
        if self.ephemeral_key is not None:
            self.ephemeral_key.fill(0)
            self.ephemeral_key = None
    
    def get_key_bytes(self) -> Optional[bytes]:
        """
        Get current ephemeral key as bytes
        
        Returns:
            Key bytes or None if no key derived
        """
        if self.ephemeral_key is None:
            return None
        
        return bytes(self.ephemeral_key)
    
    def derive_subkey(self, parent_key: np.ndarray, index: int, length: int = 32) -> np.ndarray:
        """
        Derive subkey from parent key
        
        Args:
            parent_key: Parent key vector
            index: Subkey index
            length: Desired subkey length
            
        Returns:
            Derived subkey
        """
        subkey = np.zeros(length, dtype=np.uint8)
        
        for i in range(length):
            parent_idx = (i + index * 7919) % len(parent_key)
            # BUG FIX: Convert to int first to avoid uint8 overflow
            value = (int(parent_key[parent_idx]) + index * i) % 256
            subkey[i] = value
        
        # Apply diffusion
        subkey = self._diffuse_key_vector(subkey)
        
        return subkey


def create_cke() -> ContextualKeyEmergence:
    """
    Create CKE instance
    
    Returns:
        CKE instance
    """
    return ContextualKeyEmergence()


def derive_key_from_context(
    cel_snapshot: Dict[str, Any],
    operation: str,
    seed: Optional[Union[str, bytes]] = None,
    phe_output: Optional[bytes] = None,
    key_length: int = 32
) -> bytes:
    """
    Convenience function to derive key from context
    
    Args:
        cel_snapshot: CEL snapshot
        operation: Operation type
        seed: Optional user seed
        phe_output: Optional PHE output
        key_length: Desired key length
        
    Returns:
        Derived key as bytes
    """
    cke = create_cke()
    
    context = {
        'cel_snapshot': cel_snapshot,
        'operation': operation,
        'seed': seed,
        'phe_output': phe_output
    }
    
    key_vector = cke.derive(context, key_length=key_length)
    key_bytes = bytes(key_vector)
    
    # Discard ephemeral data
    cke.discard()
    
    return key_bytes
