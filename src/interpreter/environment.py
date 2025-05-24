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

    if self.enclosing is not None:
      return self.enclosing.get(name)

    raise ExecutionError(name, f"Undefined variable '{name.lexeme}'.")


  def get_at(self, distance: int, name: str) -> object:
    return self.ancestor(distance).values.get(name)


  def assign(self, name: Token, value: object):
    if name.lexeme in self.values:
      self.values[name.lexeme] = value
      return

    if self.enclosing is not None:
      self.enclosing.assign(name, value)
      return

    raise ExecutionError(name, f"Undefined variable '{name.lexeme}'.")


  def assign_at(self, distance: int, name: Token, value: object):
    print("assign_at", distance, name)
    self.ancestor(distance).values[name.lexeme] = value


  def ancestor(self, distance: int) -> "Environment":
    environment = self
    for _ in range(distance):
      # redundant check just meant to satisfy the type-checker
      if environment.enclosing is None:
        break

      environment = environment.enclosing

    return environment
