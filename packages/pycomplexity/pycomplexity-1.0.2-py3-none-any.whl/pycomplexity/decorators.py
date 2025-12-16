"""
decorators for complexity analysis
"""

import time
import functools
import inspect
from typing import Optional, Callable, Any, List, Union

from .analyzer import ComplexityAnalyzer
from .utils import ComplexityType, format_complexity, estimate_complexity


def complexity(
    name: Optional[str] = None,
    input_param: Union[str, int] = 0,
    verbose: bool = True
):
    """
    decorator to measure function complexity
    
    usage
        @complexity(input_param="data")
        def process_data(data):
            for item in data:
                pass
    """
    def decorator(func: Callable) -> Callable:
        func._complexity_history = []
        
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            input_size = _get_input_size(func, args, kwargs, input_param)
            analyzer_name = name or func.__name__
            
            with ComplexityAnalyzer(
                name=analyzer_name,
                input_size=input_size,
                auto_detect=True,
                verbose=verbose
            ) as analyzer:
                result = func(*args, **kwargs)
            
            func._complexity_history.append({
                'input_size': input_size,
                'operations': analyzer.total_operations,
                'time': analyzer.execution_time
            })
            
            return result
        
        def get_complexity_analysis():
            if len(func._complexity_history) < 2:
                return "not enough data run function with different input sizes"
            
            sizes = [h['input_size'] for h in func._complexity_history if h['input_size']]
            ops = [h['operations'] for h in func._complexity_history]
            times = [h['time'] for h in func._complexity_history]
            
            if not sizes:
                return "no valid input sizes recorded"
            
            complexity_type, confidence = estimate_complexity(sizes, ops)
            return format_complexity(complexity_type, sum(ops), sum(times))
        
        wrapper.get_complexity_analysis = get_complexity_analysis
        wrapper.complexity_history = func._complexity_history
        
        return wrapper
    
    return decorator


def measure_complexity(
    func: Optional[Callable] = None,
    *,
    runs: List[int] = None,
    verbose: bool = True
):
    """
    decorator that runs function with multiple input sizes to determine complexity
    """
    if runs is None:
        runs = [10, 100, 1000]
    
    def decorator(fn: Callable) -> Callable:
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            return fn(*args, **kwargs)
        
        def analyze():
            sizes = []
            operations = []
            times = []
            
            print(f"\nanalyzing complexity of {fn.__name__}")
            print("-" * 40)
            
            for size in runs:
                try:
                    test_input = list(range(size))
                    
                    with ComplexityAnalyzer(
                        name=fn.__name__,
                        input_size=size,
                        verbose=False
                    ) as analyzer:
                        fn(test_input)
                    
                    sizes.append(size)
                    operations.append(analyzer.total_operations)
                    times.append(analyzer.execution_time)
                    
                    print(f"  n={size:>6} {analyzer.total_operations:>10} ops "
                          f"{analyzer.execution_time:.6f}s")
                    
                except Exception as e:
                    print(f"  n={size} error {e}")
            
            if len(sizes) >= 2:
                complexity_type, confidence = estimate_complexity(sizes, operations)
                print("-" * 40)
                print(f"\nestimated complexity {complexity_type}")
                print(f"confidence {confidence:.1%}")
            
            return sizes, operations, times
        
        wrapper.analyze = analyze
        return wrapper
    
    if func is not None:
        return decorator(func)
    return decorator


def auto_complexity(func: Callable) -> Callable:
    """
    simple decorator that automatically tracks complexity
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        input_size = None
        if args:
            first_arg = args[0]
            if hasattr(first_arg, '__len__'):
                input_size = len(first_arg)
            elif isinstance(first_arg, int):
                input_size = first_arg
        
        with ComplexityAnalyzer(
            name=func.__name__,
            input_size=input_size,
            auto_detect=True,
            verbose=True
        ):
            return func(*args, **kwargs)
    
    return wrapper


def _get_input_size(
    func: Callable,
    args: tuple,
    kwargs: dict,
    input_param: Union[str, int]
) -> Optional[int]:
    try:
        if isinstance(input_param, int):
            if input_param < len(args):
                value = args[input_param]
            else:
                return None
        else:
            sig = inspect.signature(func)
            params = list(sig.parameters.keys())
            
            if input_param in kwargs:
                value = kwargs[input_param]
            elif input_param in params:
                idx = params.index(input_param)
                if idx < len(args):
                    value = args[idx]
                else:
                    return None
            else:
                return None
        
        if hasattr(value, '__len__'):
            return len(value)
        elif isinstance(value, int):
            return value
        else:
            return None
            
    except Exception:
        return None
