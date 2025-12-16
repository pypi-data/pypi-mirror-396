# pycomplexity

**Runtime complexity analyzer for Python code**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

Stop guessing how your code performs. **pycomplexity** automatically analyzes your algorithms and tells you their Big O complexity by watching them run.

## Why Use This?

Ever wondered:
- "Is my algorithm actually O(n) or O(n²)?"
- "Why does this function slow down so much with more data?"
- "Which implementation is faster?"

**pycomplexity** answers these questions by measuring your code in real-time and determining its computational complexity

## Features

**Automatic complexity detection** - Identifies 12+ complexity types from O(1) to O(n!) 

**Multiple analysis methods** - Decorators, context managers, or simple start/end markers

**Operation tracking** - See exactly which operations dominate your runtime 

**Multi-run analysis** - Test with different input sizes automatically

**Lightweight** - Minimal overhead, only requires numpy

**Beautiful output** - Color-coded results with confidence scores

## Installation

```bash
pip install pycomplexity
```

## Quick Start

### Method 1: Decorator (Simplest)

```python
from pycomplexity import complexity

@complexity(input_param="data")
def bubble_sort(data):
    n = len(data)
    for i in range(n):
        for j in range(n - 1):
            if data[j] > data[j + 1]:
                data[j], data[j + 1] = data[j + 1], data[j]
    return data

# Run with different sizes
bubble_sort(list(range(50, 0, -1)))
bubble_sort(list(range(100, 0, -1)))

# Get analysis
print(bubble_sort.get_complexity_analysis())
```

**Output:**
```
complexity analysis for bubble_sort
complexity O(n^2)
operations 2,450
time 0.002131 seconds
input size 50
```

### Method 2: Context Manager (Fine Control)

```python
from pycomplexity import ComplexityAnalyzer

with ComplexityAnalyzer("my_algorithm", input_size=1000) as analyzer:
    for i in range(1000):
        for j in range(1000):
            analyzer.count_operation()
            result = i * j
```

### Method 3: Start/End Markers (Quick Profiling)

```python
from pycomplexity import start, end

start("processing", n=5000)
# Your code here
for i in range(5000):
    process(i)
end("processing")
```

## Real-World Examples

### Example 1: Comparing Search Algorithms

```python
from pycomplexity import complexity

@complexity(input_param="items")
def linear_search(items, target):
    """O(n) - checks every item"""
    for i, item in enumerate(items):
        if item == target:
            return i
    return -1

@complexity(input_param="items")  
def binary_search(items, target):
    """O(log n) - divides search space in half"""
    low, high = 0, len(items) - 1
    while low <= high:
        mid = (low + high) // 2
        if items[mid] == target:
            return mid
        elif items[mid] < target:
            low = mid + 1
        else:
            high = mid - 1
    return -1

# Test both
data = list(range(10000))

linear_search(data, 9999)
binary_search(data, 9999)

print("Linear:", linear_search.get_complexity_analysis())
print("Binary:", binary_search.get_complexity_analysis())
```

**Result:** Binary search is dramatically faster for large datasets!

### Example 2: Detailed Operation Tracking

```python
from pycomplexity import OperationTracker

tracker = OperationTracker("insertion_sort", input_size=100)

data = list(range(100, 0, -1))
for i in range(1, len(data)):
    key = data[i]
    j = i - 1
    
    while j >= 0:
        tracker.track("comparison")
        if data[j] > key:
            tracker.track("shift")
            data[j + 1] = data[j]
            j -= 1
        else:
            break
    
    data[j + 1] = key
    tracker.track("insertion")

tracker.report()
```

**Output:**
```
============================================================
operation tracker report insertion_sort
============================================================

estimated complexity O(n^2)
total operations 5,049
elapsed time 0.003214s
input size n 100
operations per n 50.49

------------------------------------------------------------
operation breakdown
------------------------------------------------------------
operation                        count        avg time
comparison                       4,950             n/a
shift                            4,950             n/a
insertion                           99             n/a
============================================================
```

### Example 3: Automatic Multi-Size Testing

```python
from pycomplexity import measure_complexity

@measure_complexity(runs=[100, 500, 1000, 5000])
def find_duplicates(data):
    """Find duplicates using nested loops"""
    duplicates = []
    for i in range(len(data)):
        for j in range(i + 1, len(data)):
            if data[i] == data[j] and data[i] not in duplicates:
                duplicates.append(data[i])
    return duplicates

# This automatically tests with 4 different input sizes
find_duplicates.analyze()
```

**Output:**
```
analyzing complexity of find_duplicates
----------------------------------------
  n=   100      10,106 ops 0.001877s
  n=   500     250,556 ops 0.045123s
  n= 1,000   1,001,006 ops 0.183456s
  n= 5,000  25,005,006 ops 4.521789s
----------------------------------------

estimated complexity O(n^2)
confidence 100.0%
```

## Understanding the Output

### All Supported Complexity Types

| Notation | Name | Growth Rate | Practical Limit | Example Algorithms |
|----------|------|-------------|-----------------|-------------------|
| **O(1)** | Constant | Always same | ∞ | Array access, hash lookup, simple math, len() |
| **O(log log n)** | Double logarithmic | Extremely slow | ∞ | Interpolation search (uniform data) |
| **O(log n)** | Logarithmic | Barely increases | ∞ | Binary search, balanced tree ops |
| **O(√n)** | Square root | Moderate growth | ~1,000,000 | Prime checking, Grover's algorithm |
| **O(n)** | Linear | Doubles with 2x data | ~10,000,000 | Simple loops, linear search |
| **O(n log n)** | Linearithmic | Efficient sort speed | ~1,000,000 | Merge sort, quicksort, heapsort |
| **O(n²)** | Quadratic | 4x with 2x data | ~10,000 | Nested loops, bubble sort |
| **O(n²√n)** | N-squared root-n | Between n² and n³ | ~5,000 | Some graph algorithms |
| **O(n³)** | Cubic | 8x with 2x data | ~1,000 | Triple nested, matrix multiply |
| **O(n⁴)** | Quartic | 16x with 2x data | ~500 | Four nested loops |
| **O(2^n)** | Exponential | Explodes | ~25 | Recursive fibonacci, subsets |
| **O(n!)** | Factorial | Trash | ~12 | TSP brute force, all permutations |

### Complexity Comparison (n=20)

| Type | Operations | Time (1 op = 1ms) | Real World |
|------|-----------|-------------------|------------|
| O(1) | 1 | 0.001s | ⚡ Instant |
| O(log n) | 4 | 0.004s | ⚡ Nearly instant |
| O(√n) | 4 | 0.004s | ⚡ Nearly instant |
| O(n) | 20 | 0.02s | ✅ Very fast |
| O(n log n) | 86 | 0.086s | ✅ Fast |
| O(n²) | 400 | 0.4s | ⚠️ Acceptable |
| O(n³) | 8,000 | 8s | ⚠️ Slow |
| O(2^n) | 1,048,576 | 17 min | ❌ Very slow |
| O(n!) | 2.4 × 10¹⁸ | 77 million years | ❌ **Impossible** (thats pretty rare tho, if you code something factorial you're just a bad coder atm)

### Color Coding

- 🟢 **Green** (O(1), O(log log n), O(log n), O(√n)) - Excellent performance, scalable
- 🟡 **Yellow** (O(n), O(n log n)) - Good performance, acceptable for large data
- 🟠 **Orange** (O(n²), O(n³), O(n⁴)) - Poor performance, only for small datasets
- 🔴 **Red** (O(2^n), O(n!)) - Terrible performance, avoid if possible

## API Reference

### Decorators

#### `@complexity(name=None, input_param=0, verbose=True)`

Analyze a function's complexity automatically.

**Parameters:**
- `name` (str): Custom name for the analysis
- `input_param` (str | int): Which parameter represents input size (name or index)
- `verbose` (bool): Print results after each run

**Example:**
```python
@complexity(input_param="data", verbose=True)
def process(data):
    return sum(data)
```

#### `@auto_complexity`

Simple decorator that auto-detects input size from first argument.

```python
@auto_complexity
def my_function(data):
    return sorted(data)
```

#### `@measure_complexity(runs=[10, 100, 1000])`

Test function with multiple input sizes automatically.

```python
@measure_complexity(runs=[50, 500, 5000])
def algorithm(data):
    # your code
    pass

algorithm.analyze()  # Runs all tests
```

### Context Managers

#### `ComplexityAnalyzer(name, input_size=None, verbose=True)`

Analyze a code block with fine-grained control.

```python
with ComplexityAnalyzer("algorithm", input_size=1000) as analyzer:
    for i in range(1000):
        analyzer.count_operation()  # Manual counting
        do_work()
```

#### `track_operations(name, input_size=None)`

Track and categorize different operation types.

```python
with track_operations("sort", input_size=100) as tracker:
    for i in range(100):
        tracker.track("comparison")
        if should_swap:
            tracker.track("swap")
```

### Global Profiler

#### `start(name, n=None, auto_count=True)`

Begin profiling a code section.

```python
from pycomplexity import start, end, count

start("processing", n=1000)
for i in range(1000):
    count("processing")  # Optional manual counting
    process(i)
end("processing")
```

#### `end(name) -> dict`

Stop profiling and return results.

#### `get_results(name=None) -> dict`

Retrieve historical results.

```python
results = get_results("processing")
print(results)
```

#### `reset(name=None)`

Clear profiling history.

### Operation Tracker

#### `OperationTracker(name, input_size=None)`

Detailed operation-level tracking.

```python
tracker = OperationTracker("quicksort", input_size=1000)

# Track different operations
tracker.track("comparison")
tracker.track("swap")
tracker.track("partition")

# Get detailed report
tracker.report()
```

## Algorithm Examples by Complexity

### O(1) - Constant Time
```python
@complexity(input_param=0)
def constant_time(n):
    """Array access or hash lookup"""
    data = {i: i**2 for i in range(n)}
    return data[42]  # Single lookup, always O(1)
```

### O(log n) - Logarithmic
```python
@complexity(input_param="items")
def binary_search(items, target):
    """Divide search space in half each time"""
    low, high = 0, len(items) - 1
    while low <= high:
        mid = (low + high) // 2
        if items[mid] == target:
            return mid
        elif items[mid] < target:
            low = mid + 1
        else:
            high = mid - 1
    return -1
```

### O(√n) - Square Root
```python
@complexity(input_param="n")
def is_prime(n):
    """Only need to check up to √n"""
    if n < 2:
        return False
    for i in range(2, int(n**0.5) + 1):
        if n % i == 0:
            return False
    return True
```

### O(n) - Linear
```python
@complexity(input_param="data")
def find_max(data):
    """Single pass through data"""
    max_val = data[0]
    for item in data:
        if item > max_val:
            max_val = item
    return max_val
```

### O(n log n) - Linearithmic
```python
@complexity(input_param="data")
def merge_sort(data):
    """Efficient sorting"""
    if len(data) <= 1:
        return data
    
    mid = len(data) // 2
    left = merge_sort(data[:mid])
    right = merge_sort(data[mid:])
    
    return merge(left, right)
```

### O(n²) - Quadratic
```python
@complexity(input_param="data")
def bubble_sort(data):
    """Nested loops over same data"""
    n = len(data)
    for i in range(n):
        for j in range(n - 1):
            if data[j] > data[j + 1]:
                data[j], data[j + 1] = data[j + 1], data[j]
    return data
```

### O(n³) - Cubic
```python
@complexity(input_param="n")
def matrix_multiply(n):
    """Triple nested loops"""
    A = [[i for i in range(n)] for _ in range(n)]
    B = [[i for i in range(n)] for _ in range(n)]
    C = [[0 for _ in range(n)] for _ in range(n)]
    
    for i in range(n):
        for j in range(n):
            for k in range(n):
                C[i][j] += A[i][k] * B[k][j]
    return C
```

### O(2^n) - Exponential
```python
@complexity(input_param="n")
def fibonacci_recursive(n):
    """Recursive with no memoization"""
    if n <= 1:
        return n
    return fibonacci_recursive(n-1) + fibonacci_recursive(n-2)
```

### O(n!) - Factorial
```python
@complexity(input_param="items")
def generate_permutations(items):
    """All possible orderings"""
    if len(items) <= 1:
        return [items]
    
    result = []
    for i in range(len(items)):
        rest = items[:i] + items[i+1:]
        for p in generate_permutations(rest):
            result.append([items[i]] + p)
    return result
```

## Best Practices

### 1. Run with Multiple Input Sizes

Single runs can be misleading. Always test with at least 3-5 different sizes:

```python
@complexity(input_param="data")
def my_algorithm(data):
    # your code
    pass

# Test with increasing sizes
for size in [100, 500, 1000, 5000, 10000]:
    my_algorithm(list(range(size)))

print(my_algorithm.get_complexity_analysis())
```

### 2. Use Manual Counting for Accuracy

Auto-detection is convenient but manual counting is more accurate:

```python
with ComplexityAnalyzer("algorithm", input_size=n) as analyzer:
    for i in range(n):
        for j in range(n):
            analyzer.count_operation()  # Count the important operation
            if data[i] > data[j]:
                swap(i, j)
```

### 3. Track Specific Operations

For detailed analysis, track different operation types:

```python
tracker = OperationTracker("merge_sort", input_size=1000)

def merge_sort(arr):
    if len(arr) <= 1:
        return arr
    
    mid = len(arr) // 2
    tracker.track("split")
    
    left = merge_sort(arr[:mid])
    right = merge_sort(arr[mid:])
    
    return merge(left, right, tracker)

def merge(left, right, tracker):
    result = []
    while left and right:
        tracker.track("comparison")
        if left[0] <= right[0]:
            result.append(left.pop(0))
        else:
            result.append(right.pop(0))
    return result + left + right
```

### 4. Watch Out for Low Confidence

If confidence is below 50%, you need more data:

```python
# This might give low confidence
@complexity(input_param=0)
def test(n):
    return n * 2

test(10)  # Only one run!

# Better: multiple runs with varying sizes
test(10)
test(100)
test(1000)
test(10000)  # Now confidence will be high
```

## Common Pitfalls

### Testing with Similar Sizes

```python
# Bad - sizes too similar
my_func([1, 2, 3])
my_func([1, 2, 3, 4])
my_func([1, 2, 3, 4, 5])
```

```python
# Good - sizes vary significantly
my_func(list(range(10)))
my_func(list(range(100)))
my_func(list(range(1000)))
```

### Forgetting to Count Operations

```python
# Bad - auto-detection may be inaccurate
with ComplexityAnalyzer("sort", input_size=n):
    bubble_sort(data)
```

```python
# Good - explicit counting
with ComplexityAnalyzer("sort", input_size=n) as analyzer:
    for i in range(n):
        for j in range(n):
            analyzer.count_operation()
            if data[j] > data[j+1]:
                swap(j, j+1)
```

## Performance Tips

pycomplexity adds minimal overhead, but for best performance:

1. **Disable verbose mode** in production:
   ```python
   @complexity(verbose=False)
   def production_code(data):
       pass
   ```

2. **Use `auto_count=False`** if you don't need automatic tracing:
   ```python
   start("fast_profile", n=1000, auto_count=False)
   ```

3. **Turn off color output** for cleaner logs:
   ```python
   from pycomplexity import set_config
   set_config(color_output=False)
   ```

## Real-World Use Cases

### 1. Algorithm Selection

```python
# Compare different sorting algorithms
@measure_complexity(runs=[100, 500, 1000])
def bubble_sort(data): ...

@measure_complexity(runs=[100, 500, 1000])
def merge_sort(data): ...

bubble_sort.analyze()  # O(n²)
merge_sort.analyze()   # O(n log n)
# Choose merge_sort for large datasets!
```

### 2. Performance Regression Testing

```python
def test_performance_regression():
    """Ensure algorithm stays O(n log n)"""
    
    @complexity(input_param="data", verbose=False)
    def critical_function(data):
        return sorted(data)
    
    # Test with multiple sizes
    for size in [1000, 5000, 10000]:
        critical_function(list(range(size)))
    
    # Check complexity didn't regress
    history = critical_function.complexity_history
    # Assert it's still efficient
```

### 3. Interview Preparation

```python
# Verify your solution is optimal
@complexity(input_param="nums")
def two_sum(nums, target):
    """Should be O(n) with hash map"""
    seen = {}
    for i, num in enumerate(nums):
        complement = target - num
        if complement in seen:
            return [seen[complement], i]
        seen[num] = i
    return []

# Test it
two_sum(list(range(1000)), 1500)
print(two_sum.get_complexity_analysis())  # Confirms O(n)
```

## Contributing

Contributions welcome! Please feel free to submit a Pull Request.

## License

MIT License - see LICENSE file for details.

## Author

Created by Oracle

## Changelog

### v1.0.0 (12/12/2025)
- Initial release
- Context managers and decorators
- Multiple analysis methods
- Operation tracking
- 12+ complexity type detection (O(1) to O(n!))
- Color-coded output
- Automatic complexity estimation

---

**Ready to optimize your code?** Install now: `pip install pycomplexity`

⭐ Star me on GitHub if this helped you!
