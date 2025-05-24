from enum import auto, Enum
from interpreter.interpreter import Interpreter
from logger.logger import Logger
from parser.expr import (
  Assign, Binary, Call, Expr, Get, Grouping, Literal,
  Logical, Set, Super, This, Unary, Variable, Visitor as ExprVisitor
)
from parser.stmt import (
  Block, Class, Expression, Function, If, Let, Print,
  Return, Stmt, Visitor as StmtVisitor, While
)
from scanner.token import Token
from typing import cast, Dict, List


class ClassType(Enum):
  NONE = auto()
  CLASS = auto()
  SUBCLASS = auto()


class FunctionType(Enum):
  NONE = auto()
  FUNCTION = auto()
  INITIALIZER = auto()
  METHOD = auto()


class Resolver(ExprVisitor[None], StmtVisitor[None]):
  def __init__(self, interpreter: Interpreter):
    self.interpreter = interpreter
    # stack of local scopes only
    self.scopes: List[Dict[str, bool]] = []

    self.current_function = FunctionType.NONE
    self.current_class = ClassType.NONE


  def visit_block_stmt(self, stmt: Block):
    self._begin_scope()
    self.resolve(stmt.statements)
    self._end_scope()


  def visit_class_stmt(self, stmt: Class):
    enclosing_class = self.current_class
    self.current_class = ClassType.CLASS

    self._declare(stmt.name)
    self._define(stmt.name)

    if (
      stmt.super_class is not None and
      stmt.name.lexeme == stmt.super_class.name.lexeme
    ):
      Logger.error(
        stmt.super_class.name, "A class can't inherit from itself."
      )

    if stmt.super_class is not None:
      self.current_class = ClassType.SUBCLASS
      self.resolve(stmt.super_class)

    if stmt.super_class is not None:
      self._begin_scope()
      self.scopes[-1]["super"] = True

    self._begin_scope()
    self.scopes[-1]["this"] = True

    for method in stmt.methods:
      declaration = FunctionType.METHOD
      if method.name.lexeme == "construct":
        declaration = FunctionType.INITIALIZER

      self._resolve_function(method, declaration)

    self._end_scope()

    if stmt.super_class is not None:
      self._end_scope()

    self.current_class = enclosing_class


  def visit_expression_stmt(self, stmt: Expression):
    self.resolve(stmt.expression)


  def visit_function_stmt(self, stmt: Function):
    self._declare(stmt.name)
    self._define(stmt.name)

    self._resolve_function(stmt, FunctionType.FUNCTION)


  def visit_if_stmt(self, stmt: If):
    self.resolve(stmt.condition)
    self.resolve(stmt.then_branch)

    if stmt.else_branch is not None:
      self.resolve(stmt.else_branch)


  def visit_let_stmt(self, stmt: Let):
    self._declare(stmt.name)

    if stmt.initializer is not None:
      self.resolve(stmt.initializer)

    self._define(stmt.name)


  def visit_print_stmt(self, stmt: Print):
    self.resolve(stmt.expression)


  def visit_return_stmt(self, stmt: Return):
    if self.current_function == FunctionType.NONE:
      Logger.error(
        stmt.keyword, "Can't return from top-level code."
      )

    if stmt.value is not None:
      if self.current_function == FunctionType.INITIALIZER:
        Logger.error(
          stmt.keyword, "Can't return a value from an initializer."
        )

      self.resolve(stmt.value)


  def visit_while_stmt(self, stmt: While):
    self.resolve(stmt.condition)
    self.resolve(stmt.body)


  def visit_assign_expr(self, expr: Assign):
    self.resolve(expr.value)
    self._resolve_local(expr, expr.name)


  def visit_binary_expr(self, expr: Binary):
    self.resolve(expr.left)
    self.resolve(expr.right)


  def visit_calL_expr(self, expr: Call):
    self.resolve(expr.callee)

    for argument in expr.arguments:
      self.resolve(argument)


  def visit_get_expr(self, expr: Get):
    self.resolve(expr.obj)


  def visit_grouping_expr(self, expr: Grouping):
    self.resolve(expr.expression)


  def visit_literal_expr(self, expr: Literal):
    return


  def visit_logical_expr(self, expr: Logical):
    self.resolve(expr.left)
    self.resolve(expr.right)


  def visit_set_expr(self, expr: Set):
    self.resolve(expr.value)
    self.resolve(expr.obj)


  def visit_super_expr(self, expr: Super):
    if self.current_class == ClassType.NONE:
      Logger.error(
        expr.keyword, "Can't use 'super' outside of a class."
      )
    elif self.current_class != ClassType.SUBCLASS:
      Logger.error(
        expr.keyword,
        "Can't use 'super' in a class with no superclass."
      )

    self._resolve_local(expr, expr.keyword)


  def visit_this_expr(self, expr: This):
    if self.current_class == ClassType.NONE:
      Logger.error(
        expr.keyword, "Can't use 'this' outside of a class."
      )
      return

    self._resolve_local(expr, expr.keyword)


  def visit_unary_expr(self, expr: Unary):
    self.resolve(expr.right)


  def visit_variable_expr(self, expr: Variable):
    if (
      len(self.scopes) != 0 and
      self.scopes[-1].get(expr.name.lexeme) == False
    ):
      Logger.error(
        expr.name,
        "Can't read local variable in its own initializer."
      )

    self._resolve_local(expr, expr.name)


  def _begin_scope(self):
    self.scopes.append({})


  def _end_scope(self):
    self.scopes.pop()


  def _declare(self, name: Token):
    if len(self.scopes) == 0:
      return

    scope = self.scopes[-1]
    if name.lexeme in scope:
      Logger.error(name, "Already a variable with this name in this scope.")

    # false means not ready yet
    scope[name.lexeme] = False


  def _define(self, name: Token):
    if len(self.scopes) == 0:
      return

    self.scopes[-1][name.lexeme] = True


  def _resolve_local(self, expr: Expr, name: Token):
    for i in range(len(self.scopes) - 1, -1, -1):
      if name.lexeme in self.scopes[i]:
        self.interpreter.resolve(expr, len(self.scopes) - 1 - i)
        return


  def _resolve_function(
    self, function: Function, func_type: FunctionType
  ):
    enclosing_function = self.current_function
    self.current_function = func_type

    self._begin_scope()

    for param in function.params:
      self._declare(param)
      self._define(param)

    self.resolve(function.body)

    self._end_scope()

    self.current_function = enclosing_function


  def resolve(self, ast_node: object) -> None:
    if isinstance(ast_node, list):
      statements = cast(List[Stmt], ast_node)
      for statement in statements:
        self.resolve(statement)
      return

    if isinstance(ast_node, Stmt):
      ast_node.accept(self)
      return

    if isinstance(ast_node, Expr):
      ast_node.accept(self)
      return
