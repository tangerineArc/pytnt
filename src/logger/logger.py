from scanner.token import Token
from scanner.tokentype import TokenType
from typing import Union


class Logger:
  encountered_error = False

  @staticmethod
  def error(line_or_token: Union[int, Token], message: str):
    line, token = None, None
    if isinstance(line_or_token, Token):
      token = line_or_token
    else:
      line = line_or_token

    if token is not None:
      if token.type == TokenType.EOF:
        Logger._report(token.line, "at end", message)
      else:
        Logger._report(token.line, f"at '{token.lexeme}'", message)
    elif line is not None:
      Logger._report(line, "", message)

  @staticmethod
  def _report(line: int, where: str, message: str):
    print(f"[line {line}] Error {where}: {message}")
    Logger.encountered_error = True
