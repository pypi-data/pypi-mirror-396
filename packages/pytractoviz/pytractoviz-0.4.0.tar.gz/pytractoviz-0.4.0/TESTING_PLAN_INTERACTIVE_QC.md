# Testing Plan for Interactive QC Features

This document outlines the testing strategy for the new interactive QC features:
- `view_tract_interactive()` method in `TractographyVisualizer`
- `qc-interactive` CLI command
- `_collect_tract_files()` helper function

## Test Structure

### 1. Tests for `view_tract_interactive()` Method

**Location**: `tests/test_viz.py` (add to existing file)

#### Test Class: `TestViewTractInteractive`

**Test Cases:**

1. **Success Cases:**
   - `test_view_tract_interactive_success()` - Basic successful viewing with all mocks
   - `test_view_tract_interactive_with_custom_window_size()` - Test window size parameter
   - `test_view_tract_interactive_without_glass_brain()` - Test `show_glass_brain=False`
   - `test_view_tract_interactive_with_filtering()` - Test with `max_streamlines`, `subsample_factor`, etc.

2. **Error Cases:**
   - `test_view_tract_interactive_no_reference_image()` - Should raise `InvalidInputError`
   - `test_view_tract_interactive_tract_file_not_found()` - Should raise `FileNotFoundError`
   - `test_view_tract_interactive_empty_tract()` - Should handle empty tract gracefully
   - `test_view_tract_interactive_load_error()` - Should handle loading errors

3. **Parameter Validation:**
   - `test_view_tract_interactive_with_flip_lr()` - Test left-right flip
   - `test_view_tract_interactive_resample_streamlines()` - Test resampling option

**Mocking Strategy:**
- Mock `window.show()` to avoid opening actual GUI windows
- Mock `load_trk()`, `nib.load()`, `transform_streamlines()`
- Mock `_create_scene()`, `_create_streamline_actor()`, `_set_anatomical_camera()`
- Mock `_filter_streamlines()` if testing filtering options

**Example Test Structure:**
```python
@patch("pytractoviz.viz.window.show")
@patch("pytractoviz.viz.window.Scene")
@patch("pytractoviz.viz.actor.line")
@patch("pytractoviz.viz.transform_streamlines")
@patch("pytractoviz.viz.nib.load")
@patch("pytractoviz.viz.load_trk")
def test_view_tract_interactive_success(
    mock_load_trk: Mock,
    mock_nib_load: Mock,
    mock_transform: Mock,
    mock_actor_line: Mock,
    mock_scene_class: Mock,
    mock_window_show: Mock,
    visualizer: TractographyVisualizer,
    mock_tract_file: Path,
    mock_t1w_file: Path,
    mock_stateful_tractogram: Mock,
    mock_nibabel_image: Mock,
) -> None:
    """Test successful interactive viewing."""
    # Setup mocks
    mock_tract = Mock()
    mock_tract.streamlines = mock_stateful_tractogram.streamlines
    mock_load_trk.return_value = mock_tract
    mock_nib_load.return_value = mock_nibabel_image
    mock_transform.return_value = mock_stateful_tractogram.streamlines
    mock_actor = Mock()
    mock_actor_line.return_value = mock_actor
    mock_scene = Mock()
    mock_scene_class.return_value = mock_scene
    
    # Call method
    visualizer.view_tract_interactive(mock_tract_file, ref_img=mock_t1w_file)
    
    # Assertions
    mock_load_trk.assert_called_once()
    mock_window_show.assert_called_once()
    assert mock_window_show.call_args[0][0] == mock_scene
```

### 2. Tests for CLI `qc-interactive` Command

**Location**: `tests/test_cli.py` (add to existing file)

#### Test Class: `TestQcInteractiveCommand`

**Test Cases:**

1. **File Collection:**
   - `test_qc_interactive_collect_files_from_directory()` - Collect .trk files from directory
   - `test_qc_interactive_collect_files_from_file_list()` - Collect from explicit file list
   - `test_qc_interactive_collect_files_mixed_input()` - Mix of files and directories
   - `test_qc_interactive_collect_files_no_files_found()` - Error when no files found
   - `test_qc_interactive_collect_files_duplicates()` - Handle duplicate files

2. **Command Execution:**
   - `test_qc_interactive_success_single_file()` - Single tract file
   - `test_qc_interactive_success_multiple_files()` - Multiple tract files
   - `test_qc_interactive_with_skip()` - Test `--skip` option
   - `test_qc_interactive_with_options()` - Test various CLI options

3. **Error Handling:**
   - `test_qc_interactive_missing_ref_image()` - Missing `--ref` argument
   - `test_qc_interactive_invalid_ref_image()` - Invalid reference image path
   - `test_qc_interactive_keyboard_interrupt()` - Handle Ctrl+C gracefully
   - `test_qc_interactive_viewing_error_continue()` - Continue on error with user prompt

4. **Output and Progress:**
   - `test_qc_interactive_progress_output()` - Verify progress messages
   - `test_qc_interactive_instructions_displayed()` - Verify instructions are shown

**Mocking Strategy:**
- Mock `TractographyVisualizer.view_tract_interactive()` to avoid actual GUI
- Use `capsys` fixture to capture stdout/stderr
- Mock `input()` for user prompts
- Use `pytest.raises(SystemExit)` for argument parsing errors

**Example Test Structure:**
```python
@patch("pytractoviz._internal.cli.TractographyVisualizer")
def test_qc_interactive_success_single_file(
    mock_visualizer_class: Mock,
    tmp_path: Path,
    capsys: pytest.CaptureFixture,
) -> None:
    """Test qc-interactive with single file."""
    # Setup
    tract_file = tmp_path / "tract.trk"
    tract_file.touch()
    ref_file = tmp_path / "t1w.nii.gz"
    ref_file.touch()
    
    mock_visualizer = Mock()
    mock_visualizer_class.return_value = mock_visualizer
    
    # Execute
    result = main(["qc-interactive", str(tract_file), "--ref", str(ref_file)])
    
    # Assertions
    assert result == 0
    mock_visualizer_class.assert_called_once_with(reference_image=ref_file)
    mock_visualizer.view_tract_interactive.assert_called_once()
    captured = capsys.readouterr()
    assert "Found 1 tract file(s)" in captured.out
```

### 3. Tests for `_collect_tract_files()` Helper

**Location**: `tests/test_cli.py` (add to existing file)

#### Test Class: `TestCollectTractFiles`

**Test Cases:**

1. **Basic Functionality:**
   - `test_collect_tract_files_from_directory()` - Collect from directory
   - `test_collect_tract_files_from_file()` - Collect single file
   - `test_collect_tract_files_mixed()` - Mix of files and directories
   - `test_collect_tract_files_sorted()` - Verify files are sorted

2. **Edge Cases:**
   - `test_collect_tract_files_empty_directory()` - Empty directory (warning)
   - `test_collect_tract_files_nonexistent_path()` - Non-existent path (warning)
   - `test_collect_tract_files_non_trk_file()` - Skip non-.trk files (warning)
   - `test_collect_tract_files_duplicates()` - Remove duplicates
   - `test_collect_tract_files_case_insensitive()` - Handle .TRK vs .trk

3. **Error Handling:**
   - `test_collect_tract_files_no_valid_files()` - Return empty list when no files

**Example Test Structure:**
```python
def test_collect_tract_files_from_directory(tmp_path: Path) -> None:
    """Test collecting .trk files from directory."""
    # Setup
    tract_dir = tmp_path / "tracts"
    tract_dir.mkdir()
    tract1 = tract_dir / "tract1.trk"
    tract2 = tract_dir / "tract2.trk"
    tract1.touch()
    tract2.touch()
    
    # Execute
    from pytractoviz._internal.cli import _collect_tract_files
    result = _collect_tract_files([str(tract_dir)])
    
    # Assertions
    assert len(result) == 2
    assert tract1 in result
    assert tract2 in result
    assert result == sorted(result)  # Should be sorted
```

## Integration Tests

### Manual Testing Checklist

Since interactive GUI features are difficult to fully test automatically, include manual testing:

1. **GUI Functionality:**
   - [ ] Window opens and displays tract correctly
   - [ ] Mouse rotation works
   - [ ] Zoom works (scroll wheel)
   - [ ] Pan works (middle-click)
   - [ ] Window closes properly
   - [ ] Next tract loads after closing window

2. **CLI Workflow:**
   - [ ] Progress messages display correctly
   - [ ] Instructions are clear
   - [ ] Error messages are helpful
   - [ ] Keyboard interrupt (Ctrl+C) works
   - [ ] Skip option works correctly

3. **Performance:**
   - [ ] Large tracts load without crashing
   - [ ] Memory usage is reasonable
   - [ ] Window size options work

## Test Coverage Goals

- **Unit Tests**: 90%+ coverage for new code
- **Integration Tests**: All CLI paths covered
- **Error Cases**: All error paths tested
- **Edge Cases**: File collection edge cases covered

## Test Data Requirements

Create test fixtures for:
- Valid .trk files (can be minimal/mock)
- Valid T1-weighted reference images (can be minimal/mock)
- Directory structures with various .trk files
- Empty directories
- Invalid file types

## Notes

- Use `pytest.mark.skipif` for tests requiring GUI if running in headless CI
- Consider using `pytest-xvfb` for GUI tests in CI environments
- Mock `window.show()` to avoid blocking in automated tests
- Use `unittest.mock.patch` extensively for external dependencies

