from scanner.token import Token
from scanner.tokentype import TokenType

from typing import List


class Scanner:
  def __init__(self, source: str):
    self.source = source
    self.tokens: List[Token] = []
    self.start = 0
    self.current = 0
    self.line = 1

  def scan_tokens(self) -> List[Token]:
    while self.current < len(self.source):
      self.start = self.current
      self.scan_token()

    self.tokens.append(Token(TokenType.EOF, "", None, self.line))
    return self.tokens

  def scan_token(self):
    ...
