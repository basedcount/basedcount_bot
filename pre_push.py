#!/usr/bin/env python
"""Provides simple way to run formatter/linter/static analysis/tests on the project."""

import argparse
import sys
from subprocess import CalledProcessError, check_call


def do_process(args: list[str], cwd: str = ".") -> bool:
    """Run program provided by args.

    Returns ``True`` upon success.

    Output failed message on non-zero exit and return False.

    Exit if command is not found.

    """
    print(f"Running: {' '.join(args)}")
    try:
        check_call(args, shell=False, cwd=cwd)
    except CalledProcessError:
        print(f"\nFailed: {' '.join(args)}")
        return False
    except Exception as exc:
        print(f"{exc!s}\n", file=sys.stderr)
        raise SystemExit(1) from exc
    return True


def run_static_and_lint() -> bool:
    """Runs the static analysis and linting.

    :return: False if everything ran correctly. Otherwise, it will return True

    """
    success = True

    success &= do_process(["mypy", "."])
    success &= do_process(["ruff", "format", "."])
    success &= do_process(["ruff", "check", ".", "--fix"])
    return success


def main() -> int:
    """Runs the main function.

    usage: pre_push.py [-h] [-n] [-u] [-a]

    Run static and/or unit-tests

    """
    parser = argparse.ArgumentParser(description="Run static and/or unit-tests")
    parser.add_argument(
        "-n",
        "--unstatic",
        action="store_true",
        help="Do not run static tests (black/flake8/pydocstyle/sphinx-build)",
        default=False,
    )
    parser.add_argument(
        "-a",
        "--all",
        action="store_true",
        default=False,
        help="Run all the tests (static and unit). Overrides the unstatic argument.",
    )
    args = parser.parse_args()
    success = True
    try:
        if args.all or not args.unstatic:
            success &= run_static_and_lint()

    except KeyboardInterrupt:
        return int(not False)
    return int(not success)


if __name__ == "__main__":
    exit_code = main()
    print("\npre_push.py: Success!" if not exit_code else "\npre_push.py: Fail")
    sys.exit(exit_code)
