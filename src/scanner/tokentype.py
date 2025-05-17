from enum import Enum
from typing import Optional


class TokenType(Enum):
  # single-character tokens
  COMMA = ","
  DOT = "."
  LEFT_BRACE = "{"
  LEFT_PAREN = "("
  RIGHT_BRACE = "}"
  RIGHT_PAREN = ")"
  MINUS = "-"
  PLUS = "+"
  SEMICOLON = ";"
  SLASH = "/"
  STAR = "*"

  # one or two-character tokens
  BANG = "!"
  BANG_EQUAL = "!="
  EQUAL = "="
  EQUAL_EQUAL = "=="
  GREATER = ">"
  GREATER_EQUAL = ">="
  LESS = "<"
  LESS_EQUAL = "<="

  # literals
  IDENTIFIER = "ident"
  NUMBER = "num"
  STRING = "str"

  # keywords
  AND = "and"
  CLASS = "class"
  ELSE = "else"
  FALSE = "false"
  FOR = "for"
  FUNCTION = "function"
  IF = "if"
  LET = "let"
  OR = "or"
  PRINT = "print"
  RETURN = "return"
  SUPER = "super"
  THIS = "this"
  TRUE = "true"
  VOID = "void"
  WHILE = "while"

  EOF = "eof"

  # to-do: new, construct, <-

  @staticmethod
  def key_words(key: str) -> Optional["TokenType"]:
    reserved_words = {
      "and": TokenType.AND,
      "class": TokenType.CLASS,
      "else": TokenType.ELSE,
      "false": TokenType.FALSE,
      "for": TokenType.FOR,
      "function": TokenType.FUNCTION,
      "if": TokenType.IF,
      "let": TokenType.LET,
      "or": TokenType.OR,
      "print": TokenType.PRINT,
      "return": TokenType.RETURN,
      "super": TokenType.SUPER,
      "this": TokenType.THIS,
      "true": TokenType.TRUE,
      "void": TokenType.VOID,
      "while": TokenType.WHILE,
    }

    return reserved_words.get(key, None)
