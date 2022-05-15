# mast_compiler.py

from string import ascii_uppercase
from typing import Iterator, NamedTuple, Optional, TextIO
import re

import operator
import compiler.mast as mast

from compiler.expression_builder import expr_to_masm
from compiler.namespace import Namespace


def _indent_str(string: str, spaces: int = 4) -> str:
    indent = " " * spaces
    return indent + string.replace("\n", "\n" + indent)


def _remove_comments(string: str) -> str:
    return re.sub(r"#.*?\n", "", string)


def _traverse(parent: mast.MAST, parent_namespace: Namespace | None) -> str:
    namespace = Namespace(parent_namespace)
    output_str = ""
    for child in parent.body:
        match child:
            case mast.Comment():
                output_str += f"{child.value}\n"

            case mast.Literal():
                output_str += f"{child.value}"

            case mast.Identifier():
                output_str += f"{child.value}"

            case mast.Type():
                pass

            case mast.VarDef():
                var_name = child.identifier.value
                namespace.add_identifier(var_name, "int")

            case mast.Expression():
                masm_instrs = expr_to_masm(child, namespace)
                output_str += f"# {child!r}\n"
                output_str += _indent_str("\n".join(masm_instrs))
                output_str += "\n"

            case mast.BinOp(mast.Identifier(), mast.Operator("="), mast.Literal()):
                var_address = child.left.get_addr_str(namespace)
                const = child.right.value
                output_str += f"SET {var_address} {const}\n"

            case mast.BinOp(mast.Identifier(), mast.Operator("="), mast.Identifier()):
                dest_address = child.left.get_addr_str(namespace)
                src_address = child.right.get_addr_str(namespace)
                output_str += f"MOV {dest_address} {src_address}\n"

            case mast.BinOp(mast.Identifier(), mast.Operator("+="), mast.Literal()):
                var_address = child.left.get_addr_str(namespace)
                const = child.right.value
                output_str += f"ADDC {var_address} {const}\n"

            case mast.BinOp(mast.Identifier(), mast.Operator("+="), mast.Identifier()):
                dest_address = child.left.get_addr_str(namespace)
                src_address = child.right.get_addr_str(namespace)
                output_str += f"ADD {dest_address} {src_address}\n"

            case mast.If(mast.Identifier()):
                condition_addr = namespace[child.condition.value].addr_as_str
                body_str = _traverse(child, namespace)
                body_len = len(_remove_comments(body_str).split())

                output_str += f"JZ {condition_addr} @LEN+{body_len + 1}\n"
                output_str += _indent_str(body_str)
                output_str += "\n"

            case mast.While(mast.Identifier()):
                condition_addr = namespace[child.condition.value].addr_as_str
                body_str = _traverse(child, namespace)
                body_len = len(_remove_comments(body_str).split())

                output_str += f"JZ {condition_addr} @LEN+{body_len + 3}\n"
                output_str += _indent_str(body_str)
                output_str += f"JMPC @LEN-{body_len + 4}\n"

            case mast.FunctionDef(name="main"):
                output_str += f"&MAIN\n"
                output_str += _indent_str(_traverse(child, None))
                output_str += "\nEND\n"

            case mast.FunctionDef():
                output_str += f"&{child.name}\n"
                output_str += _indent_str(_traverse(child, None))
                output_str += "\nJMPC @A\n"

            case default:
                raise Exception(f"Unsupported node type: {child}")

    return output_str


def compile_mast(root: mast.Root, output_file: Optional[TextIO] = None) -> str:
    output = _traverse(root, None)
    if output_file is not None:
        output_file.write(output)

    return output


if __name__ == "__main__":
    from mast_generator import generate_mast

    root = generate_mast(open("basic.lcom", "r"))
    compiled = compile_mast(root)

    print("# COMPILED:\n" + compiled, file=open("basic.lasm", "w"))
