from logger.logger import Logger
from parser.expr import Binary, Expr, Grouping, Literal, Unary
from parser.stmt import Expression, Print, Stmt
from scanner.token import Token
from scanner.tokentype import TokenType
from typing import List


class Parser:
  def __init__(self, tokens: List[Token]):
    self.tokens = tokens
    self.current = 0


  def parse(self) -> List[Stmt]:
    statements: List[Stmt] = []
    while not self.is_at_end():
      statements.append(self.statement())

    return statements


  def statement(self) -> Stmt:
    if self.match(TokenType.PRINT):
      return self._print_statement()

    return self._expression_statement()


  def _print_statement(self) -> Stmt:
    value = self.expression()
    self.consume(TokenType.SEMICOLON, "Expect ';' after value.")
    return Print(value)


  def _expression_statement(self) -> Stmt:
    expr = self.expression()
    self.consume(TokenType.SEMICOLON, "Expect ';' after expression.")
    return Expression(expr)


  def expression(self) -> Expr:
    return self.equality()


  def equality(self) -> Expr:
    expr = self.comparison()

    while self.match(TokenType.BANG_EQUAL, TokenType.EQUAL_EQUAL):
      operator = self.previous()
      right = self.comparison()
      expr = Binary(expr, operator, right)

    return expr


  def comparison(self) -> Expr:
    expr = self.term()

    while self.match(
      TokenType.GREATER, TokenType.GREATER_EQUAL,
      TokenType.LESS, TokenType.LESS_EQUAL
    ):
      operator = self.previous()
      right = self.term()
      expr = Binary(expr, operator, right)

    return expr


  def term(self) -> Expr:
    expr = self.factor()

    while self.match(TokenType.MINUS, TokenType.PLUS):
      operator = self.previous()
      right = self.factor()
      expr = Binary(expr, operator, right)

    return expr


  def factor(self) -> Expr:
    expr = self.unary()

    while self.match(TokenType.SLASH, TokenType.STAR):
      operator = self.previous()
      right = self.unary()
      expr = Binary(expr, operator, right)

    return expr


  def unary(self) -> Expr:
    if self.match(TokenType.BANG, TokenType.MINUS, TokenType.PLUS):
      operator = self.previous()
      right = self.unary()
      return Unary(operator, right)

    return self.primary()


  def primary(self) -> Expr:
    if self.match(TokenType.FALSE):
      return Literal(False)
    if self.match(TokenType.TRUE):
      return Literal(True)
    if self.match(TokenType.VOID):
      return Literal(None)

    if self.match(TokenType.NUMBER, TokenType.STRING):
      return Literal(self.previous().literal)

    if self.match(TokenType.LEFT_PAREN):
      expr = self.expression()
      self.consume(TokenType.RIGHT_PAREN, "Expect ')' after expression")
      return Grouping(expr)

    Logger.error(self.peek(), "Expect expression.")
    raise ParseError()


  def synchronize(self):
    self.advance()

    while not self.is_at_end():
      if self.previous().type == TokenType.SEMICOLON:
        return

      match self.peek().type:
        case TokenType.CLASS:
          return
        case TokenType.FUNCTION:
          return
        case TokenType.LET:
          return
        case TokenType.FOR:
          return
        case TokenType.IF:
          return
        case TokenType.WHILE:
          return
        case TokenType.PRINT:
          return
        case TokenType.RETURN:
          return
        case _:
          pass

      self.advance()


  def match(self, *types: TokenType) -> bool:
    for token_type in types:
      if self.check(token_type):
        self.advance()
        return True

    return False


  def check(self, token_type: TokenType) -> bool:
    if self.is_at_end():
      return False

    return self.peek().type == token_type


  def advance(self) -> Token:
    if not self.is_at_end():
      self.current += 1

    return self.previous()


  def is_at_end(self) -> bool:
    return self.peek().type == TokenType.EOF


  def peek(self) -> Token:
    return self.tokens[self.current]


  def previous(self) -> Token:
    return self.tokens[self.current - 1]


  def consume(self, token_type: TokenType, message: str) -> Token:
    if self.check(token_type):
      return self.advance()

    Logger.error(self.peek(), message)
    raise ParseError()


class ParseError(RuntimeError):
  def __init__(self, *args: object):
    super().__init__(*args)
