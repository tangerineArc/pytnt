from logger.logger import Logger
from scanner.token import Token
from scanner.tokentype import TokenType
from typing import List, Optional, Union


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
      case "\"":
        self._scan_string()
      case " ":
        pass
      case "\r":
        pass
      case "\t":
        pass
      case "\n":
        self.line += 1
      case _:
        if self._is_digit(char):
          self._scan_number()
        elif self._is_alpha(char):
          self._scan_identifier()
        else:
          Logger.error(self.line, f"Unexpected character {char}.")

  def _advance(self) -> str:
    char = self.source[self.current]
    self.current += 1
    return char

  def add_token(
    self, token_type: TokenType, literal: Optional[Union[str, float]] = None
  ):
    lexeme = self.source[self.start : self.current]
    self.tokens.append(Token(token_type, lexeme, literal, self.line))

  def _match(self, expected: str) -> bool:
    if self._is_at_end():
      return False
    if self.source[self.current] != expected:
      return False

    self.current += 1
    return True

  def _scan_string(self):
    while self._peek() != '\"' and not self._is_at_end():
      if self._peek() == "\n":
        self.line += 1
      self._advance()

    if self._is_at_end():
      Logger.error(self.line, "Unterminated string.")
      return

    self._advance() # consume the closing "

    value = self.source[self.start + 1 : self.current - 1]
    self.add_token(TokenType.STRING, value)

  def _scan_number(self):
    while self._is_digit(self._peek()):
      self._advance()

    if self._peek() == "." and self._is_digit(self._peek_next()):
      self._advance()
      while self._is_digit(self._peek()):
        self._advance()

    self.add_token(
      TokenType.NUMBER, float(self.source[self.start : self.current])
    )

  def _scan_identifier(self):
    while self._is_alpha_numeric(self._peek()):
      self._advance()

    text = self.source[self.start : self.current]

    self.add_token(TokenType.key_words(text) or TokenType.IDENTIFIER)

  def _peek(self) -> str:
    if self._is_at_end():
      return "\0"
    return self.source[self.current]

  def _peek_next(self) -> str:
    if self.current + 1 >= len(self.source):
      return '\0'

    return self.source[self.current + 1]

  def _is_digit(self, char: str) -> bool:
    return char >= "0" and char <= "9"

  def _is_alpha(self, char: str) -> bool:
    return (
      (char >= "A" and char <= "Z") or
      (char >= "a" and char <= "z") or
      (char == "_")
    )

  def _is_alpha_numeric(self, char: str) -> bool:
    return self._is_alpha(char) or self._is_digit(char)
