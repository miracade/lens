# tester.py

import compiler
import assembler
from assembler import INSTR, LOCATION
from interpreter import cycle

from pathlib import Path


def run_test_file(test_path: Path):
    """
    Runs the test file at the given path.

    A test file has the extension .ltest. Tests are separated by
    header lines with the following format:

    >>> <test_name> outputs <expected_output>
    >>> <test_name> concludes <expected_output>
    >>> <test_name> fails

    Each test is run as a separate file.
    """

    print(f"\nRunning test file {test_path}")

    # Get the full text of the test file
    with open(test_path, "r") as file:
        text = file.read()

    # Split by ">>>" to get the test cases. Ignore all text before
    # the first test case
    tests = text.split(">>>")[1:]

    # Run each test
    for test in tests:
        # Separate the header line from the test code
        header, _, code = test.partition("\n")

        # Split the header line by whitespace to get the test title and
        # expectation (either "outputs" or "fails")
        header = header.strip().split()
        title = f"{header[0]:<40}"
        expectation = header[1]

        # Write the test code to "_test.lcom"
        with open("_test.lcom", "w") as lcom:
            lcom.write(code)

        if expectation in ("outputs", "concludes"):
            expected_output = [int(i) for i in header[2:]]

            try:
                compiler.compile("_test.lcom", "_test.lasm")
                with open("_test.lasm", "r") as lasm:
                    state = assembler.masm_to_bytecode(lasm)

            except Exception as e:
                print(f"  {title} - Failed")
                print(f"  {e}")
                continue

            if expectation == "outputs":
                output: list[int] = []
                for _ in range(len(expected_output)):
                    output.append(cycle(state))

            elif expectation == "concludes":
                while state[state[LOCATION.INSTR_PTR]] != INSTR.END:
                    cycle(state)

                stack_ptr = state[LOCATION.STACK_PTR]
                output = state[stack_ptr : stack_ptr + len(expected_output)]
                output = [int(i) for i in output]

            if output == expected_output:
                print(f"  {title} - Passed")
            else:
                print(f"  {title} - Failed")
                print(f"    Expected: {expected_output}")
                print(f"    Output:   {output}")

        elif expectation == "fails":
            try:
                compiler.compile("_test.lcom", "_test.lasm")
                with open("_test.lasm", "r") as lasm:
                    state = assembler.masm_to_bytecode(lasm)

            except Exception as e:
                print(f"  {title} - Passed (Successfully raised exception)")

            else:
                print(f"  {title} - Failed")
                print(f"    Expected exception, but none was raised")

        else:
            print(f"  {title} - Invalid test")
            print(f'    Header must use "outputs", "expects", or "fails"')


if __name__ == "__main__":
    test_dir = Path("tests/")
    for path in test_dir.glob("*.ltest"):
        run_test_file(path)
