#!/usr/bin/env python3

import logging
import sys

LOG_HEAVY = 9
LOG_VERBOSE = 15

def setup_logging(level=logging.INFO, _format='[%(asctime)s %(levelname)-4s %(name)s] %(message)s', handlers=[]):
  logging.addLevelName(LOG_HEAVY, 'HEAVY')
  logging.addLevelName(LOG_VERBOSE, 'VERBOSE')

  herr = logging.StreamHandler(sys.stderr)
  herr.setLevel(logging.ERROR)

  hout = logging.StreamHandler(sys.stdout)
  hout.setLevel(level)
  hout.addFilter(lambda record: record.levelno < logging.ERROR)

  logging.basicConfig(
    level=0,
    format=_format,
    handlers=[
      hout,
      herr,
      *handlers,
    ],
  )

  logging.getLogger('urllib3').setLevel(logging.WARNING)
