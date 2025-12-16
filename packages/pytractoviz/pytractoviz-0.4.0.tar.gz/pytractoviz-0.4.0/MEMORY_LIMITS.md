# Memory Limit Controls

This document explains how to limit RAM usage in pyTractoViz to prevent OOM (Out of Memory) kills.

## Methods to Limit Memory

### 1. Set Hard Memory Limit (Recommended)

Set a maximum memory limit when creating the visualizer. The process will be killed by the OS if it exceeds this limit, preventing uncontrolled memory growth.

```python
from pytractoviz.viz import TractographyVisualizer

# Limit to 8 GB
visualizer = TractographyVisualizer(
    output_directory="output/",
    max_memory_mb=8192  # 8 GB limit
)

# Limit to 4 GB
visualizer = TractographyVisualizer(
    output_directory="output/",
    max_memory_mb=4096  # 4 GB limit
)
```

**How it works:**
- Uses `resource.setrlimit()` to set a virtual memory (address space) limit
- The OS will kill the process if it exceeds this limit
- Once set, the limit cannot be increased (only decreased)
- Works on Unix systems (macOS, Linux)

### 2. Automatic n_jobs Reduction Based on Memory

The code automatically reduces the number of parallel workers (`n_jobs`) if there isn't enough memory available.

```python
# The system will automatically reduce n_jobs if memory is limited
visualizer = TractographyVisualizer(
    output_directory="output/",
    n_jobs=-1  # Auto-detect, but will be reduced if memory is limited
)

results = visualizer.run_quality_check_workflow(
    subjects_original_space=subjects,
    ref_img="t1w.nii.gz",
    n_jobs=-1  # Will be reduced based on available memory
)
```

**How it works:**
- Estimates ~2GB per worker process
- Checks available system memory
- Automatically reduces `n_jobs` if there isn't enough memory
- Logs a warning when reduction occurs

### 3. Manual n_jobs Reduction

Manually set a lower `n_jobs` value to reduce memory usage:

```python
# Use fewer parallel workers
visualizer = TractographyVisualizer(
    output_directory="output/",
    n_jobs=2  # Only 2 parallel workers instead of all CPUs
)

# Or set it in the workflow
results = visualizer.run_quality_check_workflow(
    subjects_original_space=subjects,
    ref_img="t1w.nii.gz",
    n_jobs=1  # Sequential processing (lowest memory usage)
)
```

### 4. System-Level Limits (ulimit)

Set memory limits at the system level before running Python:

```bash
# Limit virtual memory to 8 GB (in KB)
ulimit -v 8388608

# Then run your script
python your_script.py

# Or combine with the Python limit
ulimit -v 8388608 && python your_script.py
```

**Note:** `ulimit -v` sets virtual memory limit in KB. For 8 GB: 8 * 1024 * 1024 = 8388608 KB

## Memory Estimation

The code estimates memory usage as:
- **Per worker process**: ~2 GB (default)
- **Safety margin**: 20% extra buffer
- **Main process**: Reserves 50% of current memory for main process

You can adjust the estimate if your data is larger/smaller:

```python
# If you know your tracts are very large, increase the estimate
# This will reduce n_jobs more aggressively
n_jobs = _get_n_jobs_with_memory_limit(
    base_n_jobs=8,
    estimated_memory_per_job_mb=4000.0,  # 4 GB per worker
    safety_margin=0.3,  # 30% safety margin
)
```

## Best Practices

1. **Start with a hard limit**: Always set `max_memory_mb` to prevent runaway memory usage
   ```python
   visualizer = TractographyVisualizer(max_memory_mb=8192)  # 8 GB
   ```

2. **Monitor memory usage**: Use the logging function to track memory
   ```python
   import logging
   logging.basicConfig(level=logging.DEBUG)
   # Memory usage will be logged automatically
   ```

3. **Use sequential processing for large datasets**: If you have very large tracts, use `n_jobs=1`
   ```python
   results = visualizer.run_quality_check_workflow(
       subjects_original_space=subjects,
       n_jobs=1  # Sequential = lowest memory
   )
   ```

4. **Process in batches**: For many subjects, process them in smaller batches
   ```python
   # Process 5 subjects at a time
   batch_size = 5
   for i in range(0, len(subjects), batch_size):
       batch = dict(list(subjects.items())[i:i+batch_size])
       results = visualizer.run_quality_check_workflow(
           subjects_original_space=batch,
           n_jobs=2  # Fewer workers per batch
       )
   ```

## Example: Complete Memory-Limited Workflow

```python
from pytractoviz.viz import TractographyVisualizer
import logging

# Enable debug logging to see memory usage
logging.basicConfig(level=logging.DEBUG)

# Create visualizer with memory limit
visualizer = TractographyVisualizer(
    output_directory="output/",
    max_memory_mb=8192,  # 8 GB hard limit
    n_jobs=-1  # Auto-detect, will be reduced if needed
)

# Run workflow (n_jobs will be automatically adjusted based on memory)
results = visualizer.run_quality_check_workflow(
    subjects_original_space={
        "sub-001": {"AF_L": "sub-001_AF_L.trk"},
        "sub-002": {"AF_L": "sub-002_AF_L.trk"},
    },
    ref_img="t1w.nii.gz",
    n_jobs=-1  # Will be reduced if memory is limited
)
```

## Troubleshooting

### Process Still Gets Killed

1. **Reduce max_memory_mb**: Set a lower limit
   ```python
   max_memory_mb=4096  # Try 4 GB instead of 8 GB
   ```

2. **Reduce n_jobs**: Use fewer parallel workers
   ```python
   n_jobs=1  # Sequential processing
   ```

3. **Increase estimated_memory_per_job_mb**: If workers need more memory
   ```python
   # In the code, adjust the estimate
   estimated_memory_per_job_mb=3000.0  # 3 GB instead of 2 GB
   ```

### Memory Limit Not Working

- **Check platform**: `resource.setrlimit()` only works on Unix (macOS, Linux)
- **Check permissions**: Some systems may restrict setting limits
- **Use ulimit**: Set system-level limits as fallback

### Want More Control

You can manually check memory before loading large data:

```python
from pytractoviz.viz import _check_memory_available

# Check if we have enough memory before loading
if _check_memory_available(required_mb=2000, safety_margin=0.2):
    # Safe to load
    tract = load_trk("large_tract.trk")
else:
    # Not enough memory, skip or reduce
    logger.warning("Skipping large tract due to memory constraints")
```

## Summary

- **Hard limit**: Set `max_memory_mb` in constructor (prevents OOM kills)
- **Automatic reduction**: `n_jobs=-1` will be reduced if memory is limited
- **Manual control**: Set `n_jobs=1` for sequential processing (lowest memory)
- **System limits**: Use `ulimit -v` for system-level control
- **Monitoring**: Enable DEBUG logging to see memory usage













