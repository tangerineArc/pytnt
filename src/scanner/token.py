from scanner.tokentype import TokenType

from typing import Optional


class Token:
  def __init__(self, token_type: TokenType, lexeme: str, literal: Optional[str], line: int):
    self.type = token_type
    self.lexeme = lexeme
    self.literal = literal # change datatype to object later
    self.line = line

  def to_string(self):
    return f"{self.type} {self.lexeme} {self.literal}"
