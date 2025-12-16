# Running Quality Checks in Separate Rounds

This directory contains scripts for running the quality check workflow in separate rounds, allowing memory to be cleared between rounds. This is particularly useful for large datasets that may cause memory issues when processing all checks at once.

## Overview

The workflow is split into the following rounds:

1. **anatomical** - Generate anatomical views (coronal, axial, sagittal) for each subject/tract
2. **cci** - Calculate and visualize Cluster Confidence Index (CCI)
3. **before_after_cci** - Generate before/after CCI comparison views
4. **atlas_views** - Generate atlas views **once for all subjects** (saves time and space)
5. **shape_similarity** - Calculate and visualize shape similarity between subject and atlas tracts
6. **afq_profile** - Generate AFQ (Automated Fiber Quantification) profiles
7. **bundle_assignment** - Visualize bundle assignment
8. **html** - Generate HTML report from all accumulated results

## Configuration File

Create a JSON configuration file (see `config_example.json` for a template) with the following structure:

```json
{
  "output_dir": "output",
  "n_jobs": 1,
  "figure_size": [800, 800],
  "flip_lr": false,
  "ref_img": "path/to/t1w.nii.gz",
  "atlas_ref_img": "path/to/mni_template.nii.gz",
  "subjects_original_space": {
    "sub-001": {
      "AF_L": "path/to/sub-001_AF_L_original.trk",
      "AF_R": "path/to/sub-001_AF_R_original.trk"
    }
  },
  "subjects_mni_space": {
    "sub-001": {
      "AF_L": "path/to/sub-001_AF_L_mni.trk",
      "AF_R": "path/to/sub-001_AF_R_mni.trk"
    }
  },
  "atlas_files": {
    "AF_L": "path/to/atlas_AF_L.trk",
    "AF_R": "path/to/atlas_AF_R.trk"
  },
  "metric_files": {
    "sub-001": {
      "FA": "path/to/sub-001_FA.nii.gz"
    }
  },
  "subject_kwargs": {
    "max_streamlines": 500
  },
  "atlas_kwargs": {
    "max_streamlines": 1000
  }
}
```

### Configuration Options

- **output_dir**: Output directory for generated files
- **n_jobs**: Number of parallel jobs (use 1 for sequential processing to save memory)
- **figure_size**: Image size in pixels [width, height]
- **flip_lr**: Whether to flip left-right when transforming atlas
- **ref_img**: Reference image path(s). Can be:
  - A string: Single reference image used for all subjects
  - A dict: Mapping subject IDs to their reference images: `{"sub-001": "path/to/sub-001_t1w.nii.gz", "sub-002": "path/to/sub-002_t1w.nii.gz"}`
- **atlas_ref_img**: Reference image matching atlas coordinate space (e.g., MNI template)
- **subjects_original_space**: Dictionary mapping subject IDs to their tract files in original space
- **subjects_mni_space**: Dictionary mapping subject IDs to their tract files in MNI space (optional)
- **atlas_files**: Dictionary mapping tract names to atlas files (shared across all subjects)
- **metric_files**: Dictionary mapping subject IDs to their metric files (optional, for AFQ profiles)
- **subject_kwargs**: Additional kwargs for subject tract visualization methods
- **atlas_kwargs**: Additional kwargs for atlas visualization methods
- **kwargs**: Additional kwargs for all methods
- **html_output**: Path for HTML report (optional, defaults to `output_dir/quality_check_report.html`)

## Usage

### Running All Rounds

Run all rounds sequentially (default behavior):

```bash
python3 scripts/run_rounds.py --config config.json [--output-dir OUTPUT_DIR] [--results-file RESULTS_FILE] [--verbose]
```

Or explicitly:
```bash
python3 scripts/run_rounds.py all --config config.json --output-dir results --verbose
```

Example:
```bash
python3 scripts/run_rounds.py --config my_config.json --output-dir results --verbose
```

You can skip specific rounds:
```bash
python3 scripts/run_rounds.py --config config.json --skip cci --skip before_after_cci
```

### Running Individual Rounds

You can also run individual rounds:

```bash
python3 scripts/run_rounds.py <round_name> --config config.json [options]
```

Available rounds:
- `anatomical`
- `cci`
- `before_after_cci`
- `atlas_views`
- `shape_similarity`
- `afq_profile`
- `bundle_assignment`
- `html`
- `all` (default - runs all rounds)

Example:
```bash
# Run only anatomical views
python3 scripts/run_rounds.py anatomical --config config.json --output-dir results

# Generate HTML report from accumulated results
python3 scripts/run_rounds.py html --config config.json --output-dir results
```

## How It Works

1. **Results Accumulation**: Each round saves its results to a JSON file (`results.json` by default). Results from all rounds are merged together.

2. **Memory Management**: After each round, the Python script explicitly clears memory using garbage collection. The shell script also includes a small delay between rounds to allow the system to free memory.

3. **Atlas Views Optimization**: The `atlas_views` round generates atlas views **once for all subjects** instead of per subject. These views are stored in a shared `atlas_views/` directory and are automatically linked to all subjects that have the corresponding tract in the results.

4. **HTML Generation**: The final `html` round reads all accumulated results and generates a single HTML report.

## Benefits

- **Memory Efficiency**: Memory is cleared between rounds, preventing OOM (Out of Memory) errors
- **Time Savings**: Atlas views are generated once instead of per subject
- **Space Savings**: Atlas views are stored once and referenced by all subjects
- **Resumability**: If a round fails, you can re-run just that round without starting over
- **Flexibility**: You can run specific rounds as needed

## Troubleshooting

### Memory Issues

If you still encounter memory issues:
- Set `n_jobs: 1` in the config to force sequential processing
- Reduce `figure_size` (e.g., `[600, 600]` instead of `[800, 800]`)
- Add `max_streamlines` and `max_points_per_streamline` to `subject_kwargs` and `atlas_kwargs`
- Process fewer subjects at a time

### Missing Files

Make sure all file paths in the configuration are correct and accessible. Use absolute paths if relative paths don't work.

### Atlas Views Not Found

If atlas views are not appearing in the HTML report:
- Make sure the `atlas_views` round completed successfully
- Check that `atlas_files` is properly configured in the config file
- Verify that the atlas views were generated in the `atlas_views/` directory


