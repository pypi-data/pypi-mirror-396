# Memory Monitoring Guide

This document describes various ways to monitor RAM usage for pyTractoViz.

## 1. System-Level Tools (External Monitoring)

### macOS (your system)
```bash
# Real-time process monitoring
top -pid $(pgrep -f python)

# Or use htop (if installed)
htop

# Memory statistics
vm_stat

# Process-specific memory
ps aux | grep python | grep -v grep

# Watch memory in real-time (updates every 1 second)
watch -n 1 'ps aux | grep python | grep -v grep'

# Get detailed memory info for a specific process
ps -o pid,rss,vsz,pmem,comm -p $(pgrep -f python)
```

### Linux
```bash
# Real-time monitoring
top -p $(pgrep -f python)

# Memory info
free -h

# Process memory
ps aux --sort=-%mem | head -20

# Continuous monitoring
watch -n 1 'ps aux | grep python'
```

## 2. Python Built-in Methods

### Using `resource` module (Unix/Linux/macOS)
```python
import resource

def get_memory_usage():
    """Get current memory usage in MB."""
    usage = resource.getrusage(resource.RUSAGE_SELF)
    # ru_maxrss is in KB on macOS, MB on Linux
    if sys.platform == 'darwin':  # macOS
        return usage.ru_maxrss / 1024  # Convert KB to MB
    else:  # Linux
        return usage.ru_maxrss  # Already in MB

# Usage
print(f"Memory usage: {get_memory_usage():.2f} MB")
```

### Using `sys.getsizeof()` for objects
```python
import sys

# Get size of a specific object
tract_size = sys.getsizeof(tract)
print(f"Tract object size: {tract_size / (1024**2):.2f} MB")

# Note: This only gives shallow size, not deep size
# For deep size, use pympler (see below)
```

## 3. Python Libraries

### memory_profiler (line-by-line profiling)
```python
# Install: pip install memory-profiler

from memory_profiler import profile

@profile
def your_function():
    # Your code here
    pass

# Or run from command line:
# python -m memory_profiler your_script.py
```

### pympler (object analysis)
```python
# Install: pip install pympler

from pympler import tracker, muppy, summary

# Track memory usage
tr = tracker.SummaryTracker()
tr.print_diff()  # Shows what changed since last call

# Get all objects in memory
all_objects = muppy.get_objects()
sum1 = summary.summarize(all_objects)
summary.print_(sum1)

# Get size of specific object (deep size)
from pympler import asizeof
size = asizeof.asizeof(tract)
print(f"Deep size: {size / (1024**2):.2f} MB")
```

### objgraph (object reference graphs)
```python
# Install: pip install objgraph

import objgraph

# Show most common types
objgraph.show_most_common_types()

# Show growth
objgraph.show_growth()

# Generate graph of object references
objgraph.show_backrefs([tract], max_depth=3)
```

## 4. Enhanced Monitoring Function

You can extend the existing `_log_memory_usage()` function with additional methods:

```python
import resource
import sys

def _log_memory_usage_enhanced(
    label: str = "",
    *,
    use_resource: bool = True,
    use_tracemalloc: bool = False,
    log_level: int = logging.DEBUG,
) -> dict[str, float | int] | None:
    """Enhanced memory monitoring with multiple methods."""
    memory_info: dict[str, float | int] = {}
    
    # Method 1: resource module (built-in, Unix/macOS/Linux)
    if use_resource:
        try:
            usage = resource.getrusage(resource.RUSAGE_SELF)
            if sys.platform == 'darwin':  # macOS
                rss_mb = usage.ru_maxrss / 1024
            else:  # Linux
                rss_mb = usage.ru_maxrss
            memory_info['resource_rss_mb'] = round(rss_mb, 2)
            logger.log(log_level, "Resource module: RSS=%.2f MB", rss_mb)
        except (OSError, AttributeError):
            pass
    
    # Method 2: psutil (if available)
    if psutil is not None:
        process = psutil.Process(os.getpid())
        mem_info = process.memory_info()
        memory_info['psutil_rss_mb'] = round(mem_info.rss / (1024**2), 2)
        logger.log(log_level, "psutil: RSS=%.2f MB", mem_info.rss / (1024**2))
    
    # Method 3: tracemalloc (if enabled)
    if use_tracemalloc and tracemalloc.is_tracing():
        current, peak = tracemalloc.get_traced_memory()
        memory_info['tracemalloc_current_mb'] = round(current / (1024**2), 2)
        memory_info['tracemalloc_peak_mb'] = round(peak / (1024**2), 2)
        logger.log(log_level, "Tracemalloc: Current=%.2f MB, Peak=%.2f MB",
                   current / (1024**2), peak / (1024**2))
    
    return memory_info
```

## 5. Continuous Monitoring Script

Create a separate monitoring script that watches your process:

```python
# monitor_memory.py
import psutil
import time
import sys

def monitor_process(pid, interval=1):
    """Monitor a process's memory usage."""
    try:
        process = psutil.Process(pid)
        while True:
            mem_info = process.memory_info()
            mem_percent = process.memory_percent()
            print(f"RSS: {mem_info.rss / (1024**2):.2f} MB | "
                  f"VMS: {mem_info.vms / (1024**2):.2f} MB | "
                  f"Percent: {mem_percent:.2f}%")
            time.sleep(interval)
    except psutil.NoSuchProcess:
        print(f"Process {pid} not found")
    except KeyboardInterrupt:
        print("\nMonitoring stopped")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        pid = int(sys.argv[1])
    else:
        # Find Python process
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            if 'python' in proc.info['name'].lower():
                if 'pytractoviz' in ' '.join(proc.info['cmdline'] or []):
                    pid = proc.info['pid']
                    break
        else:
            print("No pyTractoViz process found")
            sys.exit(1)
    
    monitor_process(pid)
```

Usage:
```bash
python monitor_memory.py <PID>
# Or let it auto-detect:
python monitor_memory.py
```

## 6. Using OS-Specific Commands

### macOS: `vm_stat` and `top`
```bash
# System memory stats
vm_stat

# Monitor specific process
top -pid $(pgrep -f "python.*pytractoviz") -l 1

# Get RSS for Python processes
ps -o pid,rss,command -p $(pgrep -f python) | grep pytractoviz
```

### Linux: `/proc` filesystem
```bash
# Process memory from /proc
cat /proc/$(pgrep -f python)/status | grep VmRSS

# Or use pmap
pmap -x $(pgrep -f python)
```

## Recommendations

1. **For quick checks**: Use system tools (`top`, `htop`, `ps`)
2. **For programmatic monitoring**: Use `psutil` (already in your code) or `resource` module
3. **For detailed analysis**: Use `memory_profiler` for line-by-line profiling
4. **For debugging leaks**: Use `tracemalloc` or `pympler`
5. **For continuous monitoring**: Run a separate monitoring script

## Example: Adding resource module to existing function

The `resource` module is built-in and works on Unix systems (macOS, Linux) without any dependencies. It's a good fallback when `psutil` isn't available.













