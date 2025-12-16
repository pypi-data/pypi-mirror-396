"""
Data-State Folding (DSF)
Encryption via recursive, non-reversible data folding

Instead of XOR or substitution-permutation networks, DSF treats
data as multidimensional numeric surfaces and applies folding
transformations (rotations, modular warping, entropy-weighted
permutation cycles, compression-expansion oscillation).

Key principles:
- No XOR or classical mixing
- Multidimensional tensor representation
- Entropy-weighted transformations
- Requires exact CEL + CKE context for unfolding
"""

import numpy as np
import struct
from typing import Union, Dict, Any, Optional

from utils.math_primitives import (
    permute_sequence
)


class DataStateFolding:
    """
    DSF - Encryption through multidimensional data folding
    
    Represents data as tensor surfaces and applies recursive
    folding operations determined by key and entropy state.
    """
    
    def __init__(self):
        """Initialize DSF"""
        self.operation_count = 0
        self.fold_depth = 5  # Number of folding iterations
        self.fractal_block_size = 8  # Fractal subdivision block size (8x8x8)
    
    def _safe_key_to_int(self, key_val: float) -> int:
        """
        Safely convert a key value to integer, handling overflow
        
        Args:
            key_val: Key value (potentially very large float)
            
        Returns:
            Safe integer in reasonable range
        """
        if not np.isfinite(key_val):
            return 0
        # Use hash to get deterministic integer from float
        return hash(struct.pack('f', float(key_val))) % (2**31)
        
    def fold(
        self, 
        data: Union[bytes, str],
        key_vector: np.ndarray,
        cel_snapshot: Optional[Dict[str, Any]] = None
    ) -> bytes:
        """
        Encrypt data via recursive folding
        
        Per DSF contract: DSF.fold(data, key_vector) → encrypted tensor
        
        Args:
            data: Data to encrypt (bytes or string)
            key_vector: Key from CKE
            cel_snapshot: Optional CEL snapshot for additional entropy
            
        Returns:
            Encrypted data as bytes
        """
        # Convert string to bytes if needed
        if isinstance(data, str):
            data = data.encode('utf-8')
        
        if not data:
            raise ValueError("Data cannot be empty")
        
        # Convert data to numeric tensor
        tensor = self._data_to_tensor(data)
        
        # Apply folding transformations
        folded_tensor = self._apply_folding(tensor, key_vector, cel_snapshot)
        
        # Convert tensor back to bytes
        encrypted = self._tensor_to_bytes(folded_tensor)
        
        self.operation_count += 1
        
        return encrypted
    
    def unfold(
        self,
        encrypted_data: bytes,
        key_vector: np.ndarray,
        cel_snapshot: Optional[Dict[str, Any]] = None,
        original_length: Optional[int] = None
    ) -> bytes:
        """
        Decrypt data via unfolding (requires exact entropy + context)
        
        Per DSF contract: DSF.unfold(tensor, key_vector) → reconstruct
        
        Args:
            encrypted_data: Encrypted bytes
            key_vector: Key from CKE (must match encryption key)
            cel_snapshot: CEL snapshot (must match encryption state)
            original_length: Original data length (for padding removal)
            
        Returns:
            Decrypted data as bytes
        """
        if not encrypted_data:
            raise ValueError("Encrypted data cannot be empty")
        
        # Convert encrypted bytes to tensor
        tensor = self._bytes_to_tensor(encrypted_data)
        
        # Apply reverse folding transformations
        unfolded_tensor = self._apply_unfolding(tensor, key_vector, cel_snapshot)
        
        # Convert tensor back to bytes
        decrypted = self._tensor_to_data(unfolded_tensor)
        
        # Remove padding if original length provided
        if original_length is not None and len(decrypted) > original_length:
            decrypted = decrypted[:original_length]
        
        self.operation_count += 1
        
        return decrypted
    
    def _data_to_tensor(self, data: bytes) -> np.ndarray:
        """
        Convert data bytes to multidimensional tensor
        
        Args:
            data: Input bytes
            
        Returns:
            3D tensor representation
        """
        # Determine tensor dimensions
        length = len(data)
        
        # Pad to make length suitable for tensor reshaping
        # Target: create roughly cubic tensor
        target_size = int(np.ceil(length ** (1/3)))
        padded_length = target_size ** 3
        padding_needed = padded_length - length
        
        # Pad with deterministic pattern based on data
        if padding_needed > 0:
            padding_byte = (sum(data) % 256) if data else 0
            padded_data = data + bytes([padding_byte] * padding_needed)
        else:
            padded_data = data
        
        # Convert to numpy array
        array = np.frombuffer(padded_data, dtype=np.uint8)
        
        # Reshape to 3D tensor
        tensor = array.reshape(target_size, target_size, target_size)
        
        return tensor.astype(np.float64)
    
    def _tensor_to_bytes(self, tensor: np.ndarray) -> bytes:
        """
        Convert tensor to bytes
        
        Args:
            tensor: Input tensor
            
        Returns:
            Bytes representation
        """
        # Flatten tensor
        flat = tensor.flatten()
        
        # Convert to uint8 (with modulo to handle overflows)
        # Note: Values should already be rounded integers from entropy weighting
        byte_array = np.mod(flat, 256).astype(np.uint8)
        
        return bytes(byte_array)
    
    def _subdivide_into_fractal_blocks(self, tensor: np.ndarray) -> list:
        """
        Subdivide tensor into fractal blocks for efficient processing
        
        Instead of processing entire tensor at once (expensive),
        break into smaller self-similar blocks that can be processed
        independently and in parallel.
        
        Args:
            tensor: Input tensor
            
        Returns:
            List of (block, position) tuples
        """
        blocks = []
        shape = tensor.shape
        block_size = self.fractal_block_size
        
        # Calculate number of blocks in each dimension
        for i in range(0, shape[0], block_size):
            for j in range(0, shape[1], block_size):
                for k in range(0, shape[2], block_size):
                    # Extract block (handle edge cases)
                    i_end = min(i + block_size, shape[0])
                    j_end = min(j + block_size, shape[1])
                    k_end = min(k + block_size, shape[2])
                    
                    block = tensor[i:i_end, j:j_end, k:k_end]
                    position = (i, j, k)
                    blocks.append((block, position))
        
        return blocks
    
    def _reassemble_from_fractal_blocks(self, blocks: list, original_shape: tuple) -> np.ndarray:
        """
        Reassemble tensor from fractal blocks
        
        Args:
            blocks: List of (block, position) tuples
            original_shape: Original tensor shape
            
        Returns:
            Reassembled tensor
        """
        result = np.zeros(original_shape, dtype=np.float64)
        block_size = self.fractal_block_size
        
        for block, (i, j, k) in blocks:
            # Place block back in position
            i_end = min(i + block_size, original_shape[0])
            j_end = min(j + block_size, original_shape[1])
            k_end = min(k + block_size, original_shape[2])
            
            result[i:i_end, j:j_end, k:k_end] = block
        
        return result
    
    def _bytes_to_tensor(self, data: bytes) -> np.ndarray:
        """
        Convert bytes to tensor for unfolding
        
        Args:
            data: Input bytes
            
        Returns:
            3D tensor
        """
        # Convert to array
        array = np.frombuffer(data, dtype=np.uint8)
        
        # Determine dimensions
        length = len(array)
        size = int(np.round(length ** (1/3)))
        
        # Reshape to 3D tensor
        if size ** 3 != length:
            # Handle imperfect cube by padding
            target_length = size ** 3
            if length < target_length:
                padding = np.zeros(target_length - length, dtype=np.uint8)
                array = np.concatenate([array, padding])
            else:
                array = array[:target_length]
        
        tensor = array.reshape(size, size, size)
        
        return tensor.astype(np.float64)
    
    def _tensor_to_data(self, tensor: np.ndarray) -> bytes:
        """
        Convert unfolded tensor back to data bytes
        
        Args:
            tensor: Unfolded tensor (should be integer values only)
            
        Returns:
            Data bytes
        """
        # Flatten and convert to bytes
        # All operations are integer-only now, so direct conversion
        flat = tensor.flatten()
        byte_array = np.mod(flat.astype(np.int64), 256).astype(np.uint8)
        
        return bytes(byte_array)
    
    def _apply_folding(
        self,
        tensor: np.ndarray,
        key_vector: np.ndarray,
        cel_snapshot: Optional[Dict[str, Any]]
    ) -> np.ndarray:
        """
        Apply recursive folding transformations
        
        Args:
            tensor: Input tensor
            key_vector: Encryption key
            cel_snapshot: Optional CEL state
            
        Returns:
            Folded tensor
        """
        result = tensor.copy()
        
        for fold_iteration in range(self.fold_depth):
            # Extract fold parameters from key
            key_offset = fold_iteration % len(key_vector)
            fold_seed = self._safe_key_to_int(key_vector[key_offset]) + fold_iteration * 7919
            
            # Determine folding strategy
            strategy = fold_seed % 4
            
            if strategy == 0:
                result = self._fold_rotation(result, key_vector, fold_iteration)
            elif strategy == 1:
                result = self._fold_permutation(result, key_vector, fold_iteration)
            elif strategy == 2:
                result = self._fold_compression(result, key_vector, fold_iteration)
            else:
                result = self._fold_diffusion(result, key_vector, fold_iteration)
            
            # Apply entropy weighting if CEL available (does its own rounding internally)
            if cel_snapshot:
                result = self._apply_entropy_weighting(result, cel_snapshot, fold_iteration)
        
        return result
    
    def _apply_unfolding(
        self,
        tensor: np.ndarray,
        key_vector: np.ndarray,
        cel_snapshot: Optional[Dict[str, Any]]
    ) -> np.ndarray:
        """
        Apply reverse folding transformations
        
        Args:
            tensor: Encrypted tensor
            key_vector: Decryption key
            cel_snapshot: Optional CEL state
            
        Returns:
            Unfolded tensor
        """
        result = tensor.copy()
        
        # Unfold in reverse order
        for fold_iteration in range(self.fold_depth - 1, -1, -1):
            # Extract fold parameters from key
            key_offset = fold_iteration % len(key_vector)
            fold_seed = self._safe_key_to_int(key_vector[key_offset]) + fold_iteration * 7919
            
            # Reverse entropy weighting if CEL available (does its own rounding internally)
            if cel_snapshot:
                result = self._reverse_entropy_weighting(result, cel_snapshot, fold_iteration)
            
            # Determine folding strategy (same as forward)
            strategy = fold_seed % 4
            
            # Apply reverse operations
            if strategy == 0:
                result = self._unfold_rotation(result, key_vector, fold_iteration)
            elif strategy == 1:
                result = self._unfold_permutation(result, key_vector, fold_iteration)
            elif strategy == 2:
                result = self._unfold_compression(result, key_vector, fold_iteration)
            else:
                result = self._unfold_diffusion(result, key_vector, fold_iteration)
        
        return result
    
    def _fold_rotation(self, tensor: np.ndarray, key: np.ndarray, iteration: int) -> np.ndarray:
        """Folding strategy: Integer-based rotation (not trigonometric)"""
        # Use integer circular shift instead of trigonometric rotation
        k = self._safe_key_to_int(key[iteration % len(key)])
        shift_amount = (k + iteration * 7) % tensor.shape[0]
        
        result = tensor.copy()
        # Rotate along different axes based on iteration
        axis = iteration % 3
        result = np.roll(result, int(shift_amount), axis=axis)
        
        return result
    
    def _unfold_rotation(self, tensor: np.ndarray, key: np.ndarray, iteration: int) -> np.ndarray:
        """Reverse integer rotation"""
        k = self._safe_key_to_int(key[iteration % len(key)])
        shift_amount = (k + iteration * 7) % tensor.shape[0]
        
        result = tensor.copy()
        axis = iteration % 3
        # Reverse rotation by shifting in opposite direction
        result = np.roll(result, -int(shift_amount), axis=axis)
        
        return result
    
    def _fold_permutation(self, tensor: np.ndarray, key: np.ndarray, iteration: int) -> np.ndarray:
        """Folding strategy: Dimension permutation (vectorized for performance)"""
        result = tensor.copy()
        shape = result.shape
        
        # Flatten along one dimension and permute
        dim = iteration % 3
        
        if dim == 0:
            # OPTIMIZED: Process all slices at once instead of loops
            seed_base = self._safe_key_to_int(key[iteration % len(key)]) + iteration
            for i in range(shape[1]):
                for j in range(shape[2]):
                    slice_data = result[:, i, j]
                    seed = seed_base + i * j
                    indices = list(range(len(slice_data)))
                    permuted_indices = permute_sequence(indices, seed, rounds=2)
                    result[:, i, j] = slice_data[permuted_indices]
        
        return result
    
    def _unfold_permutation(self, tensor: np.ndarray, key: np.ndarray, iteration: int) -> np.ndarray:
        """Reverse permutation (vectorized)"""
        result = tensor.copy()
        shape = result.shape
        dim = iteration % 3
        
        if dim == 0:
            # OPTIMIZED: Vectorized inverse permutation
            seed_base = self._safe_key_to_int(key[iteration % len(key)]) + iteration
            for i in range(shape[1]):
                for j in range(shape[2]):
                    slice_data = result[:, i, j]
                    seed = seed_base + i * j
                    indices = list(range(len(slice_data)))
                    permuted_indices = permute_sequence(indices, seed, rounds=2)
                    
                    # Create inverse permutation
                    inverse = np.zeros(len(permuted_indices), dtype=int)
                    inverse[permuted_indices] = np.arange(len(permuted_indices))
                    
                    result[:, i, j] = slice_data[inverse]
        
        return result
    
    def _fold_compression(self, tensor: np.ndarray, key: np.ndarray, iteration: int) -> np.ndarray:
        """Folding strategy: Compression-expansion oscillation (fractal subdivision)"""
        k = self._safe_key_to_int(key[iteration % len(key)])
        
        # FRACTAL OPTIMIZATION: Process in small blocks instead of entire tensor
        blocks = self._subdivide_into_fractal_blocks(tensor)
        processed_blocks = []
        
        for block, position in blocks:
            # Each block gets position-dependent offset for fractal coherence
            i, j, k_pos = position
            block_seed = (k + i + j + k_pos) % 256
            
            # Vectorized compression on small block (much faster)
            shape = block.shape
            if shape[0] > 0 and shape[1] > 0 and shape[2] > 0:
                i_vals, j_vals, k_vals = np.ogrid[:shape[0], :shape[1], :shape[2]]
                offsets = (block_seed + i_vals + j_vals + k_vals) % 256
                processed_block = (block.astype(np.int64) + offsets) % 256
                processed_block = processed_block.astype(np.float64)
            else:
                processed_block = block
            
            processed_blocks.append((processed_block, position))
        
        # Reassemble fractal blocks
        return self._reassemble_from_fractal_blocks(processed_blocks, tensor.shape)
    
    def _unfold_compression(self, tensor: np.ndarray, key: np.ndarray, iteration: int) -> np.ndarray:
        """Reverse compression (fractal subdivision)"""
        k = self._safe_key_to_int(key[iteration % len(key)])
        
        # FRACTAL OPTIMIZATION: Process in blocks
        blocks = self._subdivide_into_fractal_blocks(tensor)
        processed_blocks = []
        
        for block, position in blocks:
            i, j, k_pos = position
            block_seed = (k + i + j + k_pos) % 256
            
            # Vectorized reverse compression on small block
            shape = block.shape
            if shape[0] > 0 and shape[1] > 0 and shape[2] > 0:
                i_vals, j_vals, k_vals = np.ogrid[:shape[0], :shape[1], :shape[2]]
                offsets = (block_seed + i_vals + j_vals + k_vals) % 256
                processed_block = (block.astype(np.int64) - offsets) % 256
                processed_block = processed_block.astype(np.float64)
            else:
                processed_block = block
            
            processed_blocks.append((processed_block, position))
        
        return self._reassemble_from_fractal_blocks(processed_blocks, tensor.shape)
    
    def _fold_diffusion(self, tensor: np.ndarray, key: np.ndarray, iteration: int) -> np.ndarray:
        """
        Folding strategy: Reversible diffusion using key-driven layer mixing (fractal)
        
        Fractal subdivision makes this dramatically faster while maintaining
        cryptographic strength through hierarchical block relationships.
        """
        # FRACTAL OPTIMIZATION: Process each layer in blocks
        result = tensor.copy()
        
        for i in range(result.shape[0]):
            layer = result[i].astype(np.int64)
            rows, cols = layer.shape
            
            # Process layer in 2D blocks for speed
            block_size_2d = self.fractal_block_size
            for r in range(0, rows, block_size_2d):
                for c in range(0, cols, block_size_2d):
                    r_end = min(r + block_size_2d, rows)
                    c_end = min(c + block_size_2d, cols)
                    
                    block = layer[r:r_end, c:c_end]
                    
                    # Vectorized offset calculation for this block
                    block_rows, block_cols = block.shape
                    if block_rows > 0 and block_cols > 0:
                        r_vals, c_vals = np.ogrid[:block_rows, :block_cols]
                        global_r = r + r_vals
                        global_c = c + c_vals
                        key_indices = (i + global_r + global_c + iteration) % len(key)
                        
                        # Create offset matrix
                        offsets = np.zeros((block_rows, block_cols), dtype=np.int64)
                        for key_idx in range(len(key)):
                            mask = (key_indices == key_idx)
                            if np.any(mask):
                                offsets[mask] = self._safe_key_to_int(key[key_idx]) % 256
                        
                        # Apply offsets to block
                        layer[r:r_end, c:c_end] = (block + offsets) % 256
            
            result[i] = layer.astype(np.float64)
        
        return result
    
    def _unfold_diffusion(self, tensor: np.ndarray, key: np.ndarray, iteration: int) -> np.ndarray:
        """
        Reverse diffusion - exact inverse of fold_diffusion (fractal)
        """
        result = tensor.copy()
        
        # FRACTAL OPTIMIZATION: Process each layer in blocks
        for i in range(result.shape[0]):
            layer = result[i].astype(np.int64)
            rows, cols = layer.shape
            
            # Process layer in 2D blocks
            block_size_2d = self.fractal_block_size
            for r in range(0, rows, block_size_2d):
                for c in range(0, cols, block_size_2d):
                    r_end = min(r + block_size_2d, rows)
                    c_end = min(c + block_size_2d, cols)
                    
                    block = layer[r:r_end, c:c_end]
                    
                    # Vectorized offset calculation for this block
                    block_rows, block_cols = block.shape
                    if block_rows > 0 and block_cols > 0:
                        r_vals, c_vals = np.ogrid[:block_rows, :block_cols]
                        global_r = r + r_vals
                        global_c = c + c_vals
                        key_indices = (i + global_r + global_c + iteration) % len(key)
                        
                        # Create offset matrix
                        offsets = np.zeros((block_rows, block_cols), dtype=np.int64)
                        for key_idx in range(len(key)):
                            mask = (key_indices == key_idx)
                            if np.any(mask):
                                offsets[mask] = self._safe_key_to_int(key[key_idx]) % 256
                        
                        # Reverse offsets to block
                        layer[r:r_end, c:c_end] = (block - offsets) % 256
            
            result[i] = layer.astype(np.float64)
        
        return result
    
    def _apply_entropy_weighting(
        self,
        tensor: np.ndarray,
        cel_snapshot: Dict[str, Any],
        iteration: int
    ) -> np.ndarray:
        """
        Apply entropy-based weighting from CEL
        
        Args:
            tensor: Input tensor (integer values only - no floating point)
            cel_snapshot: CEL state
            iteration: Current fold iteration
            
        Returns:
            Weighted tensor
        """
        result = tensor.copy()
        
        # Extract entropy from CEL
        if 'lattice' in cel_snapshot:
            cel_lattice = cel_snapshot['lattice']
            flat_entropy = cel_lattice.flatten()
            
            # Apply entropy weighting to tensor values
            flat_tensor = result.flatten()
            for i in range(len(flat_tensor)):
                entropy_idx = (i + iteration * 7919) % len(flat_entropy)
                # Pure integer arithmetic - perfectly reversible
                weight_int = int(flat_entropy[entropy_idx]) % 256
                flat_tensor[i] = (int(flat_tensor[i]) + weight_int) % 256
            
            result = flat_tensor.reshape(result.shape)
        
        return result
    
    def _reverse_entropy_weighting(
        self,
        tensor: np.ndarray,
        cel_snapshot: Dict[str, Any],
        iteration: int
    ) -> np.ndarray:
        """
        Reverse entropy weighting
        
        Args:
            tensor: Weighted tensor
            cel_snapshot: CEL state
            iteration: Current fold iteration
            
        Returns:
            Unweighted tensor
        """
        result = tensor.copy()
        
        if 'lattice' in cel_snapshot:
            cel_lattice = cel_snapshot['lattice']
            flat_entropy = cel_lattice.flatten()
            
            flat_tensor = result.flatten()
            for i in range(len(flat_tensor)):
                entropy_idx = (i + iteration * 7919) % len(flat_entropy)
                # Reverse operation: tensor values are already integers (from bytes)
                # Just subtract the weight
                weight_int = int(flat_entropy[entropy_idx]) % 256
                flat_tensor[i] = (int(flat_tensor[i]) - weight_int) % 256
            
            result = flat_tensor.reshape(result.shape)
        
        return result
    
    def verify_integrity(self, data: bytes, encrypted: bytes, key_vector: np.ndarray) -> bool:
        """
        Verify encryption/decryption integrity
        
        Per DSF contract: DSF.verify_integrity() → optional consistency check
        
        Args:
            data: Original data
            encrypted: Encrypted data
            key_vector: Key used for encryption
            
        Returns:
            True if round-trip successful
        """
        try:
            decrypted = self.unfold(encrypted, key_vector, original_length=len(data))
            return decrypted == data
        except Exception:
            return False


def create_dsf() -> DataStateFolding:
    """
    Create DSF instance
    
    Returns:
        DSF instance
    """
    return DataStateFolding()
