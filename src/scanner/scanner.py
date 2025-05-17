from scanner.token import Token
from typing import List


class Scanner:
  def __init__(self, source: str):
    ...

  def scan_tokens(self) -> List[Token]:
    ...
