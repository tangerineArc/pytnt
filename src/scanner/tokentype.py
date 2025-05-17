from enum import Enum


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
  COLON_EQUAL = ":="
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
