from scanner.scanner import Scanner
from sys import argv, exit


class Thanatos:
  def __init__(self):
    self.had_error = False

  def main(self):
    if len(argv) > 1:
      print("Usage: thanatos [script]")
      exit(64)

    if len(argv) == 1:
      self._run_file(argv[0])
    else:
      self._run_repl()

  def _run_file(self, path: str):
    file_contents = None
    with open(path) as file:
      file_contents = file.read()

    self._run(file_contents)

    if self.had_error:
      exit(65)

  def _run_repl(self):
    while True:
      line = input("> ")
      if line == "": break

      self._run(line)
      self.had_error = False

  def _run(self, source: str):
    scanner = Scanner(source)
    tokens = scanner.scan_tokens()

    for token in tokens:
      print(token)

  # implement better error handling later
  def error(self, line: int, message: str):
    self._report(line, "", message)

  def _report(self, line: int, where: str, message: str):
    print(f"[line {line}] Error {where}: {message}")
    self.had_error = True


if __name__ == "__main__":
  thanatos = Thanatos()
  thanatos.main()
