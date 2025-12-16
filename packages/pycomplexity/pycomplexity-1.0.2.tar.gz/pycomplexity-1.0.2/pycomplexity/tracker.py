"""
operation tracker for detailed complexity analysis
"""

import time
from typing import Optional, Callable, Any
from contextlib import contextmanager
from dataclasses import dataclass, field
from collections import defaultdict

from .utils import ComplexityType, format_complexity


@dataclass
class OperationStats:
    count: int = 0
    total_time: float = 0.0
    min_time: float = float('inf')
    max_time: float = 0.0
    
    def record(self, duration: float):
        self.count += 1
        self.total_time += duration
        self.min_time = min(self.min_time, duration)
        self.max_time = max(self.max_time, duration)
    
    @property
    def avg_time(self) -> float:
        return self.total_time / self.count if self.count > 0 else 0


class OperationTracker:
    """
    track individual operations for detailed complexity analysis
    
    usage
        tracker = OperationTracker("algorithm")
        
        for i in range(n):
            tracker.track("comparison")
            if condition:
                tracker.track("swap")
        
        tracker.report()
    """
    
    def __init__(self, name: str = "tracker", input_size: Optional[int] = None):
        self.name = name
        self.input_size = input_size
        self.operations: dict[str, OperationStats] = defaultdict(OperationStats)
        self.start_time = time.perf_counter()
        self._operation_times: dict[str, float] = {}
    
    def track(self, operation: str = "default", count: int = 1):
        """track an operation"""
        for _ in range(count):
            self.operations[operation].count += 1
    
    def start_operation(self, operation: str):
        """start timing an operation"""
        self._operation_times[operation] = time.perf_counter()
    
    def end_operation(self, operation: str):
        """end timing an operation"""
        if operation in self._operation_times:
            duration = time.perf_counter() - self._operation_times[operation]
            self.operations[operation].record(duration)
            del self._operation_times[operation]
    
    @contextmanager
    def operation(self, name: str):
        """context manager for timing an operation"""
        start = time.perf_counter()
        try:
            yield
        finally:
            duration = time.perf_counter() - start
            self.operations[name].record(duration)
    
    @property
    def total_operations(self) -> int:
        return sum(stats.count for stats in self.operations.values())
    
    @property
    def elapsed_time(self) -> float:
        return time.perf_counter() - self.start_time
    
    def estimate_complexity(self) -> ComplexityType:
        ops = self.total_operations
        n = self.input_size or ops
        
        if n <= 0:
            return ComplexityType.UNKNOWN
        
        ratio = ops / n
        
        if ratio < 1.5:
            return ComplexityType.CONSTANT
        elif ratio < 2:
            return ComplexityType.LOGARITHMIC
        elif ratio < n * 0.5:
            return ComplexityType.LINEAR
        elif ratio < n:
            return ComplexityType.LINEARITHMIC
        elif ratio < n * n * 0.5:
            return ComplexityType.QUADRATIC
        else:
            return ComplexityType.EXPONENTIAL
    
    def report(self, detailed: bool = True):
        complexity = self.estimate_complexity()
        
        print(f"\n{'='*60}")
        print(f"operation tracker report {self.name}")
        print(f"{'='*60}")
        
        print(f"\nestimated complexity {complexity}")
        print(f"total operations {self.total_operations:,}")
        print(f"elapsed time {self.elapsed_time:.6f}s")
        
        if self.input_size:
            print(f"input size n {self.input_size:,}")
            print(f"operations per n {self.total_operations / self.input_size:.2f}")
        
        if detailed and self.operations:
            print(f"\n{'-'*60}")
            print("operation breakdown")
            print(f"{'-'*60}")
            print(f"{'operation':<25} {'count':>12} {'avg time':>15}")
            print(f"{'-'*60}")
            
            for op_name, stats in sorted(
                self.operations.items(), 
                key=lambda x: x[1].count, 
                reverse=True
            ):
                avg_time = f"{stats.avg_time*1000:.4f}ms" if stats.avg_time > 0 else "n/a"
                print(f"{op_name:<25} {stats.count:>12,} {avg_time:>15}")
        
        print(f"{'='*60}\n")
    
    def get_summary(self) -> dict:
        return {
            'name': self.name,
            'complexity': self.estimate_complexity(),
            'total_operations': self.total_operations,
            'elapsed_time': self.elapsed_time,
            'input_size': self.input_size,
            'operations': {
                name: {'count': stats.count, 'avg_time': stats.avg_time}
                for name, stats in self.operations.items()
            }
        }


@contextmanager
def track_operations(name: str = "block", input_size: Optional[int] = None):
    """context manager for tracking operations in a code block"""
    tracker = OperationTracker(name, input_size)
    try:
        yield tracker
    finally:
        tracker.report()
