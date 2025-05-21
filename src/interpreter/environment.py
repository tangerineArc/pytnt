from errors.executionerror import ExecutionError
from scanner.token import Token
from typing import Dict, Optional


class Environment:
  def __init__(self, enclosing: Optional["Environment"] = None):
    self.values: Dict[str, object] = {}
    self.enclosing = enclosing

  def define(self, name: str, value: object):
    self.values[name] = value

  def get(self, name: Token) -> object:
    if name.lexeme in self.values:
      return self.values[name.lexeme]

    if self.enclosing != None:
      return self.enclosing.get(name)

    raise ExecutionError(name, f"Undefined variable '{name.lexeme}'.")

  def assign(self, name: Token, value: object):
    if name.lexeme in self.values:
      self.values[name.lexeme] = value
      return

    if self.enclosing != None:
      self.enclosing.assign(name, value)
      return

    raise ExecutionError(name, f"Undefined variable '{name.lexeme}'.")
