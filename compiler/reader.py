# reader.py

from io import BytesIO
from pprint import pprint
from typing import Iterator, TextIO
from compiler._constants import SYMBOL_CHARS, LONG_SYMBOLS, SEPARATORS
from exceptions import EndOfFile

class Reader:
	def __init__(self, file: TextIO):
		self.file = file
		full_text = file.read()
		self.tokens: list[str] = []

		token = ''
		for char in full_text:
			if token and (token[0] == '#') and (char not in SEPARATORS):
				token += char
				continue

			match char:
				case char if char.isalpha():
					# If the token is empty or the token is alphabetical, 
					# 	append char to the token.
					# Otherwise, start a new token with char.
					if (not token) or token.isalpha():
						token += char
					else:
						self.tokens.append(token)
						token = char

				case char if (char in SEPARATORS):
					# If the token is 0 or more line separators, append char 
					# 	to the token. Otherwise, start a new token with char.
					if token:
						self.tokens.append(token)
						token = ''
					self.tokens.append(char)
					

				case char if char.isspace():
					# If the token is not empty, append it to the list
					# 	and start a new empty token.
					if token:
						self.tokens.append(token)
						token = ''

				case char if char.isnumeric():
					# If the token is empty or the token
					# 	is numeric, append char to the token.
					# Otherwise, start a new token with char.
					if (not token) or token.isnumeric():
						token += char
					else:
						self.tokens.append(token)
						token = char

				case char if (char in SYMBOL_CHARS):
					# If the token is empty, add the char to the token.
					# If the current token + the char is a long symbol,
					# 	add the char to the token.
					# Otherwise, add the current token to the tokens list
					# 	and start a new token with char.
					if not token:
						token += char
					elif (token + char) in LONG_SYMBOLS:
						token += char
					else:
						self.tokens.append(token)
						token = char

				case default:
					raise SyntaxError(f'Illegal character: {default!r}')

		if token:
			self.tokens.append(token)

		self.index = 0


	def read_token(self, skip_separators=True) -> str:
		try:		
			while skip_separators and (self.tokens[self.index] in SEPARATORS):
				self.index += 1			
			self.index += 1
			return self.tokens[self.index - 1]

		except IndexError:
			raise EndOfFile()


	def peek_token(self, skip_separators=True) -> str:
		peek_index = self.index
		try:
			while skip_separators and (self.tokens[peek_index] in SEPARATORS):
				peek_index += 1
			return self.tokens[peek_index]

		except IndexError:
			raise EndOfFile()


	def read_until_separator(self) -> list[str]:
		tokens = []
		while self.peek_token(skip_separators=False) not in SEPARATORS:
			tokens.append(self.read_token())

		return tokens


if __name__ == "__main__":
	with open('basic.mcom', 'r') as file:
		reader = Reader(file)
		pprint(reader.tokens)