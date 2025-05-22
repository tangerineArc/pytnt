from abc import ABC, abstractmethod
from interpreter.environment import Environment
from parser.stmt import Function
from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
  from interpreter.interpreter import Interpreter


class Callable(ABC):
  @abstractmethod
  def call(
    self, interpreter: "Interpreter", arguments: List[object]
  ) -> object:
    ...

  @abstractmethod
  def arity(self) -> int:
    ...


class FunctionObj(Callable):
  def __init__(self, declaration: Function):
    self.declaration = declaration


  def call(
    self, interpreter: "Interpreter", arguments: List[object]
  ) -> object:
    environment = Environment(interpreter.universe)
    for i in range(len(self.declaration.params)):
      environment.define(
        self.declaration.params[i].lexeme, arguments[i]
      )

    interpreter.execute_block(self.declaration.body, environment)

    return None


  def arity(self) -> int:
    return len(self.declaration.params)


  def __repr__(self) -> str:
    return f"<function {self.declaration.name.lexeme}>"
