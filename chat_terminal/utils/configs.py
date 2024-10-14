#!/usr/bin/env python3

from pathlib import Path
from typing import Union

APP_ROOT = Path(__file__).parent.parent
CONFIGS_SEARCH_DIRS = [
  Path.home() / '.config' / 'chat-terminal',
  APP_ROOT,
]

def search_config_file(filename: Union[str, Path]):
  for dir in CONFIGS_SEARCH_DIRS:
    path = dir / filename
    if path.exists():
      return path
  raise FileNotFoundError(f'File "{filename}" not found')
