from __future__ import annotations

import argparse

from src.pipeline_runner import run_pipeline


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="DDR generation pipeline")
    parser.add_argument("--inspection", required=True, help="Path to inspection report (.pdf or .docx)")
    parser.add_argument("--thermal", required=True, help="Path to thermal report (.pdf or .docx)")
    parser.add_argument("--output_dir", required=True, help="Directory for generated DDR outputs")
    parser.add_argument("--config", required=False, default=None, help="Optional YAML config path")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    raise SystemExit(
        run_pipeline(
            inspection_path=args.inspection,
            thermal_path=args.thermal,
            output_dir=args.output_dir,
            config_path=args.config,
        )
    )
