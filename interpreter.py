# interpreter.py

from assembler import LOCATION, INSTR
from exceptions import InterpreterError


def read(state: bytearray) -> int:
    current_instr = state[LOCATION.INSTR_PTR]
    state[LOCATION.INSTR_PTR] += 1
    return state[current_instr]


def set_instr_ptr(state: bytearray, addr: int):
    state[LOCATION.INSTR_PTR] = addr


def read_rel(state: bytearray):
    stack_ptr = state[LOCATION.STACK_PTR]
    return (read(state) + stack_ptr) % 256


def add(state: bytearray, addr: int, value: int, set_flag: bool = True):
    res = state[addr] + value
    if set_flag:
        state[LOCATION.FLAG_CARRY] = res not in range(256)

    state[addr] = res % 256


def heapflags(state: bytearray) -> list[bool]:
    flag_bytes = state[LOCATION.HEAPFLAG_START : LOCATION.HEAPFLAG_END + 1]
    flags_as_int = int.from_bytes(flag_bytes, byteorder="big")
    flag_str = bin(flags_as_int)[2:].zfill(64)
    return [bool(int(flag)) for flag in flag_str]


def cycle(state: bytearray) -> int:
    clock_byte = LOCATION.CLOCK_END
    while clock_byte >= LOCATION.CLOCK_START:
        add(state, clock_byte, 1, set_flag=False)
        if state[clock_byte] != 0:
            break
        clock_byte -= 1

    state[LOCATION.OUTPUT] = 0x00

    instr = read(state)
    match instr:
        # NOP
        # Does nothing.
        case INSTR.NOP:
            pass

        # END
        # Keeps the instruction pointer at the current address,
        # effectively preventing the program from doing anything else.
        case INSTR.END:
            set_instr_ptr(state, state[LOCATION.INSTR_PTR] - 1)

        # SET <addr> <value>
        # Sets the value at address <addr> to <value>.
        case INSTR.SET:
            addr = read_rel(state)
            value = read(state)
            state[addr] = value

        # MOV <dest> <src>
        # Copies the value at <src> to <dest>.
        case INSTR.MOV:
            dest = read_rel(state)
            src = read_rel(state)
            state[dest] = state[src]

        # SEND <src> <offset>
        # Copies the value at <src> to the address <src+offset>.
        case INSTR.SEND:
            src = read_rel(state)
            offset_addr = read_rel(state)
            offset = state[offset_addr]
            state[(src + offset) % 256] = state[src]

        # STACK <offset>
        # Adds <offset> to the stack pointer.
        case INSTR.STACK:
            offset = read(state)
            new_stack_ptr = (state[LOCATION.STACK_PTR] + offset) % 256
            state[LOCATION.STACK_PTR] = new_stack_ptr

        # SWAP <addr1> <addr2>
        # Swaps the values at <addr1> and <addr2>.
        case INSTR.SWAP:
            addr1 = read_rel(state)
            addr2 = read_rel(state)
            state[addr1], state[addr2] = state[addr2], state[addr1]

        # JMP <addr>
        # Sets the instruction pointer to the
        # (absolute) address at <addr>.
        case INSTR.JMP:
            addr = read_rel(state)
            set_instr_ptr(state, state[addr])

        # JMPC <dest>
        # Sets the instruction pointer <dest>
        case INSTR.JMPC:
            dest = read(state)
            set_instr_ptr(state, dest)

        # <INSTR> <addr>
        # Conditional jump to the (absolute) address at <addr>
        case (INSTR.JZ | INSTR.JNZ | INSTR.JPOS | INSTR.JNEG):
            condition = read_rel(state)
            dest = read(state)
            predicates = {
                INSTR.JZ: lambda x: x == 0,
                INSTR.JNZ: lambda x: x != 0,
                INSTR.JPOS: lambda x: x in range(0x01, 0x7F),
                INSTR.JNEG: lambda x: x in range(0x80, 0xFF),
            }
            if predicates[instr](state[condition]):
                set_instr_ptr(state, dest)

        # JCARRY <addr>
        # Jump to the absolute address at <addr> if the carry flag is set
        case INSTR.JCARRY:
            dest = read(state)
            if state[LOCATION.FLAG_CARRY]:
                set_instr_ptr(state, dest)

        # JCARRY <addr>
        # Jump to the absolute address at <addr> unless the carry flag is set
        case INSTR.JNCARRY:
            dest = read(state)
            if not state[LOCATION.FLAG_CARRY]:
                set_instr_ptr(state, dest)

        # ADD <dest> <src>
        # Adds the value at relative address <src> to relative address <dest>
        case INSTR.ADD:
            dest = read_rel(state)
            src = read_rel(state)
            add(state, dest, state[src])

        # ADD <dest> <src_const>
        # Adds the constant <src_const> to relative address <dest>
        case INSTR.ADDC:
            dest = read_rel(state)
            src_const = read(state)
            add(state, dest, src_const)

        case INSTR.SUB:
            dest = read_rel(state)
            src = read_rel(state)
            add(state, dest, -state[src])

        case INSTR.SUBC:
            dest = read_rel(state)
            src_const = read(state)
            add(state, dest, -src_const)

        case INSTR.MUL:
            dest = read_rel(state)
            src = read_rel(state)
            state[dest] = (state[dest] * state[src]) % 256

        case INSTR.MULC:
            dest = read_rel(state)
            src_const = read(state)
            state[dest] = (state[dest] * src_const) % 256

        case INSTR.INC:
            addr = read_rel(state)
            add(state, addr, 1)

        case INSTR.DEC:
            addr = read_rel(state)
            add(state, addr, -1)

        case INSTR.IN:
            dest = read_rel(state)
            state[dest] = state[LOCATION.INPUT]

        case INSTR.OUT:
            src = read_rel(state)
            state[LOCATION.OUTPUT] = state[src]

        case INSTR.OUTC:
            src_const = read(state)
            state[LOCATION.OUTPUT] = src_const

        case _:
            raise InterpreterError(f"Unknown instruction: {instr}")

    return state[LOCATION.OUTPUT]
