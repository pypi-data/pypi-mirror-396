# src/civic_data_identity_us_il/make_chicago_identity_sample.py
"""
Generate an identity-focused sample from the Chicago contracts CSV.

Defaults (when run with no arguments):

- Input:  latest data/raw/chicago_contracts_*.csv
- Output: data/identity/chicago_contracts_vendors_sample_20k.csv
- Rows:   20000

Usage examples:

    # Use defaults
    uv run python src/civic_data_identity_us_il/make_chicago_identity_sample.py

    # Custom number of rows
    uv run python src/civic_data_identity_us_il/make_chicago_identity_sample.py \
        --n-rows 5000

    # Custom input and output, overwriting if exists
    uv run python src/civic_data_identity_us_il/make_chicago_identity_sample.py \
        --input data/raw/chicago_contracts_2025-12-11.csv \
        --output data/identity/chicago_sample_10k.csv \
        --n-rows 10000 \
        --overwrite
"""

import argparse
import sys
from pathlib import Path
from typing import Optional, Sequence

import pandas as pd
from pandas.errors import EmptyDataError


DEFAULT_ROWS = 20_000
RAW_PATTERN = "chicago_contracts_*.csv"
DEFAULT_OUTPUT_NAME = "chicago_contracts_vendors_sample_20k.csv"


def find_default_input(raw_dir: Path) -> Optional[Path]:
    """Find the default input CSV under data/raw.

    Strategy:
    - Look for files matching RAW_PATTERN.
    - If multiple, pick the lexicographically last (usually newest by naming).
    """
    candidates = sorted(raw_dir.glob(RAW_PATTERN))
    if not candidates:
        return None
    return candidates[-1]


def default_paths() -> tuple[Optional[Path], Path]:
    """Compute default input and output paths relative to project root."""
    # This file: src/civic_data_identity_us_il/make_chicago_identity_sample.py
    here = Path(__file__).resolve()
    # Project root is two levels up: repo_root / src / package / this_file
    project_root = here.parents[2]

    raw_dir = project_root / "data" / "raw"
    identity_dir = project_root / "data" / "identity"

    default_input = find_default_input(raw_dir)
    default_output = identity_dir / DEFAULT_OUTPUT_NAME

    return default_input, default_output


def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    default_input, default_output = default_paths()

    parser = argparse.ArgumentParser(
        description="Generate an identity-focused sample from the Chicago contracts CSV."
    )

    parser.add_argument(
        "--input",
        type=Path,
        default=default_input,
        help=(
            "Path to the full Chicago contracts CSV. "
            "Defaults to the latest chicago_contracts_*.csv under data/raw."
        ),
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=default_output,
        help=(
            "Path to write the sampled CSV. "
            "Defaults to data/identity/chicago_contracts_vendors_sample_20k.csv."
        ),
    )
    parser.add_argument(
        "--n-rows",
        type=int,
        default=DEFAULT_ROWS,
        help=f"Number of rows to include in the sample (default: {DEFAULT_ROWS}).",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite output file if it already exists.",
    )

    args = parser.parse_args(argv)

    # Basic sanity checks and friendly messages
    if args.input is None:
        parser.error(
            "Could not find a default input file under data/raw.\n"
            "Expected something like data/raw/chicago_contracts_YYYY-MM-DD.csv.\n"
            "Please specify --input explicitly."
        )

    if not args.input.exists():
        parser.error(f"Input file does not exist: {args.input}")

    if args.output.exists() and not args.overwrite:
        parser.error(f"Output file already exists: {args.output}\nUse --overwrite to replace it.")

    if args.n_rows <= 0:
        parser.error("--n-rows must be a positive integer.")

    return args


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = parse_args(argv)

    # Ensure parent directory exists for output
    args.output.parent.mkdir(parents=True, exist_ok=True)

    # Overwrite behavior messaging
    if args.output.exists():
        if args.overwrite:
            print(f"Overwriting existing file: {args.output}")
        else:
            print(
                f"Error: Output file already exists and --overwrite was not provided:\n"
                f"  {args.output}",
                file=sys.stderr,
            )
            return 1

    print(f"Input CSV:  {args.input}")
    print(f"Output CSV: {args.output}")
    print(f"Rows:       {args.n_rows}")

    try:
        # Read the full CSV; keep all columns so we can evolve later without
        # changing this script when the adapter needs more fields.
        df = pd.read_csv(args.input, dtype=str, low_memory=False)
    except EmptyDataError:
        print(
            f"Error: The input file '{args.input}' appears to be empty or has no columns.\n"
            "Please verify that it is a valid CSV export from the City of Chicago portal.",
            file=sys.stderr,
        )
        return 1
    except OSError as exc:
        print(
            f"Error: Could not read input file '{args.input}': {exc}",
            file=sys.stderr,
        )
        return 1

    if df.empty:
        print(
            f"Error: The input file '{args.input}' was read successfully, "
            "but it contains zero rows.",
            file=sys.stderr,
        )
        return 1

    # Deterministic "first N rows" sample.
    n = min(args.n_rows, len(df))
    if n < args.n_rows:
        print(
            f"Warning: Requested {args.n_rows} rows, but input only has {len(df)}; "
            f"using {n} rows instead.",
            file=sys.stderr,
        )

    sample = df.head(n)
    sample.to_csv(args.output, index=False)
    print(f"Wrote {len(sample)} rows to {args.output}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
