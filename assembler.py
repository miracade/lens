# assembler.py

from string import ascii_uppercase
from typing import TextIO
import enum


class LOCATION(enum.IntEnum):
    INSTR_PTR = 0x00
    STACK_PTR = 0x01
    FLAG_CARRY = 0x02
    CLOCK_START = 0x04
    CLOCK_END = 0x07
    INPUT = 0x08
    OUTPUT = 0x09
    HEAPFLAG_START = 0x0A
    HEAPFLAG_END = 0x0F
    HEADER_END = 0x0F

    HEAP_START = 0x80
    HEAP_END = 0xFF


@enum.unique
class INSTR(enum.IntEnum):
    NOP = 0x00
    END = 0x01
    SET = 0x02
    # SETN = 0x03
    # CLR = 0x04
    # CLRN = 0x05
    MOV = 0x06
    # MOVN = 0x07
    SEND = 0x08
    STACK = 0x0A
    SWAP = 0x0C

    JMP = 0x10
    JMPC = 0x11
    JZ = 0x12
    JNZ = 0x13
    JPOS = 0x14
    JNEG = 0x15

    JCARRY = 0x18
    JNCARRY = 0x19

    ADD = 0x20
    ADDC = 0x21
    SUB = 0x22
    SUBC = 0x23
    MUL = 0x24
    MULC = 0x26

    INC = 0x30
    DEC = 0x31
    # OR  = 0x32
    # ORC = 0x33
    # AND = 0x34
    # ANDC = 0x35
    # INV = 0x36

    IN = 0x40
    OUT = 0x48


def masm_to_bytecode(file: TextIO):
    macros = {char: index for index, char in enumerate(ascii_uppercase)}
    bytecode = bytearray([0x00] * LOCATION.HEADER_END)
    for line in file:
        for word in line.split():
            macros["LEN"] = len(bytecode)

            word = word.strip()

            # Comment
            if word.startswith("#"):
                break

            # Defining a macro
            elif word.startswith("&"):
                macros[word[1:]] = len(bytecode)
                continue

            # Using a macro
            elif word.startswith("@"):
                if "+" in word:
                    macro, shift = word[1:].split("+")
                    word = macros[macro] + int(shift)
                elif "-" in word:
                    macro, shift = word[1:].split("-")
                    word = macros[macro] - int(shift)
                else:
                    word = macros[word[1:]]

            # Using an instruction
            elif word in INSTR.__members__:
                word = INSTR[word]

            # Adding instruction to bytecode
            bytecode.append(int(word) % 256)

    bytecode[LOCATION.INSTR_PTR] = macros["MAIN"]
    bytecode[LOCATION.STACK_PTR] = len(bytecode) // 16 * 16 + 16

    while len(bytecode) < 0x100:
        bytecode.append(0x00)

    return bytecode


if __name__ == "__main__":
    with open("basic.masm") as file:
        bytecode = masm_to_bytecode(file)
        print(bytecode.hex(sep=" "))

    with open("code.mbin", "wb") as file:
        file.write(bytecode)
