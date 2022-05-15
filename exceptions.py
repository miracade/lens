# exceptions.py


class InterpreterError(Exception):
    pass


class AssemblerError(Exception):
    pass


class CompilerError(Exception):
    pass


class EndOfFile(Exception):
    pass


class MASTError(CompilerError):
    pass
