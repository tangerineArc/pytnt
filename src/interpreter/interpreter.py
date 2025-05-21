from interpreter.environment import Environment
from errors.executionerror import ExecutionError
from logger.logger import Logger
from parser.expr import (
  Assign, Binary, Expr, Grouping, Literal, Unary, Variable, Visitor as ExprVisitor
)
from parser.stmt import (
  Block, Expression, Let, Print, Stmt, Visitor as StmtVisitor
)
from scanner.token import Token
from scanner.tokentype import TokenType
from typing import Any, List


class Interpreter(ExprVisitor[Any], StmtVisitor[None]):
  def __init__(self):
    self.environment = Environment()


  def interpret(self, statements: List[Stmt]):
    try:
      for statement in statements:
        self._execute(statement)
    except ExecutionError as e:
      Logger.execution_error(e)


  def visit_expression_stmt(self, stmt: Expression):
    self._evaluate(stmt.expression)


  def visit_print_stmt(self, stmt: Print):
    value = self._evaluate(stmt.expression)
    print(self._stringify(value))


  def visit_block_stmt(self, stmt: Block):
    self._execute_block(stmt.statements, Environment(self.environment))


  def visit_let_stmt(self, stmt: Let):
    value = None
    if stmt.initializer != None:
      value = self._evaluate(stmt.initializer)

    self.environment.define(stmt.name.lexeme, value)


  def visit_variable_expr(self, expr: Variable) -> Any:
    return self.environment.get(expr.name)


  def visit_assign_expr(self, expr: Assign) -> Any:
    value = self._evaluate(expr.value)
    self.environment.assign(expr.name, value)

    return value


  def visit_literal_expr(self, expr: Literal) -> Any:
    return expr.value


  def visit_grouping_expr(self, expr: Grouping) -> Any:
    return self._evaluate(expr.expression)


  def visit_unary_expr(self, expr: Unary) -> Any:
    right = self._evaluate(expr.right)

    match expr.operator.type:
      case TokenType.MINUS:
        self._check_number_operand(expr.operator, right)
        return -float(right)
      case TokenType.PLUS:
        self._check_number_operand(expr.operator, right)
        return +float(right)
      case TokenType.BANG:
        return not self._is_truthy(right)
      case _: # unreachable
        return


  def visit_binary_expr(self, expr: Binary) -> Any:
    left = self._evaluate(expr.left)
    right = self._evaluate(expr.right)

    match expr.operator.type:
      case TokenType.GREATER:
        self._check_number_operands(expr.operator, left, right)
        return float(left) > float(right)

      case TokenType.GREATER_EQUAL:
        self._check_number_operands(expr.operator, left, right)
        return float(left) >= float(right)

      case TokenType.LESS:
        self._check_number_operands(expr.operator, left, right)
        return float(left) < float(right)

      case TokenType.LESS_EQUAL:
        self._check_number_operands(expr.operator, left, right)
        return float(left) <= float(right)

      case TokenType.BANG_EQUAL:
        return left != right # might cause problems later

      case TokenType.EQUAL_EQUAL:
        return left == right

      case TokenType.MINUS:
        self._check_number_operands(expr.operator, left, right)
        return float(left) - float(right)

      case TokenType.PLUS:
        if isinstance(left, float) and isinstance(right, float):
          return float(left) + float(right)

        if isinstance(left, str) and isinstance(right, str):
          return str(left) + str(right)

        raise ExecutionError(
          expr.operator,
          "Operands must be two numbers or two strings."
        )

      case TokenType.SLASH:
        self._check_number_operands(expr.operator, left, right)
        return float(left) / float(right)

      case TokenType.STAR:
        self._check_number_operands(expr.operator, left, right)
        return float(left) * float(right)

      case _: # unreachable
        return


  def _execute(self, stmt: Stmt):
    stmt.accept(self)


  def _execute_block(self, statements: List[Stmt], environment: Environment):
    previous = self.environment

    try:
      self.environment = environment

      for statement in statements:
        self._execute(statement)
    finally:
      self.environment = previous


  def _evaluate(self, expr: Expr) -> Any:
    return expr.accept(self)


  def _is_truthy(self, obj: Any) -> bool:
    if obj == None:
      return False

    if isinstance(obj, bool):
      return bool(obj)

    return True


  def _stringify(self, obj: Any) -> str:
    if obj is None:
      return TokenType.VOID.value

    if isinstance(obj, float):
      text = str(obj)
      if text.endswith(".0"):
        text = text[ : -2]
      return text

    if isinstance(obj, bool):
      if obj == True:
        return TokenType.TRUE.value
      return TokenType.FALSE.value

    return str(obj)


  def _check_number_operand(self, operator: Token, operand: Any):
    if isinstance(operand, float):
      return

    raise ExecutionError(operator, "Operand must be a number.")


  def _check_number_operands(self, operator: Token, left: Any, right: Any):
    if isinstance(left, float) and isinstance(right, float):
      return

    raise ExecutionError(operator, "Operands must be numbers.")
