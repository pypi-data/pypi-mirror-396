"""
global profiler with start end markers
"""

import time
import sys
import threading
import atexit
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, field

from .utils import ComplexityType, format_complexity, estimate_complexity


@dataclass
class ProfileSession:
    name: str
    start_time: float = 0.0
    end_time: float = 0.0
    operation_count: int = 0
    input_size: Optional[int] = None
    line_count: int = 0
    is_active: bool = False
    original_trace: Any = None
    
    @property
    def duration(self) -> float:
        if self.end_time > 0:
            return self.end_time - self.start_time
        return time.perf_counter() - self.start_time


class Profiler:
    """
    global profiler for tracking complexity across code sections
    
    usage
        from pycomplexity import start end
        
        start("my_algorithm", n=1000)
        # your code here
        end("my_algorithm")
    """
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
            
        self._sessions: Dict[str, ProfileSession] = {}
        self._active_sessions: List[str] = []
        self._history: Dict[str, List[dict]] = {}
        self._config = {
            'verbose': True,
            'auto_trace': True,
            'color_output': True
        }
        self._initialized = True
        
        atexit.register(self._cleanup)
    
    def start(
        self, 
        name: str, 
        n: Optional[int] = None,
        auto_count: bool = True
    ):
        session = ProfileSession(
            name=name,
            start_time=time.perf_counter(),
            input_size=n,
            is_active=True
        )
        
        if auto_count and self._config['auto_trace']:
            session.original_trace = sys.gettrace()
            sys.settrace(self._create_trace_function(name))
        
        self._sessions[name] = session
        self._active_sessions.append(name)
        
        if self._config['verbose']:
            msg = f"started profiling {name}"
            if n:
                msg += f" n={n}"
            print(msg)
    
    def end(self, name: str) -> Optional[dict]:
        if name not in self._sessions:
            print(f"no active session named {name}")
            return None
        
        session = self._sessions[name]
        session.end_time = time.perf_counter()
        session.is_active = False
        
        if session.original_trace is not None or sys.gettrace():
            sys.settrace(session.original_trace)
        
        if name in self._active_sessions:
            self._active_sessions.remove(name)
        
        result = self._analyze_session(session)
        
        if name not in self._history:
            self._history[name] = []
        self._history[name].append(result)
        
        if self._config['verbose']:
            self._print_result(session, result)
        
        return result
    
    def count(self, name: str, operations: int = 1):
        if name in self._sessions:
            self._sessions[name].operation_count += operations
    
    def _create_trace_function(self, session_name: str):
        def trace(frame, event, arg):
            if session_name in self._sessions:
                session = self._sessions[session_name]
                if session.is_active and event == 'line':
                    session.line_count += 1
            return trace
        return trace
    
    def _analyze_session(self, session: ProfileSession) -> dict:
        ops = max(session.operation_count, session.line_count, 1)
        n = session.input_size or ops
        
        if n > 0:
            ratio = ops / n if n > 0 else 0
            
            if ratio < 1.5:
                complexity = ComplexityType.CONSTANT
            elif ratio < 2:
                complexity = ComplexityType.LOGARITHMIC
            elif ratio < n * 0.3:
                complexity = ComplexityType.LINEAR
            elif ratio < n:
                complexity = ComplexityType.LINEARITHMIC
            elif ratio < n * n * 0.3:
                complexity = ComplexityType.QUADRATIC
            else:
                complexity = ComplexityType.EXPONENTIAL
        else:
            complexity = ComplexityType.UNKNOWN
        
        if session.name in self._history and len(self._history[session.name]) >= 1:
            history = self._history[session.name]
            sizes = [h['input_size'] for h in history if h.get('input_size')]
            all_ops = [h['operations'] for h in history]
            
            sizes.append(n)
            all_ops.append(ops)
            
            if len(sizes) >= 2 and all(sizes):
                complexity, _ = estimate_complexity(sizes, all_ops)
        
        return {
            'name': session.name,
            'complexity': complexity,
            'operations': ops,
            'input_size': n,
            'time': session.duration,
            'line_count': session.line_count
        }
    
    def _print_result(self, session: ProfileSession, result: dict):
        print(f"\n{'='*50}")
        print(f"complexity analysis {session.name}")
        print(f"{'='*50}")
        print(format_complexity(
            result['complexity'],
            result['operations'],
            result['time'],
            result['input_size'],
            color=self._config['color_output']
        ))
    
    def get_results(self, name: Optional[str] = None) -> dict:
        if name:
            return self._history.get(name, [])
        return dict(self._history)
    
    def reset(self, name: Optional[str] = None):
        if name:
            if name in self._sessions:
                del self._sessions[name]
            if name in self._history:
                del self._history[name]
        else:
            self._sessions.clear()
            self._history.clear()
            self._active_sessions.clear()
    
    def set_config(self, **kwargs):
        self._config.update(kwargs)
    
    def _cleanup(self):
        for name in list(self._active_sessions):
            try:
                self.end(name)
            except Exception:
                pass


_profiler = Profiler()


def start(name: str, n: Optional[int] = None, auto_count: bool = True):
    """start profiling a code section"""
    _profiler.start(name, n, auto_count)


def end(name: str) -> Optional[dict]:
    """end profiling a code section"""
    return _profiler.end(name)


def count(name: str, operations: int = 1):
    """manually count operations"""
    _profiler.count(name, operations)


def get_results(name: Optional[str] = None) -> dict:
    """get profiling results"""
    return _profiler.get_results(name)


def reset(name: Optional[str] = None):
    """reset profiler state"""
    _profiler.reset(name)


def set_config(**kwargs):
    """configure the profiler"""
    _profiler.set_config(**kwargs)
