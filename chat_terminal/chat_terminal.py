import logging
import os
from typing import List

import yaml
from mext import Mext
from pydantic import BaseModel

from .libs.text_completion_endpoint import LLamaTextCompletion, OpenAITextCompletion
from .utils import search_config_file, LOG_HEAVY
from .settings import Settings


_logger = logging.getLogger(__name__)


class ChatHistoryItem(BaseModel):
  query: str
  thinking: str = ""
  command: str = ""
  observation: str = ""
  reply: str = ""

  command_refused: bool = False
  observation_received: bool = False

class ChatTerminal:
  def __init__(self, settings: Settings):
    self._logger = _logger
    self._logger.debug(str(settings))

    self._configs = settings.chat_terminal
    self._user = self._configs.user
    self._agent = self._configs.agent

    tc_logger = logging.getLogger('text-completion')
    text_completion_endpoints = settings.text_completion_endpoints
    self._tc_endpoint = self._configs.endpoint
    if self._tc_endpoint not in text_completion_endpoints:
      raise ValueError(f"Invalid endpoint '{self._tc_endpoint}'")
    self._tc_cfg = text_completion_endpoints[self._tc_endpoint]
    self._tc_params = self._tc_cfg.get('params', {})

    if self._tc_endpoint == 'local-llama':
      self._tc = LLamaTextCompletion(
        server_url=self._tc_cfg['server_url'],
        logger=tc_logger,
      )
    elif self._tc_endpoint == 'openai':
      api_key = None
      creds_file = self._tc_cfg.get('credentials', None)
      if creds_file:
        openai_creds_path = search_config_file(creds_file)
        with open(openai_creds_path) as f:
          openai_creds = yaml.safe_load(f)
          api_key = openai_creds.get('api_key', None)

      self._tc = OpenAITextCompletion(
        model_name=self._tc_cfg['model'],
        api_key=api_key,
        logger=tc_logger,
      )

    self._logger.info(f"Using endpoint '{self._tc_endpoint}' for text completion")

    self._roles = [
      f"{self._user}",
      f"{self._agent} Thinking",
      "Command",
      "Observation",
      f"{self._agent}",
    ]
    self._roles_hint = list(map(lambda x: f'[{x}]', self._roles))

    prompts_path = search_config_file(self._configs.prompt)
    self._context_mgr = Mext()
    self._context_mgr.set_template(template_fn=prompts_path)
    self._context_mgr.set_params(
      user=self._user,
      agent=self._agent,

      shell="bash",  # default using bash
    )
    self._history: List[ChatHistoryItem] = []

  def _get_stop_from_role(self, role: str):
    return self._roles_hint

  def chat(self, gen_role, stop=[], cb=None):
    prompt = self._context_mgr.compose(
      gen_role=gen_role,
      history=self._history,
    )
    params = {
      **self._tc_params,
      "stop": self._tc_params.get("stop", []) + stop,
    }

    _logger.log(LOG_HEAVY, f"Prompt:\n{prompt}")

    reply = self._tc.create(prompt=prompt, params=params, cb=cb)
    reply = reply.strip()

    _logger.log(LOG_HEAVY, f"Response:\n{reply}")

    return reply

  def query_command(self, query, env={}, cb=None):
    self._history.append(
      ChatHistoryItem(query=query),
    )

    with self._context_mgr.use_params(**env):
      if self._configs.use_thinking:
        gen_role = f"{self._agent} Thinking"
        thinking = self.chat(
          gen_role=gen_role,
          stop=self._get_stop_from_role(gen_role),
          cb=cb,
        )
        self._history[-1].thinking = thinking

      gen_role = "Command"
      command = self.chat(
        gen_role=gen_role,
        stop=self._get_stop_from_role(gen_role),
        cb=cb,
      )
      command = command.strip('`')
      self._history[-1].command = command

    return {
      'thinking': thinking,
      'command': command,
    }

  def query_reply(self, command_refused, observation="", env={}, cb=None):
    self._history[-1].command_refused = command_refused
    self._history[-1].observation = observation
    self._history[-1].observation_received = True

    with self._context_mgr.use_params(**env):
      gen_role = f"{self._agent}"
      reply = self.chat(
        gen_role=gen_role,
        stop=self._get_stop_from_role(gen_role),
        cb=cb,
      )
      self._history[-1].reply = reply

    return {
      'reply': reply,
    }
