#!/usr/bin/env python3

# Import standard libraries.
import importlib
import itertools
import pathlib
import re
import shlex
import sys
import tomllib
import traceback

# For type hints.
from typing import Any, TypeAlias

# Import Yadopt.
sys.path.append(str(pathlib.Path(__file__).parent.parent))
import yadopt
import yadopt.errors

# Type aliases.
Path: TypeAlias = pathlib.Path

# Define color code.
COLOR_RED   : str = "\x1b[31m"
COLOR_GREEN : str = "\x1b[32m"
COLOR_YELLOW: str = "\x1b[33m"
COLOR_NONE  : str = "\x1b[0m"


def parse_argv_string_in_toml(testcase_data_argv: str) -> tuple[list[str], str]:
    """
    Parse the argv_xx string in the testcase.

    Args:
        testcase_data_argv (str): String of "argv_xx" in a testcase.

    Returns:
        (tuple[list[str], list[str]]): A tuple of "argv" and assertion lines.
    """
    # Parse the argv_xx string in the testcase.
    (argv_line, *check_lines) = testcase_data_argv.strip().split("\n")

    # Parse the argv line.
    argv: list[str] = shlex.split(argv_line.strip())

    # Parse the check lines.
    check_lines: list[str] = [line[4:].rstrip() for line in check_lines if line.startswith(">>> ")]

    return (argv, "\n".join(check_lines))


def main() -> None:
    """
    Main function of this test script.
    """
    print(f"{COLOR_YELLOW}Starts the tests...{COLOR_NONE}")
    print()

    # Run unittests.
    print("----- Test: run_all_unittests -----")
    unit_test = importlib.import_module("unit_test")
    unit_test.run_all_unittests()
    print(f"{COLOR_GREEN}Passed{COLOR_NONE}")
    print()

    # Load the TOML file of testcases.
    path_testacses: Path = Path(__file__).parent / "testcases.toml"
    with open(path_testacses, "rb") as ifp:
        data: dict[str, Any] = tomllib.load(ifp)

    for testcase_name, testcase_data in data.items():

        # Check the entries of the testcase.
        for key in testcase_data.keys():
            if (key != "docstr") and (not key.startswith("argv_")):
                raise KeyError(f"Extra key: {key}")

        # Get the docstring used in the testcase.
        docstr: str = testcase_data["docstr"]

        # Get the names of "argv_xx" in the testcase.
        argv_names: list[str] = [key for key in testcase_data.keys() if key.startswith("argv_")]

        for argv_name in sorted(argv_names):

            print(f"----- Test: {testcase_name}.{argv_name} -----")

            # Parse the argv_xx string in the testcase.
            (argv, check_code) = parse_argv_string_in_toml(testcase_data[argv_name])

            # Parse the docstring.
            try:
                args = yadopt.parse(docstr, argv, verbose=True)
            except yadopt.errors.YadOptErrorBase as error:
                args = error
            except SystemExit as error:
                args = error

            # Run assertions.
            try:
                exec(check_code)
            except Exception:
                traceback.print_exc()
                print(f"{COLOR_RED}Not passed: {testcase_name}.{argv_name}{COLOR_NONE}")
                return

            print(f"{COLOR_GREEN}Passed{COLOR_NONE}")
            print()

    # Test wrap function.
    print("----- Test: testcase_wrap -----")
    testcase = importlib.import_module("testcase_wrap")
    testcase.test()
    print(f"{COLOR_GREEN}Passed{COLOR_NONE}")
    print()

    print("----- Test results summary -----")
    print(f"{COLOR_GREEN}Passed all tests!!{COLOR_NONE}")


if __name__ == "__main__":
    main()


# vim: expandtab tabstop=4 shiftwidth=4 fdm=marker
