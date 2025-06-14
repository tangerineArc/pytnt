from logger.logger import Logger
from parser.expr import (
  Assign, Binary, Call, Expr, Get, Grouping, Literal,
  Logical, Set, Super, This, Unary, Variable
)
from parser.stmt import (
  Block, Class, Expression, Function,
  If, Let, Print, Return, Stmt, While
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


  def declaration(self) -> Stmt: # type: ignore
    try:
      if self.match(TokenType.CLASS):
        return self._class_declaration()

      if self.match(TokenType.FUNCTION):
        return self._function("function")

      if self.match(TokenType.LET):
        return self._var_declaration()

      return self.statement()
    except ParseError:
      self.synchronize()


  def _function(self, kind: str) -> Function:
    name = self.consume(TokenType.IDENTIFIER, f"Expect {kind} name.")
    self.consume(TokenType.LEFT_PAREN, f"Expect '(' after {kind} name.")

    parameters: List[Token] = []
    if not self.check(TokenType.RIGHT_PAREN):
      parameters.append(
        self.consume(TokenType.IDENTIFIER, "Expect parameter name.")
      )

      while self.match(TokenType.COMMA):
        if len(parameters) >= 255:
          Logger.error(
            self.peek(), "Can't have more than 255 parameters."
          )
          # raise ParseError() no throwing errors here

        parameters.append(
          self.consume(
            TokenType.IDENTIFIER, "Expect parameter name."
          )
        )
    self.consume(
      TokenType.RIGHT_PAREN, "Expect ')' after parameters."
    )

    self.consume(
      TokenType.LEFT_BRACE, f"Expect '{{' before {kind} body."
    )
    body = self.block()

    return Function(name, parameters, body)


  def _class_declaration(self) -> Stmt:
    name = self.consume(TokenType.IDENTIFIER, "Expect class name.")

    super_class = None
    if self.match(TokenType.LESS):
      self.consume(TokenType.IDENTIFIER, "Expect superclass name.")
      super_class = Variable(self.previous())

    self.consume(
      TokenType.LEFT_BRACE, "Expect '{' before class body."
    )

    methods: List[Function] = []
    while (
      not self.check(TokenType.RIGHT_BRACE) and
      not self.is_at_end()
    ):
      methods.append(self._function("method"))

    self.consume(
      TokenType.RIGHT_BRACE, "Expect '}' after class body."
    )

    return Class(name, super_class, methods)


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

    if self.match(TokenType.RETURN):
      return self._return_statement()

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


  def _return_statement(self) -> Stmt:
    keyword = self.previous()

    value = None
    if not self.check(TokenType.SEMICOLON):
      value = self.expression()

    self.consume(
      TokenType.SEMICOLON, "Expect ';' after return value."
    )
    return Return(keyword, value)


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
        return Assign(expr.name, value)

      if isinstance(expr, Get):
        return Set(expr.obj, expr.name, value)

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
      elif self.match(TokenType.DOT):
        name = self.consume(TokenType.IDENTIFIER, "Expect property name after '.'.")
        expr = Get(expr, name)
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

    if self.match(TokenType.SUPER):
      keyword = self.previous()
      self.consume(TokenType.DOT, "Expect '.' after 'super'.")

      method = self.consume(
        TokenType.IDENTIFIER, "Expect superclass method name."
      )
      return Super(keyword, method)

    if self.match(TokenType.THIS):
      return This(self.previous())

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
