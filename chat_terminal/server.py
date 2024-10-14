import argparse
import sys
import logging
from pathlib import Path
from typing import Union

import yaml
import uvicorn

from .utils import DEBUG_MODE, search_config_file, setup_logging
from .app import app, set_settings
from .settings import Settings


_logger = logging.getLogger(__name__)


def chat(settings, host, port):
  set_settings(settings)
  uvicorn.run(app, host=host, port=port)

def parse_arg(argv=sys.argv[1:]):
  parser = argparse.ArgumentParser()
  parser.add_argument('--debug', action='store_true')
  parser.add_argument('--config', '-c', type=str, default="configs/chat_terminal.yaml")
  parser.add_argument('--host', type=str, default="127.0.0.1")
  parser.add_argument('--port', type=int, default=16099)
  return parser.parse_args(argv)

def load_config(config_file: Union[str, Path]):
  cfg_path = search_config_file(config_file)
  if DEBUG_MODE:
    _logger.debug(f'Loaded config from {cfg_path}')

  with open(cfg_path) as f:
    configs = yaml.safe_load(f)

  configs = Settings(**configs)

  return configs

def main():
  args = parse_arg()

  if args.debug:
    DEBUG_MODE.set(args.debug)

  setup_logging(level=logging.DEBUG if DEBUG_MODE else logging.INFO)

  settings = load_config(args.config)
  chat(settings, args.host, args.port)

if __name__ == "__main__":
  main()
