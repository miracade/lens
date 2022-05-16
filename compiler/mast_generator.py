# compiler.py

from pprint import pprint
from typing import TextIO
from exceptions import CompilerError

from compiler.expression_builder import build_expression
from compiler.reader import EndOfFile, Reader
import compiler.mast as mast


def _process_token(root: mast.Root, reader: Reader):
    """
    Reads one token from the reader and processes it, adding
    any appropriate MASTs to the root.

    Note that this function is not guaranteed to only read one token.
    """
    token = reader.read_token()
    match token:
        # If the token starts with a '#' sign, treat it as
        # a comment and add a mast.Comment node to the root.
        case comment_str if token.startswith("#"):
            comment = mast.Comment(comment_str)
            root.add(comment)

        # If the token is the literal 'if', ensures that the next two
        # tokens are a condition followed by a '{'. Then, constructs
        # a mast.If node and adds it to the root.
        case "if":
            condition = reader.read_token()
            if_ = mast.If(condition)
            root.add(if_)

            brace = reader.read_token()
            if brace != "{":
                raise CompilerError(f"Expected {brace!r} to be {'{'!r}")

        # If the token is the literal 'while', ensures that the next two
        # tokens are a condition followed by a '{'. Then, constructs
        # a mast.While node and adds it to the root.
        case "while":
            condition = reader.read_token()
            while_ = mast.While(condition)
            root.add(while_)

            brace = reader.read_token()
            if brace != "{":
                raise CompilerError(f"Expected {brace!r} to be {'{'!r}")

        # If the token is the literal 'def':
        # 	1. Ensure the next token is  '('.
        # 	2. Continue to read tokens, treating them as function parameters
        # 	   	until a ')' is found.
        # 	3. Ensure the next token is '{'.
        case "def":
            func_name = reader.read_token()
            if reader.read_token() != "(":
                raise CompilerError("A function name must be followed by parentheses.")

            params = []
            while reader.peek_token() != ")":
                params.append(reader.read_token())

            func = mast.FunctionDef(func_name, params)
            root.add(func)

            right_paren = reader.read_token()
            brace = reader.read_token()
            if brace != "{":
                raise CompilerError(f"Expected {brace!r} to be {'{'!r}")

        # If the token is '}', calls root.close() to close the
        # innermost open MAST, thus ending a scope.
        case "}":
            root.close()

        # If the token is a type name such as 'int', the statement is
        # treated as a variable definition. The next token is read and
        # stored as the variable name (identifier).
        case ("int" | "var"):
            type_name = mast.Type(token)
            identifier = mast.Identifier(reader.read_token())
            var_def = mast.VarDef(type_name, identifier)
            root.add(var_def)

        # If the token is the literal 'print', the next token is read.
        # If the next token is alphabetical, it is treated as an identifier.
        # If the next token is numeric, it is treated as a literal.
        case "print":
            printed = reader.read_token()
            if printed.isalpha():
                print_ = mast.Print(mast.Identifier(printed))
            elif printed.isnumeric:
                print_ = mast.Print(mast.Literal(printed))
            else:
                raise CompilerError(
                    f"Expected {printed!r} in print statement to be alphabetic or numeric"
                )

            root.add(print_)

        # If the token is alphabetic but does not meet any of the
        # above criteria, it is assumed to be an identifier.
        case token if token.isalpha():
            expr_tokens = [token] + reader.read_until_separator()
            expr = build_expression(expr_tokens)
            root.add(expr)
            # left = mast.Identifier(token)
            # operator = mast.Operator(reader.read_token())
            # right = reader.read_token()
            # if right.isnumeric():
            # 	right = mast.Literal(right)
            # elif right.isalpha():
            # 	right = mast.Identifier(right)

            # operation = mast.BinOp(left, operator, right)
            # root.add(operation)

        # The token has not been recognized. Raise an error
        case _:
            # print(f"WARN: Unidentified word: {token!r}")
            raise CompilerError(f"Unknown token: {token!r}")


def generate_mast(file: TextIO):
    reader = Reader(file)
    root = mast.Root()
    try:
        while True:
            _process_token(root, reader)

    except EndOfFile:
        ...
        # print(root)

    return root


generate_mast(open("basic.lcom", "r"))
