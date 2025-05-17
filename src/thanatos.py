from scanner.scanner import Scanner
from sys import argv, exit


class Thanatos:
  _had_error = False

  @staticmethod
  def main():
    if len(argv) > 1:
      print("Usage: thanatos [script]")
      exit(64)

    if len(argv) == 1:
      Thanatos._run_file(argv[0])
    else:
      Thanatos._run_repl()

  @staticmethod
  def _run_file(path: str):
    file_contents = None
    with open(path) as file:
      file_contents = file.read()

    Thanatos._run(file_contents)

    if Thanatos._had_error:
      exit(65)

  @staticmethod
  def _run_repl():
    while True:
      line = input("> ")
      if line == "": break

      Thanatos._run(line)
      Thanatos._had_error = False

  @staticmethod
  def _run(source: str):
    scanner = Scanner(source)
    tokens = scanner.scan_tokens()

    for token in tokens:
      print(token)

  # implement better error handling later
  @staticmethod
  def error(line: int, message: str):
    Thanatos._report(line, "", message)

  @staticmethod
  def _report(line: int, where: str, message: str):
    print(f"[line {line}] Error {where}: {message}")
    Thanatos._had_error = True


if __name__ == "__main__":
  Thanatos.main()
