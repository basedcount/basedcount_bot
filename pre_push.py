#!/usr/bin/env python3
"""Run static analysis on the project."""

import sys
from subprocess import CalledProcessError, check_call


def do_process(args: list[str], shell: bool = False, cwd: str = ".") -> bool:
    """Run program provided by args.

    Return ``True`` on success.

    Output failed message on non-zero exit and return False.

    Exit if command is not found.

    """
    print(f"Running: {' '.join(args)}")
    try:
        check_call(args, shell=shell, cwd=cwd)
    except CalledProcessError:
        print(f"\nFailed: {' '.join(args)}")
        return False
    except Exception as exc:
        sys.stderr.write(f"{str(exc)}\n")
        sys.exit(1)
    return True


def run_static() -> bool:
    """Runs the static tests.

    Returns a statuscode of 0 if everything ran correctly. Otherwise, it will return statuscode 1

    """
    success = True
    success &= do_process(["pre-commit", "run", "--all-files"])
    success &= do_process(["mypy", "."])
    return success


def main() -> int:
    """Runs the main function.

    Run static and lint on code

    """
    success = True
    try:
        if success:
            success &= run_static()
    except KeyboardInterrupt:
        return int(not False)
    return int(not success)


if __name__ == "__main__":
    exit_code = main()
    print("\npre_push.py: Success!" if not exit_code else "\npre_push.py: Fail")
    sys.exit(exit_code)
