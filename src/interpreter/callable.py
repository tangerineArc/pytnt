from abc import ABC, abstractmethod
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
