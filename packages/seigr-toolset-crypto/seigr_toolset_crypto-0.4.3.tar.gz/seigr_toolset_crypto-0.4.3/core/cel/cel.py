"""
Continuous Entropy Lattice (CEL)
Foundation of STC entropy generation and evolution

The CEL is a self-evolving matrix of numerical states that regenerates
at each interaction using internal computational deltas, not external randomness.

Key properties:
- Deterministic regeneration from seed
- Context-sensitive evolution
- Snapshot/restore capability
- No reliance on environmental entropy sources
"""

import numpy as np
from typing import Dict, Any, Optional, List, Union

from utils.math_primitives import (
    non_linear_diffusion,
    permute_sequence,
    compute_time_delta_entropy,
    memory_allocation_entropy,
    data_fingerprint_entropy,
    rotate_bits,
    modular_exponentiation,
    compute_chained_timing_entropy
)


class ContinuousEntropyLattice:
    """
    CEL - The continuous entropy field for STC
    
    Generates and maintains an evolving lattice of entropy values
    derived exclusively from computational deltas, memory patterns,
    and temporal micro-variations.
    """
    
    # Bounds for lattice parameters to prevent resource exhaustion
    MIN_LATTICE_SIZE = 4
    MAX_LATTICE_SIZE = 1024  # Limits memory to ~8GB max at depth=8
    MIN_DEPTH = 1
    MAX_DEPTH = 32
    
    def __init__(self, lattice_size: int = 256, depth: int = 8):
        """
        Initialize CEL structure
        
        Args:
            lattice_size: Dimension of entropy lattice (lattice_size x lattice_size)
                         Must be between MIN_LATTICE_SIZE and MAX_LATTICE_SIZE
            depth: Number of layered entropy matrices
                   Must be between MIN_DEPTH and MAX_DEPTH
        
        Raises:
            ValueError: If lattice_size or depth are outside valid bounds
        """
        # Validate bounds to prevent resource exhaustion attacks
        if not (self.MIN_LATTICE_SIZE <= lattice_size <= self.MAX_LATTICE_SIZE):
            raise ValueError(
                f"lattice_size must be between {self.MIN_LATTICE_SIZE} and {self.MAX_LATTICE_SIZE}, "
                f"got {lattice_size}"
            )
        if not (self.MIN_DEPTH <= depth <= self.MAX_DEPTH):
            raise ValueError(
                f"depth must be between {self.MIN_DEPTH} and {self.MAX_DEPTH}, "
                f"got {depth}"
            )
        
        self.lattice_size = lattice_size
        self.depth = depth
        
        # Multi-layered entropy lattice
        self.lattice: Optional[np.ndarray] = None
        
        # Operation counter for evolution tracking
        self.operation_count = 0
        
        # Seed fingerprint for reproducibility
        self.seed_fingerprint: Optional[int] = None
        
        # Historical entropy accumulator (for context continuity)
        self.entropy_history: List[int] = []
        
        # Audit log for entropy quality monitoring (v0.2.0)
        self.audit_log: List[Dict[str, Any]] = []
        
        # Internal state version (increments on each update)
        self.state_version = 0
        
    def init(self, seed: Union[str, bytes, int]) -> None:
        """
        Initialize entropy lattice from seed
        
        Per CEL contract: CEL.init(seed) → initialize from compact seed vector
        
        Args:
            seed: Seed value (string, bytes, or integer)
        """
        # Convert seed to deterministic numeric value
        if isinstance(seed, str):
            seed_bytes = seed.encode('utf-8')
        elif isinstance(seed, int):
            seed_bytes = seed.to_bytes((seed.bit_length() + 7) // 8, 'big')
        else:
            seed_bytes = seed
        
        # Generate seed fingerprint
        self.seed_fingerprint = data_fingerprint_entropy(seed_bytes)
        
        # Initialize lattice using seed-derived values
        self._initialize_lattice_from_seed(seed_bytes)
        
        # Reset state
        self.operation_count = 0
        self.entropy_history = [self.seed_fingerprint]
        self.state_version = 1
        
    def _initialize_lattice_from_seed(self, seed_bytes: bytes) -> None:
        """
        Create initial lattice state from seed bytes
        
        Args:
            seed_bytes: Seed as bytes
        """
        # Create deterministic but complex initialization
        # Use seed bytes to generate initial lattice values
        
        # Expand seed to fill lattice using deterministic process
        seed_value = int.from_bytes(seed_bytes, 'big') if seed_bytes else 1
        
        # Initialize each layer of the lattice
        self.lattice = np.zeros((self.depth, self.lattice_size, self.lattice_size), dtype=np.int64)
        
        # Use a prime modulus to avoid zeros from modular exponentiation
        prime_mod = 65521  # Large prime
        
        for layer in range(self.depth):
            for i in range(self.lattice_size):
                for j in range(self.lattice_size):
                    # Deterministic value generation from seed, position, and layer
                    # Uses modular exponentiation with prime modulus to avoid zeros
                    pos_factor = (i * self.lattice_size + j + 1)
                    layer_factor = (layer + 1) * 7919  # Prime multiplier
                    
                    # Compute base using seed and position
                    base = ((seed_value % prime_mod) + pos_factor) % prime_mod
                    if base == 0:
                        base = 1
                    
                    # Compute exponent
                    exp = (pos_factor + layer_factor) % (prime_mod - 1)  # Use Fermat's little theorem
                    if exp == 0:
                        exp = 1
                    
                    value = modular_exponentiation(base, exp, prime_mod)
                    
                    # Ensure non-zero value
                    if value == 0:
                        value = (pos_factor * layer_factor) % prime_mod + 1
                    
                    self.lattice[layer, i, j] = value
        
        # Apply initial diffusion to create complex patterns
        for layer in range(self.depth):
            self.lattice[layer] = non_linear_diffusion(
                self.lattice[layer],
                iterations=3
            )
    
    def update(self, context: Optional[Dict[str, Any]] = None) -> None:
        """
        Regenerate entropy field based on operation context
        
        Per CEL contract: CEL.update(context) → regenerate entropy field
        
        Args:
            context: Optional context dictionary with keys:
                     - 'data': bytes to incorporate
                     - 'operation': operation type string
                     - 'parameters': additional parameters
        """
        if self.lattice is None:
            raise RuntimeError("CEL not initialized. Call init() first.")
        
        # Increment operation counter
        self.operation_count += 1
        
        # Gather entropy from multiple sources
        entropy_sources = self._gather_entropy_sources(context)
        
        # Evolve lattice based on entropy sources
        self._evolve_lattice(entropy_sources)
        
        # Update state version
        self.state_version += 1
        
        # Store in history (keep last 100 for context)
        combined_entropy = sum(entropy_sources.values()) % (2**64)
        self.entropy_history.append(combined_entropy)
        if len(self.entropy_history) > 100:
            self.entropy_history.pop(0)
        
        # Perform entropy quality audit (reduced frequency for performance)
        if self.operation_count % 100 == 0:  # Was every 50th, now every 100th (v0.2.1)
            self._audit_entropy_quality(entropy_sources)
    
    def _gather_entropy_sources(self, context: Optional[Dict[str, Any]]) -> Dict[str, int]:
        """
        Gather entropy from various computational sources
        Enhanced with 3-tier historical feedback and chained timing entropy
        
        Args:
            context: Optional context dictionary
            
        Returns:
            Dictionary of entropy source values
        """
        sources = {}
        
        # Time-based entropy (chained computational loads for higher variance)
        # Reduced frequency for performance
        if self.operation_count % 200 == 0:  # Was every 100th, now every 200th (v0.2.1)
            # Use expensive chained entropy rarely
            sources['time_delta'] = compute_chained_timing_entropy(self.seed_fingerprint or 0)
        else:
            # Use fast timing entropy otherwise
            sources['time_delta'] = compute_time_delta_entropy()
        
        # Memory-based entropy (allocation patterns)
        sources['memory'] = memory_allocation_entropy()
        
        # Operation count entropy
        sources['operation'] = self.operation_count * 7919 % (2**32)
        
        # 3-Tier Historical Feedback (v0.2.0 enhancement)
        if len(self.entropy_history) >= 5:
            # Tier 1 (Recent): Last 5 states → immediate mixing weight
            tier1 = sum(self.entropy_history[-5:]) % 65521  # Prime modulus
            sources['history_tier1'] = tier1
            
            # Tier 2 (Medium): States 6-20 → rotation bias
            if len(self.entropy_history) >= 20:
                tier2 = sum(self.entropy_history[-20:-5]) % 524287  # Larger prime
                sources['history_tier2'] = tier2
            
            # Tier 3 (Deep): States 21-100 → diffusion iteration count
            if len(self.entropy_history) >= 100:
                tier3 = sum(self.entropy_history[-100:-20]) % 2147483647  # Large prime
                sources['history_tier3'] = tier3
        elif self.entropy_history:
            # Fallback for initial operations
            sources['history'] = sum(self.entropy_history[-10:]) % (2**32)
        
        # Context-specific entropy
        if context:
            if 'data' in context:
                sources['data'] = data_fingerprint_entropy(context['data'])
            
            if 'operation' in context:
                op_bytes = context['operation'].encode('utf-8')
                sources['operation_type'] = data_fingerprint_entropy(op_bytes)
            
            if 'parameters' in context:
                param_str = str(context['parameters'])
                sources['parameters'] = data_fingerprint_entropy(param_str.encode('utf-8'))
        
        return sources
    
    def _evolve_lattice(self, entropy_sources: Dict[str, int]) -> None:
        """
        Evolve lattice state using entropy sources
        Enhanced with nonlinear temporal mixing (v0.2.0)
        
        Args:
            entropy_sources: Dictionary of entropy values
        """
        # Nonlinear temporal mixing with Fibonacci weights
        fib_weights = [1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144]
        
        combined_entropy = 0
        for i, (key, value) in enumerate(entropy_sources.items()):
            weight = fib_weights[i % len(fib_weights)]
            
            # Polynomial mixing for key sources
            if key in ['time_delta', 'memory']:
                # Quadratic contribution
                combined_entropy += (value ** 2) * weight
            elif key.startswith('history_tier'):
                # Cubic contribution for historical tiers
                combined_entropy += (value ** 3) * weight
            else:
                # Linear contribution
                combined_entropy += value * weight
        
        combined_entropy = combined_entropy % (2**64)
        
        # Determine evolution strategy based on combined entropy
        # Use tier2 to influence strategy selection if available
        tier2_bias = entropy_sources.get('history_tier2', 0)
        strategy = (combined_entropy + tier2_bias) % 3
        
        if strategy == 0:
            # Strategy 0: Rotation and permutation
            self._evolve_rotation(combined_entropy)
        elif strategy == 1:
            # Strategy 1: Non-linear diffusion (tier3 influences iteration count)
            tier3_iterations = entropy_sources.get('history_tier3', 0)
            self._evolve_diffusion(combined_entropy, tier3_iterations)
        else:
            # Strategy 2: Layer mixing
            self._evolve_mixing(combined_entropy)
        
        # Apply cross-layer interaction with fresh timing injection
        self._cross_layer_interaction(combined_entropy)
    
    def _evolve_rotation(self, entropy: int) -> None:
        """
        Evolution strategy: Rotate lattice values
        
        Args:
            entropy: Combined entropy value
        """
        for layer in range(self.depth):
            shift = (entropy + layer * 7919) % 64
            
            # Rotate all values in this layer
            flat = self.lattice[layer].flatten()
            for i in range(len(flat)):
                # Constrain value to 32 bits to prevent overflow
                val = int(flat[i]) % (2**32)
                rotated = rotate_bits(val, shift, 32)  # Use 32-bit rotation
                flat[i] = rotated % (2**16)  # Keep in 16-bit range
            
            self.lattice[layer] = flat.reshape(self.lattice_size, self.lattice_size)
    
    def _evolve_diffusion(self, entropy: int, tier3_modulator: int = 0) -> None:
        """
        Evolution strategy: Apply non-linear diffusion
        Enhanced with tier3 historical modulation (v0.2.0)
        Optimized: reduced iterations for performance
        
        Args:
            entropy: Combined entropy value
            tier3_modulator: Deep historical entropy (modulates iteration count)
        """
        # Reduced iterations from 1-8 to 1-3 for performance
        base_iterations = (entropy % 2) + 1  # 1-2 iterations (was 1-5)
        
        # Modulate with tier3 deep history (max +1 instead of +2)
        if tier3_modulator > 0:
            tier3_bonus = (tier3_modulator % 2)  # 0-1 bonus iteration (was 0-2)
            iterations = base_iterations + tier3_bonus
        else:
            iterations = base_iterations
        
        for layer in range(self.depth):
            self.lattice[layer] = non_linear_diffusion(
                self.lattice[layer],
                iterations=iterations
            )
    
    def _evolve_mixing(self, entropy: int) -> None:
        """
        Evolution strategy: Mix layers
        
        Args:
            entropy: Combined entropy value
        """
        # Permute layer order
        layer_indices = list(range(self.depth))
        layer_indices = permute_sequence(layer_indices, entropy, rounds=2)
        
        # Apply permutation
        new_lattice = np.zeros_like(self.lattice)
        for new_idx, old_idx in enumerate(layer_indices):
            new_lattice[new_idx] = self.lattice[old_idx]
        
        self.lattice = new_lattice
    
    def _cross_layer_interaction(self, entropy: int) -> None:
        """
        Apply interactions between lattice layers
        Enhanced with fresh timing entropy injection at each boundary (v0.2.0)
        
        Args:
            entropy: Combined entropy value
        """
        for layer in range(self.depth - 1):
            # Inject fresh timing entropy at layer boundary
            boundary_entropy = compute_time_delta_entropy()
            
            interaction = (
                self.lattice[layer] + 
                self.lattice[layer + 1] + 
                boundary_entropy % 65536
            ) % 65536
            
            # Apply to both layers (bidirectional influence)
            self.lattice[layer] = (self.lattice[layer] + interaction) % 65536
            self.lattice[layer + 1] = (self.lattice[layer + 1] + interaction) % 65536
    
    def snapshot(self) -> Dict[str, Any]:
        """
        Export current entropy lattice state for reproducibility
        
        Per CEL contract: CEL.snapshot() → export current entropy lattice state
        
        Returns:
            Dictionary containing complete state information
        """
        if self.lattice is None:
            raise RuntimeError("CEL not initialized. Call init() first.")
        
        return {
            'lattice': self.lattice.copy(),
            'lattice_size': self.lattice_size,
            'depth': self.depth,
            'operation_count': self.operation_count,
            'seed_fingerprint': self.seed_fingerprint,
            'state_version': self.state_version,
            'entropy_history': self.entropy_history.copy(),
        }
    
    def restore_snapshot(self, snapshot: Dict[str, Any]) -> None:
        """
        Restore CEL state from snapshot
        
        Args:
            snapshot: State dictionary from snapshot()
        """
        self.lattice = snapshot['lattice'].copy()
        self.lattice_size = snapshot['lattice_size']
        self.depth = snapshot['depth']
        self.operation_count = snapshot['operation_count']
        self.seed_fingerprint = snapshot['seed_fingerprint']
        self.state_version = snapshot['state_version']
        self.entropy_history = snapshot['entropy_history'].copy()
    
    def extract_entropy(self, length: int, context: Optional[str] = None) -> np.ndarray:
        """
        Extract entropy vector from current lattice state
        
        Args:
            length: Length of entropy vector to extract
            context: Optional context string for extraction variation
            
        Returns:
            Entropy vector as numpy array
        """
        if self.lattice is None:
            raise RuntimeError("CEL not initialized. Call init() first.")
        
        # Flatten lattice
        flat_lattice = self.lattice.flatten()
        
        # Add context variation if provided
        offset = 0
        if context:
            offset = data_fingerprint_entropy(context.encode('utf-8'))
        
        # Extract entropy values using deterministic indexing
        entropy_vector = np.zeros(length, dtype=np.int64)
        
        for i in range(length):
            # Deterministic index selection
            idx = (i * 7919 + offset + self.operation_count) % len(flat_lattice)
            entropy_vector[i] = flat_lattice[idx]
        
        return entropy_vector
    
    def get_state_hash(self) -> int:
        """
        Compute compact hash of current CEL state
        
        Returns:
            Integer hash of current state
        """
        if self.lattice is None:
            return 0
        
        # Create deterministic hash from lattice state
        # Use clip and modulo to prevent overflow
        clipped_sum = int(np.clip(np.sum(self.lattice, dtype=np.float64), 0, 2**63 - 1))
        state_sum = clipped_sum % (2**32)
        state_product = (self.operation_count * self.state_version) % (2**32)
        
        return (state_sum + state_product) % (2**32)
    
    def _audit_entropy_quality(self, entropy_sources: Dict[str, int]) -> None:
        """
        Audit entropy quality and trigger remediation if needed (v0.2.0)
        Implements self-auditing with internal logging
        
        Args:
            entropy_sources: Current entropy sources
        """
        audit_entry = {
            'type': 'audit',
            'operation_count': self.operation_count,
            'state_version': self.state_version,
            'quality': 'GOOD',
            'metrics': {},
            'remediation': None
        }
        
        # Metric 1: Timing variance (if we have timing data)
        if 'time_delta' in entropy_sources:
            time_delta = entropy_sources['time_delta']
            # Check if timing entropy is suspiciously low
            if time_delta < 100:  # Less than 100 units indicates low-resolution timer
                audit_entry['quality'] = 'LOW_RESOLUTION_TIMER'
                audit_entry['metrics']['time_delta'] = time_delta
                audit_entry['remediation'] = 'EMERGENCY_REINIT'
                self._trigger_emergency_reinit()
        
        # Metric 2: CEL State Diversity
        if self.lattice is not None:
            unique_values = len(np.unique(self.lattice))
            expected = int(self.lattice.size * 0.8)
            diversity_ratio = unique_values / self.lattice.size
            
            audit_entry['metrics']['unique_values'] = unique_values
            audit_entry['metrics']['diversity_ratio'] = diversity_ratio
            
            if unique_values < expected:
                audit_entry['quality'] = 'DEGENERATE_STATE'
                audit_entry['remediation'] = 'FORCED_DIFFUSION'
                self._trigger_forced_diffusion(iterations=10)
        
        # Metric 3: Historical Trend Staleness
        if len(self.entropy_history) >= 20:
            recent = self.entropy_history[-20:]
            # Calculate variance proxy (integer-only)
            mean = sum(recent) // len(recent)
            variance_sum = sum((x - mean) ** 2 for x in recent)
            stddev_proxy = int((variance_sum / len(recent)) ** 0.5)
            
            audit_entry['metrics']['history_stddev'] = stddev_proxy
            
            if stddev_proxy < 1000:
                audit_entry['quality'] = 'STALE_ENTROPY'
                audit_entry['remediation'] = 'CROSS_LAYER_FORCED'
                # Force additional cross-layer interactions
                for _ in range(3):
                    self._cross_layer_interaction(compute_time_delta_entropy())
        
        # Store audit entry in separate audit log
        if audit_entry['quality'] != 'GOOD' or self.operation_count % 100 == 0:
            # Only store significant audits or periodic checkpoints
            self.audit_log.append(audit_entry)
            if len(self.audit_log) > 100:
                self.audit_log.pop(0)
    
    def _trigger_emergency_reinit(self) -> None:
        """Emergency re-initialization for low-quality entropy"""
        if self.seed_fingerprint is not None:
            # Re-initialize with enhanced seed
            enhanced_seed = (self.seed_fingerprint + self.operation_count) % (2**32)
            seed_bytes = enhanced_seed.to_bytes(8, 'big')
            self._initialize_lattice_from_seed(seed_bytes)
    
    def _trigger_forced_diffusion(self, iterations: int = 10) -> None:
        """Force aggressive diffusion to improve state diversity"""
        for layer in range(self.depth):
            self.lattice[layer] = non_linear_diffusion(
                self.lattice[layer],
                iterations=iterations
            )
    
    def get_audit_log(self, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Retrieve internal audit log (v0.2.0)
        
        Args:
            limit: Maximum number of audit entries to return
            
        Returns:
            List of audit entries (most recent first)
        """
        return self.audit_log[-limit:][::-1]  # Reverse to get most recent first
    
    def get_entropy_profile(self) -> Dict[str, Any]:
        """
        Get comprehensive entropy health profile (v0.3.0)
        
        Returns actionable metrics about entropy quality, warnings,
        and recommendations for security-conscious users.
        
        Returns:
            Dictionary with:
                - quality_score: 0.0-1.0 overall entropy health
                - status: 'excellent', 'good', 'acceptable', 'weak', 'critical'
                - warnings: List of current issues
                - recommendations: List of suggested actions
                - metrics: Detailed measurements
                - recent_audits: Last 5 audit entries
        """
        profile = {
            'quality_score': 1.0,
            'status': 'excellent',
            'warnings': [],
            'recommendations': [],
            'metrics': {
                'operation_count': self.operation_count,
                'state_version': self.state_version,
                'lattice_size': self.lattice_size,
                'depth': self.depth,
                'history_length': len(self.entropy_history)
            },
            'recent_audits': self.get_audit_log(limit=5)
        }
        
        # Calculate quality score based on recent audits
        recent_audits = self.audit_log[-10:] if self.audit_log else []
        if recent_audits:
            quality_issues = sum(1 for a in recent_audits if a['quality'] != 'GOOD')
            quality_ratio = 1.0 - (quality_issues / len(recent_audits))
            profile['quality_score'] = max(0.0, quality_ratio)
        
        # Check lattice diversity if available
        if self.lattice is not None:
            unique_values = len(np.unique(self.lattice))
            diversity_ratio = unique_values / self.lattice.size
            profile['metrics']['diversity_ratio'] = diversity_ratio
            profile['metrics']['unique_values'] = unique_values
            
            if diversity_ratio < 0.5:
                profile['quality_score'] *= 0.7
                profile['warnings'].append('Low lattice diversity detected')
                profile['recommendations'].append('Consider reinitializing with fresh seed')
        
        # Check entropy history variance
        if len(self.entropy_history) >= 20:
            recent = self.entropy_history[-20:]
            mean = sum(recent) // len(recent)
            variance_sum = sum((x - mean) ** 2 for x in recent)
            stddev = int((variance_sum / len(recent)) ** 0.5)
            
            profile['metrics']['entropy_stddev'] = stddev
            
            if stddev < 1000:
                profile['quality_score'] *= 0.8
                profile['warnings'].append('Low entropy variance - state may be predictable')
                profile['recommendations'].append('Inject fresh context via update()')
        
        # Check for recent remediation actions
        recent_remediations = [a for a in recent_audits if a['remediation']]
        if recent_remediations:
            profile['warnings'].append(f'{len(recent_remediations)} remediation actions in last 10 operations')
            profile['recommendations'].append('Monitor for persistent entropy issues')
        
        # Determine overall status
        score = profile['quality_score']
        if score >= 0.9:
            profile['status'] = 'excellent'
        elif score >= 0.75:
            profile['status'] = 'good'
        elif score >= 0.6:
            profile['status'] = 'acceptable'
            profile['recommendations'].append('Consider increasing lattice size or depth')
        elif score >= 0.4:
            profile['status'] = 'weak'
            profile['warnings'].append('SECURITY WARNING: Entropy quality below safe threshold')
            profile['recommendations'].append('URGENT: Reinitialize CEL with strong seed')
        else:
            profile['status'] = 'critical'
            profile['warnings'].append('CRITICAL: Entropy failure - DO NOT USE FOR ENCRYPTION')
            profile['recommendations'].append('IMMEDIATE ACTION REQUIRED: Restart CEL')
        
        return profile


# Module-level singleton for convenient access
_global_cel: Optional[ContinuousEntropyLattice] = None


def get_global_cel() -> ContinuousEntropyLattice:
    """
    Get or create global CEL instance
    
    Returns:
        Global CEL instance
    """
    global _global_cel
    if _global_cel is None:
        _global_cel = ContinuousEntropyLattice()
    return _global_cel


def initialize_cel(seed: Union[str, bytes, int], lattice_size: int = 256, depth: int = 8) -> ContinuousEntropyLattice:
    """
    Initialize and return a new CEL instance
    
    Args:
        seed: Seed value for initialization
        lattice_size: Lattice dimension
        depth: Number of lattice layers
        
    Returns:
        Initialized CEL instance
    """
    cel = ContinuousEntropyLattice(lattice_size=lattice_size, depth=depth)
    cel.init(seed)
    return cel
