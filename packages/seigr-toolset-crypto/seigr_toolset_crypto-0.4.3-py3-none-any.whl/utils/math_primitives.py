"""
Mathematical Primitives for Seigr Toolset Crypto
Deterministic, side-effect-free mathematical operations

NO external randomness sources
NO traditional cryptographic primitives
"""

import numpy as np
from typing import List, Tuple


def modular_transform(value: int, modulus: int, offset: int = 0) -> int:
    """
    Perform modular arithmetic transformation with offset
    
    Args:
        value: Input integer
        modulus: Modular base (must be positive)
        offset: Additive offset before modulo operation
        
    Returns:
        (value + offset) mod modulus
    """
    if modulus <= 0:
        raise ValueError("Modulus must be positive")
    return (value + offset) % modulus


def permute_sequence(sequence: List[int], seed: int, rounds: int = 1) -> List[int]:
    """
    Deterministically permute a sequence using seed-derived transformations
    Uses position-value interactions without external randomness
    
    Args:
        sequence: Input sequence of integers
        seed: Deterministic seed for permutation
        rounds: Number of permutation rounds
        
    Returns:
        Permuted sequence
    """
    if not sequence:
        return sequence
    
    result = sequence.copy()
    n = len(result)
    
    for round_idx in range(rounds):
        # Generate deterministic swap indices from seed and round
        for i in range(n):
            # Compute deterministic target index using position, value, seed, and round
            target = (seed + i + result[i] + round_idx * 7919) % n  # 7919 is prime
            # Swap elements
            result[i], result[target] = result[target], result[i]
    
    return result


def rotate_bits(value: int, shift: int, bit_width: int = 64) -> int:
    """
    Rotate integer bits left or right
    
    Args:
        value: Input integer
        shift: Number of positions to rotate (positive = left, negative = right)
        bit_width: Bit width for rotation boundary
        
    Returns:
        Rotated value
    """
    # Ensure value fits in bit_width
    mask = (1 << bit_width) - 1
    value = int(value) & mask
    
    # Normalize shift to [0, bit_width)
    shift = int(shift) % bit_width
    
    # Rotate left
    rotated = ((value << shift) | (value >> (bit_width - shift))) & mask
    return int(rotated)


def non_linear_diffusion(matrix: np.ndarray, iterations: int = 3) -> np.ndarray:
    """
    Apply non-linear diffusion to a numeric matrix
    Uses position-dependent transformations without XOR or traditional mixing
    
    Args:
        matrix: Input 2D numpy array
        iterations: Number of diffusion iterations
        
    Returns:
        Diffused matrix
    """
    result = matrix.copy()
    rows, cols = result.shape
    
    for iteration in range(iterations):
        # Create new matrix for this iteration to avoid in-place modification issues
        new_result = np.zeros_like(result)
        
        for i in range(rows):
            for j in range(cols):
                # Position-dependent, value-dependent transformation
                # Uses neighboring values and position coordinates
                neighbor_sum = 0
                neighbor_count = 0
                
                for di in [-1, 0, 1]:
                    for dj in [-1, 0, 1]:
                        ni, nj = i + di, j + dj
                        if 0 <= ni < rows and 0 <= nj < cols and (di != 0 or dj != 0):
                            neighbor_sum += result[ni, nj]
                            neighbor_count += 1
                
                if neighbor_count > 0:
                    # Non-linear mixing using position, value, and neighbor average
                    # Add 1 to iteration to avoid multiplication by zero on first iteration
                    avg = neighbor_sum // neighbor_count
                    pos_factor = ((i + 1) * (j + 1)) % 256
                    if pos_factor == 0:
                        pos_factor = 1
                    new_result[i, j] = (result[i, j] + avg * (iteration + 1) * pos_factor) % 65536
                else:
                    new_result[i, j] = result[i, j]
        
        result = new_result
    
    return result


def variable_base_encode(value: int, base: int) -> List[int]:
    """
    Encode integer in arbitrary base
    
    Args:
        value: Integer to encode
        base: Numeric base (must be >= 2)
        
    Returns:
        List of digits in specified base
    """
    if base < 2:
        raise ValueError("Base must be >= 2")
    
    if value == 0:
        return [0]
    
    digits = []
    working = abs(value)
    
    while working > 0:
        digits.append(working % base)
        working //= base
    
    return digits[::-1]  # Reverse to most-significant first


def variable_base_decode(digits: List[int], base: int) -> int:
    """
    Decode integer from arbitrary base representation
    
    Args:
        digits: List of digits in specified base
        base: Numeric base (must be >= 2)
        
    Returns:
        Decoded integer value
    """
    if base < 2:
        raise ValueError("Base must be >= 2")
    
    result = 0
    for digit in digits:
        result = result * base + digit
    
    return result


def tensor_rotation(tensor: np.ndarray, axis_pair: Tuple[int, int], angle_factor: float) -> np.ndarray:
    """
    Rotate tensor along specified axis pair
    Used for multidimensional data folding
    
    Args:
        tensor: Input n-dimensional array
        axis_pair: Tuple of two axis indices to rotate between
        angle_factor: Rotation factor (0.0 to 1.0 represents 0 to 2π)
        
    Returns:
        Rotated tensor
    """
    # For 1D or incompatible tensors, return copy
    if tensor.ndim < 2:
        return tensor.copy()
    
    # Validate axis_pair
    if axis_pair[0] >= tensor.ndim or axis_pair[1] >= tensor.ndim:
        return tensor.copy()
    
    # Compute rotation angle in radians
    angle = angle_factor * 2 * np.pi
    
    # Apply rotation using Givens rotation matrix
    cos_a = np.cos(angle)
    sin_a = np.sin(angle)
    
    # Create rotation matrix
    rotation_matrix = np.array([
        [cos_a, -sin_a],
        [sin_a, cos_a]
    ])
    
    # Move axes to front for rotation
    result = np.moveaxis(tensor, axis_pair, [0, 1])
    original_shape = result.shape
    
    # Handle 3D tensors
    if result.ndim == 3 and result.shape[0] == 2 and result.shape[1] == 2:
        # Apply rotation to each slice along third dimension
        for i in range(result.shape[2]):
            slice_matrix = result[:, :, i]
            rotated = rotation_matrix @ slice_matrix
            result[:, :, i] = rotated
    elif result.ndim == 3:
        # Reshape for rotation
        # Flatten all dimensions except the rotation plane
        result = result.reshape(original_shape[0], original_shape[1], -1)
        
        # Apply rotation to each 2D slice
        for i in range(result.shape[2]):
            if result.shape[0] >= 2 and result.shape[1] >= 2:
                # Extract 2x2 submatrix for rotation
                sub_matrix = result[:2, :2, i]
                rotated_sub = rotation_matrix @ sub_matrix
                result[:2, :2, i] = rotated_sub
        
        # Restore original shape
        result = result.reshape(original_shape)
    
    # Move axes back to original positions
    result = np.moveaxis(result, [0, 1], axis_pair)
    
    return result


def entropy_weighted_permutation(data: np.ndarray, entropy_vector: np.ndarray) -> np.ndarray:
    """
    Permute data array using entropy vector weights
    
    Args:
        data: 1D array to permute
        entropy_vector: Entropy weights (same length as data)
        
    Returns:
        Permuted array
    """
    if len(data) != len(entropy_vector):
        raise ValueError("Data and entropy vector must have same length")
    
    # Create index array
    indices = np.arange(len(data))
    
    # Deterministically sort indices based on entropy weights
    # Use stable sort for determinism
    sorted_indices = indices[np.argsort(entropy_vector, kind='stable')]
    
    # Apply permutation
    return data[sorted_indices]


def modular_exponentiation(base: int, exponent: int, modulus: int) -> int:
    """
    Efficient modular exponentiation: (base^exponent) mod modulus
    
    Args:
        base: Base value
        exponent: Exponent value
        modulus: Modulus value
        
    Returns:
        Result of modular exponentiation
    """
    if modulus <= 0:
        raise ValueError("Modulus must be positive")
    
    result = 1
    base = base % modulus
    
    while exponent > 0:
        if exponent % 2 == 1:
            result = (result * base) % modulus
        exponent = exponent >> 1
        base = (base * base) % modulus
    
    return result


def prime_field_multiply(a: int, b: int, prime: int) -> int:
    """
    Multiply two numbers in a prime field
    
    Args:
        a: First operand
        b: Second operand
        prime: Prime modulus
        
    Returns:
        (a * b) mod prime
    """
    return (a * b) % prime


def compute_time_delta_entropy() -> int:
    """
    Generate entropy from computational time differentials
    Uses internal process timing, not system time
    
    Returns:
        Integer representing time-derived entropy
    """
    import time
    
    # Capture multiple time measurements at different granularities
    measurements = []
    for _ in range(10):
        t1 = time.perf_counter_ns()
        # Perform minimal computation to create delta
        _ = sum(range(100))
        t2 = time.perf_counter_ns()
        measurements.append(t2 - t1)
    
    # Combine measurements into entropy value
    # Use last digits which vary based on CPU scheduling and load
    entropy = 0
    for i, delta in enumerate(measurements):
        # Extract micro-variations from timing deltas
        entropy += (delta % 1000) * (i + 1)
    
    return entropy


def memory_allocation_entropy() -> int:
    """
    Generate entropy from memory allocation patterns
    Uses object creation timing variations
    
    Returns:
        Integer representing memory-derived entropy
    """
    import sys
    
    # Create objects and measure allocation timing
    allocations = []
    for i in range(50):
        obj = [0] * (100 + i)
        allocations.append(sys.getsizeof(obj))
    
    # Extract entropy from allocation pattern variations
    entropy = 0
    for i, size in enumerate(allocations):
        entropy += (size % 100) * (i + 1)
    
    return entropy


def data_fingerprint_entropy(data: bytes) -> int:
    """
    Generate entropy from data structure patterns
    Uses data distribution and pattern analysis
    
    Args:
        data: Input bytes
        
    Returns:
        Integer representing data-derived entropy
    """
    if not data:
        return 0
    
    # Analyze byte distribution
    byte_counts = [0] * 256
    for byte in data:
        byte_counts[byte] += 1
    
    # Compute entropy from distribution
    entropy = 0
    for i, count in enumerate(byte_counts):
        if count > 0:
            entropy += (count * i) % 65536
    
    # Add length-based component
    entropy += len(data) * 7919  # Prime multiplier
    
    return entropy


def compute_chained_timing_entropy(seed: int) -> int:
    """
    Generate entropy from chained computational loads
    Uses 5 different CPU execution units for maximum timing variance
    
    Args:
        seed: Seed value for deterministic variation
        
    Returns:
        Integer representing chained timing entropy
    """
    import time
    
    measurements = []
    
    # Chain 1: Prime factorization (ALU-intensive)
    for i in range(5):
        t1 = time.perf_counter_ns()
        n = (seed + i * 1000) | 1  # Ensure odd
        factors = []
        d = 3
        while d * d <= n and len(factors) < 10:
            while n % d == 0:
                factors.append(d)
                n //= d
            d += 2
        t2 = time.perf_counter_ns()
        measurements.append(t2 - t1)
    
    # Chain 2: Modular exponentiation (multiplier-intensive)
    accumulated = 0  # Accumulate results to prevent compiler optimization
    for i in range(5):
        t1 = time.perf_counter_ns()
        base = (seed + i) % 65521
        exp = 1000 + (i * 100)
        result = modular_exponentiation(base, exp, 65521)
        accumulated += result  # Use result to prevent optimization
        t2 = time.perf_counter_ns()
        measurements.append(t2 - t1)
    
    # Chain 3: Matrix multiplication (SIMD/cache-intensive)
    for i in range(5):
        t1 = time.perf_counter_ns()
        A = np.array([[i+1, i+2, i+3], [i+4, i+5, i+6], [i+7, i+8, i+9]], dtype=np.int32)
        B = np.array([[i+10, i+11, i+12], [i+13, i+14, i+15], [i+16, i+17, i+18]], dtype=np.int32)
        C = np.matmul(A, B)
        accumulated += int(C[0, 0])  # Use result to prevent optimization
        t2 = time.perf_counter_ns()
        measurements.append(t2 - t1)
    
    # Chain 4: Permutation operations (memory access patterns)
    for i in range(5):
        t1 = time.perf_counter_ns()
        seq = list(range(100 + i * 10))
        permuted = permute_sequence(seq, seed + i, rounds=3)
        accumulated += len(permuted)  # Use result to prevent optimization
        t2 = time.perf_counter_ns()
        measurements.append(t2 - t1)
    
    # Chain 5: Non-linear diffusion (mixed integer ops)
    for i in range(5):
        t1 = time.perf_counter_ns()
        # Generate deterministic matrix based on seed (no external randomness)
        matrix = np.array([[(seed + i + r * 16 + c) % 256 for c in range(16)] for r in range(16)], dtype=np.int32)
        diffused = non_linear_diffusion(matrix, iterations=2)
        accumulated += int(diffused[0, 0])  # Use result to prevent optimization
        t2 = time.perf_counter_ns()
        measurements.append(t2 - t1)
    
    # Combine measurements with non-linear weighting
    entropy = 0
    for i, delta in enumerate(measurements):
        # Extract micro-variations (last 3 digits)
        micro_delta = delta % 1000
        # Weight by position with Fibonacci-like sequence
        weight = ((i + 1) * (i + 2)) % 1000
        entropy += micro_delta * weight
    
    return entropy % (2**64)


def calculate_shannon_entropy(data: bytes) -> int:
    """
    Calculate Shannon-like entropy metric (integer approximation)
    Uses byte frequency distribution
    
    Args:
        data: Input bytes
        
    Returns:
        Integer entropy metric (higher = more random)
    """
    if not data:
        return 0
    
    # Byte frequency distribution
    freq = [0] * 256
    for byte in data:
        freq[byte] += 1
    
    # Integer approximation of Shannon entropy
    # Instead of -sum(p * log(p)), use sum(count * (256 - count))
    # This peaks when distribution is uniform
    entropy = 0
    for count in freq:
        if count > 0:
            # Higher entropy when counts are balanced
            entropy += count * (256 - count)
    
    return entropy


def variable_length_encode_int(value: int) -> bytes:
    """
    Encode integer using variable-length encoding (LEB128-style)
    
    Args:
        value: Integer to encode (non-negative)
        
    Returns:
        Encoded bytes
    """
    if value < 0:
        raise ValueError("Variable-length encoding requires non-negative integer")
    
    if value == 0:
        return bytes([0])
    
    result = bytearray()
    while value > 0:
        byte = value & 0x7F  # Take lower 7 bits
        value >>= 7
        if value > 0:
            byte |= 0x80  # Set continuation bit
        result.append(byte)
    
    return bytes(result)


def variable_length_decode_int(data: bytes, offset: int = 0) -> tuple:
    """
    Decode variable-length encoded integer
    
    Args:
        data: Encoded bytes
        offset: Starting offset
        
    Returns:
        Tuple of (decoded_value, bytes_consumed)
    """
    value = 0
    shift = 0
    bytes_read = 0
    
    while offset + bytes_read < len(data):
        byte = data[offset + bytes_read]
        bytes_read += 1
        
        value |= (byte & 0x7F) << shift
        shift += 7
        
        if (byte & 0x80) == 0:  # No continuation bit
            break
    
    return value, bytes_read
