"""
Seigr Dynamic TLV - Production Native Serialization System
Fully dynamic, self-describing binary format with zero hardcoded mappings

Design Principles:
1. Complete type inference - handles ANY Python data structure
2. Zero hardcoded field mappings - fully extensible
3. Compact binary format with intelligent compression
4. Self-describing - metadata embedded in stream
5. Production-ready error handling

Format: [Type:1 byte][Length:varint][Value:variable]

Type System (single byte):
0x01 = Version marker
0x10 = Integer (size auto-detected)
0x20 = String (UTF-8)
0x30 = Bytes
0x40 = Boolean
0x50 = List
0x60 = Dictionary
0x70 = Numpy array
0xFF = Null/None
"""

import numpy as np
from typing import Dict, Any, List, Tuple
import struct

# Import compression utilities (public API)
from utils.tlv_format import compress_int_array, decompress_int_array


class DynamicTLV:
    """
    Fully dynamic TLV serialization system
    
    Automatically handles any Python data structure without hardcoded mappings
    """
    
    # Base type codes (high nibble)
    TYPE_METADATA = 0x00
    TYPE_INTEGER = 0x10
    TYPE_STRING = 0x20
    TYPE_BYTES = 0x30
    TYPE_BOOLEAN = 0x40
    TYPE_ARRAY = 0x50
    TYPE_DICT = 0x60
    TYPE_NUMPY = 0x70
    TYPE_COMPLEX = 0x80
    TYPE_CONTROL = 0xF0
    
    # Specific type codes
    TYPE_VERSION = 0x00
    TYPE_FIELD_NAME = 0x01  # Dynamic field name registration
    
    TYPE_INT8 = 0x10
    TYPE_INT16 = 0x11
    TYPE_INT32 = 0x12
    TYPE_INT64 = 0x13
    TYPE_UINT8 = 0x14
    TYPE_UINT16 = 0x15
    TYPE_UINT32 = 0x16
    TYPE_UINT64 = 0x17
    TYPE_VARINT = 0x18  # Variable-length integer (LEB128)
    
    TYPE_UTF8 = 0x20
    TYPE_HEX_STRING = 0x21
    
    TYPE_BYTES_RAW = 0x30
    TYPE_BYTES_COMPRESSED = 0x31
    
    TYPE_BOOL_TRUE = 0x40
    TYPE_BOOL_FALSE = 0x41
    
    TYPE_LIST = 0x50
    TYPE_TUPLE = 0x51
    
    TYPE_DICT_GENERIC = 0x60
    TYPE_DICT_ORDERED = 0x61  # Preserves insertion order
    
    TYPE_NUMPY_INT = 0x70
    TYPE_NUMPY_FLOAT = 0x71
    TYPE_NUMPY_COMPRESSED = 0x72
    
    TYPE_CEL_SNAPSHOT = 0x80
    TYPE_DIFFERENTIAL_DELTAS = 0x81
    TYPE_POLYMORPHIC_CONFIG = 0x82
    
    TYPE_RLE_MARKER = 0xFF
    
    # Well-known field names for optimization
    # These get assigned specific codes, but system is fully extensible
    KNOWN_FIELDS = {
        'metadata_version': 0x00,
        'cel_snapshot': 0x80,
        'differential_deltas': 0x81,
        'polymorphic': 0x82,
        'original_length': 0x02,
        'was_string': 0x03,
        'phe_hash': 0x04,
        'metadata_mac': 0x05,
        'decoy_snapshots': 0x06,
        'ephemeral_seed': 0x08,
        'encrypted_metadata': 0x0C,
        'differential_encoded': 0x0D,
        'obfuscated': 0x0E,
        'num_vectors': 0x0F,
        'vectors': 0x10,
    }
    
    # Reverse mapping for deserialization
    FIELD_CODES = {v: k for k, v in KNOWN_FIELDS.items()}
    
    # Dynamic field registry (runtime extension)
    dynamic_field_registry: Dict[str, int] = {}
    dynamic_code_registry: Dict[int, str] = {}
    next_dynamic_code: int = 0xA0  # Start dynamic codes at 0xA0
    
    @classmethod
    def serialize(cls, data: Any, field_name: str = None, _is_nested: bool = False) -> bytes:
        """
        Dynamically serialize any Python data structure to TLV format
        
        Args:
            data: Data to serialize (dict, list, int, str, bytes, etc.)
            field_name: Optional field name for context
            _is_nested: Internal flag to prevent version header in nested dicts
            
        Returns:
            TLV-encoded bytes
        """
        buffer = bytearray()
        
        # Version header (only for top-level dicts)
        if isinstance(data, dict) and field_name is None and not _is_nested:
            cls._write_field(buffer, cls.TYPE_VERSION, bytes([1]))
        
        # Auto-detect type and serialize
        if isinstance(data, dict):
            cls._serialize_dict(buffer, data)
        elif isinstance(data, (list, tuple)):
            type_code = cls.TYPE_TUPLE if isinstance(data, tuple) else cls.TYPE_LIST
            cls._serialize_list(buffer, data, type_code)
        elif isinstance(data, bool):
            type_code = cls.TYPE_BOOL_TRUE if data else cls.TYPE_BOOL_FALSE
            cls._write_field(buffer, type_code, b'')  # Boolean is in type itself
        elif isinstance(data, int):
            cls._serialize_int(buffer, data)
        elif isinstance(data, str):
            cls._serialize_string(buffer, data)
        elif isinstance(data, bytes):
            cls._write_field(buffer, cls.TYPE_BYTES_RAW, data)
        elif isinstance(data, np.ndarray):
            cls._serialize_numpy(buffer, data)
        elif data is None:
            pass  # Skip None values
        else:
            # Fallback: convert to string representation
            cls._serialize_string(buffer, str(data))
        
        return bytes(buffer)
    
    @classmethod
    def deserialize(cls, data: bytes) -> Any:
        """
        Dynamically deserialize TLV format to Python data structures
        
        Args:
            data: TLV-encoded bytes
            
        Returns:
            Deserialized Python object
        """
        if not data:
            return {}
        
        # Check if this is a top-level dict (starts with version)
        if data[0] == cls.TYPE_VERSION:
            # Skip version, deserialize rest as dict
            offset = 1  # Skip type byte
            # Read version length using varint (consistent with _write_field)
            length, bytes_read = cls._read_varint(data, offset)
            offset += bytes_read + length
            
            # Rest should be a dict
            if offset < len(data):
                result, _ = cls._deserialize_value(data, offset)
                return result
            return {}
        else:
            # Direct value
            result, _ = cls._deserialize_value(data, 0)
            return result
    
    @classmethod
    def _serialize_dict(cls, buffer: bytearray, data: Dict[str, Any]) -> None:
        """Serialize dictionary with dynamic field detection"""
        dict_buffer = bytearray()
        
        # Write number of fields
        cls._write_varint(dict_buffer, len(data))
        
        for key, value in data.items():
            # Write field name
            key_bytes = key.encode('utf-8')
            cls._write_varint(dict_buffer, len(key_bytes))
            dict_buffer.extend(key_bytes)
            
            # Check if this is a known field with special handling
            if key in cls.KNOWN_FIELDS:
                field_code = cls.KNOWN_FIELDS[key]
                cls._serialize_known_field(dict_buffer, field_code, value, key)
            else:
                # Generic dynamic field - serialize based on type
                field_data = cls.serialize(value, field_name=key, _is_nested=True)
                cls._write_varint(dict_buffer, len(field_data))
                dict_buffer.extend(field_data)
        
        cls._write_field(buffer, cls.TYPE_DICT_ORDERED, bytes(dict_buffer))
    
    @classmethod
    def _serialize_known_field(cls, buffer: bytearray, field_code: int, value: Any, field_name: str) -> None:
        """
        Serialize known field with optimized format
        
        Special handling for complex structures like CEL snapshots
        """
        # All fields use generic serialization
        # The TLV functions return complete TLV blocks, not raw data
        # So we just use the generic path which properly nests the data
        field_data = cls.serialize(value, field_name=field_name, _is_nested=True)
        cls._write_varint(buffer, len(field_data))
        buffer.extend(field_data)
    
    @classmethod
    def _serialize_list(cls, buffer: bytearray, data: List[Any], type_code: int) -> None:
        """Serialize list or tuple"""
        list_buffer = bytearray()
        
        # Write number of elements
        cls._write_varint(list_buffer, len(data))
        
        for item in data:
            item_data = cls.serialize(item, _is_nested=True)
            cls._write_varint(list_buffer, len(item_data))
            list_buffer.extend(item_data)
        
        cls._write_field(buffer, type_code, bytes(list_buffer))
    
    @classmethod
    def _serialize_int(cls, buffer: bytearray, value: int) -> None:
        """Intelligently serialize integer based on size and sign"""
        # For non-negative values, prefer unsigned types first to avoid ambiguity
        if value >= 0:
            if value < 256:
                cls._write_field(buffer, cls.TYPE_UINT8, struct.pack('B', value))
            elif value < 65536:
                cls._write_field(buffer, cls.TYPE_UINT16, struct.pack('>H', value))
            elif value < 4294967296:
                cls._write_field(buffer, cls.TYPE_UINT32, struct.pack('>I', value))
            else:
                # Use varint for very large positive numbers
                varint_buffer = bytearray()
                cls._write_signed_varint(varint_buffer, value)
                cls._write_field(buffer, cls.TYPE_VARINT, bytes(varint_buffer))
        else:
            # For negative values, use signed types
            if -128 <= value:
                cls._write_field(buffer, cls.TYPE_INT8, struct.pack('b', value))
            elif -32768 <= value:
                cls._write_field(buffer, cls.TYPE_INT16, struct.pack('>h', value))
            elif -2147483648 <= value:
                cls._write_field(buffer, cls.TYPE_INT32, struct.pack('>i', value))
            else:
                # Use varint for very large negative numbers
                varint_buffer = bytearray()
                cls._write_signed_varint(varint_buffer, value)
                cls._write_field(buffer, cls.TYPE_VARINT, bytes(varint_buffer))
    
    @classmethod
    def _serialize_string(cls, buffer: bytearray, value: str) -> None:
        """Serialize string with intelligent encoding detection"""
        # Check if it's a hex string
        if len(value) % 2 == 0:
            try:
                bytes.fromhex(value)
                cls._write_field(buffer, cls.TYPE_HEX_STRING, value.encode('utf-8'))
                return
            except ValueError:
                pass  # Not a valid hex string, treat as regular UTF-8
        
        # UTF-8 string
        cls._write_field(buffer, cls.TYPE_UTF8, value.encode('utf-8'))
    
    @classmethod
    def _serialize_numpy(cls, buffer: bytearray, arr: np.ndarray) -> None:
        """Serialize numpy array with compression for large arrays"""
        if arr.dtype == np.int64 or arr.dtype == np.int32:
            # Use compression for integer arrays
            compressed = compress_int_array(arr.flatten())
            
            # Write shape first
            shape_data = bytearray()
            cls._write_varint(shape_data, len(arr.shape))
            for dim in arr.shape:
                cls._write_varint(shape_data, dim)
            
            full_data = bytes(shape_data) + compressed
            cls._write_field(buffer, cls.TYPE_NUMPY_COMPRESSED, full_data)
        else:
            # Float or other types - use raw bytes with shape
            shape_data = bytearray()
            cls._write_varint(shape_data, len(arr.shape))
            for dim in arr.shape:
                cls._write_varint(shape_data, dim)
            
            full_data = bytes(shape_data) + arr.tobytes()
            cls._write_field(buffer, cls.TYPE_NUMPY_FLOAT, full_data)
    
    @classmethod
    def _deserialize_value(cls, data: bytes, offset: int) -> Tuple[Any, int]:
        """
        Deserialize value at offset, return (value, new_offset)
        """
        if offset >= len(data):
            return None, offset
        
        # Need at least 1 byte for type code
        if offset + 1 > len(data):
            return None, offset
        
        type_code = data[offset]
        offset += 1
        
        # Read length using varint (consistent with _write_field_varint)
        length, bytes_read = cls._read_varint(data, offset)
        offset += bytes_read
        
        if offset + length > len(data):
            raise ValueError(f"Invalid TLV: length {length} exceeds data")
        
        value_data = data[offset:offset+length]
        offset += length
        
        # Deserialize based on type
        if type_code == cls.TYPE_VERSION:
            return int.from_bytes(value_data, 'big'), offset
        
        elif type_code == cls.TYPE_DICT_ORDERED or type_code == cls.TYPE_DICT_GENERIC:
            return cls._deserialize_dict(value_data), offset
        
        elif type_code == cls.TYPE_LIST:
            return cls._deserialize_list(value_data), offset
        
        elif type_code == cls.TYPE_TUPLE:
            items = cls._deserialize_list(value_data)
            return tuple(items), offset
        
        elif type_code == cls.TYPE_BOOL_TRUE:
            return True, offset
        
        elif type_code == cls.TYPE_BOOL_FALSE:
            return False, offset
        
        elif type_code == cls.TYPE_INT8:
            return struct.unpack('b', value_data)[0], offset
        
        elif type_code == cls.TYPE_INT16:
            return struct.unpack('>h', value_data)[0], offset
        
        elif type_code == cls.TYPE_INT32:
            return struct.unpack('>i', value_data)[0], offset
        
        elif type_code == cls.TYPE_INT64:
            return struct.unpack('>q', value_data)[0], offset
        
        elif type_code == cls.TYPE_UINT8:
            return struct.unpack('B', value_data)[0], offset
        
        elif type_code == cls.TYPE_UINT16:
            return struct.unpack('>H', value_data)[0], offset
        
        elif type_code == cls.TYPE_UINT32:
            return struct.unpack('>I', value_data)[0], offset
        
        elif type_code == cls.TYPE_UINT64:
            return struct.unpack('>Q', value_data)[0], offset
        
        elif type_code == cls.TYPE_VARINT:
            val, _ = cls._read_signed_varint(value_data, 0)
            return val, offset
        
        elif type_code == cls.TYPE_UTF8:
            return value_data.decode('utf-8'), offset
        
        elif type_code == cls.TYPE_HEX_STRING:
            return value_data.decode('utf-8'), offset
        
        elif type_code == cls.TYPE_BYTES_RAW:
            return value_data, offset
        
        elif type_code == cls.TYPE_NUMPY_COMPRESSED or type_code == cls.TYPE_NUMPY_FLOAT:
            return cls._deserialize_numpy(value_data, type_code), offset
        
        else:
            # Unknown type - return raw bytes
            return value_data, offset
    
    @classmethod
    def _deserialize_dict(cls, data: bytes) -> Dict[str, Any]:
        """Deserialize dictionary"""
        result = {}
        offset = 0
        
        # Read number of fields
        num_fields, bytes_read = cls._read_varint(data, offset)
        offset += bytes_read
        
        for _ in range(num_fields):
            # Read field name
            name_len, bytes_read = cls._read_varint(data, offset)
            offset += bytes_read
            
            field_name = data[offset:offset+name_len].decode('utf-8')
            offset += name_len
            
            # Read value length
            value_len, bytes_read = cls._read_varint(data, offset)
            offset += bytes_read
            
            # Deserialize value
            value_data = data[offset:offset+value_len]
            offset += value_len
            
            if value_len > 0:
                value, _ = cls._deserialize_value(value_data, 0)
                result[field_name] = value
        
        return result
    
    @classmethod
    def _deserialize_list(cls, data: bytes) -> List[Any]:
        """Deserialize list"""
        result = []
        offset = 0
        
        # Read number of elements
        num_elements, bytes_read = cls._read_varint(data, offset)
        offset += bytes_read
        
        for _ in range(num_elements):
            # Read element length
            elem_len, bytes_read = cls._read_varint(data, offset)
            offset += bytes_read
            
            # Deserialize element
            elem_data = data[offset:offset+elem_len]
            offset += elem_len
            
            if elem_len > 0:
                elem, _ = cls._deserialize_value(elem_data, 0)
                result.append(elem)
        
        return result
    
    @classmethod
    def _deserialize_numpy(cls, data: bytes, type_code: int) -> np.ndarray:
        """Deserialize numpy array"""
        offset = 0
        
        # Read shape
        num_dims, bytes_read = cls._read_varint(data, offset)
        offset += bytes_read
        
        shape = []
        for _ in range(num_dims):
            dim, bytes_read = cls._read_varint(data, offset)
            offset += bytes_read
            shape.append(dim)
        
        # Read array data
        if type_code == cls.TYPE_NUMPY_COMPRESSED:
            flat = decompress_int_array(data[offset:], np.prod(shape))
            return flat.reshape(shape)
        else:
            # Float array
            remaining = data[offset:]
            flat = np.frombuffer(remaining, dtype=np.float64)
            return flat.reshape(shape)
    
    @classmethod
    def _write_field(cls, buffer: bytearray, type_code: int, value: bytes) -> None:
        """Write TLV field with varint length encoding"""
        buffer.append(type_code)
        cls._write_varint(buffer, len(value))  # Use varint for consistent encoding
        buffer.extend(value)
    
    @classmethod
    def _write_varint(cls, buffer: bytearray, value: int) -> None:
        """Write unsigned varint (LEB128)"""
        while value >= 0x80:
            buffer.append((value & 0x7F) | 0x80)
            value >>= 7
        buffer.append(value & 0x7F)
    
    @classmethod
    def _read_varint(cls, data: bytes, offset: int) -> Tuple[int, int]:
        """Read unsigned varint, return (value, bytes_read)"""
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
    
    @classmethod
    def _write_signed_varint(cls, buffer: bytearray, value: int) -> None:
        """Write signed varint using zigzag encoding (works for arbitrary precision integers)"""
        # Zigzag encoding: positive n -> 2n, negative n -> 2|n|-1
        # This works for arbitrary precision Python integers
        if value >= 0:
            zigzag = value << 1
        else:
            zigzag = ((-value) << 1) - 1
        cls._write_varint(buffer, zigzag)
    
    @classmethod
    def _read_signed_varint(cls, data: bytes, offset: int) -> Tuple[int, int]:
        """Read signed varint with zigzag decoding (works for arbitrary precision integers)"""
        zigzag, bytes_read = cls._read_varint(data, offset)
        # Decode: even -> positive (n/2), odd -> negative (-(n+1)/2)
        if zigzag & 1:
            value = -((zigzag + 1) >> 1)
        else:
            value = zigzag >> 1
        return value, bytes_read


# Convenience functions
def serialize_dynamic(data: Any) -> bytes:
    """Serialize data using dynamic TLV format"""
    return DynamicTLV.serialize(data)


def deserialize_dynamic(data: bytes) -> Any:
    """Deserialize TLV data to Python objects"""
    return DynamicTLV.deserialize(data)
