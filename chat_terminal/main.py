import subprocess
import os
import re
import requests
import argparse
import sys
import logging
from pathlib import Path
from typing import List, Union

import yaml

from .utils import DEBUG_MODE, setup_logging, search_config_file
from .chat_terminal import ChatTerminal

DEFAULT_SETTINGS = {
  "use_black_list": False,
  "black_list_pattern": r"\b(rm|sudo)\b",
}

_logger = logging.getLogger(__name__)

def exec_command(command):
  process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
  stdout, stderr = process.communicate()
  return process, stdout, stderr

def chat(settings):
  chat_terminal = ChatTerminal(settings)
  chat_cfg = settings['chat_terminal']

  while True:
    query = input('[User]: ')
    print('[Command]:', end='')

    def streamResponse(content, stop, res):
      if not stop and content is not None:
        print(content, end='')

    command = chat_terminal.query_command(query, cb=streamResponse)
    if not command.endswith('\n'):
      print('')
    command = command.strip()
    command = command.strip('`')

    skip_confirm = False
    if chat_cfg['use_black_list']:
      if not re.match(chat_cfg['black_list_pattern'], command):
        skip_confirm = True

    if not skip_confirm:
      choice = input('Execute the command?(y/n) ')
      confirmed = choice.lower() == 'y'
    else:
      confirmed = True

    observation = "Illegal command: Command execution refused."
    if confirmed:
      process, stdout, stderr = exec_command(command)
      print('[Observation]: ', end='')
      observation = ""
      if len(stdout):
        output = stdout.decode().strip()
        observation = f"Stdout: {repr(output)}\n"
        print(f'\nStdout:\n{output}')
      if len(stderr):
        errors = stderr.decode().strip()
        observation += f"Stderr: {repr(errors)}"
        print(f'\nStderr:\n{errors}')
      if len(stdout) == 0 and len(stderr) == 0:
        print('""""""')
      observation = observation.strip()
      observation = f'"""{observation}"""'
    else:
      print(f'[Observation]: {observation}')

    print('[Alice]:', end='')
    reply = chat_terminal.query_answer(observation, cb=streamResponse)
    if not reply.endswith('\n'):
      print('')
    reply = reply.strip()

def parse_arg(argv=sys.argv[1:]):
  parser = argparse.ArgumentParser()
  parser.add_argument('--debug', action='store_true')
  parser.add_argument('--config', '-c', type=str, default="configs/chat_terminal.yaml")
  parser.add_argument('--use-black-list', '-bl', action="store_true", required=False)
  parser.add_argument('--black-list-pattern', '-blc', type=str, required=False)
  return parser.parse_args(argv)

def load_config(config_file: Union[str, Path]):
  cfg_path = search_config_file(config_file)
  if DEBUG_MODE:
    _logger.debug(f'Loaded config from {cfg_path}')

  with open(cfg_path) as f:
    configs = yaml.safe_load(f)

  return configs

def main():
  args = parse_arg()

  if args.debug:
    DEBUG_MODE.set(args.debug)

  setup_logging(level=logging.DEBUG if DEBUG_MODE else logging.INFO)

  settings = load_config(args.config)

  chat_cfg = settings['chat_terminal']
  for opt, default_val in DEFAULT_SETTINGS.items():
    if opt not in chat_cfg and getattr(args, opt) is None:
      chat_cfg[opt] = default_val
    elif getattr(args, opt) is not None:
      chat_cfg[opt] = getattr(args, opt)

  chat(settings)

if __name__ == "__main__":
  main()
