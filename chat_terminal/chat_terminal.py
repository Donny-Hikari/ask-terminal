import logging

import yaml

from .libs.text_completion_endpoint import LLamaTextCompletion, OpenAITextCompletion
from .utils import search_config_file
from .settings import Settings


_logger = logging.getLogger(__name__)


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
      openai_creds_path = search_config_file(self._tc_cfg['credentials'])
      with open(openai_creds_path) as f:
        openai_creds = yaml.safe_load(f)
      self._tc = OpenAITextCompletion(
        model_name=self._tc_cfg['model'],
        api_key=openai_creds['api_key'],
        logger=tc_logger,
      )

    self._logger.info(f"Using endpoint '{self._tc_endpoint}' for text completion")

    prompts_path = search_config_file(self._configs.prompt)
    with open(prompts_path) as f:
      lines = f.readlines()
    self._prompt = ''.join(lines).strip()
    self._n_keep = self._tc.tokenize(self._prompt)

  def chat(self, req_role, content, res_role, stop=[], cb=None):
    self._prompt += f'\n[{req_role}]: {content}\n[{res_role}]:'
    params = {
      **self._tc_params,
      "stop": self._tc_params.get("stop", []) + stop,
    }

    reply = self._tc.create(prompt=self._prompt, params=params, cb=cb)
    self._prompt += reply.strip()

    return reply

  def query_command(self, query, cb=None):
    return self.chat(
      req_role=self._user,
      content=query,
      res_role='Command',
      stop=["[Observation]:", f"[{self._agent}]:"],
      cb=cb,
    )

  def query_answer(self, observation, cb):
    return self.chat(
      req_role='Observation',
      content=observation,
      res_role=self._agent,
      stop=["[Command]:", "[Observation]:"],
      cb=cb,
    )
