import argparse
from pathlib import Path

from .core import main as _main   # assumes you have main(config_path=None) in core.py


def main():
    parser = argparse.ArgumentParser(
        description="Run the epi2hit pipeline."
    )
    parser.add_argument(
        "-c", "--config",
        help="Path to configuration file (YAML/JSON/etc.).",
    )
    args = parser.parse_args()

    config_path = None
    if args.config is not None:
        p = Path(args.config).expanduser().resolve()
        if not p.is_file():
            raise SystemExit(f"Config file not found: {p}")
        config_path = str(p)

    _main(config_path=config_path)

