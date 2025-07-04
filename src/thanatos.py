from interpreter.interpreter import Interpreter
from logger.logger import Logger
from logger.repl import Repl
from parser.parser import Parser
from resolver.resolver import Resolver
from scanner.scanner import Scanner
from sys import argv, exit
# from tools.astprinter import AstPrinter


interpreter = Interpreter()


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
  if Logger.encountered_runtime_error:
    exit(70)


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
  statements = parser.parse()

  if Logger.encountered_error:
    return

  resolver = Resolver(interpreter)
  resolver.resolve(statements)

  if Logger.encountered_error:
    return

  interpreter.interpret(statements)


if __name__ == "__main__":
  main()
