# Quality Check File Requirements

This document outlines what needs to be implemented/updated to create a comprehensive quality check file for each tract and subject.

## Currently Implemented ✅

1. **CCI Calculation** - `calc_cci()` method calculates Cluster Confidence Index
2. **CCI Plotting** - `plot_cci()` creates histogram and anatomical views (coronal, axial, sagittal) with CCI-colored streamlines
3. **AFQ Profile Calculation** - `weighted_afq()` calculates weighted AFQ profile
4. **AFQ Profile Visualization** - `plot_afq()` generates anatomical views with AFQ profile colors AND line plot of profile values
5. **Anatomical Views** - `generate_anatomical_views()` generates standard anatomical views (coronal, axial, sagittal)
6. **Atlas Views** - `generate_atlas_views()` generates anatomical views for atlas tracts (for comparison)
7. **Best View Detection** - `find_best_view()` with multiple methods (PCA, coverage, length)
8. **Static Image Generation** - `generate_static_image()` generates images from specific viewing angles
9. **GIF/Video Generation** - `generate_gif()` and `generate_videos()` create rotation animations
10. **Tract Loading** - `load_tract()` loads and transforms tractography files
11. **HTML Report Generator** - `create_quality_check_html()` creates interactive HTML reports

## Missing Features to Implement ❌

### 1. Tract Compared to Atlas (Movie/Multiple Views)
**Status:** ✅ Implemented

**Current Implementation:**
- ✅ `generate_anatomical_views()` - Generates subject tract views (coronal, axial, sagittal)
- ✅ `generate_atlas_views()` - Generates atlas tract views with coordinate space handling
- ✅ HTML report can display images side-by-side for comparison
- Both functions support multiple views and can be used together for comparison

**Note:** Comparison is achieved by generating separate images for subject and atlas, then displaying them side-by-side in the HTML report. This approach is more flexible and allows for better control over individual image properties.

**Optional Enhancements (not required):**
- Option for post-CCI filtering before comparison (can be done by filtering tract before calling `generate_anatomical_views()`)
- Option for downsampling for faster rendering (can be implemented as preprocessing step)
- Animated comparison (movie/GIF) showing both tracts together (can be added if needed)

### 2. Tract with AFQ Profile Info (Best View Image)
**Status:** ✅ Implemented

**Current Implementation:**
- ✅ `plot_afq()` - Generates anatomical views (coronal, axial, sagittal) with streamlines colored by AFQ profile values
- ✅ `find_best_view()` - Determines optimal viewing angle (multiple methods available)
- ✅ `generate_static_image()` - Can generate images from best view with AFQ colors

**Note:** Currently uses standard anatomical views rather than "best view" for consistency. Can be combined with `find_best_view()` and `generate_static_image()` if best-view images are needed.

### 3. Plot of AFQ Values Along Tract Nodes
**Status:** ✅ Implemented

**Current Implementation:**
- ✅ `plot_afq()` - Includes a line plot of AFQ profile values along tract nodes
- Returns "profile_plot" key in the output dictionary
- X-axis: node position along tract
- Y-axis: metric value (FA, MD, etc.)
- Saved as PNG with proper labels and grid

### 4. Plot of Cluster Confidence Index Values
**Status:** ✅ Implemented

**Current Implementation:**
- ✅ `plot_cci()` - Creates histogram plot with statistics
- ✅ `plot_cci()` - Generates anatomical views (coronal, axial, sagittal) with CCI-colored streamlines
- Histogram includes proper labels, title, and grid

**Note:** CCI values are per-streamline (not per-node), so a line plot along tract nodes isn't applicable. The histogram shows the distribution of CCI values across all streamlines.

### 5. Comparison of Tract Before/After Cluster Confidence
**Status:** ✅ Implemented

**Current Implementation:**
- ✅ `compare_before_after_cci()` - Generates side-by-side anatomical views (coronal, axial, sagittal)
- ✅ Shows tract before CCI filtering (left) and after CCI filtering (right)
- ✅ Customizable colors for before and after tracts
- ✅ Optional glass brain outline
- ✅ Combines images side-by-side automatically

### 6. Bundle Assignment Map
**Status:** ✅ Implemented

**Current Implementation:**
- ✅ `visualize_bundle_assignment()` - Uses DIPY's `assignment_map` to assign target streamlines to model bundle segments
- ✅ Color-codes each streamline by its assigned segment
- ✅ Generates anatomical views (coronal, axial, sagittal) showing bundle assignments
- ✅ Requires model bundle file for assignment reference
- ✅ Configurable number of segments (default: 100)
- ✅ Customizable colormap for segment colors (default: "tab20")

### 7. Shape Similarity Score
**Status:** ✅ Implemented

**Current Implementation:**
- ✅ `calculate_shape_similarity()` - Wrapper method using DIPY's `bundle_shape_similarity()`
- ✅ Uses Bundle Adjacency (BA) metric from `dipy.segment.bundles.bundle_shape_similarity`
- ✅ Handles tract loading and coordinate space alignment
- ✅ Supports atlas reference image for different coordinate spaces (e.g., MNI)
- ✅ Supports left-right flipping option
- ✅ Configurable clustering thresholds and similarity threshold

### 8. Shape Similarity Image Comparing to Atlas
**Status:** ✅ Implemented

**Current Implementation:**
- ✅ `visualize_shape_similarity()` - Generates anatomical views (coronal, axial, sagittal) with subject and atlas tracts overlaid
- ✅ Each tract uses a single color (subject: red by default, atlas: blue by default)
- ✅ Handles coordinate space alignment for atlases in different spaces (e.g., MNI)
- ✅ Supports left-right flipping option
- ✅ Customizable colors for subject and atlas tracts
- ✅ Optional glass brain outline

## Integration with HTML Report

The HTML report generator (`create_quality_check_html`) should support these new media types:

- `atlas_comparison` - Tract compared to atlas (image/video)
- `afq_profile_image` - Tract with AFQ profile overlay
- `afq_profile_plot` - Line plot of AFQ values
- `cci_plot` - CCI distribution plot (already supported)
- `before_after_cci` - Before/after CCI comparison image
- `bundle_assignment` - Bundle assignment map
- `shape_similarity_score` - Numerical score (display as text/badge)
- `shape_similarity_image` - Shape similarity visualization

## Summary of Implementation Status

### ✅ Fully Implemented
1. ✅ `find_best_view()` - Determine optimal viewing angle (multiple methods)
2. ✅ `generate_static_image()` - Generate static images from specific views
3. ✅ `generate_anatomical_views()` - Generate standard anatomical views
4. ✅ `generate_atlas_views()` - Generate atlas views for comparison
5. ✅ `plot_afq()` - AFQ profile visualization with anatomical views + line plot
6. ✅ `plot_cci()` - CCI visualization with anatomical views + histogram
7. ✅ `calc_cci()` - CCI calculation
8. ✅ `weighted_afq()` - AFQ profile calculation
9. ✅ Atlas comparison - Using `generate_anatomical_views()` + `generate_atlas_views()` with side-by-side HTML display
10. ✅ `calculate_shape_similarity()` - Calculate shape similarity score between tract and atlas using DIPY's bundle_shape_similarity
11. ✅ `visualize_shape_similarity()` - Visualize shape similarity by overlaying subject and atlas tracts with different colors
12. ✅ `compare_before_after_cci()` - Compare tract before/after CCI filtering with side-by-side views
13. ✅ `visualize_bundle_assignment()` - Show bundle assignment map using clustering with color-coded streamlines

### ❌ Still Needed
None - All quality check features have been implemented! 🎉

## Dependencies to Consider

- **For shape similarity:** ✅ Use `bundle_shape_similarity` from `dipy.segment.bundles` (already available in DIPY)
- **For best view:** ✅ Using PCA from `numpy.linalg` (already implemented)
- **For bundle assignment:** ✅ Already using `QuickBundles` from `dipy.segment.clustering`

## Testing Considerations

Each new method should:
- Have proper error handling
- Support optional parameters with sensible defaults
- Return file paths for generated outputs
- Be compatible with existing HTML report generator
- Include docstrings with examples

