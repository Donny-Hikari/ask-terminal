#!/usr/bin/env python3

import logging
import sys

LOG_STATS = 11
LOG_VERBOSE = 15

def setup_logging(level=logging.INFO, _format='[%(asctime)s %(levelname)-4s %(name)s] %(message)s'):
  logging.addLevelName(LOG_STATS, 'STATS')
  logging.addLevelName(LOG_VERBOSE, 'VERBOSE')

  herr = logging.StreamHandler(sys.stderr)
  herr.setLevel(logging.ERROR)

  hout = logging.StreamHandler(sys.stdout)
  hout.addFilter(lambda record: record.levelno < logging.ERROR)

  logging.basicConfig(
    level=level,
    format=_format,
    handlers=[
      hout,
      herr,
    ],
  )
