"""
Polymorphic Cryptographic Flow (PCF)
Manages algorithmic morphing and internal state evolution

Determines operation order, arithmetic base, and transformation
topology dynamically. Every N operations triggers a morph event
that reconfigures the cryptographic behavior.

Key principles:
- Periodic morphing events
- Affects operation order, arithmetic model, folding strategy
- Deterministic within seed context
- Non-repeatable across distinct contexts
"""

from typing import Dict, Any, Optional, List

from utils.math_primitives import (
    permute_sequence,
    data_fingerprint_entropy
)


class PolymorphicCryptographicFlow:
    """
    PCF - Algorithmic morphing and flow control
    
    Manages the evolution of cryptographic behavior through
    deterministic but context-dependent morphing events.
    """
    
    def __init__(self, morph_interval: int = 100, adaptive_morphing: bool = True):
        """
        Initialize PCF (v0.3.0: Enhanced with adaptive morphing)
        
        Args:
            morph_interval: Base number of operations between morph events
            adaptive_morphing: Use CEL-delta-driven adaptive intervals (v0.3.0)
        """
        self.morph_interval = morph_interval
        self.base_morph_interval = morph_interval  # v0.3.0: Store base for adaptive calculation
        self.adaptive_morphing = adaptive_morphing  # v0.3.0: Enable adaptive intervals
        self.operation_count = 0
        self.morph_version = 0
        
        # Meta-state: current configuration
        self.meta_state: Dict[str, Any] = {
            'arithmetic_base': 256,
            'operation_order': ['cel', 'phe', 'cke', 'dsf'],
            'folding_strategy': 'balanced',
            'diffusion_rounds': 3,
            'permutation_rounds': 2,
        }
        
        # CEL binding
        self.cel_snapshot: Optional[Dict[str, Any]] = None
        self.last_cel_entropy: Optional[int] = None  # v0.3.0: Track entropy for delta calculation
        
        # Morph history
        self.morph_history: List[int] = []
        
        # v0.3.0: Context-adaptive tracking
        self.context_hash_history: List[int] = []
        self.operation_pattern: List[str] = []
        
    def cycle(self, meta_state: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Apply polymorphic morph (v0.3.0: Enhanced with adaptive morphing)
        
        Per PCF contract: PCF.cycle(meta_state) → apply polymorphic morph
        
        Args:
            meta_state: Optional external meta-state to influence morph
            
        Returns:
            Updated meta-state
        """
        self.operation_count += 1
        
        # v0.3.0: Track operation patterns for context awareness
        if meta_state and 'operation' in meta_state:
            self.operation_pattern.append(meta_state['operation'])
            if len(self.operation_pattern) > 50:
                self.operation_pattern.pop(0)
        
        # v0.3.0: Determine if morph should occur (adaptive or fixed)
        should_morph = self._should_morph_now(meta_state)
        
        if should_morph:
            self._trigger_morph(meta_state)
        
        return self.meta_state.copy()
    
    def _should_morph_now(self, meta_state: Optional[Dict[str, Any]] = None) -> bool:
        """
        Determine if morph should occur now (v0.3.0: Adaptive decision)
        
        Args:
            meta_state: Optional external state
            
        Returns:
            True if morph should occur
        """
        # Fixed interval mode (backward compatible)
        if not self.adaptive_morphing:
            return self.operation_count % self.morph_interval == 0
        
        # v0.3.0: Adaptive morphing based on CEL entropy delta
        if self.cel_snapshot is None:
            # No CEL bound yet - use fixed interval
            return self.operation_count % self.morph_interval == 0
        
        # Calculate CEL entropy delta
        current_entropy = self.cel_snapshot.get('current_entropy', 0)
        
        if self.last_cel_entropy is None:
            self.last_cel_entropy = current_entropy
            return False  # Skip first check
        
        entropy_delta = abs(current_entropy - self.last_cel_entropy)
        
        # Adaptive interval: morph more frequently when entropy changes rapidly
        # High delta (>10000) → morph every 50 ops
        # Medium delta (1000-10000) → morph every 100 ops (base)
        # Low delta (<1000) → morph every 200 ops
        if entropy_delta > 10000:
            adaptive_interval = max(50, self.base_morph_interval // 2)
        elif entropy_delta > 1000:
            adaptive_interval = self.base_morph_interval
        else:
            adaptive_interval = self.base_morph_interval * 2
        
        self.morph_interval = adaptive_interval  # Update current interval
        
        # Check if it's time to morph
        if self.operation_count % adaptive_interval == 0:
            self.last_cel_entropy = current_entropy
            return True
        
        return False
    
    def _trigger_morph(self, external_state: Optional[Dict[str, Any]] = None) -> None:
        """
        Trigger morphing event
        
        Args:
            external_state: Optional external state to incorporate
        """
        self.morph_version += 1
        
        # Determine morph seed from current state
        morph_seed = self._compute_morph_seed(external_state)
        
        # Morph different aspects based on seed
        self._morph_arithmetic_base(morph_seed)
        self._morph_operation_order(morph_seed)
        self._morph_folding_strategy(morph_seed)
        self._morph_iteration_counts(morph_seed)
        
        # Record morph in history
        self.morph_history.append(morph_seed)
        if len(self.morph_history) > 100:
            self.morph_history.pop(0)
    
    def _compute_morph_seed(self, external_state: Optional[Dict[str, Any]]) -> int:
        """
        Compute seed for morphing (v0.3.0: Enhanced with context awareness)
        
        Args:
            external_state: Optional external state
            
        Returns:
            Morph seed integer
        """
        seed = self.operation_count * 7919 + self.morph_version * 6547
        
        # Incorporate CEL state if available
        if self.cel_snapshot:
            cel_hash = self.cel_snapshot.get('seed_fingerprint', 0)
            cel_version = self.cel_snapshot.get('state_version', 0)
            cel_entropy = self.cel_snapshot.get('current_entropy', 0)
            seed += cel_hash + cel_version * 5381 + (cel_entropy % 65536)
        
        # v0.3.0: Incorporate context hash from external state
        if external_state:
            state_str = str(external_state)
            state_entropy = data_fingerprint_entropy(state_str.encode('utf-8'))
            seed += state_entropy
            
            # Hash the context for pattern detection
            context_hash = hash(state_str) % (2**32)
            self.context_hash_history.append(context_hash)
            if len(self.context_hash_history) > 20:
                self.context_hash_history.pop(0)
            
            # Detect repeating patterns - increase seed variance
            if len(self.context_hash_history) >= 5:
                recent_hashes = self.context_hash_history[-5:]
                if len(set(recent_hashes)) < 3:
                    # Pattern detected - inject randomness
                    import secrets
                    seed += int.from_bytes(secrets.token_bytes(4), 'big')
        
        # Incorporate morph history
        if self.morph_history:
            history_sum = sum(self.morph_history[-10:])
            seed += history_sum
        
        return seed % (2**32)
    
    def _morph_arithmetic_base(self, seed: int) -> None:
        """
        Morph arithmetic base
        
        Args:
            seed: Morph seed
        """
        # Select from multiple possible bases
        bases = [256, 257, 251, 509, 1021, 2053, 4099]  # Primes and powers
        base_idx = seed % len(bases)
        self.meta_state['arithmetic_base'] = bases[base_idx]
    
    def _morph_operation_order(self, seed: int) -> None:
        """
        Morph operation order
        
        Args:
            seed: Morph seed
        """
        operations = ['cel', 'phe', 'cke', 'dsf']
        permuted = permute_sequence(list(range(len(operations))), seed, rounds=3)
        
        new_order = [operations[i] for i in permuted]
        self.meta_state['operation_order'] = new_order
    
    def _morph_folding_strategy(self, seed: int) -> None:
        """
        Morph folding strategy
        
        Args:
            seed: Morph seed
        """
        strategies = ['balanced', 'rotation_heavy', 'diffusion_heavy', 'permutation_heavy', 'adaptive']
        strategy_idx = seed % len(strategies)
        self.meta_state['folding_strategy'] = strategies[strategy_idx]
    
    def _morph_iteration_counts(self, seed: int) -> None:
        """
        Morph iteration counts for various operations
        
        Args:
            seed: Morph seed
        """
        # Diffusion rounds: 2-7
        self.meta_state['diffusion_rounds'] = (seed % 6) + 2
        
        # Permutation rounds: 1-5
        self.meta_state['permutation_rounds'] = ((seed >> 8) % 5) + 1
        
        # Folding depth: 3-8
        self.meta_state['folding_depth'] = ((seed >> 16) % 6) + 3
    
    def bind(self, cel_snapshot: Dict[str, Any]) -> None:
        """
        Synchronize with entropy lattice
        
        Per PCF contract: PCF.bind(CEL) → synchronize with entropy lattice
        
        Args:
            cel_snapshot: CEL snapshot
        """
        self.cel_snapshot = cel_snapshot
        
        # Trigger immediate morph based on new CEL state
        if self.operation_count % self.morph_interval != 0:
            # Force a morph when binding to new CEL state
            self._trigger_morph()
    
    def describe(self) -> str:
        """
        Human-readable representation for debugging
        
        Per PCF contract: PCF.describe() → human-readable representation
        
        Returns:
            Description string
        """
        lines = [
            "=== Polymorphic Cryptographic Flow State ===",
            f"Operation Count: {self.operation_count}",
            f"Morph Version: {self.morph_version}",
            f"Morph Interval: {self.morph_interval}",
            "",
            "Meta-State:",
            f"  Arithmetic Base: {self.meta_state['arithmetic_base']}",
            f"  Operation Order: {' -> '.join(self.meta_state['operation_order'])}",
            f"  Folding Strategy: {self.meta_state['folding_strategy']}",
            f"  Diffusion Rounds: {self.meta_state['diffusion_rounds']}",
            f"  Permutation Rounds: {self.meta_state['permutation_rounds']}",
            f"  Folding Depth: {self.meta_state.get('folding_depth', 'N/A')}",
            "",
            f"CEL Bound: {'Yes' if self.cel_snapshot else 'No'}",
            f"Morph History Length: {len(self.morph_history)}",
        ]
        
        return "\n".join(lines)
    
    def get_meta_state(self) -> Dict[str, Any]:
        """
        Get current meta-state
        
        Returns:
            Meta-state dictionary
        """
        return self.meta_state.copy()
    
    def set_morph_interval(self, interval: int) -> None:
        """
        Update morph interval (base interval for adaptive mode)
        
        Args:
            interval: New morph interval
        """
        if interval <= 0:
            raise ValueError("Morph interval must be positive")
        self.morph_interval = interval
        self.base_morph_interval = interval  # v0.3.0: Update base as well
    
    def get_adaptive_status(self) -> Dict[str, Any]:
        """
        Get adaptive morphing status (v0.3.0)
        
        Returns:
            Dictionary with adaptive morphing metrics
        """
        return {
            'adaptive_enabled': self.adaptive_morphing,
            'base_interval': self.base_morph_interval,
            'current_interval': self.morph_interval,
            'last_cel_entropy': self.last_cel_entropy,
            'context_patterns_detected': len(self.context_hash_history) >= 5 and len(set(self.context_hash_history[-5:])) < 3,
            'operation_pattern_length': len(self.operation_pattern),
            'morph_version': self.morph_version
        }
    
    def get_operation_order(self) -> List[str]:
        """
        Get current operation order
        
        Returns:
            List of operation names in current order
        """
        return self.meta_state['operation_order'].copy()
    
    def get_folding_parameters(self) -> Dict[str, int]:
        """
        Get current folding parameters
        
        Returns:
            Dictionary of folding parameters
        """
        return {
            'diffusion_rounds': self.meta_state['diffusion_rounds'],
            'permutation_rounds': self.meta_state['permutation_rounds'],
            'folding_depth': self.meta_state.get('folding_depth', 5),
        }
    
    def predict_next_morph(self) -> int:
        """
        Predict operations until next morph
        
        Returns:
            Number of operations until next morph event
        """
        return self.morph_interval - (self.operation_count % self.morph_interval)
    
    def export_state(self) -> Dict[str, Any]:
        """
        Export complete PCF state (v0.3.0: includes adaptive state)
        
        Returns:
            State dictionary
        """
        return {
            'operation_count': self.operation_count,
            'morph_version': self.morph_version,
            'morph_interval': self.morph_interval,
            'base_morph_interval': self.base_morph_interval,  # v0.3.0
            'adaptive_morphing': self.adaptive_morphing,  # v0.3.0
            'last_cel_entropy': self.last_cel_entropy,  # v0.3.0
            'meta_state': self.meta_state.copy(),
            'morph_history': self.morph_history.copy(),
            'context_hash_history': self.context_hash_history.copy(),  # v0.3.0
            'operation_pattern': self.operation_pattern.copy(),  # v0.3.0
        }
    
    def import_state(self, state: Dict[str, Any]) -> None:
        """
        Import PCF state (v0.3.0: includes adaptive state)
        
        Args:
            state: State dictionary from export_state()
        """
        self.operation_count = state['operation_count']
        self.morph_version = state['morph_version']
        self.morph_interval = state['morph_interval']
        self.base_morph_interval = state.get('base_morph_interval', state['morph_interval'])  # v0.3.0
        self.adaptive_morphing = state.get('adaptive_morphing', True)  # v0.3.0
        self.last_cel_entropy = state.get('last_cel_entropy')  # v0.3.0
        self.meta_state = state['meta_state'].copy()
        self.morph_history = state['morph_history'].copy()
        self.context_hash_history = state.get('context_hash_history', [])  # v0.3.0
        self.operation_pattern = state.get('operation_pattern', [])  # v0.3.0


def create_pcf(morph_interval: int = 100, adaptive_morphing: bool = True) -> PolymorphicCryptographicFlow:
    """
    Create PCF instance (v0.3.0: Enhanced with adaptive morphing)
    
    Args:
        morph_interval: Operations between morph events (base interval for adaptive mode)
        adaptive_morphing: Enable CEL-delta-driven adaptive intervals (v0.3.0)
        
    Returns:
        PCF instance
    """
    return PolymorphicCryptographicFlow(morph_interval=morph_interval, adaptive_morphing=adaptive_morphing)
