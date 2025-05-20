from scanner.token import Token


class ExecutionError(RuntimeError):
  def __init__(self, token: Token, message: str):
    super().__init__(message)
    self.message = message
    self.token = token
