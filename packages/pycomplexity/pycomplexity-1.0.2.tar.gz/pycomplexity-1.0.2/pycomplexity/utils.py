"""
utility functions and complexity types
"""

import math
from enum import Enum
from typing import List, Tuple, Optional
from dataclasses import dataclass
import numpy as np


class ComplexityType(Enum):
    """all major algorithmic complexities"""
    CONSTANT = "O(1)"
    LOG_LOG = "O(log log n)"
    LOGARITHMIC = "O(log n)"
    SQRT = "O(√n)"
    LINEAR = "O(n)"
    LINEARITHMIC = "O(n log n)"
    N_LOG_SQUARED = "O(n log² n)"
    QUADRATIC = "O(n^2)"
    N_SQUARED_SQRT = "O(n^2√n)"
    CUBIC = "O(n^3)"
    QUARTIC = "O(n^4)"
    POLYNOMIAL = "O(n^k)"
    EXPONENTIAL = "O(2^n)"
    FACTORIAL = "O(n!)"
    UNKNOWN = "unknown"
    
    def __str__(self):
        return self.value


@dataclass
class ComplexityResult:
    """holds the result of complexity analysis"""
    complexity_type: ComplexityType
    confidence: float
    operations: int
    input_size: int
    execution_time: float
    details: dict
    
    def __str__(self):
        return (
            f"complexity {self.complexity_type} "
            f"confidence {self.confidence:.1%}\n"
            f"operations {self.operations:,}\n"
            f"input size {self.input_size:,}\n"
            f"time {self.execution_time:.6f}s"
        )


def estimate_complexity(
    sizes: List[int], 
    operations: List[int],
    times: Optional[List[float]] = None
) -> Tuple[ComplexityType, float]:
    """
    figures out complexity from input sizes and operation counts
    returns tuple of complexity type and confidence score
    """
    if len(sizes) < 2:
        return ComplexityType.UNKNOWN, 0.0
    
    sizes = np.array(sizes, dtype=float)
    ops = np.array(operations, dtype=float)
    
    # Handle edge cases
    if len(sizes) == 0 or len(ops) == 0:
        return ComplexityType.UNKNOWN, 0.0
    
    # Ensure minimum values to avoid division issues
    sizes = np.maximum(sizes, 1)
    ops = np.maximum(ops, 1)
    
    # Check for constant complexity first (special case)
    # If all operations are the same (or very close), it's O(1)
    ops_std = np.std(ops)
    ops_mean = np.mean(ops)
    if ops_mean > 0 and ops_std / ops_mean < 0.1:  # Less than 10% variation
        return ComplexityType.CONSTANT, 0.95
    
    # Check if operations don't grow with input size
    # Calculate correlation between sizes and operations
    if np.std(sizes) > 0 and np.std(ops) > 0:
        correlation = np.corrcoef(sizes, ops)[0, 1]
        if np.isnan(correlation):
            correlation = 0
    else:
        correlation = 0
    
    # If very low correlation, likely constant
    if abs(correlation) < 0.3:
        return ComplexityType.CONSTANT, 0.7
    
    # Define complexity functions for curve fitting
    complexity_functions = {
        ComplexityType.CONSTANT: lambda n: np.ones_like(n),
        ComplexityType.LOG_LOG: lambda n: np.maximum(np.log2(np.maximum(np.log2(n + 1), 1)), 0.1),
        ComplexityType.LOGARITHMIC: lambda n: np.log2(n + 1),
        ComplexityType.SQRT: lambda n: np.sqrt(n),
        ComplexityType.LINEAR: lambda n: n,
        ComplexityType.LINEARITHMIC: lambda n: n * np.log2(n + 1),
        ComplexityType.N_LOG_SQUARED: lambda n: n * (np.log2(n + 1) ** 2),
        ComplexityType.QUADRATIC: lambda n: n ** 2,
        ComplexityType.N_SQUARED_SQRT: lambda n: (n ** 2) * np.sqrt(n),
        ComplexityType.CUBIC: lambda n: n ** 3,
        ComplexityType.QUARTIC: lambda n: n ** 4,
        ComplexityType.EXPONENTIAL: lambda n: np.minimum(2 ** np.minimum(n, 50), 1e15),
    }
    
    best_fit = ComplexityType.UNKNOWN
    best_score = -float('inf')
    
    for complexity_type, func in complexity_functions.items():
        try:
            expected = func(sizes)
            
            # Skip if invalid values
            if np.any(np.isnan(expected)) or np.any(np.isinf(expected)):
                continue
            
            # Skip if all zeros or negative
            if np.max(expected) <= 0 or np.max(ops) <= 0:
                continue
            
            # Normalize both arrays
            expected_norm = expected / np.max(expected)
            ops_norm = ops / np.max(ops)
            
            # Calculate correlation
            corr_matrix = np.corrcoef(expected_norm, ops_norm)
            if corr_matrix.shape == (2, 2):
                corr = corr_matrix[0, 1]
            else:
                continue
            
            if np.isnan(corr):
                continue
            
            # Calculate RMSE
            rmse = np.sqrt(np.mean((expected_norm - ops_norm) ** 2))
            
            # Combined score: high correlation, low RMSE
            score = corr - rmse * 0.5
            
            if score > best_score:
                best_score = score
                best_fit = complexity_type
                
        except (ValueError, RuntimeWarning, FloatingPointError, IndexError):
            continue
    
    # Detect factorial (grows faster than exponential)
    if len(sizes) >= 2 and best_fit == ComplexityType.EXPONENTIAL:
        try:
            growth_ratios = []
            for i in range(1, len(ops)):
                if ops[i-1] > 0:
                    growth_ratios.append(ops[i] / ops[i-1])
            
            if growth_ratios:
                avg_growth = np.mean(growth_ratios)
                size_diff = np.mean(np.diff(sizes))
                
                # Factorial grows roughly by factor of n each step
                if avg_growth > 2 ** size_diff * 1.5:
                    best_fit = ComplexityType.FACTORIAL
                    best_score = min(best_score, 0.7)
        except:
            pass
    
    # Convert score to confidence (0 to 1)
    confidence = max(0.0, min(1.0, (best_score + 1) / 2))
    
    # If we still have UNKNOWN but have data, make a guess based on growth rate
    if best_fit == ComplexityType.UNKNOWN and len(sizes) >= 2:
        growth_rate = calculate_growth_rate(list(sizes), list(ops))
        best_fit = complexity_from_growth_rate(growth_rate)
        confidence = 0.4
    
    return best_fit, confidence


def format_complexity(
    complexity_type: ComplexityType,
    operations: int,
    time_taken: float,
    input_size: Optional[int] = None,
    color: bool = True
) -> str:
    """formats complexity result for console output"""
    
    COLORS = {
        ComplexityType.CONSTANT: "\033[92m",           # Green
        ComplexityType.LOG_LOG: "\033[92m",            # Green
        ComplexityType.LOGARITHMIC: "\033[92m",        # Green
        ComplexityType.SQRT: "\033[92m",               # Green
        ComplexityType.LINEAR: "\033[93m",             # Yellow
        ComplexityType.LINEARITHMIC: "\033[93m",       # Yellow
        ComplexityType.N_LOG_SQUARED: "\033[93m",      # Yellow
        ComplexityType.QUADRATIC: "\033[38;5;208m",    # Orange
        ComplexityType.N_SQUARED_SQRT: "\033[38;5;208m", # Orange
        ComplexityType.CUBIC: "\033[38;5;208m",        # Orange
        ComplexityType.QUARTIC: "\033[38;5;208m",      # Orange
        ComplexityType.POLYNOMIAL: "\033[91m",         # Red
        ComplexityType.EXPONENTIAL: "\033[91m",        # Red
        ComplexityType.FACTORIAL: "\033[91m",          # Red
        ComplexityType.UNKNOWN: "\033[90m",            # Gray
    }
    RESET = "\033[0m"
    BOLD = "\033[1m"
    
    color_code = COLORS.get(complexity_type, "") if color else ""
    reset_code = RESET if color else ""
    bold_code = BOLD if color else ""
    
    lines = [
        f"{bold_code}complexity analysis result{reset_code}",
        f"complexity {color_code}{str(complexity_type)}{reset_code}",
        f"operations {operations:,}",
        f"time       {time_taken:.6f} seconds",
    ]
    
    if input_size is not None:
        lines.append(f"input size {input_size:,}")
    
    return "\n".join(lines)


def calculate_growth_rate(sizes: List[int], values: List[float]) -> float:
    """calculates the growth rate of values relative to input sizes"""
    if len(sizes) < 2:
        return 0.0
    
    sizes = np.array(sizes, dtype=float)
    values = np.array(values, dtype=float)
    
    # Handle zeros and negatives
    sizes = np.maximum(sizes, 1)
    values = np.maximum(values, 1)
    
    try:
        log_sizes = np.log(sizes)
        log_values = np.log(values)
        
        # Linear regression in log-log space gives us the exponent
        coeffs = np.polyfit(log_sizes, log_values, 1)
        
        return coeffs[0]
    except:
        return 1.0  # Default to linear


def complexity_from_growth_rate(rate: float) -> ComplexityType:
    """figures out complexity type from growth rate"""
    if rate < 0.1:
        return ComplexityType.CONSTANT
    elif rate < 0.3:
        return ComplexityType.LOG_LOG
    elif rate < 0.6:
        return ComplexityType.LOGARITHMIC
    elif rate < 0.8:
        return ComplexityType.SQRT
    elif rate < 1.2:
        return ComplexityType.LINEAR
    elif rate < 1.6:
        return ComplexityType.LINEARITHMIC
    elif rate < 1.9:
        return ComplexityType.N_LOG_SQUARED
    elif rate < 2.2:
        return ComplexityType.QUADRATIC
    elif rate < 2.7:
        return ComplexityType.N_SQUARED_SQRT
    elif rate < 3.2:
        return ComplexityType.CUBIC
    elif rate < 4.2:
        return ComplexityType.QUARTIC
    elif rate < 8.0:
        return ComplexityType.EXPONENTIAL
    else:
        return ComplexityType.FACTORIAL


def get_complexity_description(complexity_type: ComplexityType) -> str:
    """returns a human-readable description of the complexity"""
    descriptions = {
        ComplexityType.CONSTANT: "Excellent - Always takes the same time regardless of input size",
        ComplexityType.LOG_LOG: "Excellent - Extremely slow growth, highly scalable",
        ComplexityType.LOGARITHMIC: "Excellent - Barely increases with more data, very scalable",
        ComplexityType.SQRT: "Very Good - Moderate growth, scalable to large inputs",
        ComplexityType.LINEAR: "Good - Doubles time when data doubles, acceptable for large data",
        ComplexityType.LINEARITHMIC: "Good - Slightly worse than linear, typical of efficient sorts",
        ComplexityType.N_LOG_SQUARED: "Fair - Between linearithmic and quadratic",
        ComplexityType.QUADRATIC: "Poor - Time quadruples when data doubles, only for small inputs",
        ComplexityType.N_SQUARED_SQRT: "Poor - Between quadratic and cubic complexity",
        ComplexityType.CUBIC: "Very Poor - Time increases 8x when data doubles, very limited",
        ComplexityType.QUARTIC: "Very Poor - Time increases 16x when data doubles, extremely limited",
        ComplexityType.POLYNOMIAL: "Poor - Higher degree polynomial, limited practical use",
        ComplexityType.EXPONENTIAL: "Terrible - Explodes rapidly, only works for tiny inputs",
        ComplexityType.FACTORIAL: "Catastrophic - Practically unusable beyond n=12",
        ComplexityType.UNKNOWN: "Cannot determine - need more data or clearer patterns",
    }
    return descriptions.get(complexity_type, "Unknown complexity type")


def get_practical_limit(complexity_type: ComplexityType) -> str:
    """returns practical input size limits for each complexity"""
    limits = {
        ComplexityType.CONSTANT: "Unlimited",
        ComplexityType.LOG_LOG: "Unlimited",
        ComplexityType.LOGARITHMIC: "Unlimited",
        ComplexityType.SQRT: "~1,000,000",
        ComplexityType.LINEAR: "~10,000,000",
        ComplexityType.LINEARITHMIC: "~1,000,000",
        ComplexityType.N_LOG_SQUARED: "~500,000",
        ComplexityType.QUADRATIC: "~10,000",
        ComplexityType.N_SQUARED_SQRT: "~5,000",
        ComplexityType.CUBIC: "~1,000",
        ComplexityType.QUARTIC: "~500",
        ComplexityType.POLYNOMIAL: "Depends on degree",
        ComplexityType.EXPONENTIAL: "~25",
        ComplexityType.FACTORIAL: "~12",
        ComplexityType.UNKNOWN: "Unknown",
    }
    return limits.get(complexity_type, "Unknown")


def analyze_from_function(func, test_sizes: List[int] = None) -> Tuple[ComplexityType, float, dict]:
    """
    Analyze a function's complexity by running it with different input sizes
    
    Args:
        func: A function that takes a list/array as input
        test_sizes: List of input sizes to test (default: [10, 50, 100, 500, 1000])
    
    Returns:
        Tuple of (complexity_type, confidence, details_dict)
    """
    import time
    
    if test_sizes is None:
        test_sizes = [10, 50, 100, 500, 1000]
    
    sizes = []
    times = []
    
    for size in test_sizes:
        try:
            # Generate test input
            test_input = list(range(size))
            
            # Measure time
            start = time.perf_counter()
            func(test_input)
            end = time.perf_counter()
            
            sizes.append(size)
            times.append(end - start)
        except Exception as e:
            continue
    
    if len(sizes) < 2:
        return ComplexityType.UNKNOWN, 0.0, {'error': 'Not enough successful runs'}
    
    # Use times as proxy for operations
    # Normalize times to avoid floating point issues
    min_time = min(times)
    if min_time > 0:
        ops = [int(t / min_time * 1000) for t in times]
    else:
        ops = [1000] * len(times)
    
    complexity_type, confidence = estimate_complexity(sizes, ops, times)
    
    details = {
        'sizes': sizes,
        'times': times,
        'operations': ops
    }
    
    return complexity_type, confidence, details