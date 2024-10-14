#!/usr/bin/env python3

class DEBUG_MODE_CLASS():
  def __init__(self, mode=False):
    self._mode = mode

  def set(self, mode):
    self._mode = mode

  def __bool__(self):
    return bool(self._mode)

DEBUG_MODE = DEBUG_MODE_CLASS()
