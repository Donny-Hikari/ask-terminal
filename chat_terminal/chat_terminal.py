import logging
import yaml

from .libs.text_completion_endpoint import LLamaTextCompletion, OpenAITextCompletion
from .utils import search_config_file

_logger = logging.getLogger(__name__)

class ChatTerminal:
  def __init__(self, settings):
    tc_logger = logging.getLogger('text-completion')
    self.logger = _logger

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
      openai_creds_path = search_config_file(settings['credentials']['openai'])
      with open(openai_creds_path) as f:
        openai_creds = yaml.safe_load(f)
      self.tc = OpenAITextCompletion(
        model_name=self.tc_cfg['model'],
        api_key=openai_creds['api_key'],
        logger=tc_logger,
      )
    else:
      raise RuntimeError(f"Unknown endpoint {self.tc_endpoint}")
    self.logger.info(f"Using endpoint '{self.tc_endpoint}' for text completion")

    self.configs = settings['chat_terminal']
    self.user = self.configs['user']
    self.agent = self.configs['agent']

    prompts_path = search_config_file(self.configs['prompt'])
    with open(prompts_path) as f:
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
