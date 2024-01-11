import subprocess
import os
import re
import requests
import yaml
import argparse
import sys
import logging

from libs.utils import setupLogging
from libs.text_completion_endpoint import LLamaTextCompletion, OpenAITextCompletion

default_settings = {
  "use_black_list": False,
  "black_list_pattern": r"\b(rm|sudo)\b",
}

class ChatTerminal:
  def __init__(self, settings, logger=logging.getLogger('chat-terminal')):
    tc_logger = logging.getLogger('text-completion')
    self.logger = logger

    self.tc_def = settings['text_completion']
    self.tc_endpoint = self.tc_def['endpoint']
    self.tc_cfg = self.tc_def['configs']
    self.tc_params = self.tc_cfg.get('params', {})
    if self.tc_endpoint == 'local-llama':
      self.tc = LLamaTextCompletion(
        server_url=self.tc_cfg['server_url'],
        logger=tc_logger
      )
    elif self.tc_endpoint == 'openai':
      self.tc = OpenAITextCompletion(
        model_name=self.tc_cfg['model'],
        logger=tc_logger,
      )
    else:
      raise RuntimeError(f"Unknown endpoint {self.tc_endpoint}")
    logger.info(f"Using endpoint '{self.tc_endpoint}' for text completion")

    self.configs = settings['chat_terminal']
    self.user = self.configs['user']
    self.agent = self.configs['agent']

    with open(self.configs['prompt']) as f:
      lines = f.readlines()
    self.prompt = ''.join(lines).strip()
    self.n_keep = self.tc.tokenize(self.prompt)

  def chat(self, req_role, content, res_role, stop=[], cb=None):
    self.prompt += f'\n[{req_role}]: {content}\n[{res_role}]:'
    params = {
      **self.tc_params,
      "stop": self.tc_params.get("stop", []) + stop,
    }

    reply = self.tc.create(prompt=self.prompt, params=params, cb=cb)
    self.prompt += reply.strip()

    return reply

  def query_command(self, query, cb=None):
    return self.chat(
      req_role=self.user,
      content=query,
      res_role='Command',
      stop=["[Observation]:", f"[{self.agent}]:"],
      cb=cb,
    )

  def query_answer(self, observation, cb):
    return self.chat(
      req_role='Observation',
      content=observation,
      res_role=self.agent,
      stop=["[Command]:", "[Observation]:"],
      cb=cb,
    )

def exec_command(command):
  process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
  stdout, stderr = process.communicate()
  return process, stdout, stderr

def chat(settings):
  logger = logging.getLogger('chat-terminal')
  setupLogging(logger, log_level=logging.INFO)

  chat_terminal = ChatTerminal(settings, logger=logger)

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
    if settings['use_black_list']:
      if not re.match(settings['black_list_pattern'], command):
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
  parser.add_argument('--config', '-c', type=str, default="configs/chat_terminal.yaml")
  parser.add_argument('--use-black-list', '-bl', action="store_true", required=False)
  parser.add_argument('--black-list-pattern', '-blc', type=str, required=False)
  return parser.parse_args(argv)

def load_config(config_file):
  with open(config_file) as f:
    configs = yaml.safe_load(f)
  return configs

def main():
  args = parse_arg()
  settings = load_config(args.config)

  for opt, default_val in default_settings.items():
    if opt not in settings and getattr(args, opt) is None:
      settings[opt] = default_val
    elif getattr(args, opt) is not None:
      settings[opt] = getattr(args, opt)

  chat(settings)

if __name__ == "__main__":
  main()
