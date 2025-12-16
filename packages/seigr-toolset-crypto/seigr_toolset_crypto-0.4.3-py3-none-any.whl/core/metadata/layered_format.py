"""
Layered Metadata Format v0.3.1

Replaces the fixed 486KB metadata system with adaptive, scalable metadata
that grows with file size and security requirements.
"""

import struct
import hashlib
import time
from typing import Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum
from core.profiles.security_profiles import SecurityProfile

class DecoyStrategy(Enum):
    """Decoy generation strategies based on file size"""
    ALGORITHMIC = "algorithmic"    # <1MB: Generate on-demand from seeds
    DIFFERENTIAL = "differential"  # 1-100MB: Store differences from base CEL
    SELECTIVE = "selective"        # >100MB: Decoy only critical sections

# SecurityProfile imported from core.profiles.security_profiles

@dataclass
class CoreMetadata:
    """Core layer: Fixed 8KB of essential decryption parameters"""
    version: str = "0.3.1"
    format_type: str = "layered"
    original_file_size: int = 0  # Changed from file_size for consistency
    chunk_size: int = 1048576  # 1MB default
    chunk_count: int = 0
    final_chunk_size: int = 0
    security_profile: str = SecurityProfile.DOCUMENT.value
    cel_seed_hash: bytes = b''
    phe_path_count: int = 7
    phe_difficulty_level: int = 1
    pcf_morph_interval: int = 100
    decoy_strategy: str = DecoyStrategy.ALGORITHMIC.value
    decoy_count: int = 2
    creation_timestamp: float = 0.0  # Changed from timestamp for clarity
    
    def __post_init__(self):
        if self.creation_timestamp == 0.0:
            self.creation_timestamp = time.time()
    
    def serialize(self) -> bytes:
        """Serialize core metadata to exactly 8KB using self-sovereign binary format"""
        # Fixed-size binary structure for optimal efficiency
        
        # Version and format (16 bytes)
        version_bytes = self.version.encode('utf-8')[:8].ljust(8, b'\x00')
        format_bytes = self.format_type.encode('utf-8')[:8].ljust(8, b'\x00')
        
        # File parameters (20 bytes) 
        file_params = struct.pack('!QIII', 
                                self.original_file_size,
                                self.chunk_size,
                                self.chunk_count,
                                self.final_chunk_size)
        
        # Security profile (16 bytes)
        profile_bytes = self.security_profile.encode('utf-8')[:12].ljust(12, b'\x00')
        security_params = struct.pack('!HH', self.phe_path_count, self.phe_difficulty_level)
        
        # CEL seed hash (32 bytes - fixed size)
        cel_seed = self.cel_seed_hash[:32].ljust(32, b'\x00')
        
        # Decoy parameters (16 bytes)
        decoy_strategy_bytes = self.decoy_strategy.encode('utf-8')[:8].ljust(8, b'\x00')
        decoy_params = struct.pack('!IId', 
                                 self.decoy_count,
                                 self.pcf_morph_interval,
                                 self.creation_timestamp)
        
        # Pack everything together (16 + 20 + 16 + 32 + 16 = 100 bytes so far)
        core_data = (version_bytes + format_bytes + file_params + 
                    profile_bytes + security_params + cel_seed + 
                    decoy_strategy_bytes + decoy_params)
        
        # Variable padding based on file size for reasonable overhead
        base_size = len(core_data)  # ~100 bytes of essential data
        
        if self.original_file_size <= 1024:  # 1KB files - ultra-compact format
            # For tiny files, use minimal essential data only
            # Return just version, file_size, chunk info, seed hash, and strategy (60 bytes)
            minimal_data = (
                self.version.encode('utf-8')[:8].ljust(8, b'\x00') +  # 8 bytes
                struct.pack('!QII', self.original_file_size, self.chunk_size, self.chunk_count) +  # 16 bytes
                self.cel_seed_hash[:32].ljust(32, b'\x00') +  # 32 bytes
                self.decoy_strategy.encode('utf-8')[:8].ljust(8, b'\x00')  # 8 bytes
            )  # Total: 64 bytes
            return minimal_data
        elif self.original_file_size <= 10 * 1024:  # 10KB files
            target_size = max(base_size, 400)  # ~4% overhead
        elif self.original_file_size <= 100 * 1024:  # 100KB files
            target_size = max(base_size, 1800)  # ~1.8% overhead
        elif self.original_file_size <= 1024 * 1024:  # 1MB files
            target_size = max(base_size, 8000)  # ~0.8% overhead
        else:  # Large files can afford standard 8KB
            target_size = 8192
        
        if base_size > target_size:
            # Essential data is larger than target - use base size
            return core_data
        
        # Use cryptographic padding pattern
        padding_needed = target_size - base_size
        padding_pattern = hashlib.sha256(b'STC_CORE_PADDING_v0.3.1').digest()
        padding = (padding_pattern * ((padding_needed // 32) + 1))[:padding_needed]
        
        return core_data + padding
    
    @classmethod  
    def deserialize(cls, data: bytes) -> 'CoreMetadata':
        """Deserialize core metadata from self-sovereign binary format (variable size)"""
        
        if len(data) == 64:  # Ultra-compact format for tiny files
            # Minimal format: version(8) + file_size(8) + chunk_size(4) + chunk_count(4) + seed(32) + strategy(8)
            version = data[0:8].rstrip(b'\x00').decode('utf-8')
            original_file_size, chunk_size, chunk_count = struct.unpack('!QII', data[8:24])
            cel_seed_hash = data[24:56]
            decoy_strategy = data[56:64].rstrip(b'\x00').decode('utf-8')
            
            # Use defaults for missing fields
            return cls(
                version=version,
                format_type="seigr_cel",  # Default
                original_file_size=original_file_size,
                chunk_size=chunk_size,
                chunk_count=chunk_count,
                final_chunk_size=original_file_size % chunk_size or chunk_size,
                security_profile="document",  # Default
                cel_seed_hash=cel_seed_hash,
                phe_path_count=7,  # Default
                phe_difficulty_level=1,  # Default
                pcf_morph_interval=100,  # Default
                decoy_strategy=decoy_strategy,
                decoy_count=2,  # Default
                creation_timestamp=time.time()
            )
            
        elif len(data) < 108:  # Minimum size for full format
            raise ValueError(f"Invalid core metadata size: {len(data)} bytes")
        
        # Full format extraction
        # Extract fixed-size fields from binary format
        version = data[0:8].rstrip(b'\x00').decode('utf-8')
        format_type = data[8:16].rstrip(b'\x00').decode('utf-8')
        
        # File parameters
        file_params = struct.unpack('!QIII', data[16:36])
        original_file_size, chunk_size, chunk_count, final_chunk_size = file_params
        
        # Security profile  
        security_profile = data[36:48].rstrip(b'\x00').decode('utf-8')
        phe_path_count, phe_difficulty_level = struct.unpack('!HH', data[48:52])
        
        # CEL seed hash
        cel_seed_hash = data[52:84]
        
        # Decoy parameters
        decoy_strategy = data[84:92].rstrip(b'\x00').decode('utf-8')
        decoy_count, pcf_morph_interval, creation_timestamp = struct.unpack('!IId', data[92:108])
        
        return cls(
            version=version,
            format_type=format_type,
            original_file_size=original_file_size,
            chunk_size=chunk_size,
            chunk_count=chunk_count,
            final_chunk_size=final_chunk_size,
            security_profile=security_profile,
            cel_seed_hash=cel_seed_hash,
            phe_path_count=phe_path_count,
            phe_difficulty_level=phe_difficulty_level,
            pcf_morph_interval=pcf_morph_interval,
            decoy_strategy=decoy_strategy,
            decoy_count=decoy_count,
            creation_timestamp=creation_timestamp
        )


@dataclass
class SecurityMetadata:
    """Security layer: Variable 2-50KB for decoy system"""
    decoy_strategy: str = DecoyStrategy.ALGORITHMIC.value
    decoy_count: int = 3
    decoy_metadata: bytes = b''  # Actual decoy data/parameters
    adaptive_difficulty: bool = True
    timing_randomization: bool = False
    extra_security_data: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.extra_security_data is None:
            self.extra_security_data = {}
    
    def _serialize_dict_to_binary(self, data: Dict[str, Any]) -> bytes:
        """Serialize dictionary to self-sovereign binary format"""
        if not data:
            return b''
        
        binary_data = bytearray()
        
        # Serialize each key-value pair
        for key, value in data.items():
            # Value (type-tagged) - check type FIRST before writing key
            if isinstance(value, bool):
                # Key (length-prefixed string)
                key_bytes = key.encode('utf-8')
                binary_data.extend(struct.pack('<H', len(key_bytes)))
                binary_data.extend(key_bytes)
                binary_data.extend(b'\x01')  # Boolean type
                binary_data.extend(struct.pack('<?', value))
            elif isinstance(value, int):
                # Key (length-prefixed string)
                key_bytes = key.encode('utf-8')
                binary_data.extend(struct.pack('<H', len(key_bytes)))
                binary_data.extend(key_bytes)
                binary_data.extend(b'\x02')  # Integer type
                binary_data.extend(struct.pack('<q', value))  # 64-bit signed
            elif isinstance(value, float):
                # Key (length-prefixed string)
                key_bytes = key.encode('utf-8')
                binary_data.extend(struct.pack('<H', len(key_bytes)))
                binary_data.extend(key_bytes)
                binary_data.extend(b'\x03')  # Float type
                binary_data.extend(struct.pack('<d', value))  # 64-bit double
            elif isinstance(value, str):
                # Key (length-prefixed string)
                key_bytes = key.encode('utf-8')
                binary_data.extend(struct.pack('<H', len(key_bytes)))
                binary_data.extend(key_bytes)
                binary_data.extend(b'\x04')  # String type
                value_bytes = value.encode('utf-8')
                binary_data.extend(struct.pack('<I', len(value_bytes)))
                binary_data.extend(value_bytes)
            else:
                # Skip unsupported types for self-sovereignty
                continue
                
        return bytes(binary_data)
    
    @staticmethod
    def _deserialize_binary_to_dict(data: bytes) -> Dict[str, Any]:
        """Deserialize binary data to dictionary"""
        if not data:
            return {}
        
        result = {}
        offset = 0
        
        while offset < len(data):
            # Read key
            key_len = struct.unpack('<H', data[offset:offset+2])[0]
            offset += 2
            key = data[offset:offset+key_len].decode('utf-8')
            offset += key_len
            
            # Read value type and data
            value_type = data[offset:offset+1]
            offset += 1
            
            if value_type == b'\x01':  # Boolean
                value = struct.unpack('<?', data[offset:offset+1])[0]
                offset += 1
            elif value_type == b'\x02':  # Integer
                value = struct.unpack('<q', data[offset:offset+8])[0]
                offset += 8
            elif value_type == b'\x03':  # Float
                value = struct.unpack('<d', data[offset:offset+8])[0]
                offset += 8
            elif value_type == b'\x04':  # String
                str_len = struct.unpack('<I', data[offset:offset+4])[0]
                offset += 4
                value = data[offset:offset+str_len].decode('utf-8')
                offset += str_len
            else:
                break  # Unknown type, stop parsing
                
            result[key] = value
            
        return result
    
    def serialize(self) -> bytes:
        """Serialize security metadata using self-sovereign binary format"""
        
        # Check for ultra-compact mode (no decoy metadata and empty extra data)
        if not self.decoy_metadata and not self.extra_security_data:
            # Ultra-compact format for tiny files: 
            # Magic(4) + strategy(8) + count(4) = 16 bytes total
            data = bytearray(b'STCS')
            strategy_bytes = self.decoy_strategy.encode('ascii')[:8].ljust(8, b'\x00')
            data.extend(strategy_bytes)
            data.extend(struct.pack('<I', self.decoy_count))
            return bytes(data)
        
        # Full format for larger files
        # Magic number for security metadata: STCS (Seigr Toolset Crypto Security)
        data = bytearray(b'STCS')
        
        # Fixed-size fields for consistency
        strategy_bytes = self.decoy_strategy.encode('ascii')[:16].ljust(16, b'\x00')
        data.extend(strategy_bytes)
        
        # Decoy count (4 bytes)
        data.extend(struct.pack('<I', self.decoy_count))
        
        # Decoy metadata length + data (variable)
        decoy_meta_len = len(self.decoy_metadata) if self.decoy_metadata else 0
        data.extend(struct.pack('<I', decoy_meta_len))
        if self.decoy_metadata:
            data.extend(self.decoy_metadata)
        
        # Adaptive difficulty (4 bytes as float)
        data.extend(struct.pack('<f', self.adaptive_difficulty))
        
        # Timing randomization (1 byte boolean)
        data.extend(struct.pack('<?', self.timing_randomization))
        
        # Extra security data as self-sovereign binary format (length-prefixed)
        extra_binary = self._serialize_dict_to_binary(self.extra_security_data)
        data.extend(struct.pack('<I', len(extra_binary)))
        data.extend(extra_binary)
        
        return bytes(data)
    
    @classmethod
    def deserialize(cls, data: bytes) -> 'SecurityMetadata':
        """Deserialize security metadata from self-sovereign binary format"""
        if len(data) < 4 or data[:4] != b'STCS':
            raise ValueError("Invalid SecurityMetadata: missing STCS magic number")
        
        # Check for ultra-compact format (16 bytes total)  
        if len(data) == 16:
            # Ultra-compact: Magic(4) + strategy(8) + count(4)
            strategy_bytes = data[4:12]
            decoy_strategy = strategy_bytes.rstrip(b'\x00').decode('ascii')
            decoy_count = struct.unpack('<I', data[12:16])[0]
            
            return cls(
                decoy_strategy=decoy_strategy,
                decoy_count=decoy_count,
                decoy_metadata=b'',
                adaptive_difficulty=True,  # Default
                timing_randomization=False,  # Default
                extra_security_data={}
            )
        
        # Full format extraction
        offset = 4
        
        # Extract strategy (16 bytes)
        strategy_bytes = data[offset:offset+16]
        decoy_strategy = strategy_bytes.rstrip(b'\x00').decode('ascii')
        offset += 16
        
        # Extract decoy count (4 bytes)
        decoy_count = struct.unpack('<I', data[offset:offset+4])[0]
        offset += 4
        
        # Extract decoy metadata
        decoy_meta_len = struct.unpack('<I', data[offset:offset+4])[0]
        offset += 4
        decoy_metadata = data[offset:offset+decoy_meta_len] if decoy_meta_len > 0 else b''
        offset += decoy_meta_len
        
        # Extract adaptive difficulty (4 bytes float)
        adaptive_difficulty = struct.unpack('<f', data[offset:offset+4])[0]
        offset += 4
        
        # Extract timing randomization (1 byte boolean)
        timing_randomization = struct.unpack('<?', data[offset:offset+1])[0]
        offset += 1
        
        # Extract extra security data
        extra_len = struct.unpack('<I', data[offset:offset+4])[0]
        offset += 4
        extra_binary = data[offset:offset+extra_len]
        extra_security_data = SecurityMetadata._deserialize_binary_to_dict(extra_binary)
        
        return cls(
            decoy_strategy=decoy_strategy,
            decoy_count=decoy_count,
            decoy_metadata=decoy_metadata,
            adaptive_difficulty=adaptive_difficulty,
            timing_randomization=timing_randomization,
            extra_security_data=extra_security_data
        )

@dataclass
class ExtensionMetadata:
    """Extension layer: Future-proof hooks for v1.x features"""
    plugin_hooks: Dict[str, Any] = None
    reserved_space: bytes = None
    compatibility_flags: int = 0
    future_extensions: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.plugin_hooks is None:
            self.plugin_hooks = {}
        if self.reserved_space is None:
            self.reserved_space = b'\x00' * 200  # 200 bytes reserved to keep total under 1KB
        if self.future_extensions is None:
            self.future_extensions = {}
    
    def _serialize_dict_to_binary(self, data: Dict[str, Any]) -> bytes:
        """Serialize dictionary to self-sovereign binary format"""
        if not data:
            return b''
        
        binary_data = bytearray()
        
        # Serialize each key-value pair
        for key, value in data.items():
            # Check type FIRST, then write key only if type is supported
            if isinstance(value, bool):
                # Key (length-prefixed string)
                key_bytes = key.encode('utf-8')
                binary_data.extend(struct.pack('<H', len(key_bytes)))
                binary_data.extend(key_bytes)
                binary_data.extend(b'\x01')  # Boolean type
                binary_data.extend(struct.pack('<?', value))
            elif isinstance(value, int):
                # Key (length-prefixed string)
                key_bytes = key.encode('utf-8')
                binary_data.extend(struct.pack('<H', len(key_bytes)))
                binary_data.extend(key_bytes)
                binary_data.extend(b'\x02')  # Integer type
                binary_data.extend(struct.pack('<q', value))  # 64-bit signed
            elif isinstance(value, float):
                # Key (length-prefixed string)
                key_bytes = key.encode('utf-8')
                binary_data.extend(struct.pack('<H', len(key_bytes)))
                binary_data.extend(key_bytes)
                binary_data.extend(b'\x03')  # Float type
                binary_data.extend(struct.pack('<d', value))  # 64-bit double
            elif isinstance(value, str):
                # Key (length-prefixed string)
                key_bytes = key.encode('utf-8')
                binary_data.extend(struct.pack('<H', len(key_bytes)))
                binary_data.extend(key_bytes)
                binary_data.extend(b'\x04')  # String type
                value_bytes = value.encode('utf-8')
                binary_data.extend(struct.pack('<I', len(value_bytes)))
                binary_data.extend(value_bytes)
            elif isinstance(value, dict):
                # Key (length-prefixed string)
                key_bytes = key.encode('utf-8')
                binary_data.extend(struct.pack('<H', len(key_bytes)))
                binary_data.extend(key_bytes)
                binary_data.extend(b'\x05')  # Dictionary type
                nested_data = self._serialize_dict_to_binary(value)
                binary_data.extend(struct.pack('<I', len(nested_data)))
                binary_data.extend(nested_data)
            elif isinstance(value, list):
                # Key (length-prefixed string)
                key_bytes = key.encode('utf-8')
                binary_data.extend(struct.pack('<H', len(key_bytes)))
                binary_data.extend(key_bytes)
                binary_data.extend(b'\x06')  # List type
                list_data = bytearray()
                list_data.extend(struct.pack('<I', len(value)))  # List length
                for item in value:
                    if isinstance(item, bool):
                        list_data.extend(b'\x01')
                        list_data.extend(struct.pack('<?', item))
                    elif isinstance(item, int):
                        list_data.extend(b'\x02')
                        list_data.extend(struct.pack('<q', item))
                    elif isinstance(item, float):
                        list_data.extend(b'\x03')
                        list_data.extend(struct.pack('<d', item))
                    elif isinstance(item, str):
                        list_data.extend(b'\x04')
                        item_bytes = item.encode('utf-8')
                        list_data.extend(struct.pack('<I', len(item_bytes)))
                        list_data.extend(item_bytes)
                binary_data.extend(struct.pack('<I', len(list_data)))
                binary_data.extend(list_data)
            else:
                # Skip unsupported types for self-sovereignty
                continue
                
        return bytes(binary_data)
    
    @staticmethod
    def _deserialize_binary_to_dict(data: bytes) -> Dict[str, Any]:
        """Deserialize binary data to dictionary"""
        if not data:
            return {}
        
        result = {}
        offset = 0
        
        while offset < len(data):
            # Read key
            key_len = struct.unpack('<H', data[offset:offset+2])[0]
            offset += 2
            key = data[offset:offset+key_len].decode('utf-8')
            offset += key_len
            
            # Read value type and data
            value_type = data[offset:offset+1]
            offset += 1
            
            if value_type == b'':  # Boolean
                value = struct.unpack('<?', data[offset:offset+1])[0]
                offset += 1
            elif value_type == b'':  # Integer
                value = struct.unpack('<q', data[offset:offset+8])[0]
                offset += 8
            elif value_type == b'':  # Float
                value = struct.unpack('<d', data[offset:offset+8])[0]
                offset += 8
            elif value_type == b'':  # String
                str_len = struct.unpack('<I', data[offset:offset+4])[0]
                offset += 4
                value = data[offset:offset+str_len].decode('utf-8')
                offset += str_len
            elif value_type == b'':  # Dictionary
                dict_len = struct.unpack('<I', data[offset:offset+4])[0]
                offset += 4
                dict_data = data[offset:offset+dict_len]
                value = ExtensionMetadata._deserialize_binary_to_dict(dict_data)
                offset += dict_len
            elif value_type == b'':  # List
                list_data_len = struct.unpack('<I', data[offset:offset+4])[0]
                offset += 4
                list_data = data[offset:offset+list_data_len]
                offset += list_data_len
                
                # Parse list items
                value = []
                list_offset = 0
                list_len = struct.unpack('<I', list_data[list_offset:list_offset+4])[0]
                list_offset += 4
                
                for _ in range(list_len):
                    item_type = list_data[list_offset:list_offset+1]
                    list_offset += 1
                    
                    if item_type == b'':  # Boolean
                        item = struct.unpack('<?', list_data[list_offset:list_offset+1])[0]
                        list_offset += 1
                    elif item_type == b'':  # Integer
                        item = struct.unpack('<q', list_data[list_offset:list_offset+8])[0]
                        list_offset += 8
                    elif item_type == b'':  # Float
                        item = struct.unpack('<d', list_data[list_offset:list_offset+8])[0]
                        list_offset += 8
                    elif item_type == b'':  # String
                        item_str_len = struct.unpack('<I', list_data[list_offset:list_offset+4])[0]
                        list_offset += 4
                        item = list_data[list_offset:list_offset+item_str_len].decode('utf-8')
                        list_offset += item_str_len
                    else:
                        break
                    value.append(item)
            else:
                break  # Unknown type, stop parsing
                
            result[key] = value
            
        return result
    
    def serialize(self) -> bytes:
        """Serialize extension metadata using self-sovereign binary format"""
        
        # Check for ultra-compact mode (no reserved space, empty hooks and extensions)
        if (not self.reserved_space and 
            not self.plugin_hooks and 
            not self.future_extensions and 
            self.compatibility_flags == 0):
            # Ultra-compact format: Just magic number (4 bytes)
            return b'STCE'
        
        # Full format
        # Magic number for extension metadata: STCE (Seigr Toolset Crypto Extension)
        data = bytearray(b'STCE')
        
        # Compatibility flags (4 bytes)
        data.extend(struct.pack('<I', self.compatibility_flags))
        
        # Reserved space (variable size based on original allocation)
        reserved_len = len(self.reserved_space)
        data.extend(struct.pack('<I', reserved_len))  # Store the size
        data.extend(self.reserved_space)
        
        # Plugin hooks as self-sovereign binary format (length-prefixed)
        hooks_binary = self._serialize_dict_to_binary(self.plugin_hooks)
        data.extend(struct.pack('<I', len(hooks_binary)))
        data.extend(hooks_binary)
        
        # Future extensions as self-sovereign binary format (length-prefixed)
        ext_binary = self._serialize_dict_to_binary(self.future_extensions)
        data.extend(struct.pack('<I', len(ext_binary)))
        data.extend(ext_binary)
        
        return bytes(data)
    
    @classmethod
    def deserialize(cls, data: bytes) -> 'ExtensionMetadata':
        """Deserialize extension metadata from self-sovereign binary format"""
        if len(data) < 4 or data[:4] != b'STCE':
            raise ValueError("Invalid ExtensionMetadata: missing STCE magic number")
        
        # Check for ultra-compact format (4 bytes total)
        if len(data) == 4:
            return cls(
                plugin_hooks={},
                reserved_space=b'',
                compatibility_flags=0,
                future_extensions={}
            )
        
        offset = 4
        
        # Extract compatibility flags (4 bytes)
        compatibility_flags = struct.unpack('<I', data[offset:offset+4])[0]
        offset += 4
        
        # Extract reserved space (variable size)
        reserved_len = struct.unpack('<I', data[offset:offset+4])[0]
        offset += 4
        reserved_space = data[offset:offset+reserved_len]
        offset += reserved_len
        
        # Extract plugin hooks
        hooks_len = struct.unpack('<I', data[offset:offset+4])[0]
        offset += 4
        hooks_binary = data[offset:offset+hooks_len]
        plugin_hooks = ExtensionMetadata._deserialize_binary_to_dict(hooks_binary)
        offset += hooks_len
        
        # Extract future extensions
        ext_len = struct.unpack('<I', data[offset:offset+4])[0]
        offset += 4
        ext_binary = data[offset:offset+ext_len]
        future_extensions = ExtensionMetadata._deserialize_binary_to_dict(ext_binary)
        
        return cls(
            plugin_hooks=plugin_hooks,
            reserved_space=reserved_space,
            compatibility_flags=compatibility_flags,
            future_extensions=future_extensions
        )

class LayeredMetadata:
    """Complete layered metadata system for v0.3.1"""
    
    def __init__(self, core: CoreMetadata, security: SecurityMetadata, 
                 extension: Optional[ExtensionMetadata] = None):
        self.core = core
        self.security = security
        self.extension = extension or ExtensionMetadata()
    
    def serialize(self) -> bytes:
        """Serialize complete metadata"""
        core_bytes = self.core.serialize()
        security_bytes = self.security.serialize()
        extension_bytes = self.extension.serialize()
        
        # Create header with layer sizes
        header = struct.pack('!III', 
                           len(core_bytes),
                           len(security_bytes), 
                           len(extension_bytes))
        
        return header + core_bytes + security_bytes + extension_bytes
    
    @classmethod
    def deserialize(cls, data: bytes) -> 'LayeredMetadata':
        """Deserialize complete metadata"""
        if len(data) < 12:
            raise ValueError("Invalid metadata: too short for header")
        
        # Parse header
        core_size, security_size, extension_size = struct.unpack('!III', data[:12])
        
        offset = 12
        core_bytes = data[offset:offset + core_size]
        offset += core_size
        
        security_bytes = data[offset:offset + security_size]
        offset += security_size
        
        extension_bytes = data[offset:offset + extension_size]
        
        core = CoreMetadata.deserialize(core_bytes)
        security = SecurityMetadata.deserialize(security_bytes)
        extension = ExtensionMetadata.deserialize(extension_bytes)
        
        return cls(core, security, extension)
    
    def get_size(self) -> int:
        """Get total metadata size in bytes"""
        return len(self.serialize())
    
    def is_compatible(self, version: str) -> bool:
        """Check if metadata is compatible with given version"""
        return self.core.version == version
    
    def get_decoy_count(self) -> int:
        """Get number of decoys for this metadata"""
        return self.core.decoy_count
    
    def get_strategy(self) -> DecoyStrategy:
        """Get decoy generation strategy"""
        return DecoyStrategy(self.core.decoy_strategy)

class MetadataFactory:
    """Factory for creating optimal metadata based on file characteristics"""
    
    @staticmethod
    def calculate_decoy_count(file_size: int, security_profile: SecurityProfile) -> int:
        """Calculate optimal decoy count based on file size and security profile"""
        
        size_ranges = {
            'tiny': file_size < 10 * 1024,         # <10KB
            'small': file_size < 1024 * 1024,      # <1MB
            'medium': file_size < 100 * 1024 * 1024, # <100MB
            'large': True                           # >=100MB
        }
        
        decoy_counts = {
            SecurityProfile.DOCUMENT: {'tiny': 1, 'small': 2, 'medium': 3, 'large': 3},
            SecurityProfile.MEDIA: {'tiny': 1, 'small': 1, 'medium': 2, 'large': 2},
            SecurityProfile.CREDENTIALS: {'tiny': 2, 'small': 3, 'medium': 5, 'large': 5},
            SecurityProfile.BACKUP: {'tiny': 0, 'small': 1, 'medium': 1, 'large': 2},
            SecurityProfile.CUSTOM: {'tiny': 2, 'small': 3, 'medium': 4, 'large': 4}
        }
        
        for size_category, condition in size_ranges.items():
            if condition:
                return decoy_counts[security_profile][size_category]
        
        return 3  # Default fallback
    
    @staticmethod
    def select_decoy_strategy(file_size: int, decoy_count: int) -> DecoyStrategy:
        """Select optimal decoy strategy based on file size"""
        
        if file_size < 1024 * 1024:  # <1MB
            return DecoyStrategy.ALGORITHMIC
        elif file_size < 100 * 1024 * 1024:  # <100MB 
            return DecoyStrategy.DIFFERENTIAL
        else:  # >=100MB
            return DecoyStrategy.SELECTIVE
    
    @staticmethod
    def estimate_metadata_size(file_size: int, security_profile: SecurityProfile) -> int:
        """Estimate total metadata size optimized for reasonable overhead percentages"""
        
        decoy_count = MetadataFactory.calculate_decoy_count(file_size, security_profile) 
        strategy = MetadataFactory.select_decoy_strategy(file_size, decoy_count)
        
        # Target reasonable overhead percentages based on file size
        # Small files need much smaller metadata to meet overhead targets
        
        if file_size <= 1024:  # 1KB file - target <10% overhead = <102 bytes
            # Ultra-compact: Core(64) + Security(~20) + Extension(~15) = ~100 bytes
            return 100
            
        elif file_size <= 10 * 1024:  # 10KB file - target <5% overhead = <512 bytes
            target_size = file_size // 25  # 4% of file size
            return max(200, min(500, target_size))
            
        elif file_size <= 100 * 1024:  # 100KB file - target <2% overhead = <2KB
            target_size = file_size // 60  # ~1.7% of file size
            return max(800, min(2000, target_size))
            
        elif file_size <= 1024 * 1024:  # 1MB file - target <1% overhead = <10KB
            target_size = file_size // 120  # ~0.8% of file size
            return max(4000, min(10000, target_size))
            
        elif file_size <= 100 * 1024 * 1024:  # 100MB file - target <0.1% overhead
            # Large files still use algorithmic decoys for most cases
            # The metadata size doesn't grow significantly with file size  
            if strategy == DecoyStrategy.SELECTIVE:
                return 8500  # Selective strategy for very large files
            else:
                return 8200  # Standard size for large files
                
        else:  # Very large files (>100MB)
            # Even massive files use compact metadata due to algorithmic approach
            return 8500  # Consistent metadata size regardless of file size
    
    @classmethod
    def create_metadata(cls, file_size: int, cel_seed_hash: bytes,
                       security_profile: SecurityProfile = SecurityProfile.DOCUMENT,
                       custom_params: Optional[Dict[str, Any]] = None) -> LayeredMetadata:
        """Create optimal metadata for given file characteristics"""
        
        decoy_count = cls.calculate_decoy_count(file_size, security_profile)
        strategy = cls.select_decoy_strategy(file_size, decoy_count)
        
        # Calculate chunk info
        chunk_size = 1048576  # 1MB default
        chunk_count = (file_size + chunk_size - 1) // chunk_size
        final_chunk_size = file_size % chunk_size or chunk_size
        
        # Create core metadata
        core = CoreMetadata(
            original_file_size=file_size,
            chunk_size=chunk_size,
            chunk_count=chunk_count,
            final_chunk_size=final_chunk_size,
            security_profile=security_profile.value,
            cel_seed_hash=cel_seed_hash,
            decoy_strategy=strategy.value,
            decoy_count=decoy_count
        )
        
        # Apply custom parameters if provided
        if custom_params:
            for key, value in custom_params.items():
                if hasattr(core, key):
                    setattr(core, key, value)
        
        # Create placeholder security metadata (optimized for file size)
        if file_size <= 1024:
            extra_data = {}  # No extra data for tiny files
        else:
            extra_data = {'placeholder': True}
            
        security = SecurityMetadata(
            decoy_strategy=strategy.value,
            decoy_count=decoy_count,
            decoy_metadata=b'',  # Will be replaced by actual decoy data
            extra_security_data=extra_data
        )
        
        # Create extension metadata with adaptive reserved space
        if file_size <= 1024:  # 1KB files - ultra-minimal reserved space
            reserved_size = 0  # No reserved space for tiny files
        elif file_size <= 10 * 1024:  # 10KB files
            reserved_size = 30
        elif file_size <= 100 * 1024:  # 100KB files
            reserved_size = 80
        elif file_size <= 1024 * 1024:  # 1MB files
            reserved_size = 150
        else:  # Large files can afford full reserved space
            reserved_size = 200
            
        extension = ExtensionMetadata(
            plugin_hooks={},
            reserved_space=b'\x00' * reserved_size if reserved_size > 0 else b'',
            compatibility_flags=0
        )
        
        return LayeredMetadata(core, security, extension)

def migrate_v030_metadata(old_metadata: Dict[str, Any]) -> LayeredMetadata:
    """Migrate v0.3.0 metadata to v0.3.1 layered format"""
    
    # Extract essential information from v0.3.0 metadata
    file_size = old_metadata.get('file_size', 0)
    
    # Derive CEL seed hash from first CEL snapshot
    cel_snapshots = old_metadata.get('cel_snapshots', [])
    if cel_snapshots:
        cel_seed_hash = hashlib.sha256(str(cel_snapshots[0]).encode()).digest()
    else:
        cel_seed_hash = hashlib.sha256(b'migration_placeholder').digest()
    
    # Determine security profile based on old parameters
    decoy_count = len(cel_snapshots) - 1  # Subtract 1 for real CEL
    if decoy_count >= 5:
        profile = SecurityProfile.CREDENTIALS
    elif decoy_count <= 1:
        profile = SecurityProfile.BACKUP
    else:
        profile = SecurityProfile.DOCUMENT
    
    # Create new layered metadata
    return MetadataFactory.create_metadata(
        file_size=file_size,
        cel_seed_hash=cel_seed_hash,
        security_profile=profile
    )