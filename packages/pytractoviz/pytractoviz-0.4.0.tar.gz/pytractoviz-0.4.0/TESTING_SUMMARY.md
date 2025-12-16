# Testing Summary for Interactive QC Features

## Overview

Comprehensive tests have been added for the new interactive QC features. The testing approach follows the existing patterns in the codebase, using extensive mocking to avoid GUI dependencies in automated tests.

## Test Files Modified

### 1. `tests/test_cli.py`
Added three new test classes:

- **`TestCollectTractFiles`**: Tests for the `_collect_tract_files()` helper function
  - Collecting from directories
  - Collecting from files
  - Mixed inputs
  - Edge cases (empty dirs, non-existent paths, non-.trk files)
  - Duplicate handling

- **`TestQcInteractiveCommand`**: Tests for the `qc-interactive` CLI command
  - Single and multiple file processing
  - Skip functionality
  - Error handling (missing ref, no files found)
  - Keyboard interrupt handling
  - Error recovery with user prompts

### 2. `tests/test_viz.py`
Added one new test class:

- **`TestViewTractInteractive`**: Tests for the `view_tract_interactive()` method
  - Successful viewing with all mocks
  - Missing reference image error
  - File not found error
  - Load error handling
  - Custom window size
  - Glass brain toggle

## Testing Strategy

### Mocking Approach

All tests use extensive mocking to:
1. **Avoid GUI dependencies**: `window.show()` is mocked to prevent actual window opening
2. **Isolate units**: Each component (loading, filtering, scene creation) is mocked
3. **Control behavior**: Errors and edge cases can be simulated
4. **Speed**: Tests run quickly without GUI overhead

### Key Mocks Used

- `window.show()` - Prevents actual GUI window
- `load_trk()` - Mock tract loading
- `nib.load()` - Mock image loading
- `transform_streamlines()` - Mock coordinate transformation
- `_create_scene()` - Mock scene creation
- `_create_streamline_actor()` - Mock actor creation
- `_filter_streamlines()` - Mock filtering
- `TractographyVisualizer` class - Mock entire visualizer for CLI tests

### Test Coverage

**Unit Tests:**
- ✅ File collection from various sources
- ✅ Parameter validation
- ✅ Error handling
- ✅ Edge cases (empty files, missing paths)
- ✅ CLI argument parsing
- ✅ Progress tracking

**Integration Tests:**
- ✅ Full CLI workflow with mocked visualizer
- ✅ Error recovery workflows
- ✅ User interaction simulation

**Manual Testing Required:**
- GUI functionality (rotation, zoom, pan)
- Actual window display
- Performance with large tracts
- Memory usage

## Running Tests

```bash
# Run all tests
pytest

# Run only CLI tests
pytest tests/test_cli.py

# Run only visualization tests
pytest tests/test_viz.py

# Run specific test class
pytest tests/test_cli.py::TestQcInteractiveCommand

# Run with coverage
pytest --cov=pytractoviz --cov-report=html
```

## Test Fixtures Used

The tests leverage existing fixtures from `conftest.py`:
- `tmp_path` - Temporary directory for test files
- `mock_t1w_file` - Mock T1-weighted image
- `mock_tract_file` - Mock tractography file
- `mock_stateful_tractogram` - Mock tractogram with streamlines
- `mock_nibabel_image` - Mock nibabel image object
- `visualizer` - Pre-configured TractographyVisualizer instance

## Future Enhancements

1. **GUI Testing**: Consider using `pytest-xvfb` for headless GUI testing in CI
2. **Performance Tests**: Add benchmarks for large tract loading
3. **Memory Tests**: Verify memory cleanup after each tract
4. **Integration Tests**: Test with real (small) tract files
5. **User Experience Tests**: Verify all keyboard shortcuts work

## Notes

- All tests are designed to run in headless CI environments
- GUI-dependent functionality is mocked, not tested automatically
- Manual testing checklist is provided in `TESTING_PLAN_INTERACTIVE_QC.md`
- Tests follow existing codebase patterns for consistency

