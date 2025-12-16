"""Allow running as `python -m glvar`."""

import sys

import glvar.cli as cli_module


if __name__ == "__main__":
    # Handle -- separator for the run command
    if "--" in sys.argv:
        sep_idx = sys.argv.index("--")
        cli_module._doubledash_command = sys.argv[sep_idx + 1 :]
        sys.argv = sys.argv[:sep_idx]
    cli_module.cli()
