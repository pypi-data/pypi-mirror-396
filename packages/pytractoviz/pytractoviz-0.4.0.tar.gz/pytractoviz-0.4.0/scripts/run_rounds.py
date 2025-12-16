#!/usr/bin/env python3
"""Script to run quality check workflow in separate rounds for memory management.

This script allows running different types of image generation in separate rounds,
so that memory can be cleared between rounds. It also supports generating atlas views
once for all subjects instead of per subject.
"""

from __future__ import annotations

import argparse
import gc
import json
import logging
import sys
from pathlib import Path

# Add src to path so we can import pytractoviz
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from pytractoviz.html import create_quality_check_html
from pytractoviz.viz import TractographyVisualizer

logger = logging.getLogger(__name__)


def load_config(config_file: Path) -> dict:
    """Load configuration from JSON file."""
    with open(config_file) as f:
        return json.load(f)


def save_results(results: dict, output_file: Path) -> None:
    """Save results dictionary to JSON file."""
    # Convert Path objects to strings for JSON serialization
    results_serializable: dict[str, dict[str, dict[str, str]]] = {}
    for subject_id, subject_tracts in results.items():
        results_serializable[subject_id] = {}
        if isinstance(subject_tracts, dict):
            for tract_name, media_dict in subject_tracts.items():
                results_serializable[subject_id][tract_name] = {}
                if isinstance(media_dict, dict):
                    for media_type, file_path in media_dict.items():
                        results_serializable[subject_id][tract_name][media_type] = str(file_path)

    with open(output_file, "w") as f:
        json.dump(results_serializable, f, indent=2)


def load_results(results_file: Path) -> dict[str, dict[str, dict[str, str]]]:
    """Load results dictionary from JSON file."""
    if not results_file.exists():
        return {}
    with open(results_file) as f:
        return json.load(f)


def merge_results(existing: dict, new: dict) -> dict:
    """Merge new results into existing results."""
    for subject_id, subject_tracts in new.items():
        if subject_id not in existing:
            existing[subject_id] = {}
        if isinstance(subject_tracts, dict):
            for tract_name, media_dict in subject_tracts.items():
                if tract_name not in existing[subject_id]:
                    existing[subject_id][tract_name] = {}
                if isinstance(media_dict, dict):
                    existing[subject_id][tract_name].update(media_dict)
    return existing


def run_round(
    round_name: str,
    config: dict,
    results_file: Path,
    output_dir: Path,
) -> None:
    """Run a specific round of image generation."""
    logger.info("=" * 80)
    logger.info("Starting round: %s", round_name)
    logger.info("=" * 80)

    # Load existing results
    existing_results = load_results(results_file)

    # Create visualizer
    visualizer = TractographyVisualizer(
        output_directory=str(output_dir),
        n_jobs=config.get("n_jobs", 1),
        figure_size=tuple(config.get("figure_size", [800, 800])),
    )

    # Determine which checks to skip
    all_checks = [
        "anatomical_views",
        "atlas_comparison",
        "cci",
        "before_after_cci",
        "afq_profile",
        "bundle_assignment",
        "shape_similarity",
    ]

    # Determine skip_checks based on round
    if round_name == "anatomical":
        skip_checks = [c for c in all_checks if c != "anatomical_views"]
    elif round_name == "cci":
        skip_checks = [c for c in all_checks if c != "cci"]
    elif round_name == "before_after_cci":
        skip_checks = [c for c in all_checks if c != "before_after_cci"]
    elif round_name == "atlas_views":
        # For atlas views, we'll generate them once for all subjects
        # We also generate subject MNI views here for atlas comparison
        skip_checks = all_checks  # Skip all other checks (handled separately)
    elif round_name == "shape_similarity":
        skip_checks = [c for c in all_checks if c != "shape_similarity"]
    elif round_name == "afq_profile":
        skip_checks = [c for c in all_checks if c != "afq_profile"]
    elif round_name == "bundle_assignment":
        skip_checks = [c for c in all_checks if c != "bundle_assignment"]
    else:
        raise ValueError(f"Unknown round name: {round_name}")

    # Prepare data structures
    subjects_original_space = config["subjects_original_space"]
    subjects_mni_space = config.get("subjects_mni_space")
    atlas_files = config.get("atlas_files")
    metric_files = config.get("metric_files")
    atlas_ref_img = config.get("atlas_ref_img")
    ref_img = config.get("ref_img")
    flip_lr = config.get("flip_lr", False)

    # Handle reference image - can be single path or dict mapping subject_id -> path
    # Convert string paths to Path objects, keep dict as-is (workflow handles it)
    if isinstance(ref_img, str):
        # Single reference image for all subjects
        ref_img_path: str | Path | dict[str, str | Path] | None = Path(ref_img)
    elif isinstance(ref_img, dict):
        # Per-subject reference images - convert values to Path objects
        ref_img_path = {subject_id: Path(path) for subject_id, path in ref_img.items()}
    else:
        ref_img_path = None

    # Special handling for atlas_views round - generate once for all subjects
    if round_name == "atlas_views":
        if atlas_files is None:
            logger.warning("No atlas_files provided, skipping atlas_views round")
            return

        # Create a shared atlas output directory
        atlas_output_dir = output_dir / "atlas_views"
        atlas_output_dir.mkdir(parents=True, exist_ok=True)

        # Generate atlas views once for each tract
        atlas_results: dict[str, dict[str, dict[str, str]]] = {}
        for tract_name, atlas_file in atlas_files.items():
            logger.info("Generating atlas views for tract: %s", tract_name)
            try:
                # Note: Set flip_lr=False to match MNI views (which should match original views)
                atlas_views = visualizer.generate_atlas_views(
                    atlas_file,
                    atlas_ref_img=atlas_ref_img,
                    flip_lr=False,  # Set to False to match MNI views
                    output_dir=atlas_output_dir,
                    **config.get("atlas_kwargs", {}),
                )

                # Add atlas views to results for all subjects that have this tract
                for subject_id, tracts in subjects_original_space.items():
                    if tract_name in tracts:
                        if subject_id not in atlas_results:
                            atlas_results[subject_id] = {}
                        if tract_name not in atlas_results[subject_id]:
                            atlas_results[subject_id][tract_name] = {}
                        # Add atlas views with the same keys as in the workflow
                        for view_name, view_path in atlas_views.items():
                            atlas_results[subject_id][tract_name][f"atlas_{view_name}"] = str(view_path)

                # Clean up after each atlas
                del atlas_views
                gc.collect()
            except Exception:
                logger.exception("Failed to generate atlas views for %s", tract_name)

        # Also generate subject MNI views if subjects_mni_space is provided
        # These are needed for atlas comparison even though atlas views are generated once
        if subjects_mni_space is not None:
            logger.info("Generating subject MNI views for atlas comparison")
            for subject_id, tracts in subjects_mni_space.items():
                subject_output_dir = output_dir / subject_id
                for tract_name, tract_file_mni in tracts.items():
                    if tract_name in atlas_files:  # Only generate if atlas exists
                        tract_output_dir = subject_output_dir / tract_name
                        tract_output_dir.mkdir(parents=True, exist_ok=True)
                        try:
                            # Note: Don't apply flip_lr here - MNI views should match original anatomical views
                            subject_mni_views = visualizer.generate_anatomical_views(
                                tract_file_mni,
                                ref_img=atlas_ref_img,  # Use atlas ref image for MNI space
                                output_dir=tract_output_dir,
                                **config.get("subject_kwargs", {}),
                            )
                            # Add subject MNI views to results
                            if subject_id not in atlas_results:
                                atlas_results[subject_id] = {}
                            if tract_name not in atlas_results[subject_id]:
                                atlas_results[subject_id][tract_name] = {}
                            for view_name, view_path in subject_mni_views.items():
                                atlas_results[subject_id][tract_name][f"subject_mni_{view_name}"] = str(view_path)
                            del subject_mni_views
                            gc.collect()
                        except Exception:
                            logger.exception(
                                "Failed to generate subject MNI views for %s/%s",
                                subject_id,
                                tract_name,
                            )

        # Merge atlas results into existing results
        existing_results = merge_results(existing_results, atlas_results)
        save_results(existing_results, results_file)
        logger.info("Atlas views round completed")
        return

    # For other rounds, run the normal workflow with skip_checks
    try:
        round_results = visualizer.run_quality_check_workflow(
            subjects_original_space=subjects_original_space,
            ref_img=ref_img_path,
            subjects_mni_space=subjects_mni_space,
            atlas_files=atlas_files,
            metric_files=metric_files,
            atlas_ref_img=atlas_ref_img,
            flip_lr=flip_lr,
            output_dir=output_dir,
            skip_checks=skip_checks,
            html_output=None,  # Don't generate HTML in individual rounds
            subject_kwargs=config.get("subject_kwargs"),
            atlas_kwargs=config.get("atlas_kwargs"),
            **config.get("kwargs", {}),
        )

        # Merge results
        existing_results = merge_results(existing_results, round_results)
        save_results(existing_results, results_file)

        logger.info("Round %s completed successfully", round_name)
    except Exception:
        logger.exception("Error in round %s", round_name)
        raise
    finally:
        # Clean up visualizer
        del visualizer
        gc.collect()


def generate_html(config: dict, results_file: Path, output_dir: Path) -> None:
    """Generate HTML report from accumulated results."""
    logger.info("=" * 80)
    logger.info("Generating HTML report")
    logger.info("=" * 80)

    # Load all results
    results = load_results(results_file)

    if not results:
        logger.warning("No results found, cannot generate HTML report")
        return

    # Convert string paths back to Path objects for HTML generation
    results_for_html: dict[str, dict[str, dict[str, str]]] = {}
    for subject_id, subject_tracts in results.items():
        results_for_html[subject_id] = {}
        if isinstance(subject_tracts, dict):
            for tract_name, media_dict in subject_tracts.items():
                results_for_html[subject_id][tract_name] = {}
                if isinstance(media_dict, dict):
                    for media_type, file_path in media_dict.items():
                        results_for_html[subject_id][tract_name][media_type] = str(file_path)

    # Generate HTML
    html_output_config = config.get("html_output")
    html_output = output_dir / "quality_check_report.html" if html_output_config is None else Path(html_output_config)

    create_quality_check_html(
        results_for_html,
        str(html_output),
        title="Tractography Quality Check Report",
    )
    logger.info("HTML report generated: %s", html_output)


def run_all_rounds(
    config: dict,
    results_file: Path,
    output_dir: Path,
    skip_rounds: list[str] | None = None,
) -> None:
    """Run all rounds sequentially."""
    if skip_rounds is None:
        skip_rounds = []

    # Define rounds in order
    rounds = [
        "anatomical",
        "cci",
        "before_after_cci",
        "atlas_views",
        "shape_similarity",
        "afq_profile",
        "bundle_assignment",
    ]

    logger.info("=" * 80)
    logger.info("Running quality check workflow in rounds")
    logger.info("=" * 80)
    logger.info("Config file: %s", config.get("_config_path", "N/A"))
    logger.info("Output directory: %s", output_dir)
    logger.info("Results file: %s", results_file)
    logger.info("")

    # Run each round
    for round_name in rounds:
        if round_name in skip_rounds:
            logger.info("Skipping round: %s", round_name)
            continue

        logger.info("")
        logger.info("=" * 80)
        logger.info("Running round: %s", round_name)
        logger.info("=" * 80)

        try:
            run_round(round_name, config, results_file, output_dir)
            logger.info("Round %s completed successfully", round_name)
        except Exception:
            logger.exception("ERROR: Round %s failed", round_name)
            raise

        # Force garbage collection and memory clearing between rounds
        logger.debug("Clearing memory between rounds...")
        gc.collect()

    # Generate HTML report at the end
    logger.info("")
    logger.info("=" * 80)
    logger.info("Generating HTML report")
    logger.info("=" * 80)

    try:
        generate_html(config, results_file, output_dir)
        logger.info("HTML report generated successfully")
    except Exception:
        logger.exception("ERROR: HTML generation failed")
        raise

    logger.info("")
    logger.info("=" * 80)
    logger.info("All rounds completed successfully!")
    logger.info("=" * 80)


def main() -> int:
    """Run the main program."""
    parser = argparse.ArgumentParser(
        description="Run quality check workflow in separate rounds for memory management",
    )
    parser.add_argument(
        "round",
        nargs="?",
        choices=[
            "anatomical",
            "cci",
            "before_after_cci",
            "atlas_views",
            "shape_similarity",
            "afq_profile",
            "bundle_assignment",
            "html",
            "all",
        ],
        default="all",
        help="Round to run (default: 'all' to run all rounds sequentially)",
    )
    parser.add_argument(
        "--config",
        type=Path,
        required=True,
        help="Path to JSON configuration file",
    )
    parser.add_argument(
        "--results-file",
        type=Path,
        default=None,
        help="Path to JSON file for accumulating results (default: <output_dir>/results.json)",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=None,
        help="Output directory (overrides config)",
    )
    parser.add_argument(
        "--skip",
        action="append",
        help="Skip specific rounds (can be used multiple times)",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable verbose logging",
    )

    args = parser.parse_args()

    # Setup logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    # Load config
    config = load_config(args.config)
    # Store config path for logging
    config["_config_path"] = str(args.config)

    # Determine output directory
    output_dir = args.output_dir
    if output_dir is None:
        output_dir = Path(config.get("output_dir", "output"))
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Determine results file
    results_file = args.results_file
    if results_file is None:
        results_file = output_dir / "results.json"
    results_file = Path(results_file)

    # Determine skip rounds
    skip_rounds = args.skip if args.skip else []

    try:
        if args.round == "all":
            run_all_rounds(config, results_file, output_dir, skip_rounds=skip_rounds)
        elif args.round == "html":
            generate_html(config, results_file, output_dir)
        else:
            run_round(args.round, config, results_file, output_dir)
    except Exception:
        logger.exception("Fatal error")
        return 1
    else:
        return 0


if __name__ == "__main__":
    sys.exit(main())
