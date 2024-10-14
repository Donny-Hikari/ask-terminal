#!/usr/bin/env python3

import logging
import sys

from .debug_mode import DEBUG_MODE

LOG_STATS = 11
LOG_VERBOSE = 15

def setup_logging():
  logging.addLevelName(LOG_STATS, 'STATS')
  logging.addLevelName(LOG_VERBOSE, 'VERBOSE')

  _format = '[%(asctime)s %(levelname)-4s %(name)s] %(message)s'

  herr = logging.StreamHandler(sys.stderr)
  herr.setLevel(logging.ERROR)

  hout = logging.StreamHandler(sys.stdout)
  hout.addFilter(lambda record: record.levelno < logging.ERROR)

  logging.basicConfig(
    level=logging.DEBUG if DEBUG_MODE else logging.INFO,
    format=_format,
    handlers=[
      hout,
      herr,
    ],
  )
