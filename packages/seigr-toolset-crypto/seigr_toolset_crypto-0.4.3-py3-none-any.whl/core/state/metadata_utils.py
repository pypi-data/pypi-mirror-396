"""
Metadata Utilities for State Persistence
Implements encryption, differential encoding, and decoy injection using STC components
"""

from typing import Dict, Any, Union
import time
import struct

from core.cel.cel import ContinuousEntropyLattice
from core.phe.phe import ProbabilisticHashingEngine
from utils.seigr_tlv import encode, decode
from utils.math_primitives import data_fingerprint_entropy

# Backward compatibility aliases
serialize_metadata_tlv = encode
deserialize_metadata_tlv = decode
METADATA_VERSION_TLV = 0x01


def differential_encode_cel_snapshot(
    snapshot: Dict[str, Any],
    seed: Union[str, bytes, int]
) -> Dict[str, Any]:
    """
    Encode CEL snapshot as deltas from seed-initialized state (v0.2.0)
    Achieves 70-90% compression
    
    Args:
        snapshot: CEL snapshot from CEL.snapshot()
        seed: Original seed used for CEL initialization
        
    Returns:
        Differential-encoded snapshot
    """
    # Reconstruct reference CEL state from seed
    reference_cel = ContinuousEntropyLattice(
        lattice_size=snapshot.get('lattice_size', 256),
        depth=snapshot.get('depth', 8)
    )
    reference_cel.init(seed)
    reference_lattice = reference_cel.lattice
    
    # Compute deltas
    deltas = []
    current_lattice = snapshot.get('lattice')
    
    if current_lattice is not None and reference_lattice is not None:
        depth = snapshot.get('depth', 8)
        lattice_size = snapshot.get('lattice_size', 256)
        
        for layer in range(depth):
            for row in range(lattice_size):
                for col in range(lattice_size):
                    current_val = int(current_lattice[layer][row][col])
                    reference_val = int(reference_lattice[layer][row][col])
                    
                    delta = current_val - reference_val
                    
                    # Only store non-zero deltas
                    # Store as list (not tuple) for TLV compatibility
                    if delta != 0:
                        deltas.append([layer, row, col, delta])
    
    return {
        'differential': True,
        'deltas': deltas,
        'num_deltas': len(deltas),
        'lattice_size': snapshot.get('lattice_size', 256),
        'depth': snapshot.get('depth', 8),
        'seed_fingerprint': snapshot.get('seed_fingerprint', 0),
        'operation_count': snapshot.get('operation_count', 0),
        'state_version': snapshot.get('state_version', 0)
    }


def differential_decode_cel_snapshot(
    encoded: Dict[str, Any],
    seed: Union[str, bytes, int]
) -> Dict[str, Any]:
    """
    Reconstruct CEL snapshot from deltas (v0.2.0)
    
    Args:
        encoded: Differential-encoded snapshot
        seed: Original seed
        
    Returns:
        Full CEL snapshot
    """
    # Reconstruct reference state
    reference_cel = ContinuousEntropyLattice(
        lattice_size=encoded.get('lattice_size', 256),
        depth=encoded.get('depth', 8)
    )
    reference_cel.init(seed)
    lattice = reference_cel.lattice.copy()
    
    # Apply deltas (lists from TLV deserialization)
    for delta_entry in encoded.get('deltas', []):
        layer, row, col, delta = delta_entry
        lattice[layer][row][col] = int(lattice[layer][row][col]) + delta
    
    return {
        'lattice': lattice,
        'lattice_size': encoded.get('lattice_size', 256),
        'depth': encoded.get('depth', 8),
        'seed_fingerprint': encoded.get('seed_fingerprint', 0),
        'operation_count': encoded.get('operation_count', 0),
        'state_version': encoded.get('state_version', 0)
    }


def encrypt_metadata(
    metadata: Dict[str, Any],
    password: str,
    use_differential: bool = True,
    seed: Union[str, bytes, int, None] = None
) -> Dict[str, Any]:
    """
    Encrypt metadata with ephemeral CEL-derived key (v0.2.0)
    
    Args:
        metadata: Metadata to encrypt
        password: Password for encryption
        use_differential: Whether to use differential encoding for CEL snapshot
        seed: Original seed (required for differential encoding)
        
    Returns:
        Encrypted metadata package
    """
    # Generate timestamp-based ephemeral seed
    timestamp_seed = int(time.time() * 1_000_000) % (2**32)
    
    # Apply differential encoding if requested
    if use_differential and 'cel_snapshot' in metadata and seed is not None:
        metadata = metadata.copy()
        metadata['cel_snapshot'] = differential_encode_cel_snapshot(
            metadata['cel_snapshot'],
            seed
        )
    
    # Serialize metadata to TLV (Seigr TLV handles versioning internally)
    metadata_bytes = serialize_metadata_tlv(metadata)
    
    # Derive ephemeral key deterministically using PHE
    # Note: Using PHE instead of CEL to ensure deterministic key derivation
    key_material = password.encode('utf-8') + b'||metadata||' + timestamp_seed.to_bytes(4, 'big')
    
    phe_kdf = ProbabilisticHashingEngine()
    key_hash = phe_kdf.digest(key_material, context={'purpose': 'metadata_encryption_key'})
    encryption_key = key_hash[:32]  # 256 bits
    
    # Encrypt with CEL-derived key stream (modular addition)
    encrypted = bytearray()
    for i, byte in enumerate(metadata_bytes):
        key_byte = int(encryption_key[i % len(encryption_key)]) % 256
        encrypted_byte = (byte + key_byte) % 256
        encrypted.append(encrypted_byte)
    
    return {
        'encrypted_metadata': bytes(encrypted),
        'ephemeral_seed': timestamp_seed,
        'differential_encoded': use_differential
    }


def decrypt_metadata(
    encrypted_data: Dict[str, Any],
    password: str,
    seed: Union[str, bytes, int, None] = None
) -> Dict[str, Any]:
    """
    Decrypt metadata with ephemeral CEL-derived key (v0.2.0)
    
    Uses STC's native verification: CEL state fingerprint validation.
    Wrong password produces garbage that won't match expected CEL state.
    
    Args:
        encrypted_data: Encrypted metadata package
        password: Password for decryption
        seed: Original seed (required if differential encoding was used)
        
    Returns:
        Decrypted metadata
        
    Raises:
        ValueError: If decryption produces invalid data or CEL state mismatch
    """
    # Reconstruct ephemeral key deterministically from stored seed
    timestamp_seed = encrypted_data['ephemeral_seed']
    key_material = password.encode('utf-8') + b'||metadata||' + timestamp_seed.to_bytes(4, 'big')
    
    phe_kdf = ProbabilisticHashingEngine()
    key_hash = phe_kdf.digest(key_material, context={'purpose': 'metadata_encryption_key'})
    encryption_key = key_hash[:32]  # 256 bits
    
    # Decrypt (modular subtraction)
    encrypted_bytes = encrypted_data['encrypted_metadata']
    decrypted = bytearray()
    for i, byte in enumerate(encrypted_bytes):
        key_byte = int(encryption_key[i % len(encryption_key)]) % 256
        decrypted_byte = (byte - key_byte) % 256
        decrypted.append(decrypted_byte)
    
    metadata_bytes = bytes(decrypted)
    
    # Deserialize TLV - wrong password will likely fail here
    try:
        metadata = deserialize_metadata_tlv(metadata_bytes)
    except (ValueError, struct.error, IndexError, TypeError) as e:
        raise ValueError(f"Decryption failed - invalid password or corrupted data: {e}")
    
    # Validate metadata structure
    if not isinstance(metadata, dict):
        raise ValueError(f"Decryption failed - expected dict but got {type(metadata).__name__}")
    
    # Decode differential encoding if present
    if encrypted_data.get('differential_encoded') and seed is not None:
        if 'cel_snapshot' in metadata and isinstance(metadata.get('cel_snapshot'), dict):
            if metadata['cel_snapshot'].get('differential'):
                metadata['cel_snapshot'] = differential_decode_cel_snapshot(
                    metadata['cel_snapshot'],
                    seed
                )
    
    # STC native verification: validate CEL snapshot integrity using Seigr primitives
    if 'cel_snapshot' in metadata and seed is not None:
        snapshot = metadata.get('cel_snapshot')
        if isinstance(snapshot, dict) and 'seed_fingerprint' in snapshot:
            # Reconstruct expected fingerprint using STC's data_fingerprint_entropy
            if isinstance(seed, str):
                seed_bytes = seed.encode('utf-8')
            elif isinstance(seed, int):
                seed_bytes = seed.to_bytes((seed.bit_length() + 7) // 8, 'big') if seed > 0 else b'\x00'
            else:
                seed_bytes = bytes(seed) if not isinstance(seed, bytes) else seed
            
            expected_fingerprint = data_fingerprint_entropy(seed_bytes)
            actual_fingerprint = snapshot['seed_fingerprint']
            
            if expected_fingerprint != actual_fingerprint:
                raise ValueError(f"CEL state validation failed - seed fingerprint mismatch (expected {expected_fingerprint}, got {actual_fingerprint})")
    
    return metadata


def inject_decoy_vectors(
    real_metadata: Dict[str, Any],
    password: str,
    num_decoys: int = 3,
    variable_sizes: bool = True,
    randomize_count: bool = True,
    timing_randomization: bool = True,
    noise_padding: bool = False
) -> Dict[str, Any]:
    """
    Generate polymorphic decoy snapshots and interleave with real metadata (v0.3.0)
    
    Enhanced with variable sizes, randomized count, timing jitter, and optional padding.
    PERFORMANCE OPTIMIZED: Uses smaller lattices for decoys (64×64×4 default)
    
    Args:
        real_metadata: Real encrypted metadata
        password: Password (used to determine real index)
        num_decoys: Base number of decoy snapshots (3-5), randomized if enabled
        variable_sizes: Use variable lattice sizes for decoys (32×3 to 96×5)
        randomize_count: Randomize actual decoy count (±2 from num_decoys)
        timing_randomization: Add random timing delays during generation
        noise_padding: Add random noise padding to decoy metadata
        
    Returns:
        Obfuscated metadata with polymorphic decoys
        
    Note:
        Decoys use smaller lattices than real CEL for performance:
        - Real CEL: 128×128×6 (user-specified)
        - Decoys: 32×32×3 to 96×96×5 (optimized for speed)
        This provides plausible deniability while maintaining performance.
    """
    import time
    import secrets
    
    # Randomize decoy count if enabled (v0.3.0)
    if randomize_count:
        # Vary count by ±2, min 3, max 7
        actual_count = max(3, min(7, num_decoys + secrets.randbelow(5) - 2))
    else:
        actual_count = num_decoys
    
    decoys = []
    
    # Variable lattice configurations (v0.3.0)
    # OPTIMIZED: Smaller sizes for 5-10x faster generation
    if variable_sizes:
        size_configs = [
            (32, 3),   # Small: 32×32×3 (0.027s)
            (48, 3),   # Small-medium: 48×48×3 (0.06s)
            (64, 4),   # Medium: 64×64×4 (0.14s) ← DEFAULT for balance
            (80, 4),   # Medium-large: 80×80×4 (0.22s)
            (96, 5),   # Large: 96×96×5 (0.39s)
        ]
    else:
        # Fixed size: 64×64×4 provides good balance (0.14s vs 0.81s for 128×128×6)
        size_configs = [(64, 4)] * actual_count
    
    for i in range(actual_count):
        # Add timing jitter if enabled (v0.3.0)
        if timing_randomization:
            # Random delay 1-10ms to prevent timing analysis
            time.sleep(0.001 + secrets.randbelow(10000) / 1000000.0)
        
        # Select random configuration for this decoy
        if variable_sizes:
            lattice_size, depth = size_configs[secrets.randbelow(len(size_configs))]
        else:
            lattice_size, depth = size_configs[0]
        
        # Generate fake seed using PHE entropy
        phe_entropy = ProbabilisticHashingEngine()
        fake_seed_material = f"decoy_{i}_{password}_{time.time()}".encode('utf-8')
        fake_seed_hash = phe_entropy.digest(fake_seed_material, context={'purpose': 'decoy_seed'})
        fake_seed = fake_seed_hash[:32]
        
        # Create fake CEL snapshot with optimized size
        fake_cel = ContinuousEntropyLattice(lattice_size=lattice_size, depth=depth)
        fake_cel.init(fake_seed)
        fake_cel.update({'operation': f'decoy_{i}'})
        fake_snapshot = fake_cel.snapshot()
        
        # Add noise padding if enabled (v0.3.0)
        if noise_padding:
            # Add 10-50 bytes of PHE-generated noise to metadata
            noise_size = 10 + (hash(fake_seed) % 41)
            noise_material = f"noise_{i}_{password}".encode('utf-8')
            noise_hash = phe_entropy.digest(noise_material, context={'purpose': 'decoy_noise'})
            fake_snapshot['_noise_padding'] = noise_hash[:noise_size].hex()
        
        # Encrypt with different ephemeral key (wrong password derivative)
        fake_password = f"decoy_{i}_{password}_fake"
        fake_encrypted = encrypt_metadata(
            {'cel_snapshot': fake_snapshot},
            fake_password,
            use_differential=False
        )
        
        decoys.append(fake_encrypted)
    
    # Determine real index from password hash
    phe = ProbabilisticHashingEngine()
    phe_hash = phe.digest(password.encode('utf-8'))
    real_index = int.from_bytes(phe_hash[-4:], 'big') % (actual_count + 1)
    
    # Interleave decoys with real metadata
    all_vectors = decoys[:real_index] + [real_metadata] + decoys[real_index:]
    
    return {
        'vectors': all_vectors,
        'num_vectors': len(all_vectors),
        # v0.3.0: Store configuration for decryption
        'polymorphic': {
            'variable_sizes': variable_sizes,
            'randomize_count': randomize_count,
            'timing_randomization': timing_randomization,
            'noise_padding': noise_padding
        }
        # Do NOT store real_index - must derive it during decryption
    }


def extract_real_vector(
    obfuscated: Dict[str, Any],
    password: str
) -> Dict[str, Any]:
    """
    Extract real metadata from decoys using password-derived index (v0.2.0)
    
    Args:
        obfuscated: Obfuscated metadata with decoys
        password: Password
        
    Returns:
        Real encrypted metadata
    """
    # Derive real index from password
    phe = ProbabilisticHashingEngine()
    phe_hash = phe.digest(password.encode('utf-8'))
    real_index = int.from_bytes(phe_hash[-4:], 'big') % obfuscated['num_vectors']
    
    # Extract real encrypted metadata
    real_encrypted = obfuscated['vectors'][real_index]
    
    return real_encrypted
