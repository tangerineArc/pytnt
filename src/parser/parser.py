from logger.logger import Logger
from parser.expr import (
  Assign, Binary, Call, Expr, Grouping,
  Literal, Logical, Unary, Variable
)
from parser.stmt import (
  Block, Expression, If, Let, Print, Stmt, While
)
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
      statements.append(self.declaration())

    return statements


  def declaration(self) -> Stmt:
    try:
      if self.match(TokenType.LET):
        return self._var_declaration()

      return self.statement()
    except ParseError:
      self.synchronize()
      ... # return something


  def _var_declaration(self) -> Stmt:
    name = self.consume(
      TokenType.IDENTIFIER,
      "Expect variable name."
    )

    initializer = None
    if self.match(TokenType.EQUAL):
      initializer = self.expression()

    self.consume(
      TokenType.SEMICOLON,
      "Expect ';' after variable declaration"
    )

    return Let(name, initializer)


  def statement(self) -> Stmt:
    if self.match(TokenType.FOR):
      return self._for_statement()

    if self.match(TokenType.IF):
      return self._if_statement()

    if self.match(TokenType.PRINT):
      return self._print_statement()

    if self.match(TokenType.WHILE):
      return self._while_statement()

    if self.match(TokenType.LEFT_BRACE):
      return Block(self.block())

    return self._expression_statement()


  def _for_statement(self) -> Stmt: # lots of desugaring
    self.consume(TokenType.LEFT_PAREN, "Expect '(' after 'for'.")

    initializer = None
    if self.match(TokenType.SEMICOLON):
      initializer = None
    elif self.match(TokenType.LET):
      initializer = self._var_declaration()
    else:
      initializer = self._expression_statement()

    condition = None
    if not self.check(TokenType.SEMICOLON):
      condition = self.expression()
    self.consume(TokenType.SEMICOLON, "Expect ';' after loop condition.")

    increment = None
    if not self.check(TokenType.RIGHT_PAREN):
      increment = self.expression()
    self.consume(TokenType.RIGHT_PAREN, "Expect ')' after for clauses.")

    body = self.statement()

    if increment != None:
      body = Block([body, Expression(increment)])

    if condition == None:
      condition = Literal(True)
    body = While(condition, body)

    if initializer != None:
      body = Block([initializer, body])

    return body


  def _if_statement(self) -> Stmt:
    self.consume(TokenType.LEFT_PAREN, "Expect '(' after 'if'.")
    condition = self.expression()
    self.consume(
      TokenType.RIGHT_PAREN,
      "Expect ')' after 'if' condition."
    )

    then_branch = self.statement()
    else_branch = None
    if self.match(TokenType.ELSE):
      else_branch = self.statement()

    return If(condition, then_branch, else_branch)


  def _print_statement(self) -> Stmt:
    value = self.expression()
    self.consume(TokenType.SEMICOLON, "Expect ';' after value.")
    return Print(value)


  def _while_statement(self) -> Stmt:
    self.consume(TokenType.LEFT_PAREN, "Expect '(' after 'while'.")
    condition = self.expression()
    self.consume(TokenType.RIGHT_PAREN, "Expect ')' after condition.")
    body = self.statement()

    return While(condition, body)


  def _expression_statement(self) -> Stmt:
    expr = self.expression()
    self.consume(TokenType.SEMICOLON, "Expect ';' after expression.")
    return Expression(expr)


  def block(self) -> List[Stmt]:
    statements: List[Stmt] = []

    while not self.check(TokenType.RIGHT_BRACE) and not self.is_at_end():
      statements.append(self.declaration())

    self.consume(TokenType.RIGHT_BRACE, "Expect '}' after block.")
    return statements


  def expression(self) -> Expr:
    return self.assignment()


  def assignment(self) -> Expr:
    expr = self._or()

    if self.match(TokenType.EQUAL):
      equals = self.previous()
      value = self.assignment()

      if isinstance(expr, Variable):
        name = expr.name
        return Assign(name, value)

      Logger.error(equals, "Invalid assignment target.")
      # raise ParseError() no throwing errors here

    return expr


  def _or(self) -> Expr:
    expr = self._and()

    while self.match(TokenType.OR):
      operator = self.previous()
      right = self._and()
      expr = Logical(expr, operator, right)

    return expr


  def _and(self) -> Expr:
    expr = self.equality()

    while self.match(TokenType.AND):
      operator = self.previous()
      right = self.equality()
      expr = Logical(expr, operator, right)

    return expr


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

    return self.call()


  def call(self) -> Expr:
    expr = self.primary()

    while True:
      if self.match(TokenType.LEFT_PAREN):
        expr = self._finish_call(expr)
      else:
        break

    return expr


  def primary(self) -> Expr:
    if self.match(TokenType.FALSE):
      return Literal(False)
    if self.match(TokenType.TRUE):
      return Literal(True)
    if self.match(TokenType.VOID):
      return Literal(None)

    if self.match(TokenType.NUMBER, TokenType.STRING):
      return Literal(self.previous().literal)

    if self.match(TokenType.IDENTIFIER):
      return Variable(self.previous())

    if self.match(TokenType.LEFT_PAREN):
      expr = self.expression()
      self.consume(
        TokenType.RIGHT_PAREN, "Expect ')' after expression"
      )
      return Grouping(expr)

    Logger.error(self.peek(), "Expect expression.")
    raise ParseError


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
    raise ParseError


  def _finish_call(self, callee: Expr) -> Expr:
    arguments: List[Expr] = []
    if not self.check(TokenType.RIGHT_PAREN):
      arguments.append(self.expression())

      while self.match(TokenType.COMMA):
        if len(arguments) >= 255:
          Logger.error(self.peek(), "Can't have more than 255 arguments.")
          # raise ParseError # no throwing errors again

        arguments.append(self.expression())

    paren = self.consume(
      TokenType.RIGHT_PAREN, "Expect ')' after arguments."
    )
    return Call(callee, paren, arguments)


class ParseError(RuntimeError):
  def __init__(self, *args: object):
    super().__init__(*args)
