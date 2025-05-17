from logger.logger import Logger
from logger.repl import Repl
from scanner.scanner import Scanner
from sys import argv, exit


class Thanatos:
  @staticmethod
  def main():
    if len(argv) > 2:
      print("Usage: thanatos [script]")
      exit(64)

    if len(argv) == 2:
      Thanatos._run_file(argv[1])
    else:
      Thanatos._run_repl()

  @staticmethod
  def _run_file(path: str):
    file_contents = None
    with open(path) as file:
      file_contents = file.read()

    Thanatos._run(file_contents)

    if Logger.encountered_error:
      exit(65)

  @staticmethod
  def _run_repl():
    repl = Repl((184, 146, 255), "tnt ϟ")

    while True:
      try:
        line = repl.prompt()
        Thanatos._run(line)
        Logger.encountered_error = False
      except KeyboardInterrupt:
        print()
        break

  @staticmethod
  def _run(source: str):
    scanner = Scanner(source)
    tokens = scanner.scan_tokens()

    for token in tokens:
      print(token)


if __name__ == "__main__":
  Thanatos.main()
