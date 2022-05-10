# expression_builder.py

from typing import Iterator

from numpy import nanstd
import compiler.mast as mast
from compiler._constants import EXPR_OPS, EXPR_OP_PRECEDENCE, EXPR_INSTRS

Component = mast.Identifier | mast.Literal | mast.Expression


def _str_to_mast(string: str) -> mast.Expression:
	if string in EXPR_OPS:
		return mast.Operator(string)

	elif string.isnumeric():
		return mast.Literal(string)

	elif string.isalpha():
		return mast.Identifier(string)

	raise mast.MASTError(f'Could not convert expression token {string!r} to MAST')


def build_expression(tokens: list[str]) -> mast.Expression:
	"""
	Builds an Expression from a list of tokens.
	"""
	# Convert all tokens (strings) to MAST objects.
	tokens = [_str_to_mast(t) for t in tokens]
	operators = [op for op in tokens if isinstance(op, mast.Operator)]

	# Iterate through the list of tokens, assigning a precedence to each
	# operator. Precedence is determined by parentheses, as well as
	# the precedence value of the operator in EXPR_OP_PRECEDENCE.
	scope = 0
	for token in tokens:
		if isinstance(token, mast.Operator):
			if token.value == '(':
				scope += 10
			elif token.value == ')':
				scope -= 10

			token_precedence = EXPR_OP_PRECEDENCE[token.value] + scope
			token._p = token_precedence

	# Check for equal amount of opening and closing parentheses
	if scope != 0:
		raise mast.MASTError(f'Unbalanced parentheses in expression {tokens!r}')

	# Remove all parentheses operators from the list of tokens as well
	# as the set of operators; they are no longer needed
	for op in operators:
		if op.value in '()':
			tokens.remove(op)

	operators = [op for op in operators if op.value not in '()']

	while operators:
		# Pop the operator with the highest precedence
		highest = max(operators, key=lambda op: op._p)
		operators.remove(highest)

		# Get the index of the operator
		op_index = tokens.index(highest)
		match highest.value:
			case op if op in ('=', '+', '-', '*', '/'):
				# Get the left and right sides of the assignment
				left_index = op_index - 1
				right_index = op_index + 1
				try:
					left = tokens[left_index]
					right = tokens[right_index]
				except IndexError:
					tokens_str = '\n\t'.join(repr(t) for t in tokens)
					raise mast.MASTError(f"Invalid operator in expression \n\t{tokens_str}")

				tokens[left_index:right_index+1] = [mast.Expression(left, highest, right)]

	if len(tokens) != 1:
		raise mast.MASTError(f'Invalid expression {tokens!r}')

	return tokens[0]


def expr_to_masm(expr: mast.Expression, var_dict: dict, free_addrs: list[int]) -> list[str]:
	output: list[str] = []

	addr_instr, const_instr = EXPR_INSTRS[expr.operator.value]

	# If the expression is an assignment expression ('='), then we can use
	# expr.left as a memory address to work with. 
	if expr.operator.value == '=':
		if not isinstance(expr.left, mast.Identifier):
			raise mast.MASTError(f'Can only assign to identifiers, not {expr.left!r}')

		free_addrs.insert(0, expr.left.get_addr_str(var_dict))

	else:
		# Ensure that free_addrs[0] contains the evaluated value of expr.left
		if isinstance(expr.left, mast.Identifier):
			output.append(f'MOV {free_addrs[0]} {expr.left.get_addr_str(var_dict)}')

		elif isinstance(expr.left, mast.Literal):
			output.append(f'SET {free_addrs[0]} {expr.left.value}')
			
		elif isinstance(expr.left, mast.Expression):
			output.extend(expr_to_masm(expr.left, var_dict, free_addrs))

	# Compute the value of the right side of the expression if necessary,
	# storing it in free_addrs[1]. Then, augmented-add expr.right to expr.left.
	if isinstance(expr.right, mast.Identifier):
		if expr.right.value not in var_dict:
			raise Exception(f'Unknown identifier {expr.right!r}')

		output.append(f'{addr_instr} {free_addrs[0]} {expr.right.get_addr_str(var_dict)}')

	elif isinstance(expr.right, mast.Literal):
		output.append(f'{const_instr} {free_addrs[0]} {expr.right.value}')

	if isinstance(expr.right, mast.Expression):
		output.extend(expr_to_masm(expr.right, var_dict, free_addrs[1:]))
		output.append(f'{addr_instr} {free_addrs[0]} {free_addrs[1]}')


	return output




if __name__ == '__main__':
	print(build_expression(['1', '+', '2']))