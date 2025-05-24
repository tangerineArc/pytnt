from abc import ABC, abstractmethod
from errors.returntrickery import ReturnTrickery
from interpreter.environment import Environment
from interpreter.instance import Instance
from parser.stmt import Function
from typing import Dict, List, Optional, TYPE_CHECKING

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


class ClassObj(Callable):
  def __init__(
    self,
    name: str,
    super_class: Optional["ClassObj"],
    methods: Dict[str, "FunctionObj"]
  ):
    self.name = name
    self.super_class = super_class
    self.methods = methods


  def call(
    self, interpreter: "Interpreter", arguments: List[object]
  ) -> object:
    instance = Instance(self)

    initializer = self.find_method("construct")
    if initializer is not None:
      initializer.bind(instance).call(interpreter, arguments)

    return instance


  def arity(self) -> int:
    initializer = self.find_method("construct")
    if initializer is None:
      return 0

    return initializer.arity()


  def find_method(self, name: str) -> Optional["FunctionObj"]:
    if name in self.methods:
      return self.methods[name]

    if self.super_class is not None:
      return self.super_class.find_method(name)


  def __repr__(self) -> str:
    return f"<class '{self.name}'>"


class FunctionObj(Callable):
  def __init__(
    self,
    declaration: Function,
    closure: Environment,
    is_initializer: bool
  ):
    self.is_initializer = is_initializer
    self.declaration = declaration
    self.closure = closure


  def call(
    self, interpreter: "Interpreter", arguments: List[object]
  ) -> object:
    environment = Environment(self.closure)
    for i in range(len(self.declaration.params)):
      environment.define(
        self.declaration.params[i].lexeme, arguments[i]
      )

    try:
      interpreter.execute_block(self.declaration.body, environment)
    except ReturnTrickery as e:
      if self.is_initializer:
        return self.closure.get_at(0, "this")

      return e.value

    if self.is_initializer:
      return self.closure.get_at(0, "this")


  def arity(self) -> int:
    return len(self.declaration.params)


  def bind(self, instance: Instance):
    environment = Environment(self.closure)
    environment.define("this", instance)

    return FunctionObj(
      self.declaration, environment, self.is_initializer
    )


  def __repr__(self) -> str:
    return f"<function '{self.declaration.name.lexeme}'>"
