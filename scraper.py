#!/usr/bin/env python3
"""
Lead Generation Scraper — CLI entry point.

Usage:
    python scraper.py
"""
import os
import sys
from datetime import date

import google_places
import excel_exporter


def _prompt(message: str, default: str = "") -> str:
    """Show a prompt and return stripped input, falling back to default."""
    suffix = f" [{default}]" if default else ""
    try:
        value = input(f"{message}{suffix}: ").strip()
    except (KeyboardInterrupt, EOFError):
        print("\nAborted.")
        sys.exit(0)
    return value if value else default


def _progress_bar(current: int, total: int, width: int = 40) -> str:
    filled = int(width * current / total) if total else width
    bar = "█" * filled + "░" * (width - filled)
    return f"[{bar}] {current}/{total}"


def _safe_filename(text: str) -> str:
    """Convert user input to a filesystem-safe slug."""
    return (
        text.lower()
        .replace(" ", "-")
        .replace("/", "-")
        .replace("\\", "-")
        .replace(":", "")
        .replace("'", "")
        .replace('"', "")
    )


def main() -> None:
    print("\n=== Lead Generation Scraper ===\n")

    # ── Interactive prompts ───────────────────────────────────────────────────
    category = _prompt("Business category (e.g. plumbers, dentists)")
    if not category:
        print("Category is required.")
        sys.exit(1)

    city = _prompt("City / area (e.g. Cape Town)")
    if not city:
        print("City is required.")
        sys.exit(1)

    min_stars_str = _prompt("Minimum star rating", default="4.0")
    try:
        min_stars = float(min_stars_str)
    except ValueError:
        print(f"Invalid rating '{min_stars_str}'. Using 4.0.")
        min_stars = 4.0

    max_results_str = _prompt("Maximum results", default="50")
    try:
        max_results = int(max_results_str)
    except ValueError:
        print(f"Invalid number '{max_results_str}'. Using 50.")
        max_results = 50

    # ── Search ────────────────────────────────────────────────────────────────
    print(f'\nSearching for "{category}" in "{city}" with ≥{min_stars} stars...')

    try:
        matches = google_places.search_businesses(
            category=category,
            city=city,
            min_stars=min_stars,
            max_results=max_results,
        )
    except Exception as exc:
        print(f"Error during search: {exc}")
        sys.exit(1)

    if not matches:
        print("No businesses found matching your criteria.")
        sys.exit(0)

    print(f"Found {len(matches)} matching businesses. Fetching details...\n")

    # ── Fetch details ─────────────────────────────────────────────────────────
    enriched = []
    total = len(matches)

    for idx, business in enumerate(matches, start=1):
        place_id = business.get("place_id")
        print(f"\r{_progress_bar(idx, total)}", end="", flush=True)
        if not place_id:
            continue
        try:
            details = google_places.get_place_details(place_id)
            enriched.append(details)
        except Exception as exc:
            # Don't abort on a single failure — log and continue
            print(f"\n  Warning: could not fetch details for place_id={place_id}: {exc}")

    print()  # newline after progress bar

    if not enriched:
        print("Could not retrieve details for any businesses.")
        sys.exit(1)

    # ── Export ────────────────────────────────────────────────────────────────
    os.makedirs("output", exist_ok=True)

    today = date.today().isoformat()
    cat_slug = _safe_filename(category)
    city_slug = _safe_filename(city)
    filename = f"output/{today}_{cat_slug}_{city_slug}_{min_stars}stars.xlsx"

    try:
        excel_exporter.export(
            businesses=enriched,
            category=category,
            city=city,
            output_path=filename,
        )
    except Exception as exc:
        print(f"Error writing Excel file: {exc}")
        sys.exit(1)

    print(f"Exported → {filename}")


if __name__ == "__main__":
    main()
