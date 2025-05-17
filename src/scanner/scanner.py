from logger.logger import Logger
from scanner.token import Token
from scanner.tokentype import TokenType
from typing import List


class Scanner:
  def __init__(self, source: str):
    self.source = source
    self.tokens: List[Token] = []
    self.current = 0
    self.start = 0
    self.line = 1

  def scan_tokens(self) -> List[Token]:
    while not self._is_at_end():
      self.start = self.current
      self.scan_token()

    self.tokens.append(Token(TokenType.EOF, "", None, self.line))
    return self.tokens

  def _is_at_end(self):
    return self.current >= len(self.source)

  def scan_token(self):
    char = self._advance()
    match char:
      case ",":
        self.add_token(TokenType.COMMA)
      case ".":
        self.add_token(TokenType.DOT)
      case "{":
        self.add_token(TokenType.LEFT_BRACE)
      case "(":
        self.add_token(TokenType.LEFT_PAREN)
      case "}":
        self.add_token(TokenType.RIGHT_BRACE)
      case ")":
        self.add_token(TokenType.RIGHT_PAREN)
      case "-":
        self.add_token(TokenType.MINUS)
      case "+":
        self.add_token(TokenType.PLUS)
      case ";":
        self.add_token(TokenType.SEMICOLON)
      case "*":
        self.add_token(TokenType.STAR)
      case "!":
        self.add_token(
          TokenType.BANG_EQUAL if self._match("=")
          else TokenType.BANG
        )
      case "=":
        self.add_token(
          TokenType.EQUAL_EQUAL if self._match("=")
          else TokenType.EQUAL
        )
      case ">":
        self.add_token(
          TokenType.GREATER_EQUAL if self._match("=")
          else TokenType.GREATER
        )
      case "<":
        self.add_token(
          TokenType.LESS_EQUAL if self._match("=")
          else TokenType.LESS
        )
      case "/":
        if self._match("/"): # match comments
          while self._peek() != "\n" and not self._is_at_end():
            self._advance()
        else:
          self.add_token(TokenType.SLASH)
      case " ":
        pass
      case "\r":
        pass
      case "\t":
        pass
      case "\n":
        self.line += 1
      case _:
        Logger.error(self.line, f"Unexpected character {char}.")

  def _advance(self) -> str:
    char = self.source[self.current]
    self.current += 1
    return char

  def add_token(self, token_type: TokenType):
    lexeme = self.source[self.start : self.current]
    # overload literal
    self.tokens.append(Token(token_type, lexeme, None, self.line))

  def _match(self, expected: str) -> bool:
    if self._is_at_end():
      return False
    if self.source[self.current] != expected:
      return False

    self.current += 1
    return True

  def _peek(self) -> str:
    if self._is_at_end():
      return "\0"
    return self.source[self.current]
