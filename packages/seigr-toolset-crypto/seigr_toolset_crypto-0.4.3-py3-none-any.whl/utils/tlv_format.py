"""
TLV (Type-Length-Value) Binary Format for Metadata Serialization
Self-sovereign binary format with ~25% size reduction and versioning support

Format: [Type:1 byte][Length:4 bytes big-endian][Value:variable]
"""

import numpy as np
from typing import Dict, Any, Union


# TLV Type Definitions
TLV_TYPE_METADATA_VERSION = 0x00
TLV_TYPE_CEL_SNAPSHOT = 0x01
TLV_TYPE_ORIGINAL_LENGTH = 0x02
TLV_TYPE_WAS_STRING = 0x03
TLV_TYPE_PHE_HASH = 0x04
TLV_TYPE_METADATA_MAC = 0x05
TLV_TYPE_DECOY_SNAPSHOT = 0x06
TLV_TYPE_DIFFERENTIAL_DELTAS = 0x07
TLV_TYPE_EPHEMERAL_SEED = 0x08
TLV_TYPE_CEL_SEED_FINGERPRINT = 0x09
TLV_TYPE_CEL_OPERATION_COUNT = 0x0A
TLV_TYPE_CEL_STATE_VERSION = 0x0B
TLV_TYPE_ENCRYPTED_METADATA = 0x0C  # Encrypted metadata blob
TLV_TYPE_DIFFERENTIAL_ENCODED = 0x0D  # Boolean flag
TLV_TYPE_OBFUSCATED = 0x0E  # Boolean flag for decoy presence
TLV_TYPE_NUM_VECTORS = 0x0F  # Number of obfuscated vectors
TLV_TYPE_VECTOR = 0x10  # Single obfuscated vector (encrypted metadata blob)
TLV_TYPE_POLYMORPHIC_CONFIG = 0x11  # v0.3.0: Polymorphic decoy configuration

# Metadata format versions - only self-sovereign TLV for true sovereignty
METADATA_VERSION_TLV = 0x01   # v0.2.0+ Self-sovereign TLV format

# Field size constants (for TLV value field sizes, not TLV header length which is always 4 bytes)
FIELD_SIZE_VERSION = 1        # 1 byte for version
FIELD_SIZE_SEED = 4           # 4 bytes for seeds
FIELD_SIZE_FILE_LENGTH = 8    # 8 bytes for file length values (supports files up to 2^64 bytes)
FIELD_SIZE_BOOL = 1           # 1 byte for booleans
FIELD_SIZE_COUNT = 4          # 4 bytes for counts


def serialize_metadata_tlv(metadata: Dict[str, Any], version: int = METADATA_VERSION_TLV) -> bytes:
    """
    Serialize metadata to TLV binary format
    
    Args:
        metadata: Metadata dictionary
        version: Metadata format version
        
    Returns:
        Binary TLV-encoded bytes
    """
    buffer = bytearray()
    
    # Always write version first
    _write_tlv_field(buffer, TLV_TYPE_METADATA_VERSION, version.to_bytes(FIELD_SIZE_VERSION, 'big'))
    
    # Encrypted metadata blob (if present - from encrypt_metadata())
    if 'encrypted_metadata' in metadata:
        _write_tlv_field(buffer, TLV_TYPE_ENCRYPTED_METADATA, metadata['encrypted_metadata'])
    
    # Ephemeral seed
    if 'ephemeral_seed' in metadata:
        _write_tlv_field(buffer, TLV_TYPE_EPHEMERAL_SEED,
                        metadata['ephemeral_seed'].to_bytes(FIELD_SIZE_SEED, 'big'))
    
    # Metadata MAC
    if 'metadata_mac' in metadata:
        mac = metadata['metadata_mac']
        if isinstance(mac, str):
            mac = bytes.fromhex(mac)
        _write_tlv_field(buffer, TLV_TYPE_METADATA_MAC, mac)
    
    # Differential encoded flag
    if 'differential_encoded' in metadata:
        _write_tlv_field(buffer, TLV_TYPE_DIFFERENTIAL_ENCODED,
                        bytes([1 if metadata['differential_encoded'] else 0]))
    
    # Obfuscated flag
    if 'obfuscated' in metadata:
        _write_tlv_field(buffer, TLV_TYPE_OBFUSCATED,
                        bytes([1 if metadata['obfuscated'] else 0]))
    
    # Number of vectors
    if 'num_vectors' in metadata:
        _write_tlv_field(buffer, TLV_TYPE_NUM_VECTORS,
                        metadata['num_vectors'].to_bytes(FIELD_SIZE_COUNT, 'big'))
    
    # Obfuscated vectors (real + decoys)
    if 'vectors' in metadata:
        for vector in metadata['vectors']:
            # Each vector is encrypted metadata - serialize recursively
            vector_data = serialize_metadata_tlv(vector, version)
            _write_tlv_field(buffer, TLV_TYPE_VECTOR, vector_data)
    
    # Polymorphic decoy configuration (v0.3.0)
    if 'polymorphic' in metadata:
        poly_config = metadata['polymorphic']
        # Encode as 4 boolean flags: [variable_sizes, randomize_count, timing, noise]
        flags = 0
        if poly_config.get('variable_sizes'):
            flags |= 0b0001
        if poly_config.get('randomize_count'):
            flags |= 0b0010
        if poly_config.get('timing_randomization'):
            flags |= 0b0100
        if poly_config.get('noise_padding'):
            flags |= 0b1000
        _write_tlv_field(buffer, TLV_TYPE_POLYMORPHIC_CONFIG, bytes([flags]))
    
    # CEL snapshot (differential or full)
    if 'cel_snapshot' in metadata:
        cel_snapshot = metadata['cel_snapshot']
        
        # Check if differential-encoded
        if cel_snapshot.get('differential'):
            # Serialize header only (no lattice)
            snapshot_data = _serialize_cel_snapshot_header(cel_snapshot)
            _write_tlv_field(buffer, TLV_TYPE_CEL_SNAPSHOT, snapshot_data)
            
            # Serialize deltas separately
            deltas_data = _serialize_differential_deltas(cel_snapshot.get('deltas', []))
            _write_tlv_field(buffer, TLV_TYPE_DIFFERENTIAL_DELTAS, deltas_data)
        else:
            # Full snapshot with lattice
            snapshot_data = _serialize_cel_snapshot(cel_snapshot)
            _write_tlv_field(buffer, TLV_TYPE_CEL_SNAPSHOT, snapshot_data)
    
    # Differential deltas (if present at top level - backward compat)
    elif 'differential_deltas' in metadata:
        deltas_data = _serialize_differential_deltas(metadata['differential_deltas'])
        _write_tlv_field(buffer, TLV_TYPE_DIFFERENTIAL_DELTAS, deltas_data)
    
    # Original length
    if 'original_length' in metadata:
        _write_tlv_field(buffer, TLV_TYPE_ORIGINAL_LENGTH, 
                        metadata['original_length'].to_bytes(FIELD_SIZE_FILE_LENGTH, 'big'))
    
    # Was string flag
    if 'was_string' in metadata:
        _write_tlv_field(buffer, TLV_TYPE_WAS_STRING, 
                        bytes([1 if metadata['was_string'] else 0]))
    
    # PHE hash
    if 'phe_hash' in metadata:
        phe_hash = metadata['phe_hash']
        if isinstance(phe_hash, str):
            phe_hash = bytes.fromhex(phe_hash)
        _write_tlv_field(buffer, TLV_TYPE_PHE_HASH, phe_hash)
    
    # Decoy snapshots
    if 'decoy_snapshots' in metadata:
        for decoy in metadata['decoy_snapshots']:
            decoy_data = _serialize_cel_snapshot(decoy)
            _write_tlv_field(buffer, TLV_TYPE_DECOY_SNAPSHOT, decoy_data)
    
    return bytes(buffer)


def deserialize_metadata_tlv(data: bytes) -> Dict[str, Any]:
    """
    Deserialize TLV binary format to metadata dictionary
    
    Args:
        data: TLV-encoded bytes
        
    Returns:
        Metadata dictionary
    """
    metadata = {}
    decoy_snapshots = []
    vectors = []
    offset = 0
    
    while offset < len(data):
        if offset + 5 > len(data):  # Need at least type + length
            break
            
        tlv_type = data[offset]
        offset += 1
        
        length = int.from_bytes(data[offset:offset+4], 'big')
        offset += 4
        
        if offset + length > len(data):
            raise ValueError(f"Invalid TLV: length {length} exceeds remaining data")
        
        value_data = data[offset:offset+length]
        offset += length
        
        # Parse based on type
        if tlv_type == TLV_TYPE_METADATA_VERSION:
            metadata['metadata_version'] = int.from_bytes(value_data, 'big')
        
        elif tlv_type == TLV_TYPE_CEL_SNAPSHOT:
            metadata['cel_snapshot'] = _deserialize_cel_snapshot(value_data)
        
        elif tlv_type == TLV_TYPE_DIFFERENTIAL_DELTAS:
            metadata['differential_deltas'] = _deserialize_differential_deltas(value_data)
        
        elif tlv_type == TLV_TYPE_ORIGINAL_LENGTH:
            metadata['original_length'] = int.from_bytes(value_data, 'big')
        
        elif tlv_type == TLV_TYPE_WAS_STRING:
            metadata['was_string'] = bool(value_data[0])
        
        elif tlv_type == TLV_TYPE_PHE_HASH:
            metadata['phe_hash'] = value_data
        
        elif tlv_type == TLV_TYPE_METADATA_MAC:
            metadata['metadata_mac'] = value_data
        
        elif tlv_type == TLV_TYPE_EPHEMERAL_SEED:
            metadata['ephemeral_seed'] = int.from_bytes(value_data, 'big')
        
        elif tlv_type == TLV_TYPE_ENCRYPTED_METADATA:
            metadata['encrypted_metadata'] = value_data
        
        elif tlv_type == TLV_TYPE_DIFFERENTIAL_ENCODED:
            metadata['differential_encoded'] = bool(value_data[0])
        
        elif tlv_type == TLV_TYPE_OBFUSCATED:
            metadata['obfuscated'] = bool(value_data[0])
        
        elif tlv_type == TLV_TYPE_NUM_VECTORS:
            metadata['num_vectors'] = int.from_bytes(value_data, 'big')
        
        elif tlv_type == TLV_TYPE_VECTOR:
            # Recursively deserialize each vector
            vector = deserialize_metadata_tlv(value_data)
            vectors.append(vector)
        
        elif tlv_type == TLV_TYPE_POLYMORPHIC_CONFIG:
            # Decode polymorphic flags (v0.3.0)
            flags = value_data[0]
            metadata['polymorphic'] = {
                'variable_sizes': bool(flags & 0b0001),
                'randomize_count': bool(flags & 0b0010),
                'timing_randomization': bool(flags & 0b0100),
                'noise_padding': bool(flags & 0b1000)
            }
        
        elif tlv_type == TLV_TYPE_DECOY_SNAPSHOT:
            decoy_snapshots.append(_deserialize_cel_snapshot(value_data))
    
    # Post-processing: combine cel_snapshot with differential_deltas if both present
    if 'cel_snapshot' in metadata and 'differential_deltas' in metadata:
        cel_snapshot = metadata['cel_snapshot']
        deltas = metadata.pop('differential_deltas')  # Remove from top level
        
        # Add differential info to cel_snapshot
        cel_snapshot['differential'] = True
        cel_snapshot['deltas'] = deltas
        cel_snapshot['num_deltas'] = len(deltas)
    
    if decoy_snapshots:
        metadata['decoy_snapshots'] = decoy_snapshots
    
    if vectors:
        metadata['vectors'] = vectors
    
    return metadata


def _write_tlv_field(buffer: bytearray, tlv_type: int, value: bytes) -> None:
    """Write single TLV field to buffer"""
    buffer.append(tlv_type)
    buffer.extend(len(value).to_bytes(4, 'big'))
    buffer.extend(value)


def _serialize_cel_snapshot_header(snapshot: Dict[str, Any]) -> bytes:
    """
    Serialize only CEL snapshot header (for differential snapshots)
    
    Format:
    - lattice_size: 2 bytes
    - depth: 1 byte
    - seed_fingerprint: 8 bytes
    - operation_count: 4 bytes
    - state_version: 4 bytes
    """
    buffer = bytearray()
    
    # Header only (no lattice)
    buffer.extend(snapshot.get('lattice_size', 256).to_bytes(2, 'big'))
    buffer.append(snapshot.get('depth', 8))
    buffer.extend(snapshot.get('seed_fingerprint', 0).to_bytes(8, 'big', signed=False))
    buffer.extend(snapshot.get('operation_count', 0).to_bytes(4, 'big'))
    buffer.extend(snapshot.get('state_version', 0).to_bytes(4, 'big'))
    
    return bytes(buffer)


def _serialize_cel_snapshot(snapshot: Dict[str, Any]) -> bytes:
    """
    Serialize CEL snapshot to compact binary format
    
    Format:
    - lattice_size: 2 bytes
    - depth: 1 byte
    - seed_fingerprint: 8 bytes
    - operation_count: 4 bytes
    - state_version: 4 bytes
    - lattice data: variable (compressed)
    """
    buffer = bytearray()
    
    # Header
    buffer.extend(snapshot.get('lattice_size', 256).to_bytes(2, 'big'))
    buffer.append(snapshot.get('depth', 8))
    buffer.extend(snapshot.get('seed_fingerprint', 0).to_bytes(8, 'big', signed=False))
    buffer.extend(snapshot.get('operation_count', 0).to_bytes(4, 'big'))
    buffer.extend(snapshot.get('state_version', 0).to_bytes(4, 'big'))
    
    # Lattice data (flatten and compress)
    if 'lattice' in snapshot:
        lattice = snapshot['lattice']
        if isinstance(lattice, np.ndarray):
            # Flatten and convert to bytes
            flat = lattice.flatten()
            # Use variable-length encoding for values
            compressed = _compress_int_array(flat)
            buffer.extend(compressed)
        else:
            # Already compressed or empty
            pass
    
    return bytes(buffer)


def _deserialize_cel_snapshot(data: bytes) -> Dict[str, Any]:
    """
    Deserialize CEL snapshot from binary format
    
    Args:
        data: Binary snapshot data
        
    Returns:
        CEL snapshot dictionary
    """
    if len(data) < 19:  # Minimum header size
        raise ValueError("Invalid CEL snapshot: too short")
    
    offset = 0
    
    # Parse header
    lattice_size = int.from_bytes(data[offset:offset+2], 'big')
    offset += 2
    
    depth = data[offset]
    offset += 1
    
    seed_fingerprint = int.from_bytes(data[offset:offset+8], 'big', signed=False)
    offset += 8
    
    operation_count = int.from_bytes(data[offset:offset+4], 'big')
    offset += 4
    
    state_version = int.from_bytes(data[offset:offset+4], 'big')
    offset += 4
    
    # Validate dimensions before calculating expected length
    if depth <= 0 or lattice_size <= 0:
        raise ValueError(f"Invalid lattice dimensions: depth={depth}, lattice_size={lattice_size}")
    
    # Parse lattice data
    lattice = None
    if offset < len(data):
        remaining = data[offset:]
        expected_length = depth * lattice_size * lattice_size
        flat = _decompress_int_array(remaining, expected_length)
        lattice = flat.reshape((depth, lattice_size, lattice_size))
    
    return {
        'lattice_size': lattice_size,
        'depth': depth,
        'seed_fingerprint': seed_fingerprint,
        'operation_count': operation_count,
        'state_version': state_version,
        'lattice': lattice
    }


def _serialize_differential_deltas(deltas: list) -> bytes:
    """
    Serialize differential deltas to binary format
    
    Format for each delta: [layer:1][row:2][col:2][delta:8 signed]
    """
    buffer = bytearray()
    
    # Write number of deltas
    buffer.extend(len(deltas).to_bytes(4, 'big'))
    
    # Write each delta
    for delta in deltas:
        # BUG FIX: Handle both dict and tuple formats
        if isinstance(delta, dict):
            layer = delta['layer']
            row = delta['row']
            col = delta['col']
            value = delta['value']
        else:
            # Tuple format: (layer, row, col, value)
            layer, row, col, value = delta
            
        buffer.append(layer)
        buffer.extend(row.to_bytes(2, 'big'))
        buffer.extend(col.to_bytes(2, 'big'))
        buffer.extend(int(value).to_bytes(8, 'big', signed=True))
    
    return bytes(buffer)


def _deserialize_differential_deltas(data: bytes) -> list:
    """Deserialize differential deltas from binary format"""
    if len(data) < 4:
        return []
    
    num_deltas = int.from_bytes(data[0:4], 'big')
    deltas = []
    offset = 4
    
    for _ in range(num_deltas):
        if offset + 13 > len(data):
            break
        
        layer = data[offset]
        offset += 1
        
        row = int.from_bytes(data[offset:offset+2], 'big')
        offset += 2
        
        col = int.from_bytes(data[offset:offset+2], 'big')
        offset += 2
        
        delta = int.from_bytes(data[offset:offset+8], 'big', signed=True)
        offset += 8
        
        deltas.append((layer, row, col, delta))
    
    return deltas


def _compress_int_array(arr: np.ndarray) -> bytes:
    """
    Compress integer array using variable-length encoding (v0.3.0)
    
    Compression strategies (optimized for pseudo-random lattice data):
    1. Varint encoding (LEB128 + zigzag) - handles variable magnitude efficiently
    2. Run-length encoding for consecutive zeros (rare in CEL data but cheap to check)
    
    Note: Dictionary encoding not implemented - CEL lattice data is high-entropy
    pseudo-random with ~51% unique values, making pattern-based compression ineffective.
    """
    buffer = bytearray()
    
    # Write array length
    buffer.extend(len(arr).to_bytes(4, 'big'))
    
    # Pre-compute zero positions using numpy for efficiency
    flat_arr = arr.ravel() if hasattr(arr, 'ravel') else np.asarray(arr).ravel()
    is_zero = flat_arr == 0
    
    # Encode array with RLE for zeros + varint for all other values
    i = 0
    n = len(flat_arr)
    while i < n:
        val = int(flat_arr[i])
        
        # Check for run of zeros using pre-computed mask
        if is_zero[i]:
            # Count consecutive zeros efficiently
            zero_count = 1
            while i + zero_count < n and is_zero[i + zero_count]:
                zero_count += 1
            
            # If 3+ zeros, use RLE marker
            if zero_count >= 3:
                buffer.append(0xFF)  # RLE marker
                _write_varint(buffer, zero_count)
                i += zero_count
                continue
        
        # Use varint encoding for all non-zero values
        _write_signed_varint(buffer, val)
        i += 1
    
    return bytes(buffer)


def _decompress_int_array(data: bytes, expected_length: int) -> np.ndarray:
    """
    Decompress integer array from variable-length encoding with RLE (v0.3.0)
    
    Matches compression format: RLE for zeros, varint for all other values
    """
    if len(data) < 4:
        return np.zeros(expected_length, dtype=np.int64)
    
    arr_length = int.from_bytes(data[0:4], 'big')
    offset = 4
    
    arr = []
    while len(arr) < min(arr_length, expected_length) and offset < len(data):
        # Check for RLE marker (0xFF = run of zeros)
        if data[offset] == 0xFF:
            offset += 1
            zero_count, bytes_read = _read_varint(data, offset)
            offset += bytes_read
            arr.extend([0] * zero_count)
        else:
            # Read signed varint
            val, bytes_read = _read_signed_varint(data, offset)
            offset += bytes_read
            arr.append(val)
    
    # Pad if necessary
    while len(arr) < expected_length:
        arr.append(0)
    
    return np.array(arr[:expected_length], dtype=np.int64)


def _write_varint(buffer: bytearray, value: int) -> None:
    """
    Write unsigned integer in LEB128 varint format
    """
    while value >= 0x80:
        buffer.append((value & 0x7F) | 0x80)
        value >>= 7
    buffer.append(value & 0x7F)


def _read_varint(data: bytes, offset: int) -> tuple:
    """
    Read unsigned varint from data at offset
    Returns (value, bytes_read)
    """
    result = 0
    shift = 0
    bytes_read = 0
    
    while offset + bytes_read < len(data):
        byte = data[offset + bytes_read]
        bytes_read += 1
        
        result |= (byte & 0x7F) << shift
        if not (byte & 0x80):
            break
        shift += 7
    
    return result, bytes_read


def _write_signed_varint(buffer: bytearray, value: int) -> None:
    """
    Write signed integer using zigzag encoding + varint
    Zigzag maps signed to unsigned: 0,-1,1,-2,2... → 0,1,2,3,4...
    Works for arbitrary precision Python integers.
    """
    # Zigzag encoding: positive n -> 2n, negative n -> 2|n|-1
    # This works correctly for arbitrary precision integers
    if value >= 0:
        zigzag = value << 1
    else:
        zigzag = ((-value) << 1) - 1
    _write_varint(buffer, zigzag)


def _read_signed_varint(data: bytes, offset: int) -> tuple:
    """
    Read signed varint using zigzag decoding
    Works for arbitrary precision Python integers.
    Returns (value, bytes_read)
    """
    zigzag, bytes_read = _read_varint(data, offset)
    # Decode: even -> positive (n/2), odd -> negative (-(n+1)/2)
    if zigzag & 1:
        value = -((zigzag + 1) >> 1)
    else:
        value = zigzag >> 1
    return value, bytes_read


# Public API wrappers for compression functions
def compress_int_array(arr: np.ndarray) -> bytes:
    """
    Public API: Compress integer array using variable-length encoding
    
    Args:
        arr: Numpy array of integers to compress
        
    Returns:
        Compressed bytes
    """
    return _compress_int_array(arr)


def decompress_int_array(data: bytes, expected_length: int) -> np.ndarray:
    """
    Public API: Decompress integer array from variable-length encoding
    
    Args:
        data: Compressed bytes
        expected_length: Expected number of elements in the output array
        
    Returns:
        Numpy array of decompressed integers
    """
    return _decompress_int_array(data, expected_length)


def detect_metadata_version(data: Union[bytes, str]) -> int:
    """
    Detect metadata format version - only supports self-sovereign TLV
    
    Args:
        data: Metadata bytes in TLV format
        
    Returns:
        METADATA_VERSION_TLV (0x01) - only self-sovereign format supported
    """
    if isinstance(data, str):
        # String data is not supported - only self-sovereign binary formats
        raise ValueError("String metadata not supported. STC requires self-sovereign binary format.")
    
    if isinstance(data, bytes):
        # Check for TLV format signature
        if len(data) > 5 and data[0] == TLV_TYPE_METADATA_VERSION:
            return METADATA_VERSION_TLV
        # Non-TLV binary data is not supported
        raise ValueError("Invalid metadata format. STC requires self-sovereign TLV format.")
    
    # Only TLV format supported for self-sovereignty
    raise ValueError("Unsupported metadata type. STC requires self-sovereign TLV format.")
