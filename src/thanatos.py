from logger.logger import Logger
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
    prompt_color = "\033[38;2;184;146;255m"
    while True:
      try:
        line = input(f"{prompt_color}tnt ϟ \033[0m")
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
