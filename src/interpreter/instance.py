from errors.executionerror import ExecutionError
from scanner.token import Token
from typing import Dict, TYPE_CHECKING

if TYPE_CHECKING:
  from interpreter.callable import ClassObj


class Instance:
  def __init__(self, class_obj: "ClassObj"):
    self.class_obj = class_obj
    self.fields: Dict[str, object] = {}


  def get(self, name: Token):
    if name.lexeme in self.fields:
      return self.fields[name.lexeme]

    method = self.class_obj.find_method(name.lexeme)
    if method is not None:
      return method.bind(self)

    raise ExecutionError(
      name, f"Undefined property '{name.lexeme}'."
    )


  def set(self, name: Token, value: object):
    self.fields[name.lexeme] = value


  def __repr__(self) -> str:
    return f"<instance of '{self.class_obj.name}'>"
