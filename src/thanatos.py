from grammar.astprinter import AstPrinter
from logger.logger import Logger
from logger.repl import Repl
from parser.parser import Parser
from scanner.scanner import Scanner
from sys import argv, exit


def main():
  if len(argv) > 2:
    print("Usage: thanatos [script]")
    exit(64)

  if len(argv) == 2:
    run_file(argv[1])
  else:
    run_repl()


def run_file(path: str):
  file_contents = None
  with open(path) as file:
    file_contents = file.read()

  run(file_contents)

  if Logger.encountered_error:
    exit(65)


def run_repl():
  repl = Repl((184, 146, 255), "tnt ϟ")

  while True:
    try:
      line = repl.prompt()
      run(line)
      Logger.encountered_error = False
    except KeyboardInterrupt:
      print()
      break


def run(source: str):
  scanner = Scanner(source)
  tokens = scanner.scan_tokens()

  parser = Parser(tokens)
  expression = parser.parse()

  if Logger.encountered_error or expression is None:
    return

  printer = AstPrinter()
  print(printer.log(expression))


if __name__ == "__main__":
  main()
