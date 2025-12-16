# Test Coverage Improvement Plan

## Current Coverage Status
- `html.py`: 12.82% (27 statements, 22 missed)
- `utils.py`: 0.00% (63 statements, 63 missed) - Tests exist but skipped when deps missing
- `viz.py`: 0.00% (793 statements, 793 missed) - Tests exist but skipped when deps missing

## Priority Tests to Add

### 1. HTML Module (`test_html.py`) - **HIGH PRIORITY**
**File doesn't exist - needs to be created**

#### `create_quality_check_html` function tests:
- [ ] Test basic HTML generation with minimal data
- [ ] Test with multiple subjects and tracts
- [ ] Test with different media types (image, plot, gif, video)
- [ ] Test with numeric scores (shape_similarity_score)
- [ ] Test path conversion (relative vs absolute)
- [ ] Test Windows path handling (different drives)
- [ ] Test with missing/non-existent files
- [ ] Test custom title parameter
- [ ] Test custom items_per_page parameter
- [ ] Test empty data dictionary
- [ ] Test HTML output file creation
- [ ] Test HTML structure validation (filters, search, pagination work)

### 2. Utils Module (`test_utils.py`) - **MEDIUM PRIORITY**
**Tests exist but need to run when dependencies available**

#### Additional edge cases to add:
- [ ] `calculate_centroid`: Test with single point streamlines
- [ ] `calculate_bbox_size`: Test with negative coordinates
- [ ] `calculate_direction_colors`: Test edge cases (very small directions, NaN handling)
- [ ] `calculate_combined_centroid`: Test with empty groups (should handle gracefully)
- [ ] `calculate_combined_bbox_size`: Test with empty groups
- [ ] `set_anatomical_camera`: Test with None bbox_size and None camera_distance
- [ ] `set_anatomical_camera`: Test with custom camera_distance
- [ ] `set_anatomical_camera`: Test all three view types more thoroughly

### 3. Viz Module (`test_viz.py`) - **HIGH PRIORITY**
**Tests exist but need expansion**

#### Core Methods (currently untested):
- [ ] `generate_anatomical_views`: Test with different views, with/without glass brain
- [ ] `generate_atlas_views`: Test atlas visualization with flip_lr
- [ ] `plot_cci`: Test CCI visualization with histogram
- [ ] `plot_afq`: Test AFQ profile plotting
- [ ] `visualize_shape_similarity`: Test shape similarity visualization
- [ ] `compare_before_after_cci`: Test before/after comparison
- [ ] `visualize_bundle_assignment`: Test bundle assignment visualization
- [ ] `generate_gif`: Test GIF generation
- [ ] `convert_gif_to_mp4`: Test GIF to MP4 conversion
- [ ] `generate_videos`: Test video generation workflow
- [ ] `run_quality_check_workflow`: Test full workflow with various skip_checks options

#### Error Handling:
- [ ] Test InvalidInputError for missing files
- [ ] Test TractographyVisualizationError for processing failures
- [ ] Test error handling in each visualization method
- [ ] Test edge cases (empty tracts, invalid parameters)

#### Property and Setter Tests:
- [ ] Test all property getters/setters
- [ ] Test parameter validation in setters

### 4. Integration Tests - **MEDIUM PRIORITY**
- [ ] Test full workflow from tract loading to HTML generation
- [ ] Test with real (small) tractography files (if available)
- [ ] Test file I/O operations
- [ ] Test temporary file cleanup

## Implementation Strategy

### Phase 1: HTML Module (Quick Win)
1. Create `tests/test_html.py`
2. Add basic tests for `create_quality_check_html`
3. **Expected coverage increase**: ~15-20% for html.py

### Phase 2: Utils Module Edge Cases
1. Add missing edge case tests to `test_utils.py`
2. Ensure tests run when dependencies are available
3. **Expected coverage increase**: ~10-15% for utils.py

### Phase 3: Viz Module Core Methods
1. Expand `test_viz.py` with tests for main visualization methods
2. Use mocking to avoid requiring actual tractography files
3. **Expected coverage increase**: ~20-30% for viz.py

### Phase 4: Error Handling and Edge Cases
1. Add comprehensive error handling tests
2. Test boundary conditions
3. **Expected coverage increase**: ~10-15% overall

## Notes
- Tests are currently skipped when dependencies (numpy, nibabel, dipy, fury) aren't available
- When dependencies ARE available, existing tests should run and improve coverage
- Focus on mocking external dependencies to make tests more reliable
- Consider using pytest fixtures for common test data

## Target Coverage Goals
- `html.py`: 80%+ (currently 12.82%)
- `utils.py`: 80%+ (currently 0%)
- `viz.py`: 60%+ (currently 0%) - This is a large file, 60% is reasonable
- Overall: 50%+ (currently 12.64%)

