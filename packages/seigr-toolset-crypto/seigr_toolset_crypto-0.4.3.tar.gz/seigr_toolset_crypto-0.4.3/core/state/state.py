"""
State Management Module
Handles meta-state persistence, session reconstruction, and reproducibility

Stores compact persistence vectors (seed hashes, CEL snapshots,
meta-state signatures) and regenerates states deterministically
from compact data.

Key principles:
- State data never includes direct key material
- Version control for backward-compatible regeneration
- Compact storage format
- Deterministic reconstruction
"""

import struct
import numpy as np
from typing import Dict, Any, Optional
from datetime import datetime


class StateManager:
    """
    STATE - Persistence and reconstruction manager
    
    Handles saving and loading of complete STC context states,
    enabling deterministic reproduction without exposing secrets.
    """
    
    def __init__(self):
        """Initialize State Manager"""
        self.state_version = "0.1.0"
        self.current_context: Optional[Dict[str, Any]] = None
        
    def save(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Store reproducible state vector
        
        Per STATE contract: STATE.save(context) → store reproducible state vector
        
        Args:
            context: Complete context dictionary containing:
                    - 'cel': CEL instance or snapshot
                    - 'phe': PHE instance (optional)
                    - 'pcf': PCF instance (optional)
                    - 'seed': Original seed
                    - 'metadata': Optional metadata
                    
        Returns:
            Compact persistence vector
        """
        persistence_vector = {
            'version': self.state_version,
            'timestamp': datetime.now().isoformat(),
            'cel_state': self._extract_cel_state(context.get('cel')),
            'pcf_state': self._extract_pcf_state(context.get('pcf')),
            'seed_fingerprint': self._compute_seed_fingerprint(context.get('seed')),
            'metadata': context.get('metadata', {}),
        }
        
        # Store current context
        self.current_context = persistence_vector
        
        return persistence_vector
    
    def load(self, vector: Dict[str, Any]) -> Dict[str, Any]:
        """
        Reconstruct context from persistence vector
        
        Per STATE contract: STATE.load(vector) → reconstruct context
        
        Args:
            vector: Persistence vector from save()
            
        Returns:
            Reconstructed context dictionary
        """
        # Validate version compatibility
        if not self._is_compatible_version(vector.get('version')):
            raise ValueError(f"Incompatible state version: {vector.get('version')}")
        
        # Reconstruct context
        context = {
            'version': vector['version'],
            'timestamp': vector.get('timestamp'),
            'cel_state': vector.get('cel_state'),
            'pcf_state': vector.get('pcf_state'),
            'seed_fingerprint': vector.get('seed_fingerprint'),
            'metadata': vector.get('metadata', {}),
        }
        
        self.current_context = context
        
        return context
    
    def sync(
        self,
        phe_instance: Any = None,
        cel_instance: Any = None,
        pcf_instance: Any = None
    ) -> Dict[str, Any]:
        """
        Synchronize all modules and create unified state
        
        Per STATE contract: STATE.sync(PHE, CEL, PCF) → synchronize all modules
        
        Args:
            phe_instance: PHE instance (optional)
            cel_instance: CEL instance (optional)
            pcf_instance: PCF instance (optional)
            
        Returns:
            Synchronized state dictionary
        """
        sync_state = {
            'timestamp': datetime.now().isoformat(),
            'modules': {}
        }
        
        # Sync CEL
        if cel_instance is not None:
            if hasattr(cel_instance, 'snapshot'):
                sync_state['modules']['cel'] = cel_instance.snapshot()
            else:
                sync_state['modules']['cel'] = self._extract_cel_state(cel_instance)
        
        # Sync PHE
        if phe_instance is not None:
            if hasattr(phe_instance, 'trace'):
                sync_state['modules']['phe'] = phe_instance.trace()
            else:
                sync_state['modules']['phe'] = {}
        
        # Sync PCF
        if pcf_instance is not None:
            if hasattr(pcf_instance, 'export_state'):
                sync_state['modules']['pcf'] = pcf_instance.export_state()
            else:
                sync_state['modules']['pcf'] = self._extract_pcf_state(pcf_instance)
        
        return sync_state
    
    def _extract_cel_state(self, cel: Any) -> Dict[str, Any]:
        """
        Extract CEL state for persistence
        
        Args:
            cel: CEL instance or snapshot
            
        Returns:
            CEL state dictionary
        """
        if cel is None:
            return {}
        
        # If already a snapshot dict, return it
        if isinstance(cel, dict):
            # Convert numpy arrays to binary format for self-sovereign serialization
            state = cel.copy()
            if 'lattice' in state and isinstance(state['lattice'], np.ndarray):
                state['lattice'] = state['lattice'].tolist()
            return state
        
        # If CEL instance, get snapshot
        if hasattr(cel, 'snapshot'):
            snapshot = cel.snapshot()
            if 'lattice' in snapshot and isinstance(snapshot['lattice'], np.ndarray):
                snapshot['lattice'] = snapshot['lattice'].tolist()
            return snapshot
        
        return {}
    
    def _extract_pcf_state(self, pcf: Any) -> Dict[str, Any]:
        """
        Extract PCF state for persistence
        
        Args:
            pcf: PCF instance
            
        Returns:
            PCF state dictionary
        """
        if pcf is None:
            return {}
        
        # If already a state dict, return it
        if isinstance(pcf, dict):
            return pcf.copy()
        
        # If PCF instance, export state
        if hasattr(pcf, 'export_state'):
            return pcf.export_state()
        
        return {}
    
    def _compute_seed_fingerprint(self, seed: Any) -> Optional[int]:
        """
        Compute fingerprint of seed without storing seed itself
        
        Args:
            seed: Seed value
            
        Returns:
            Seed fingerprint
        """
        if seed is None:
            return None
        
        from utils.math_primitives import data_fingerprint_entropy
        
        if isinstance(seed, str):
            seed_bytes = seed.encode('utf-8')
        elif isinstance(seed, bytes):
            seed_bytes = seed
        elif isinstance(seed, int):
            seed_bytes = seed.to_bytes((seed.bit_length() + 7) // 8, 'big')
        else:
            seed_bytes = str(seed).encode('utf-8')
        
        return data_fingerprint_entropy(seed_bytes)
    
    def _is_compatible_version(self, version: Optional[str]) -> bool:
        """
        Check if state version is compatible
        
        Args:
            version: State version string
            
        Returns:
            True if compatible
        """
        if version is None:
            return False
        
        # Simple version check (major.minor.patch)
        # Compatible if major version matches
        try:
            current_major = int(self.state_version.split('.')[0])
            state_major = int(version.split('.')[0])
            return current_major == state_major
        except (ValueError, IndexError):
            return False
    
    def serialize(self, state: Dict[str, Any]) -> bytes:
        """
        Serialize state to self-sovereign binary format
        
        Args:
            state: State dictionary
            
        Returns:
            Binary data
        """
        return self._serialize_dict_to_binary(state)
    
    def deserialize(self, binary_data: bytes) -> Dict[str, Any]:
        """
        Deserialize state from self-sovereign binary format
        
        Args:
            binary_data: Binary data
            
        Returns:
            State dictionary
        """
        return self._deserialize_binary_to_dict(binary_data)
    
    def _serialize_dict_to_binary(self, data: Dict[str, Any]) -> bytes:
        """Serialize dictionary to self-sovereign binary format with STC state support"""
        if not data:
            return b''
        
        # Magic header for STC state: STCS (SeigrToolsetCrypto State)
        binary_data = bytearray(b'STCS')
        
        # Version info (4 bytes)
        version_parts = self.state_version.split('.')
        binary_data.extend(struct.pack('<BBB', int(version_parts[0]), int(version_parts[1]), int(version_parts[2])))
        binary_data.extend(b'\x00')  # Reserved byte
        
        # Serialize each key-value pair
        for key, value in data.items():
            # Key (length-prefixed string)
            key_bytes = key.encode('utf-8')
            binary_data.extend(struct.pack('<H', len(key_bytes)))
            binary_data.extend(key_bytes)
            
            # Value (type-tagged)
            if isinstance(value, bool):
                binary_data.extend(b'\x01')  # Boolean type
                binary_data.extend(struct.pack('<?', value))
            elif isinstance(value, int):
                binary_data.extend(b'\x02')  # Integer type
                binary_data.extend(struct.pack('<q', value))  # 64-bit signed
            elif isinstance(value, float):
                binary_data.extend(b'\x03')  # Float type
                binary_data.extend(struct.pack('<d', value))  # 64-bit double
            elif isinstance(value, str):
                binary_data.extend(b'\x04')  # String type
                value_bytes = value.encode('utf-8')
                binary_data.extend(struct.pack('<I', len(value_bytes)))
                binary_data.extend(value_bytes)
            elif isinstance(value, bytes):
                binary_data.extend(b'\x05')  # Bytes type
                binary_data.extend(struct.pack('<I', len(value)))
                binary_data.extend(value)
            elif isinstance(value, np.ndarray):
                binary_data.extend(b'\x06')  # NumPy array type
                # Store shape, dtype, and data
                shape_bytes = struct.pack('<B', len(value.shape))  # Number of dimensions
                for dim in value.shape:
                    shape_bytes += struct.pack('<I', dim)
                dtype_str = str(value.dtype).encode('utf-8')
                array_data = value.tobytes()
                
                binary_data.extend(struct.pack('<H', len(dtype_str)))
                binary_data.extend(dtype_str)
                binary_data.extend(shape_bytes)
                binary_data.extend(struct.pack('<I', len(array_data)))
                binary_data.extend(array_data)
            elif isinstance(value, dict):
                binary_data.extend(b'\x07')  # Nested dict type
                nested_binary = self._serialize_dict_to_binary(value)
                binary_data.extend(struct.pack('<I', len(nested_binary)))
                binary_data.extend(nested_binary)
            else:
                # Skip unsupported types for self-sovereignty
                continue
                
        return bytes(binary_data)
    
    def _deserialize_binary_to_dict(self, data: bytes) -> Dict[str, Any]:
        """Deserialize binary data to dictionary with STC state support"""
        if not data or len(data) < 8:
            return {}
        
        # Check magic header
        if data[:4] != b'STCS':
            raise ValueError("Invalid STC state data: missing STCS magic number")
        
        # Extract version for compatibility checking
        version_info = struct.unpack('<BBB', data[4:7])
        # Reserved byte at position 7
        
        result = {'_version': version_info}  # Store version for potential use
        offset = 8
        
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
            elif value_type == b'\x05':  # Bytes
                bytes_len = struct.unpack('<I', data[offset:offset+4])[0]
                offset += 4
                value = data[offset:offset+bytes_len]
                offset += bytes_len
            elif value_type == b'\x06':  # NumPy array
                # Read dtype
                dtype_len = struct.unpack('<H', data[offset:offset+2])[0]
                offset += 2
                dtype_str = data[offset:offset+dtype_len].decode('utf-8')
                offset += dtype_len
                
                # Read shape
                num_dims = struct.unpack('<B', data[offset:offset+1])[0]
                offset += 1
                shape = []
                for _ in range(num_dims):
                    dim = struct.unpack('<I', data[offset:offset+4])[0]
                    shape.append(dim)
                    offset += 4
                
                # Read array data
                array_len = struct.unpack('<I', data[offset:offset+4])[0]
                offset += 4
                array_data = data[offset:offset+array_len]
                offset += array_len
                
                # Reconstruct numpy array
                value = np.frombuffer(array_data, dtype=dtype_str).reshape(shape)
            elif value_type == b'\x07':  # Nested dict
                nested_len = struct.unpack('<I', data[offset:offset+4])[0]
                offset += 4
                nested_data = data[offset:offset+nested_len]
                value = self._deserialize_binary_to_dict(nested_data)
                offset += nested_len
            else:
                break  # Unknown type, stop parsing
                
            result[key] = value
            
        return result
    
    def save_to_file(self, state: Dict[str, Any], filepath: str) -> None:
        """
        Save state to file
        
        Args:
            state: State dictionary
            filepath: File path for saving
        """
        binary_data = self.serialize(state)
        with open(filepath, 'wb') as f:
            f.write(binary_data)
    
    def load_from_file(self, filepath: str) -> Dict[str, Any]:
        """
        Load state from file
        
        Args:
            filepath: File path to load from
            
        Returns:
            State dictionary
        """
        with open(filepath, 'rb') as f:
            binary_data = f.read()
        
        return self.deserialize(binary_data)
    
    def validate_state(self, state: Dict[str, Any]) -> bool:
        """
        Validate state structure
        
        Args:
            state: State dictionary to validate
            
        Returns:
            True if valid
        """
        # Check required fields
        required_fields = ['version']
        for field in required_fields:
            if field not in state:
                return False
        
        # Check version compatibility
        if not self._is_compatible_version(state['version']):
            return False
        
        return True
    
    def get_state_summary(self, state: Optional[Dict[str, Any]] = None) -> str:
        """
        Get human-readable state summary
        
        Args:
            state: Optional state dictionary (uses current if None)
            
        Returns:
            Summary string
        """
        if state is None:
            state = self.current_context
        
        if state is None:
            return "No state available"
        
        lines = [
            "=== State Summary ===",
            f"Version: {state.get('version', 'Unknown')}",
            f"Timestamp: {state.get('timestamp', 'Unknown')}",
            "",
            "Components:",
        ]
        
        # CEL state
        if 'cel_state' in state and state['cel_state']:
            cel = state['cel_state']
            lines.append(f"  CEL:")
            lines.append(f"    Lattice Size: {cel.get('lattice_size', 'N/A')}")
            lines.append(f"    Depth: {cel.get('depth', 'N/A')}")
            lines.append(f"    Operation Count: {cel.get('operation_count', 'N/A')}")
            lines.append(f"    State Version: {cel.get('state_version', 'N/A')}")
        
        # PCF state
        if 'pcf_state' in state and state['pcf_state']:
            pcf = state['pcf_state']
            lines.append(f"  PCF:")
            lines.append(f"    Morph Version: {pcf.get('morph_version', 'N/A')}")
            lines.append(f"    Operation Count: {pcf.get('operation_count', 'N/A')}")
        
        # Metadata
        if 'metadata' in state and state['metadata']:
            lines.append("  Metadata:")
            for key, value in state['metadata'].items():
                lines.append(f"    {key}: {value}")
        
        return "\n".join(lines)


def create_state_manager() -> StateManager:
    """
    Create StateManager instance
    
    Returns:
        StateManager instance
    """
    return StateManager()


def save_context(
    cel_instance: Any = None,
    pcf_instance: Any = None,
    seed: Any = None,
    metadata: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Convenience function to save complete context
    
    Args:
        cel_instance: CEL instance
        pcf_instance: PCF instance
        seed: Original seed
        metadata: Optional metadata
        
    Returns:
        Persistence vector
    """
    manager = create_state_manager()
    
    context = {
        'cel': cel_instance,
        'pcf': pcf_instance,
        'seed': seed,
        'metadata': metadata or {}
    }
    
    return manager.save(context)
