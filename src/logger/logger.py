class Logger:
  encountered_error = False

  @staticmethod
  def error(line: int, message: str):
    Logger._report(line, "", message)

  @staticmethod
  def _report(line: int, where: str, message: str):
    print(f"[line {line}] Error {where}: {message}")
    Logger.encountered_error = True
