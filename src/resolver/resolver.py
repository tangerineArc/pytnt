from enum import auto, Enum
from interpreter.interpreter import Interpreter
from logger.logger import Logger
from parser.expr import (
  Assign, Binary, Call, Expr, Grouping, Literal,
  Logical, Unary, Variable, Visitor as ExprVisitor
)
from parser.stmt import (
  Block, Expression, Function, If, Let, Print,
  Return, Stmt, Visitor as StmtVisitor, While
)
from scanner.token import Token
from typing import cast, Dict, List


class FunctionType(Enum):
  NONE = auto()
  FUNCTION = auto()


class Resolver(ExprVisitor[None], StmtVisitor[None]):
  def __init__(self, interpreter: Interpreter):
    self.interpreter = interpreter
    # stack of local scopes only
    self.scopes: List[Dict[str, bool]] = []
    self.current_function = FunctionType.NONE


  def visit_block_stmt(self, stmt: Block):
    self._begin_scope()
    self.resolve(stmt.statements)
    self._end_scope()


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


  def visit_grouping_expr(self, expr: Grouping):
    self.resolve(expr.expression)


  def visit_literal_expr(self, expr: Literal):
    return


  def visit_logical_expr(self, expr: Logical):
    self.resolve(expr.left)
    self.resolve(expr.right)


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
