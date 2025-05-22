from abc import ABC, abstractmethod
from parser.expr import Expr
from scanner.token import Token
from typing import List, Optional, Protocol, TypeVar


ReturnType = TypeVar("ReturnType", covariant = True)


class Stmt(ABC):
  @abstractmethod
  def accept(self, visitor: "Visitor[ReturnType]") -> ReturnType:
    ...


class Visitor(Protocol[ReturnType]):
  def visit_expression_stmt(self, stmt: "Expression") -> ReturnType: ...
  def visit_print_stmt(self, stmt: "Print") -> ReturnType: ...
  def visit_let_stmt(self, stmt: "Let") -> ReturnType: ...
  def visit_block_stmt(self, stmt: "Block") -> ReturnType: ...
  def visit_if_stmt(self, stmt: "If") -> ReturnType: ...
  def visit_while_stmt(self, stmt: "While") -> ReturnType: ...
  def visit_function_stmt(self, stmt: "Function") -> ReturnType: ...


class Expression(Stmt):
  def __init__(self, expression: Expr):
    self.expression = expression

  def accept(self, visitor: Visitor[ReturnType]) -> ReturnType:
    return visitor.visit_expression_stmt(self)


class Print(Stmt):
  def __init__(self, expression: Expr):
    self.expression = expression

  def accept(self, visitor: Visitor[ReturnType]) -> ReturnType:
    return visitor.visit_print_stmt(self)


class Let(Stmt):
  def __init__(self, name: Token, initializer: Optional[Expr]):
    self.name = name
    self.initializer = initializer

  def accept(self, visitor: Visitor[ReturnType]) -> ReturnType:
    return visitor.visit_let_stmt(self)


class Block(Stmt):
  def __init__(self, statements: List[Stmt]):
    self.statements = statements

  def accept(self, visitor: Visitor[ReturnType]) -> ReturnType:
    return visitor.visit_block_stmt(self)


class Function(Stmt):
  def __init__(
    self, name: Token, params: List[Token], body: List[Stmt]
  ):
    self.name = name
    self.params = params
    self.body = body

  def accept(self, visitor: Visitor[ReturnType]) -> ReturnType:
    return visitor.visit_function_stmt(self)


class If(Stmt):
  def __init__(
    self, condition: Expr, then_branch: Stmt, else_branch: Optional[Stmt]
  ):
    self.condition = condition
    self.then_branch = then_branch
    self.else_branch = else_branch

  def accept(self, visitor: Visitor[ReturnType]) -> ReturnType:
    return visitor.visit_if_stmt(self)


class While(Stmt):
  def __init__(self, condition: Expr, body: Stmt):
    self.condition = condition
    self.body = body

  def accept(self, visitor: Visitor[ReturnType]) -> ReturnType:
    return visitor.visit_while_stmt(self)
