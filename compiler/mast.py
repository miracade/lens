# mast.py

from typing import TypeAlias, TypeVar
from exceptions import MASTError


class MAST:
    def __init__(self):
        self.open = False
        self.body: list[MAST] = []

    def __repr__(self):
        type_name = type(self).__name__

        # Remove the 'open' and 'body' attributes from self.__dict__
        # for a cleaner repr() output.
        dict_clean = self.__dict__.copy()
        if not dict_clean["open"]:
            del dict_clean["open"]

        del dict_clean["body"]

        # Construct a string representation of the MAST with
        # its attributes.
        # Example: MAST(string='foo', boolean=True)
        string = f"{type_name}("
        for key, value in dict_clean.items():
            string += f"{key}={value!r}, "
        string = string[:-2]

        # If the MAST has a body, add each line of the body
        # on a separate line.
        if self.has_body():
            string += f", body=["
            for index, mast in enumerate(self.body):
                mast_repr = f"\n\t" + repr(mast).replace("\n", "\n\t")
                string += f"{mast_repr}"

            string += "\n]"

        # Add closing parenthesis, convert tabs to spaces then
        # return the string.
        string += ")"
        return string.expandtabs(4)

    def has_body(self):
        """
        Returns whether self.body contains any (MAST) objects.
        """
        return bool(self.body)

    def add(self, mast: "MAST"):
        """
        If self.open, appends the given MAST to self.body.
        Raises MASTError if self.open is False.
        """
        if self.open:
            self.body.append(mast)
        else:
            raise MASTError(f"MAST {type(self).__name__!r} is closed")


class Root(MAST):
    def __init__(self):
        super().__init__()
        self.open = True

    def add(self, mast: MAST):
        """
        Adds the given MAST to the root.
        """
        # Find the innermost open MAST and add the given MAST to it.
        candidate = self
        while candidate.open and candidate.has_body() and candidate.body[-1].open:
            candidate = candidate.body[-1]

        candidate.body.append(mast)

    def close(self):
        """
        Starting from the root, find the innermost open MAST
        and close it. If no open MAST is found, raise MASTError.
        """
        # Finds the innermost open MAST by repeatedly accessing the
        # last element of the MAST's body.
        mast_hierarchy = [self]
        while mast_hierarchy[-1].has_body():
            mast_hierarchy.append(mast_hierarchy[-1].body[-1])

        # Search for an open MAST, and close it.
        for mast in reversed(mast_hierarchy):
            if mast.open:
                mast.open = False
                return

        raise MASTError(f"Unexpected closing")


class Comment(MAST):
    def __init__(self, value: str):
        super().__init__()
        self.value = value


class Literal(MAST):
    def __init__(self, value):
        super().__init__()
        self.value = value


class Identifier(MAST):
    def __init__(self, value: str):
        super().__init__()
        if not value.isalpha():
            raise MASTError(f"Identifier {value!r} is not alphabetic")

        self.value = value

    def get_addr_str(self, local_vars: dict) -> str:
        if self.value in local_vars:
            return local_vars[self.value].address_str

        raise MASTError(f"Identifier {self.value!r} is not defined")


class Type(MAST):
    def __init__(self, value: str):
        super().__init__()
        self.value = value


class VarDef(MAST):
    def __init__(self, type_name: Type, identifier: Identifier):
        super().__init__()
        self.type_name = type_name
        self.identifier = identifier


class Operator(MAST):
    __match_args__ = ("value",)

    def __init__(self, value: str):
        super().__init__()
        self.value = value


class Expression(MAST):
    __match_args__ = ("left", "operator", "right")

    def __init__(
        self,
        left: "Literal | Identifier | Expression",
        operator: Operator,
        right: "Literal | Identifier | Expression",
    ):
        super().__init__()
        self.left = left
        self.operator = operator
        self.right = right

    @property
    def value(self):
        return f"({self.left.value} {self.operator.value} {self.right.value})"

    def __repr__(self):
        return f"Expression{self.value}"


class BinOp(MAST):
    __match_args__ = ("left", "operator", "right")

    def __init__(self, left: MAST, operator: Operator, right: MAST):
        super().__init__()
        self.left = left
        self.operator = operator
        self.right = right


class VarSet(MAST):
    def __init__(self, identifier: Identifier, value: Literal):
        super().__init__()
        self.identifier = identifier
        self.value = value


class VarCopy(MAST):
    def __init__(self, dest: Identifier, src: Identifier):
        super().__init__()
        self.dest = dest
        self.src = src


class VarAdd(MAST):
    def __init__(self, identifier: Identifier, value: Identifier):
        super().__init__()
        self.identifier = identifier
        self.value = value


class VarAddLiteral(MAST):
    def __init__(self, identifier: Identifier, value: Literal):
        super().__init__()
        self.identifier = identifier
        self.value = value


class If(MAST):
    __match_args__ = ("condition",)

    def __init__(self, condition: str):
        super().__init__()
        self.open = True

        if condition.isnumeric():
            self.condition = Literal(condition)
        elif condition.isalpha():
            self.condition = Identifier(condition)
        else:
            raise MASTError(f"Condition {condition!r} is not alphabetic or numeric")


class While(MAST):
    __match_args__ = ("condition",)

    def __init__(self, condition: str):
        super().__init__()
        self.open = True

        if condition.isalpha():
            self.condition = Identifier(condition)
        else:
            raise MASTError(f"Condition {condition!r} is not alphabetic")


class Print(MAST):
    __match_args__ = ("value",)
    def __init__(self, value: Literal | Identifier):
        super().__init__()
        self.value = value


class FunctionDef(MAST):
    def __init__(self, name: str, params: list[str]):
        super().__init__()
        self.open = True

        self.name = name
        self.params = params


