import logging
import sys

LOG_STATS = 11
LOG_VERBOSE = 15

def setupLogging(logger: logging.Logger, log_level=logging.INFO, format='[%(levelname)-s %(asctime)s]: %(message)s'):
  logging.addLevelName(LOG_STATS, 'STATS')
  logging.addLevelName(LOG_VERBOSE, 'VERBOSE')

  herr = logging.StreamHandler(sys.stderr)
  herr.setLevel(logging.ERROR)
  herr.setFormatter(logging.Formatter(format))
  logger.addHandler(herr)

  hout = logging.StreamHandler(sys.stdout)
  hout.addFilter(lambda record: record.levelno < logging.ERROR)
  hout.setFormatter(logging.Formatter(format))
  logger.addHandler(hout)

  logger.setLevel(log_level)
