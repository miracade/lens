# mast_compiler.py

from string import ascii_uppercase
from typing import Iterator, NamedTuple, Optional, TextIO
import re

import operator
import compiler.mast as mast

from compiler.expression_builder import expr_to_masm


class VarInfo(NamedTuple):
	address: int
	type_name: str
	@property
	def address_str(self):
		if self.address in range(len(ascii_uppercase)):
			return '@' + ascii_uppercase[self.address]

		return str(self.address)


def _indent_str(string: str, spaces: int = 4) -> str:
	indent = ' ' * spaces
	return indent + string.replace('\n', '\n' + indent)


def _remove_comments(string: str) -> str:
	return re.sub(r'#.*?\n', '', string)


def _next_free_address(var_dict: dict[str, VarInfo]) -> int:
	location = 0
	while location in map(operator.attrgetter('address'), var_dict.values()):
		location += 1

	return location


def _free_addresses(var_dict: dict[str, VarInfo]) -> list[int]:
	addresses = map(operator.attrgetter('address'), var_dict.values())
	free_addrs: list[int] = []
	for addr in range(0, 64):
		if addr not in addresses:
			free_addrs.append(addr)

	return free_addrs


def _traverse(parent: mast.MAST, nonlocal_vars: dict[str, VarInfo]) -> str:
	local_vars: dict[str, VarInfo] = nonlocal_vars.copy()
	output_str = ''
	for child in parent.body:
		match child:
			case mast.Comment():
				output_str += f'{child.value}\n'


			case mast.Literal():
				output_str += f'{child.value}'


			case mast.Identifier():
				output_str += f'{child.value}'


			case mast.Type():
				pass


			case mast.VarDef():
				location = _next_free_address(local_vars)
				var_id = child.identifier.value
				local_vars[var_id] = VarInfo(location, child.type_name)


			case mast.Expression():
				masm_instrs = expr_to_masm(child, local_vars, _free_addresses(local_vars))
				output_str += f'# {child!r}\n'
				output_str += _indent_str('\n'.join(masm_instrs))
				output_str += '\n'


			case mast.BinOp(mast.Identifier(), mast.Operator('='), mast.Literal()):
				var_address = child.left.get_addr_str(local_vars)
				const = child.right.value
				output_str += f'SET {var_address} {const}\n'


			case mast.BinOp(mast.Identifier(), mast.Operator('='), mast.Identifier()):
				dest_address = child.left.get_addr_str(local_vars)
				src_address = child.right.get_addr_str(local_vars)
				output_str += f'MOV {dest_address} {src_address}\n'


			case mast.BinOp(mast.Identifier(), mast.Operator('+='), mast.Literal()):
				var_address = child.left.get_addr_str(local_vars)
				const = child.right.value
				output_str += f'ADDC {var_address} {const}\n'


			case mast.BinOp(mast.Identifier(), mast.Operator('+='), mast.Identifier()):
				dest_address = child.left.get_addr_str(local_vars)
				src_address = child.right.get_addr_str(local_vars)
				output_str += f'ADD {dest_address} {src_address}\n'


			case mast.If(mast.Identifier()):
				condition_addr = child.condition.get_addr_str(local_vars)
				body_str = _traverse(child, local_vars)
				body_len = len(_remove_comments(body_str).split())

				output_str += f'JZ {condition_addr} @LEN+{body_len + 1}\n'
				output_str += _indent_str(body_str)
				output_str += '\n'


			case mast.While(mast.Identifier()):
				condition_addr = child.condition.get_addr_str(local_vars)
				body_str = _traverse(child, nonlocal_vars | local_vars)
				body_len = len(_remove_comments(body_str).split())

				output_str += f'JZ {condition_addr} @LEN+{body_len + 3}\n'
				output_str += _indent_str(body_str)
				output_str += f'JMPC @LEN-{body_len + 4}\n'


			case mast.FunctionDef(name='main'):
				output_str += f'&MAIN\n'
				output_str += _indent_str(_traverse(child, {}))
				output_str += '\nEND\n'


			case mast.FunctionDef():
				output_str += f'&{child.name}\n'
				output_str += _indent_str(_traverse(child, {}))
				output_str += '\nJMPC @A\n'

			
			case default:
				raise Exception(f'Unsupported node type: {child}')


	return output_str


def compile_mast(root: mast.Root, output_file: Optional[TextIO] = None) -> str:
	output = _traverse(root, {})
	if output_file is not None:
		output_file.write(output)

	return output


if __name__ == '__main__':
	from mast_generator import generate_mast
	root = generate_mast(open('basic.mcom', 'r'))
	compiled = compile_mast(root)

	print('# COMPILED:\n' + compiled, file=open('basic.masm', 'w'))