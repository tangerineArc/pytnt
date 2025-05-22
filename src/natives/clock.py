from interpreter.callable import Callable
from time import time
from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
  from interpreter.interpreter import Interpreter


class ClockFn(Callable):
  def arity(self) -> int:
    return 0

  def call(
    self, interpreter: "Interpreter", arguments: List[object]
  ) -> float:
    return time()

  def to_string(self) -> str:
    return "<native function>"
