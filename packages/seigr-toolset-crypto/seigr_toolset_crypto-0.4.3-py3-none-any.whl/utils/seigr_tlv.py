"""
Seigr TLV - Production-Ready Dynamic Serialization
Clean, fast, zero legacy baggage

Philosophy: Let Python types drive serialization. No field registries, no hardcoded mappings.
Just pure type-driven binary encoding that works for ANY data structure.
"""

import struct
import numpy as np
from typing import Any, Tuple


class SeigrTLV:
    """Production TLV serializer with complete dynamic type handling"""
    
    # Type codes (clean, simple)
    VERSION = 0x01
    INT = 0x10
    STRING = 0x20
    BYTES = 0x30
    BOOL_TRUE = 0x41
    BOOL_FALSE = 0x42
    LIST = 0x50
    DICT = 0x60
    NUMPY = 0x70
    NULL = 0xFF
    
    @classmethod
    def serialize(cls, obj: Any) -> bytes:
        """
        Serialize any Python object to binary TLV format
        
        Works with: dict, list, int, str, bytes, bool, None, numpy arrays
        """
        buf = bytearray()
        
        # Write version header for top-level dicts
        if isinstance(obj, dict):
            cls._write(buf, cls.VERSION, b'\x01')
        
        cls._encode(buf, obj)
        return bytes(buf)
    
    @classmethod
    def deserialize(cls, data: bytes) -> Any:
        """Deserialize TLV binary to Python objects"""
        offset = 0
        
        # Skip version if present
        if data and data[0] == cls.VERSION:
            offset += 1
            length, offset = cls._read_varint(data, offset)
            offset += length  # Skip version value
        
        if offset >= len(data):
            return {}
        
        obj, _ = cls._decode(data, offset)
        return obj
    
    @classmethod
    def _encode(cls, buf: bytearray, obj: Any) -> None:
        """Encode object into buffer"""
        
        if obj is None:
            cls._write(buf, cls.NULL, b'')
        
        elif isinstance(obj, bool):
            # Bool before int (bool is subclass of int in Python)
            type_code = cls.BOOL_TRUE if obj else cls.BOOL_FALSE
            cls._write(buf, type_code, b'')
        
        elif isinstance(obj, int):
            # Smart integer encoding based on size
            if -128 <= obj <= 127:
                cls._write(buf, cls.INT, struct.pack('b', obj))
            elif -32768 <= obj <= 32767:
                cls._write(buf, cls.INT, struct.pack('>h', obj))
            elif -2147483648 <= obj <= 2147483647:
                cls._write(buf, cls.INT, struct.pack('>i', obj))
            else:
                cls._write(buf, cls.INT, struct.pack('>q', obj))
        
        elif isinstance(obj, str):
            cls._write(buf, cls.STRING, obj.encode('utf-8'))
        
        elif isinstance(obj, bytes):
            cls._write(buf, cls.BYTES, obj)
        
        elif isinstance(obj, np.ndarray):
            # Numpy: [shape_count][dims...][dtype][data]
            shape_buf = bytearray()
            cls._write_varint(shape_buf, len(obj.shape))
            for dim in obj.shape:
                cls._write_varint(shape_buf, dim)
            
            # Dtype detection using np.issubdtype for proper classification
            if np.issubdtype(obj.dtype, np.bool_):
                dtype_code = 0x01     # Boolean
            elif np.issubdtype(obj.dtype, np.signedinteger):
                dtype_code = 0x02     # Signed integer
            elif np.issubdtype(obj.dtype, np.unsignedinteger):
                dtype_code = 0x03     # Unsigned integer
            elif np.issubdtype(obj.dtype, np.floating):
                dtype_code = 0x04     # Float
            elif np.issubdtype(obj.dtype, np.complexfloating):
                dtype_code = 0x05     # Complex
            else:
                raise TypeError(f"Unsupported numpy dtype: {obj.dtype}")
            shape_buf.append(dtype_code)
            
            # Data
            shape_buf.extend(obj.tobytes())
            cls._write(buf, cls.NUMPY, bytes(shape_buf))
        
        elif isinstance(obj, list):
            # List: [count][item1][item2]...
            list_buf = bytearray()
            cls._write_varint(list_buf, len(obj))
            for item in obj:
                item_buf = bytearray()
                cls._encode(item_buf, item)
                cls._write_varint(list_buf, len(item_buf))
                list_buf.extend(item_buf)
            cls._write(buf, cls.LIST, bytes(list_buf))
        
        elif isinstance(obj, dict):
            # Dict: [count][key1_len][key1][val1_len][val1]...
            dict_buf = bytearray()
            cls._write_varint(dict_buf, len(obj))
            
            for key, value in obj.items():
                # Key (always string)
                key_bytes = str(key).encode('utf-8')
                cls._write_varint(dict_buf, len(key_bytes))
                dict_buf.extend(key_bytes)
                
                # Value (recursive)
                value_buf = bytearray()
                cls._encode(value_buf, value)
                cls._write_varint(dict_buf, len(value_buf))
                dict_buf.extend(value_buf)
            
            cls._write(buf, cls.DICT, bytes(dict_buf))
        
        else:
            # Raise clear error for unsupported types
            raise TypeError(f"Cannot serialize object of type {type(obj).__name__}: {repr(obj)}")
    
    @classmethod
    def _decode(cls, data: bytes, offset: int) -> Tuple[Any, int]:
        """Decode object from data at offset, return (object, new_offset)"""
        
        if offset >= len(data):
            return None, offset
        
        type_code = data[offset]
        offset += 1
        
        # Read length
        length, offset = cls._read_varint(data, offset)
        
        if offset + length > len(data):
            raise ValueError(f"TLV length {length} exceeds data")
        
        value_data = data[offset:offset + length]
        offset += length
        
        # Decode based on type
        if type_code == cls.NULL:
            return None, offset
        
        elif type_code == cls.BOOL_TRUE:
            return True, offset
        
        elif type_code == cls.BOOL_FALSE:
            return False, offset
        
        elif type_code == cls.INT:
            if length == 1:
                return struct.unpack('b', value_data)[0], offset
            elif length == 2:
                return struct.unpack('>h', value_data)[0], offset
            elif length == 4:
                return struct.unpack('>i', value_data)[0], offset
            elif length == 8:
                return struct.unpack('>q', value_data)[0], offset
            else:
                # Unsupported integer length - raise error
                raise ValueError(f"Unsupported integer length {length} for TLV type code {type_code:#x}")
        
        elif type_code == cls.STRING:
            return value_data.decode('utf-8'), offset
        
        elif type_code == cls.BYTES:
            return value_data, offset
        
        elif type_code == cls.NUMPY:
            # Decode numpy array
            voffset = 0
            num_dims, voffset = cls._read_varint(value_data, voffset)
            
            shape = []
            for _ in range(num_dims):
                dim, voffset = cls._read_varint(value_data, voffset)
                shape.append(dim)
            
            dtype_code = value_data[voffset]
            voffset += 1
            
            # Dtype mapping matching serialization logic
            dtype_map = {
                0x01: np.bool_,           # Boolean
                0x02: np.int64,           # Signed integer (use int64 for compatibility)
                0x03: np.uint64,          # Unsigned integer
                0x04: np.float64,         # Float
                0x05: np.complex128,      # Complex
            }
            if dtype_code not in dtype_map:
                raise ValueError(f"Unknown numpy dtype code: {dtype_code}")
            dtype = dtype_map[dtype_code]
            arr_data = value_data[voffset:]
            arr = np.frombuffer(arr_data, dtype=dtype)
            
            if shape:
                arr = arr.reshape(shape)
            
            return arr, offset
        
        elif type_code == cls.LIST:
            # Decode list
            items = []
            voffset = 0
            count, voffset = cls._read_varint(value_data, voffset)
            
            for _ in range(count):
                item_len, voffset = cls._read_varint(value_data, voffset)
                item_data = value_data[voffset:voffset + item_len]
                voffset += item_len
                
                item, _ = cls._decode(item_data, 0)
                items.append(item)
            
            return items, offset
        
        elif type_code == cls.DICT:
            # Decode dictionary
            result = {}
            voffset = 0
            count, voffset = cls._read_varint(value_data, voffset)
            
            for _ in range(count):
                # Read key
                key_len, voffset = cls._read_varint(value_data, voffset)
                key = value_data[voffset:voffset + key_len].decode('utf-8')
                voffset += key_len
                
                # Read value
                val_len, voffset = cls._read_varint(value_data, voffset)
                val_data = value_data[voffset:voffset + val_len]
                voffset += val_len
                
                value, _ = cls._decode(val_data, 0)
                result[key] = value
            
            return result, offset
        
        else:
            # Unknown type - return raw bytes for forward compatibility
            return data[offset:offset+length], offset + length
    
    @classmethod
    def _write(cls, buf: bytearray, type_code: int, value: bytes) -> None:
        """Write TLV field"""
        buf.append(type_code)
        cls._write_varint(buf, len(value))
        buf.extend(value)
    
    @classmethod
    def _write_varint(cls, buf: bytearray, value: int) -> None:
        """Write variable-length integer (LEB128)"""
        while value >= 0x80:
            buf.append((value & 0x7F) | 0x80)
            value >>= 7
        buf.append(value & 0x7F)
    
    @classmethod
    def _read_varint(cls, data: bytes, offset: int) -> Tuple[int, int]:
        """Read varint, return (value, new_offset)"""
        result = 0
        shift = 0
        
        while offset < len(data):
            byte = data[offset]
            offset += 1
            
            result |= (byte & 0x7F) << shift
            if not (byte & 0x80):
                break
            shift += 7
        
        return result, offset


# Production API
def encode(obj: Any) -> bytes:
    """Encode Python object to Seigr TLV binary format"""
    return SeigrTLV.serialize(obj)


def decode(data: bytes) -> Any:
    """Decode Seigr TLV binary to Python object"""
    return SeigrTLV.deserialize(data)
