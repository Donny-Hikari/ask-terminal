from pathlib import Path

class DEBUG_MODE_CLASS():
  def __init__(self, mode=False):
    self.mode = mode

  def set(self, mode):
    self.mode = mode

  def __bool__(self):
    return bool(self.mode)

DEBUG_MODE = DEBUG_MODE_CLASS()
APP_ROOT = Path(__file__).parent.parent
