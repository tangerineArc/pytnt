from grammar.expr import Binary, Expr, Grouping, Literal, Unary, Visitor
# from scanner.token import Token
# from scanner.tokentype import TokenType


class AstPrinter(Visitor[str]):
  # @staticmethod
  # def main(): # to be removed
  #   expression = Binary(
  #     Unary(
  #       Token(TokenType.PLUS, "+", None, 1),
  #       Literal(123)
  #     ),
  #     Token(TokenType.STAR, "*", None, 1),
  #     Grouping(Literal(45.67))
  #   )
  #   p = AstPrinter()
  #   print(p.log(expression))

  def log(self, expr: Expr) -> str:
    return expr.accept(self)

  def visit_binary_expr(self, expr: Binary) -> str:
    return self.parenthesize(
      expr.operator.lexeme, expr.left, expr.right
    )

  def visit_grouping_expr(self, expr: Grouping) -> str:
    return self.parenthesize("group", expr.expression)

  def visit_literal_expr(self, expr: Literal) -> str:
    if expr.value == None:
      return "void"

    return str(expr.value)

  def visit_unary_expr(self, expr: Unary) -> str:
    return self.parenthesize(expr.operator.lexeme, expr.right)

  def parenthesize(self, name: str, *exprs: Expr) -> str:
    new_expr = ["(", name]

    for expr in exprs:
      new_expr.append(" ")
      new_expr.append(expr.accept(self))

    new_expr.append(")")

    return "".join(new_expr)
