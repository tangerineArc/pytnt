from abc import ABC, abstractmethod
from parser.expr import Expr
from typing import Protocol, TypeVar


ReturnType = TypeVar("ReturnType", covariant = True)


class Stmt(ABC):
  @abstractmethod
  def accept(self, visitor: "Visitor[ReturnType]") -> ReturnType:
    ...


class Visitor(Protocol[ReturnType]):
  def visit_expression_stmt(self, stmt: "Expression") -> ReturnType: ...
  def visit_print_stmt(self, stmt: "Print") -> ReturnType: ...


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
