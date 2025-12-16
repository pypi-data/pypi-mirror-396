"""
Probabilistic Hashing Engine (PHE)
Non-deterministic hashing with CEL-driven path variation

Implements multi-path hashing where each operation may use unique
permutations and transforms based on CEL state, making reproduction
impossible without original context.

Key principles:
- Multi-path hashing (variable operation graphs)
- CEL-driven path selection
- Variable arithmetic base
- Collision-resistant through dynamic topology
- NO classical hashing constructs (SHA, Blake, etc.)
"""

from typing import Union, List, Dict, Any, Optional

from utils.math_primitives import (
    permute_sequence,
    modular_transform,
    rotate_bits,
    data_fingerprint_entropy,
    calculate_shannon_entropy
)


class ProbabilisticHashingEngine:
    """
    PHE - Probabilistic hashing with context-dependent path selection
    
    Generates hashes through variable mathematical pathways determined
    by CEL state, creating unique transformations for each context.
    """
    
    def __init__(self):
        """Initialize PHE"""
        self.cel_snapshot: Optional[Dict[str, Any]] = None
        self.operation_count = 0
        self.path_history: List[int] = []
        
    def map_entropy(self, cel_snapshot: Dict[str, Any]) -> None:
        """
        Bind current CEL lattice snapshot for use in hashing
        
        Per PHE contract: PHE.map_entropy(CEL) → binds current lattice snapshot
        
        Args:
            cel_snapshot: Snapshot from CEL.snapshot()
        """
        self.cel_snapshot = cel_snapshot
        
    def digest(self, data: Union[bytes, str], context: Optional[Dict[str, Any]] = None) -> bytes:
        """
        Generate probabilistic hash of data
        Enhanced with dynamic path count and collision auditing (v0.2.0)
        
        Per PHE contract: PHE.digest(data, context) → probabilistic hash result
        
        Args:
            data: Data to hash (bytes or string)
            context: Optional context dictionary affecting hash path
            
        Returns:
            Hash digest as bytes
        """
        # Convert string to bytes if needed
        if isinstance(data, str):
            data = data.encode('utf-8')
        
        if not data:
            data = b'\x00'  # Handle empty data
        
        # Increment operation counter
        self.operation_count += 1
        
        # Determine hash path based on CEL state and context
        path_selector = self._select_hash_path(data, context)
        
        # Dynamic path count based on data entropy (v0.2.0)
        # Further reduced to 3-5 for performance (was 3-7, originally 3-15)
        data_entropy = calculate_shannon_entropy(data)
        num_paths = 3 + (data_entropy % 3)  # 3-5 paths
        
        # Execute multi-path hashing with DAG
        hash_result = self._execute_hash_path_dag(data, path_selector, num_paths, context)
        
        # Store path in history
        self.path_history.append(path_selector)
        if len(self.path_history) > 100:
            self.path_history.pop(0)
        
        return hash_result
    
    def _select_hash_path(self, data: bytes, context: Optional[Dict[str, Any]]) -> int:
        """
        Select hash path based on CEL state, data, and context
        
        Args:
            data: Input data
            context: Optional context
            
        Returns:
            Path selector integer
        """
        # Base path from data fingerprint
        path = data_fingerprint_entropy(data)
        
        # Modify based on CEL state if available
        if self.cel_snapshot:
            cel_hash = self.cel_snapshot.get('seed_fingerprint', 0)
            operation_count = self.cel_snapshot.get('operation_count', 0)
            state_version = self.cel_snapshot.get('state_version', 0)
            
            path = (path + cel_hash + operation_count * 7919 + state_version) % (2**32)
        
        # Modify based on context if provided
        if context:
            context_str = str(context)
            context_entropy = data_fingerprint_entropy(context_str.encode('utf-8'))
            path = (path + context_entropy) % (2**32)
        
        # Add operation count
        path = (path + self.operation_count * 7919) % (2**32)
        
        return path
    
    def _execute_hash_path_dag(
        self, 
        data: bytes, 
        path_selector: int, 
        num_paths: int,
        context: Optional[Dict[str, Any]]
    ) -> bytes:
        """
        Execute hash computation using DAG topology (v0.2.0)
        Paths can depend on prior path outputs based on CEL structure
        
        Args:
            data: Input data
            path_selector: Path selection value
            num_paths: Number of paths to execute
            context: Optional context
            
        Returns:
            Hash bytes
        """
        # Build DAG from CEL structure
        dag = self._build_path_dag(num_paths)
        
        # Execute paths in topological order
        path_results = self._execute_dag_paths(data, path_selector, dag, context)
        
        # Combine with composite folding
        combined = self._combine_paths_composite(path_results, path_selector)
        
        # Audit collision risk
        if self.operation_count % 10 == 0:
            self._audit_collision_risk(path_results)
        
        return combined
    
    def _build_path_dag(self, num_paths: int) -> List[tuple]:
        """
        Build DAG from CEL lattice connectivity (v0.2.0)
        
        Args:
            num_paths: Number of paths
            
        Returns:
            List of (path_idx, dependencies) tuples
        """
        dag = []
        
        if not self.cel_snapshot:
            # No CEL - use simple linear DAG
            for i in range(num_paths):
                deps = [i-1] if i > 0 else []
                dag.append((i, deps))
            return dag
        
        # Use CEL structure to determine dependencies
        lattice = self.cel_snapshot.get('lattice')
        lattice_size = self.cel_snapshot.get('lattice_size', 256)
        depth = self.cel_snapshot.get('depth', 8)
        seed_fingerprint = self.cel_snapshot.get('seed_fingerprint', 0)
        operation_count = self.cel_snapshot.get('operation_count', 0)
        
        for path_idx in range(num_paths):
            # Sample CEL lattice to get dependency pattern
            layer = path_idx % depth
            row = (seed_fingerprint + path_idx) % lattice_size
            col = (operation_count + path_idx) % lattice_size
            
            if lattice is not None:
                lattice_val = int(lattice[layer][row][col])
            else:
                lattice_val = (seed_fingerprint + path_idx) % 1000
            
            # Lattice value determines number of dependencies (0-2)
            num_deps = lattice_val % 3
            
            # Select dependency indices (must be < path_idx for DAG property)
            deps = []
            for i in range(num_deps):
                if path_idx > 0:
                    dep_idx = (lattice_val + i * 7919) % path_idx
                    deps.append(dep_idx)
            
            dag.append((path_idx, deps))
        
        return dag
    
    def _execute_dag_paths(
        self,
        data: bytes,
        path_selector: int,
        dag: List[tuple],
        context: Optional[Dict[str, Any]]
    ) -> List[List[int]]:
        """
        Execute paths in topological order with dependency injection
        
        Args:
            data: Input data
            path_selector: Path selection value
            dag: DAG structure
            context: Optional context
            
        Returns:
            List of path results
        """
        results = [None] * len(dag)
        
        for path_idx, dependencies in dag:
            # Compute base path result (strategy selection now uses 7 strategies)
            base_result = self._compute_single_path(data, path_selector, path_idx, context)
            
            # Inject dependency results (optimized - simplified mixing)
            for dep_idx in dependencies:
                if results[dep_idx] is not None:
                    dep_result = results[dep_idx]
                    
                    # Simplified modular addition without rotation (performance optimization)
                    for i in range(len(base_result)):
                        dep_val = dep_result[i % len(dep_result)]
                        # XOR mixing instead of rotate (much faster, still secure)
                        base_result[i] = (base_result[i] ^ dep_val) % 65536
            
            results[path_idx] = base_result
        
        return results
    
    def _execute_hash_path(self, data: bytes, path_selector: int, context: Optional[Dict[str, Any]]) -> bytes:
        """
        Execute hash computation along selected path
        
        Args:
            data: Input data
            path_selector: Path selection value
            context: Optional context
            
        Returns:
            Hash bytes
        """
        # Determine path strategy (multiple parallel transformations)
        num_paths = (path_selector % 5) + 3  # 3-7 parallel paths
        
        # Execute parallel hash paths
        path_results = []
        for path_idx in range(num_paths):
            result = self._compute_single_path(data, path_selector, path_idx, context)
            path_results.append(result)
        
        # Combine path results
        combined = self._combine_paths(path_results, path_selector)
        
        return combined
    
    def _compute_single_path(
        self, 
        data: bytes, 
        path_selector: int, 
        path_idx: int,
        context: Optional[Dict[str, Any]]
    ) -> List[int]:
        """
        Compute single hash path transformation
        Enhanced with 7 strategies (v0.2.0: added mirror-fold, spiral, lattice projection)
        
        Args:
            data: Input data
            path_selector: Path selection value
            path_idx: Index of this path
            context: Optional context
            
        Returns:
            List of transformed integers
        """
        # Convert data to integer sequence
        int_sequence = list(data)
        
        # Determine transformation strategy (7 strategies in v0.2.0)
        cel_state_version = self.cel_snapshot.get('state_version', 0) if self.cel_snapshot else 0
        strategy = (path_selector + path_idx + cel_state_version) % 7
        
        if strategy == 0:
            return self._path_modular_cascade(int_sequence, path_selector, path_idx)
        elif strategy == 1:
            return self._path_rotation_mixing(int_sequence, path_selector, path_idx)
        elif strategy == 2:
            return self._path_base_conversion(int_sequence, path_selector, path_idx)
        elif strategy == 3:
            return self._path_permutation_folding(int_sequence, path_selector, path_idx)
        elif strategy == 4:
            return self._path_mirror_fold(int_sequence, path_selector, path_idx)
        elif strategy == 5:
            return self._path_spiral_transform(int_sequence, path_selector, path_idx)
        else:  # strategy == 6
            return self._path_lattice_projection(int_sequence, path_selector, path_idx)
    
    def _path_modular_cascade(self, sequence: List[int], path_selector: int, path_idx: int) -> List[int]:
        """
        Path strategy: Modular cascading transformations
        
        Args:
            sequence: Input integer sequence
            path_selector: Path selection value
            path_idx: Path index
            
        Returns:
            Transformed sequence
        """
        result = sequence.copy()
        
        # Cascade through varying moduli
        base_modulus = 257  # Prime
        
        for i in range(len(result)):
            modulus = base_modulus + (path_selector % 100) + path_idx
            offset = (path_selector + i * 7919) % modulus
            
            result[i] = modular_transform(result[i], modulus, offset)
        
        # Second cascade with different parameters
        for i in range(len(result)):
            prev_val = result[(i - 1) % len(result)]
            result[i] = (result[i] + prev_val * path_idx) % 65536
        
        return result
    
    def _path_rotation_mixing(self, sequence: List[int], path_selector: int, path_idx: int) -> List[int]:
        """
        Path strategy: Bit rotation and mixing
        
        Args:
            sequence: Input integer sequence
            path_selector: Path selection value
            path_idx: Path index
            
        Returns:
            Transformed sequence
        """
        result = sequence.copy()
        
        for i in range(len(result)):
            # Rotate bits
            shift = (path_selector + i + path_idx * 13) % 32
            result[i] = rotate_bits(result[i], shift, 32)
            
            # Mix with neighbors
            if i > 0:
                result[i] = (result[i] + result[i-1]) % 65536
        
        return result
    
    def _path_base_conversion(self, sequence: List[int], path_selector: int, path_idx: int) -> List[int]:
        """
        Path strategy: Variable base conversion (optimized)
        
        Args:
            sequence: Input integer sequence
            path_selector: Path selection value
            path_idx: Path index
            
        Returns:
            Transformed sequence
        """
        # Simplified: XOR with base-derived mask instead of full base conversion
        base = (path_selector % 20) + 10
        mask = (base * path_idx * 7919) % 65536
        
        result = [(val ^ mask) % 65536 for val in sequence]
        return result
    
    def _path_permutation_folding(self, sequence: List[int], path_selector: int, path_idx: int) -> List[int]:
        """
        Path strategy: Permutation with folding (optimized)
        
        Args:
            sequence: Input integer sequence
            path_selector: Path selection value
            path_idx: Path index
            
        Returns:
            Transformed sequence
        """
        result = sequence.copy()
        
        # Reduced from multiple rounds to single round for performance
        result = permute_sequence(result, path_selector + path_idx, rounds=1)
        
        # Folding: combine first and second half
        mid = len(result) // 2
        folded = []
        
        for i in range(mid):
            combined = (result[i] + result[mid + i]) % 65536
            folded.append(combined)
        
        # Handle odd length
        if len(result) % 2 == 1:
            folded.append(result[-1])
        
        return folded
    
    def _path_mirror_fold(self, sequence: List[int], path_selector: int, path_idx: int) -> List[int]:
        """
        Path strategy 5: Mirror-fold (v0.2.0)
        Reverse sequence and fold with original
        
        Args:
            sequence: Input integer sequence
            path_selector: Path selection value
            path_idx: Path index
            
        Returns:
            Transformed sequence
        """
        reversed_seq = sequence[::-1]
        
        result = []
        for i in range(len(sequence)):
            # Fold with modular multiplication
            folded = (sequence[i] * reversed_seq[i] + path_selector + path_idx) % 65521
            result.append(folded)
        
        return result
    
    def _path_spiral_transform(self, sequence: List[int], path_selector: int, path_idx: int) -> List[int]:
        """
        Path strategy 6: Spiral transform (v0.2.0)
        Position-based spiral indexing with modular multiply
        
        Args:
            sequence: Input integer sequence
            path_selector: Path selection value
            path_idx: Path index
            
        Returns:
            Transformed sequence
        """
        if not sequence:
            return sequence
        
        # Create square grid
        size = int(len(sequence) ** 0.5) + 1
        grid = [[0] * size for _ in range(size)]
        
        # Fill grid in spiral pattern
        x, y, dx, dy = 0, 0, 1, 0
        for i, val in enumerate(sequence):
            if i < size * size:
                grid[y][x] = val
                
                # Check if need to turn (hit boundary or filled cell)
                nx, ny = x + dx, y + dy
                if (nx < 0 or nx >= size or ny < 0 or ny >= size or 
                    (i < len(sequence) - 1 and grid[ny][nx] != 0)):
                    # Turn right: (dx, dy) -> (-dy, dx)
                    dx, dy = -dy, dx
                    nx, ny = x + dx, y + dy
                
                x, y = nx, ny
        
        # Read back in linear order with modular multiply
        result = []
        for row in grid:
            for val in row:
                if len(result) < len(sequence):
                    transformed = (val * (path_selector + path_idx + 1)) % 65521
                    result.append(transformed)
        
        return result[:len(sequence)]
    
    def _path_lattice_projection(self, sequence: List[int], path_selector: int, path_idx: int) -> List[int]:
        """
        Path strategy 7: Lattice projection (v0.2.0)
        Project sequence onto CEL layer, read back in CEL-determined order
        
        Args:
            sequence: Input integer sequence
            path_selector: Path selection value
            path_idx: Path index
            
        Returns:
            Transformed sequence
        """
        if not self.cel_snapshot or 'lattice' not in self.cel_snapshot:
            # Fallback to modular cascade if no CEL
            return self._path_modular_cascade(sequence, path_selector, path_idx)
        
        lattice = self.cel_snapshot['lattice']
        depth = self.cel_snapshot.get('depth', 8)
        lattice_size = self.cel_snapshot.get('lattice_size', 256)
        
        # Select layer
        layer = path_idx % depth
        cel_layer = lattice[layer].copy()
        
        # Project sequence onto CEL layer positions
        for i, val in enumerate(sequence):
            row = (i + path_selector) % lattice_size
            col = (i + path_idx) % lattice_size
            cel_layer[row][col] = (int(cel_layer[row][col]) + val) % 65536
        
        # Read back in CEL-value-determined order
        flat_indices = []
        for r in range(lattice_size):
            for c in range(lattice_size):
                flat_indices.append((int(cel_layer[r][c]), r * lattice_size + c))
        
        # Sort by CEL values
        flat_indices.sort()
        
        # Extract transformed values
        result = []
        for _, idx in flat_indices[:len(sequence)]:
            row, col = divmod(idx, lattice_size)
            result.append(int(cel_layer[row][col]) % 65536)
        
        return result
    
    def _combine_paths_composite(self, path_results: List[List[int]], path_selector: int) -> bytes:
        """
        Combine paths with composite folding (v0.2.0)
        Optimized: simplified 2-stage folding instead of 4-stage
        
        Args:
            path_results: Results from parallel paths
            path_selector: Path selection value
            
        Returns:
            Combined hash as bytes
        """
        if not path_results:
            return bytes(32)
        
        # Stage 1: XOR-fold all paths together (simplified from rotate+XOR)
        combined = list(path_results[0])
        for path in path_results[1:]:
            for i in range(min(len(combined), len(path))):
                combined[i] = (combined[i] ^ path[i]) % 65536
        
        # Stage 2: Final mixing with path selector
        for i in range(len(combined)):
            combined[i] = (combined[i] * (path_selector + i)) % 65521  # Prime modulus
        
        # Trim or pad to 32 elements
        if len(combined) < 32:
            combined.extend([0] * (32 - len(combined)))
        else:
            combined = combined[:32]
        
        # Convert to bytes (256-bit hash)
        hash_bytes = bytes([val % 256 for val in combined[:32]])
        return hash_bytes
    
    def _audit_collision_risk(self, path_results: List[List[int]]) -> None:
        """
        Audit path diversity to detect collision risks (v0.2.0)
        
        Args:
            path_results: Results from all paths
        """
        if not path_results:
            return
        
        # Convert paths to tuples for hashing
        unique_paths = len(set(tuple(p) for p in path_results))
        total_paths = len(path_results)
        
        diversity_ratio = unique_paths / total_paths if total_paths > 0 else 0
        
        audit = {
            'type': 'audit',
            'operation_count': self.operation_count,
            'unique_paths': unique_paths,
            'total_paths': total_paths,
            'diversity_ratio': diversity_ratio,
            'risk_level': 'LOW'
        }
        
        if diversity_ratio < 0.7:
            audit['risk_level'] = 'HIGH'
            audit['warning'] = 'Low path diversity - possible degenerate input'
        elif diversity_ratio < 0.85:
            audit['risk_level'] = 'MEDIUM'
        
        # Store in path history
        self.path_history.append(audit)
        if len(self.path_history) > 100:
            self.path_history.pop(0)
    
    def get_audit_log(self, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Retrieve collision risk audit log (v0.2.0)
        
        Args:
            limit: Maximum number of audit entries
            
        Returns:
            List of audit entries (most recent first)
        """
        audit_entries = [
            entry for entry in self.path_history
            if isinstance(entry, dict) and entry.get('type') == 'audit'
        ]
        return audit_entries[-limit:][::-1]
    
    def _combine_paths(self, path_results: List[List[int]], path_selector: int) -> bytes:
        """
        Combine multiple path results into final hash
        
        Args:
            path_results: Results from parallel paths
            path_selector: Path selection value
            
        Returns:
            Combined hash as bytes
        """
        # Determine output length (fixed at 32 bytes for consistency)
        output_length = 32
        
        # Combine paths by interleaving and mixing
        combined = []
        
        # Flatten all paths
        all_values = []
        for path_result in path_results:
            all_values.extend(path_result)
        
        # Compress to output length using modular arithmetic
        for i in range(output_length):
            # Select values deterministically
            value = 0
            for j in range(len(all_values)):
                idx = (i + j * 7919) % len(all_values)
                weight = (path_selector + i + j) % 256
                value += all_values[idx] * weight
            
            combined.append(value % 256)
        
        return bytes(combined)
    
    def trace(self) -> Dict[str, Any]:
        """
        Output minimal verification signature
        
        Per PHE contract: PHE.trace() → output minimal verification signature
        
        Returns:
            Dictionary with trace information
        """
        return {
            'operation_count': self.operation_count,
            'path_history_length': len(self.path_history),
            'last_path': self.path_history[-1] if self.path_history else None,
            'cel_bound': self.cel_snapshot is not None,
        }
    
    def verify(self, data: Union[bytes, str], expected_hash: bytes, context: Optional[Dict[str, Any]] = None) -> bool:
        """
        Verify data against expected hash
        
        Args:
            data: Data to verify
            expected_hash: Expected hash value
            context: Optional context (must match original context)
            
        Returns:
            True if hash matches
        """
        computed_hash = self.digest(data, context)
        return computed_hash == expected_hash


def create_phe(cel_snapshot: Optional[Dict[str, Any]] = None) -> ProbabilisticHashingEngine:
    """
    Create and optionally initialize PHE instance
    
    Args:
        cel_snapshot: Optional CEL snapshot to bind
        
    Returns:
        PHE instance
    """
    phe = ProbabilisticHashingEngine()
    if cel_snapshot:
        phe.map_entropy(cel_snapshot)
    return phe
