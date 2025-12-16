"""
Version module for boulder-opal-scale-up package.

This module uses the centralized version utilities from boulder-opal-scale-up-sdk
to provide version information in a format compatible with the poetry-get-version workflow.
"""

import argparse
import sys

from boulderopalscaleupsdk.utils.version import get_version


def main():
    """Main entry point for version script."""
    parser = argparse.ArgumentParser(description="Get package version")
    parser.add_argument(
        "--strip-local",
        action="store_true",
        help="Strip local version identifiers",
    )

    args = parser.parse_args()

    try:
        version = get_version(
            package_name="boulder-opal-scale-up",
            strip_local=args.strip_local,
        )
        print(version)  # noqa: T201
        return 0  # noqa: TRY300
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)  # noqa: T201
        return 1


if __name__ == "__main__":
    sys.exit(main())
