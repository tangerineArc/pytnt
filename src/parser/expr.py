from abc import ABC, abstractmethod
from scanner.token import Token
from typing import Protocol, TypeVar, Union


ReturnType = TypeVar("ReturnType", covariant = True)


class Expr(ABC):
  @abstractmethod
  def accept(self, visitor: "Visitor[ReturnType]") -> ReturnType:
    ...


class Visitor(Protocol[ReturnType]):
  def visit_binary_expr(self, expr: "Binary") -> ReturnType: ...
  def visit_grouping_expr(self, expr: "Grouping") -> ReturnType: ...
  def visit_literal_expr(self, expr: "Literal") -> ReturnType: ...
  def visit_unary_expr(self, expr: "Unary") -> ReturnType: ...
  def visit_variable_expr(self, expr: "Variable") -> ReturnType: ...
  def visit_assign_expr(self, expr: "Assign") -> ReturnType: ...
  def visit_logical_expr(self, expr: "Logical") -> ReturnType: ...


class Binary(Expr):
  def __init__(self, left: Expr, operator: Token, right: Expr):
    self.left = left
    self.operator = operator
    self.right = right

  def accept(self, visitor: Visitor[ReturnType]) -> ReturnType:
    return visitor.visit_binary_expr(self)


class Grouping(Expr):
  def __init__(self, expression: Expr):
    self.expression = expression

  def accept(self, visitor: Visitor[ReturnType]) -> ReturnType:
    return visitor.visit_grouping_expr(self)


class Literal(Expr):
  def __init__(self, value: Union[str, float, bool, None]):
    self.value = value

  def accept(self, visitor: Visitor[ReturnType]) -> ReturnType:
    return visitor.visit_literal_expr(self)


class Logical(Expr):
  def __init__(self, left: Expr, operator: Token, right: Expr):
    self.left = left
    self.operator = operator
    self.right = right

  def accept(self, visitor: Visitor[ReturnType]) -> ReturnType:
    return visitor.visit_logical_expr(self)


class Unary(Expr):
  def __init__(self, operator: Token, right: Expr):
    self.operator = operator
    self.right = right

  def accept(self, visitor: Visitor[ReturnType]) -> ReturnType:
    return visitor.visit_unary_expr(self)


class Variable(Expr):
  def __init__(self, name: Token):
    self.name = name

  def accept(self, visitor: Visitor[ReturnType]) -> ReturnType:
    return visitor.visit_variable_expr(self)


class Assign(Expr):
  def __init__(self, name: Token, value: Expr):
    self.name = name
    self.value = value

  def accept(self, visitor: Visitor[ReturnType]) -> ReturnType:
    return visitor.visit_assign_expr(self)
