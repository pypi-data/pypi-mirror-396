"""
core complexity analyzer using context manager
"""

import time
import sys
import threading
from typing import Optional, Callable, Any, List
from contextlib import contextmanager
from dataclasses import dataclass, field

from .utils import (
    ComplexityType, 
    ComplexityResult, 
    estimate_complexity,
    format_complexity,
    calculate_growth_rate,
    complexity_from_growth_rate,
    get_complexity_description
)


class ComplexityAnalyzer:
    """
    context manager for analyzing code complexity during execution
    
    usage
        with ComplexityAnalyzer("my_algorithm") as analyzer:
            for i in range(n):
                analyzer.count_operation()
    """
    
    _instances = {}
    _lock = threading.Lock()
    
    def __init__(
        self,
        name: str = "anonymous",
        input_size: Optional[int] = None,
        auto_detect: bool = True,
        verbose: bool = True,
        track_memory: bool = False
    ):
        self.name = name
        self.input_size = input_size
        self.auto_detect = auto_detect
        self.verbose = verbose
        self.track_memory = track_memory
        
        self.operation_count = 0
        self.loop_iterations = 0
        self.function_calls = 0
        self.line_executions = 0
        
        self.start_time = 0.0
        self.end_time = 0.0
        
        self.start_memory = 0
        self.peak_memory = 0
        
        self.result: Optional[ComplexityResult] = None
        self._history: List[dict] = []
        self._original_trace = None
        
    def __enter__(self):
        self.start_time = time.perf_counter()
        self.operation_count = 0
        self.loop_iterations = 0
        self.function_calls = 0
        self.line_executions = 0
        
        if self.auto_detect:
            self._original_trace = sys.gettrace()
            sys.settrace(self._trace_function)
        
        if self.track_memory:
            try:
                import tracemalloc
                tracemalloc.start()
                self.start_memory = tracemalloc.get_traced_memory()[0]
            except ImportError:
                pass
        
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end_time = time.perf_counter()
        
        if self.auto_detect:
            sys.settrace(self._original_trace)
        
        if self.track_memory:
            try:
                import tracemalloc
                _, self.peak_memory = tracemalloc.get_traced_memory()
                tracemalloc.stop()
            except ImportError:
                pass
        
        self._calculate_complexity()
        
        self._history.append({
            'input_size': self.input_size,
            'operations': self.total_operations,
            'time': self.execution_time
        })
        
        if self.verbose:
            self._print_results()
        
        return False
    
    def _trace_function(self, frame, event, arg):
        if event == 'line':
            self.line_executions += 1
        elif event == 'call':
            self.function_calls += 1
        return self._trace_function
    
    def count_operation(self, count: int = 1):
        """manually count operations call this inside loops"""
        self.operation_count += count
    
    def count_iteration(self, count: int = 1):
        """count loop iterations"""
        self.loop_iterations += count
        self.operation_count += count
    
    @property
    def total_operations(self) -> int:
        if self.operation_count > 0:
            return self.operation_count
        return max(self.line_executions, self.loop_iterations, 1)
    
    @property
    def execution_time(self) -> float:
        return self.end_time - self.start_time
    
    def _calculate_complexity(self):
        ops = self.total_operations
        n = self.input_size or ops
        
        if n > 0:
            ratio = ops / n
            
            if ratio < 1.2:
                complexity_type = ComplexityType.CONSTANT
                confidence = 0.6
            elif ratio < 2:
                complexity_type = ComplexityType.LOGARITHMIC
                confidence = 0.5
            elif ratio < n * 0.1:
                complexity_type = ComplexityType.SQRT
                confidence = 0.5
            elif ratio < n * 0.5:
                complexity_type = ComplexityType.LINEAR
                confidence = 0.6
            elif ratio < n * 2:
                complexity_type = ComplexityType.LINEARITHMIC
                confidence = 0.5
            elif ratio < n * n * 0.3:
                complexity_type = ComplexityType.QUADRATIC
                confidence = 0.6
            elif ratio < n * n * 2:
                complexity_type = ComplexityType.N_SQUARED_SQRT
                confidence = 0.5
            elif ratio < n * n * n * 0.3:
                complexity_type = ComplexityType.CUBIC
                confidence = 0.5
            elif ratio < n * n * n * n * 0.3:
                complexity_type = ComplexityType.QUARTIC
                confidence = 0.4
            else:
                complexity_type = ComplexityType.EXPONENTIAL
                confidence = 0.4
        else:
            complexity_type = ComplexityType.UNKNOWN
            confidence = 0.0
        
        if len(self._history) >= 2:
            sizes = [h['input_size'] for h in self._history if h['input_size']]
            operations = [h['operations'] for h in self._history]
            
            if sizes:
                complexity_type, confidence = estimate_complexity(sizes, operations)
        
        self.result = ComplexityResult(
            complexity_type=complexity_type,
            confidence=confidence,
            operations=ops,
            input_size=n,
            execution_time=self.execution_time,
            details={
                'manual_operations': self.operation_count,
                'loop_iterations': self.loop_iterations,
                'function_calls': self.function_calls,
                'line_executions': self.line_executions,
                'peak_memory': self.peak_memory
            }
        )
    
    def _print_results(self):
        if self.result:
            print(f"\ncomplexity analysis for {self.name}")
            print(format_complexity(
                self.result.complexity_type,
                self.result.operations,
                self.result.execution_time,
                self.input_size
            ))
            
            description = get_complexity_description(self.result.complexity_type)
            print(f"\n{description}")
            
            if self.result.confidence < 0.5:
                print("\nLow confidence - run with more varied input sizes for better accuracy")
    
    @classmethod
    def get_instance(cls, name: str) -> 'ComplexityAnalyzer':
        with cls._lock:
            if name not in cls._instances:
                cls._instances[name] = cls(name, verbose=False)
            return cls._instances[name]
    
    @classmethod
    def analyze_multi_run(
        cls,
        name: str,
        sizes: List[int],
        operations: List[int],
        times: List[float]
    ) -> ComplexityResult:
        complexity_type, confidence = estimate_complexity(sizes, operations, times)
        
        return ComplexityResult(
            complexity_type=complexity_type,
            confidence=confidence,
            operations=sum(operations),
            input_size=max(sizes) if sizes else 0,
            execution_time=sum(times),
            details={
                'sizes': sizes,
                'operations': operations,
                'times': times
            }
        )