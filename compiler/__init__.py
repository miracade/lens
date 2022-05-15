# __init__.py

__all__ = ["mast_compiler.py", "mast_generator.py", "mast.py", "reader.py"]

from compiler.mast_generator import generate_mast
from compiler.mast_compiler import compile_mast


def compile(filename: str, outfilename: str):
    """
    Compilation of a .mcom file involves two essential steps:
            1. Generating a MiniMini Abstract Syntax Tree (MAST) from
                    the .mcom source code.
            2. Compiling the MAST into a .masm file.

    """
    with open(filename, "r") as file:
        root = generate_mast(file)
        # print(root)
    compiled = compile_mast(root)
    with open(outfilename, "w") as file:
        file.write(compiled)


if __name__ == "__main__":
    compile("basic.mcom", "basic.masm")
    with open("basic.masm", "r") as file:
        text = file.read()
        print("-" * 80)
        print(text)
