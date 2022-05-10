# namespace.py

from typing import NamedTuple
from string import ascii_uppercase


class Var(NamedTuple):
	name: str
	type: str
	addr: int

	def __repr__(self):
		return f'Var({self.type} {self.name}: addr={self.addr_as_str})'

	@property
	def addr_as_str(self):
		return Namespace.addr_as_str(self.addr)


class Namespace:
	def __init__(self, parent: 'Namespace' = None):
		self.vars: list[Var] = []
		if parent:
			self.vars.extend(parent.vars)


	def __repr__(self):
		return f'Namespace(vars={self.vars!r})'


	def __getitem__(self, name: str) -> Var:
		"""
		Returns the Var object for the given variable name.
		"""
		for var in self.vars:
			if var.name == name:
				return var

		raise KeyError(f'{name} is not in the namespace')


	def __contains__(self, name: str) -> bool:
		"""
		Returns whether or not the given name is in the namespace.
		"""
		return name in [v.name for v in self.vars]


	@staticmethod
	def addr_as_str(addr: int) -> str:
		"""
		Given an address, returns the address's string representation
		in @ macro notation. If such a macro does not exist, returns
		the integer as a string.

		For example, 
			addr_to_str( 0) returns '@A'
			addr_to_str( 1) returns '@B'
			addr_to_str(-1) returns '-1'
		"""
		if addr in range(len(ascii_uppercase)):
			return '@' + ascii_uppercase[addr]

		return str(addr)


	def address_occupied(self, address: int) -> bool:
		"""
		Given an address, returns whether or not the address is
		currently occupied.
		"""
		for var in self.vars:
			if var.addr == address:
				return True

		return False


	def get_free_addresses(self, check_dist: int = 64) -> list[int]:
		"""
		Returns a list of string representations of free addresses.
		"""
		free_addrs: list[int] = []
		for i in range(check_dist):
			if not self.address_occupied(i):
				free_addrs.append(i)

		return free_addrs


	def get_free_address(self, check_dist: int = 64) -> int:
		"""
		Gets the next free address as a string.
		"""
		for i in range(check_dist):
			if not self.address_occupied(i):
				return i


	def add_identifier(self, name: str, type: str) -> Var:
		"""
		Adds an identifier to the namespace, returning the Var
		object created
		"""
		addr = self.get_free_address()
		var = Var(name, type, addr)
		self.vars.append(var)
		print(self)
		return var
