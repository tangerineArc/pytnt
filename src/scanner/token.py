from scanner.tokentype import TokenType
from typing import Optional, Union


class Token:
  def __init__(
    self,
    token_type: TokenType,
    lexeme: str,
    literal: Optional[Union[str, float]],
    line: int
  ):
    self.type = token_type
    self.lexeme = lexeme
    self.literal = literal # change datatype to object later
    self.line = line

  def to_string(self): # remove this method
    return f"{self.type} {self.lexeme} {self.literal}"

  def __repr__(self):
    return f"Token({self.type}, {self.lexeme}, {self.literal}, {self.line})"
