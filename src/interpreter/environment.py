from errors.executionerror import ExecutionError
from scanner.token import Token
from typing import Dict


class Environment:
  def __init__(self):
    self.values: Dict[str, object] = {}

  def define(self, name: str, value: object):
    self.values[name] = value

  def get(self, name: Token) -> object:
    if name.lexeme in self.values:
      return self.values[name.lexeme]

    raise ExecutionError(name, f"Undefined variable '{name.lexeme}'.")

  def assign(self, name: Token, value: object):
    if name.lexeme in self.values:
      self.values[name.lexeme] = value
      return

    raise ExecutionError(name, f"Undefined variable '{name.lexeme}'.")
