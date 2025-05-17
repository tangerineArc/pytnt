import readline
from typing import Tuple


class Repl:
  def __init__(self, rgb: Tuple[int, int, int], prompt_text: str):
    self.prompt_text = Repl.get_ansi_prompt(rgb, prompt_text)
    Repl.configure_readline()

  @staticmethod
  def get_ansi_prompt(rgb: Tuple[int, int, int], prompt_text: str) -> str:
    r, g, b = rgb
    return f"\033[38;2;{r};{g};{b}m{prompt_text} \033[0m"

  @staticmethod
  def configure_readline():
    readline.parse_and_bind("Control-Backspace: backward-kill-word")
    readline.parse_and_bind('Control-u: unix-line-discard')
    readline.parse_and_bind('Control-k: kill-line')

  def prompt(self) -> str:
    return input(self.prompt_text)
