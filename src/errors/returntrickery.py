class ReturnTrickery(RuntimeError):
  def __init__(self, value: object):
    super().__init__()
    self.value = value
