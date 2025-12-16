# Troubleshooting `std::bad_alloc` Errors

## What is `std::bad_alloc`?

`std::bad_alloc` is a C++ exception that occurs when memory allocation fails. In pyTractoViz, this typically comes from VTK/FURY (C++ libraries) when they try to allocate memory for large tractography visualizations.

## Common Causes

1. **Very large tractograms**: Tractograms with millions of streamlines or points
2. **Memory exhaustion**: System has run out of available RAM
3. **Memory fragmentation**: Available memory is fragmented, preventing large contiguous allocations
4. **Multiple parallel workers**: Each worker process needs memory, multiplying usage
5. **Memory leaks**: Gradual accumulation of memory over time
6. **Large image sizes**: High-resolution images (e.g., 4K) require more memory

## Where It Typically Occurs

The error usually happens when:
- Creating actors with `actor.line()` for large tractograms
- Recording scenes with `window.record()` or `window.snapshot()`
- Creating GIF frames (multiple frames in memory)
- Processing multiple views in parallel

## Solutions

### 1. Set Memory Limits (Prevent OOM Kills)

```python
visualizer = TractographyVisualizer(
    max_memory_mb=8192,  # 8 GB limit
    n_jobs=1  # Sequential processing
)
```

### 2. Reduce Parallel Workers

```python
# Use fewer workers to reduce memory pressure
visualizer = TractographyVisualizer(n_jobs=1)  # Sequential
# Or
visualizer = TractographyVisualizer(n_jobs=2)  # Only 2 workers
```

### 3. Process in Smaller Batches

```python
# Process 5 subjects at a time instead of all at once
batch_size = 5
for i in range(0, len(subjects), batch_size):
    batch = dict(list(subjects.items())[i:i+batch_size])
    results = visualizer.run_quality_check_workflow(
        subjects_original_space=batch,
        n_jobs=1  # Sequential within batch
    )
```

### 4. Reduce Image Resolution

```python
# Smaller images use less memory
visualizer = TractographyVisualizer(
    gif_size=(400, 400)  # Instead of (608, 608)
)

# Or for static images
views = visualizer.generate_anatomical_views(
    tract_file,
    figure_size=(400, 400)  # Smaller images
)
```

### 5. Filter Large Tractograms

```python
# Increase CCI threshold to reduce number of streamlines
visualizer = TractographyVisualizer(
    cci_threshold=2.0,  # Higher threshold = fewer streamlines
    min_streamline_length=50.0  # Filter out short streamlines
)
```

### 6. Skip Memory-Intensive Operations

```python
# Skip operations that use a lot of memory
results = visualizer.run_quality_check_workflow(
    subjects_original_space=subjects,
    skip_checks=["bundle_assignment", "afq_profile"],  # Skip memory-intensive checks
    n_jobs=1
)
```

### 7. Monitor Memory Usage

Enable debug logging to see memory usage:

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Memory usage will be logged at key points
visualizer.run_quality_check_workflow(...)
```

### 8. Use System-Level Memory Limits

```bash
# Limit virtual memory to 8 GB (in KB)
ulimit -v 8388608

# Then run your script
python your_script.py
```

### 9. Check Available Memory Before Processing

```python
from pytractoviz.viz import _check_memory_available

# Check if we have enough memory (estimate 2GB per tract)
if _check_memory_available(required_mb=2000, safety_margin=0.3):
    # Safe to process
    results = visualizer.run_quality_check_workflow(...)
else:
    # Not enough memory, reduce workload
    logger.warning("Insufficient memory, processing with n_jobs=1")
    results = visualizer.run_quality_check_workflow(..., n_jobs=1)
```

## Debugging

### 1. Enable Memory Monitoring

```python
import logging
import tracemalloc

logging.basicConfig(level=logging.DEBUG)
tracemalloc.start()

# Your code here
visualizer.run_quality_check_workflow(...)

# Check peak memory
current, peak = tracemalloc.get_traced_memory()
print(f"Peak memory: {peak / (1024**2):.2f} MB")
```

### 2. Check System Memory

```bash
# macOS
vm_stat

# Linux
free -h

# Check process memory
ps aux | grep python
```

### 3. Identify Which Operation Fails

Add logging around VTK operations:

```python
logger.info("About to create actor for %d streamlines", len(streamlines))
tract_actor = actor.line(streamlines)  # This might fail
logger.info("Actor created successfully")
```

## Prevention Strategies

1. **Always set `max_memory_mb`**: Prevents runaway memory usage
2. **Start with `n_jobs=1`**: Test with sequential processing first
3. **Monitor memory**: Use `_log_memory_usage()` at key points
4. **Process incrementally**: Don't load all data at once
5. **Clean up explicitly**: Ensure VTK objects are deleted
6. **Use smaller images**: Reduce resolution if memory is limited

## Example: Safe Processing Workflow

```python
from pytractoviz.viz import TractographyVisualizer
import logging

logging.basicConfig(level=logging.DEBUG)

# Create visualizer with memory limits
visualizer = TractographyVisualizer(
    output_directory="output/",
    max_memory_mb=8192,  # 8 GB limit
    n_jobs=1,  # Sequential to reduce memory
    gif_size=(400, 400),  # Smaller images
)

# Process with error handling
try:
    results = visualizer.run_quality_check_workflow(
        subjects_original_space=subjects,
        ref_img="t1w.nii.gz",
        n_jobs=1,  # Sequential processing
        skip_checks=["bundle_assignment"],  # Skip if memory is tight
    )
except MemoryError:
    logger.error("Memory error occurred. Try reducing n_jobs or increasing memory limit.")
except Exception as e:
    if "bad_alloc" in str(e).lower():
        logger.error("VTK memory allocation failed. Try:")
        logger.error("  1. Reduce n_jobs to 1")
        logger.error("  2. Reduce image sizes")
        logger.error("  3. Filter tractograms (increase cci_threshold)")
        logger.error("  4. Process in smaller batches")
    raise
```

## When It Happens

The error typically occurs at these points:
- `actor.line()` - Creating line actors for large tractograms
- `window.record()` - Recording scenes to images
- `window.snapshot()` - Taking snapshots for GIF frames
- `scene.add()` - Adding large actors to scenes

## Quick Fix Checklist

- [ ] Set `max_memory_mb` to limit memory
- [ ] Use `n_jobs=1` (sequential processing)
- [ ] Reduce `gif_size` and `figure_size`
- [ ] Increase `cci_threshold` to filter streamlines
- [ ] Process in smaller batches
- [ ] Skip memory-intensive checks
- [ ] Monitor memory with debug logging
- [ ] Check system memory availability












