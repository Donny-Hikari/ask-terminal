import json
import openai
import requests
import os
import time
import logging
import math


class TextCompletionBase:
  def __init__(self, *args, **kwargs):
    pass

  def tokenize(self, content):
    raise NotImplementedError

  def create(self, *args, **kwargs):
    raise NotImplementedError

  def _truncate_count_tokens(self, content):
    return len(self.tokenize(content))

  def truncate(self, content, target_num, truncation_indicator, front_ratio=0.5, coarse_gap=0, return_is_truncated=False):
    """
    Params
    ======
    front_ratio:
      the ratio of the content to be preserved in the front over the truncated content

    coarse_gap:
      allowing the final number of tokens to be `coarse_gap` tokens larger or smaller than the `target_num`.
      This could speed up the binary search largely. The speed up ratio can be calculated as `log2(coarse_gap) / log2(original_tokens_count_of_content)`.
    """

    if self._truncate_count_tokens(content) <= target_num:
      if return_is_truncated:
        return content, False
      else:
        return content

    if coarse_gap > 0:
      coarse_gap = min(coarse_gap, target_num//2)

    l = 0; r = len(content)
    while l < r:
      m = (l+r)>>1
      front = int(m*front_ratio)
      rear = m - front
      num_tokens = self._truncate_count_tokens(content[:front] + truncation_indicator + content[-rear:])
      if coarse_gap > 0 and abs(num_tokens - target_num) <= coarse_gap:
        l = m
        break
      if num_tokens < target_num:
        l = m+1
      else:
        r = m
    front = int(l*front_ratio)
    rear = l - front
    res = content[:front] + truncation_indicator + content[-rear:]

    if return_is_truncated:
      return res, True
    else:
      return res


class LLamaTextCompletion(TextCompletionBase):
  def __init__(self, server_url, logger=None):
    self.server_url = server_url
    self.logger = logger

  def tokenize(self, content):
    data = {
      "content": content,
    }

    res = requests.post(f"{self.server_url}/tokenize", json=data)
    return json.loads(res.content)['tokens']

  def create(self,
           prompt=None, params={},
           cb=None):
    req = params
    if prompt is not None:
      req['prompt'] = prompt
    req['stream'] = True

    # Creating a streaming connection with a POST request
    reply = ''
    with requests.post(f"{self.server_url}/completion", json=req, stream=True) as response:
      # Processing streaming data in chunks
      buffer = ""  # Buffer to accumulate streamed data
      for chunk in response.iter_content(chunk_size=1024, decode_unicode=True):
        if chunk:
          buffer += chunk
          try:
            # Attempt to decode JSON from the accumulated buffer
            res = json.loads(buffer[6:])

            reply += res['content']
            if cb is not None:
              cb(content=res['content'], stop=res['stop'], res=res)

            if res['stop']:
              break

            buffer = ""  # Clear the buffer after processing
          except json.JSONDecodeError:
            pass  # Incomplete JSON, continue accumulating data

    return reply

class OpenAITextCompletion(TextCompletionBase):
  MAX_STOPS = 4

  def __init__(self, model_name, api_key=None, logger: logging.Logger=None, initial_system_msg=None):
    from transformers import AutoTokenizer
    from openai import OpenAI

    self.model_name = model_name
    self.logger = logger
    self.tokenizer = AutoTokenizer.from_pretrained('gpt2')
    self.client = OpenAI(api_key=api_key)
    self.initial_system_msg = initial_system_msg

  def tokenize(self, content):
    return self.tokenizer.tokenize(content)

  def create(self,
           messages=None, params={ 'stream': True }, prompt=None,
           cb=None, max_retries=5):
    """
    params
    -------------
    max_retries: <= 0 means forever
    """

    if messages is None:
      messages = []
      if self.initial_system_msg is not None:
        messages.append({ "role": "system", "content": self.initial_system_msg })
      messages.append({ "role": "user", "content": prompt })

    if len(params.get('stop', [])) > (max_stops := OpenAITextCompletion.MAX_STOPS):
      params['stop'] = params['stop'][-max_stops:]
      self.logger.warning(f'OpenAI only supports up to {max_stops}, using only the last few ones.')

    reply = ''
    n_retries = 0
    while max_retries <= 0 or n_retries < max_retries:
      n_retries += 1
      try:
        response = self.client.chat.completions.create(
          **params,
          model=self.model_name,
          messages=messages,
        )
        if not params.get('stream', False):
          reply = response.choices[0].message.content
          stop = response.choices[0].finish_reason is not None
          if cb is not None:
            cb(content=reply, stop=stop, res=response)
        else:
          for chunk in response:
            content = chunk.choices[0].delta.content
            stop = chunk.choices[0].finish_reason is not None
            if not stop:
              reply += content
            if cb is not None:
              cb(content=content, stop=stop, res=chunk)
        break
      except Exception as e:
        if n_retries >= max_retries:
          raise e
        elif n_retries == 1:
          if self.logger:
            if type(e) == openai.RateLimitError:
              self.logger.warning("Encounter rate limit, retrying.")
            else:
              self.logger.warning(f"Encounter unknown error, retrying: {str(e)}")
        # wait 1 5 13 29 60 120 ...
        time.sleep(int(4.5*(1.94**n_retries)-3))

    return reply

class AnthropicTokenizer:
  def tokenize(self, text):
    from langchain_community.utilities.anthropic import get_token_ids_anthropic
    return get_token_ids_anthropic(text)

class AnthropicTextCompletion(TextCompletionBase):
  def __init__(self, model_name, api_key=None, logger=None, initial_system_msg: str=None):
    from anthropic import Anthropic

    self.model_name = model_name
    self.logger = logger
    self.tokenizer = AnthropicTokenizer()
    self.client = Anthropic(api_key=api_key)
    self.initial_system_msg = initial_system_msg

  def tokenize(self, content):
    return self.tokenizer.tokenize(content)

  def create(self,
           messages=None, params={}, prompt=None,
           cb=None):
    import anthropic

    system_prompt = anthropic.NOT_GIVEN

    if messages is None:
      if self.initial_system_msg is not None:
        system_prompt = self.initial_system_msg

      messages = []
      messages.append({ "role": "user", "content": prompt })
    else:
      user_ai_messages = []
      for m in messages:
        if 'role' in m and m['role'] == 'system':
          if system_prompt is anthropic.NOT_GIVEN:
            system_prompt = m['content']
          else:
            raise ValueError("Anthropic does not accept more than one system message.")
        else:
          user_ai_messages.append(m)
      messages = user_ai_messages

    reply = ''
    response = self.client.messages.create(
      **params,
      model=self.model_name,
      messages=messages,
      system=system_prompt,
    )
    if not params.get('stream', False):
      reply = response.content[0].text
      stop = response.stop_reason is not None
      if cb is not None:
        cb(content=reply, stop=stop, res=response)
    else:
      raise NotImplementedError

    return reply

class OllamaTextCompletion(TextCompletionBase):
  def __init__(self, server_url, model_name, logger=None):
    self.server_url = server_url
    self.model_name = model_name
    self.logger = logger

  def tokenize(self, content):
    raise NotImplementedError  # too bad ollama doesn't support tokenziation for now

  def create(self, prompt, params={}, cb=None):
    req = {
      'model': self.model_name,
      'prompt': prompt,
      'raw': True,
      "options": params,
    }

    reply = ''
    with requests.post(f"{self.server_url}/api/generate", json=req, stream=True) as response:
      # Processing streaming data in chunks
      buffer = b""  # Buffer to accumulate streamed data
      for chunk in response.iter_content(chunk_size=1024, decode_unicode=True):
        if chunk:
          buffer += chunk
          try:
            # Attempt to decode JSON from the accumulated buffer
            res = json.loads(buffer)

            if 'error' in res:
              if self.logger:
                self.logger.warning(f"Encounter error: {res['error']}")
              raise RuntimeError(f"Error from server: {res['error']}")

            reply += res['response']
            if cb is not None:
              cb(content=res['response'], stop=res['done'], res=res)

            if res['done']:
              break

            buffer = b""  # Clear the buffer after processing
          except json.JSONDecodeError:
            pass  # Incomplete JSON, continue accumulating data

    return reply

  def count_tokens(self, content, truncate=True):
    data = {
      'model': self.model_name,
      'input': content,
      'truncate': truncate,
    }

    raw_res = requests.post(f"{self.server_url}/api/embed", json=data)
    res = json.loads(raw_res.content)

    if 'error' in res:
      raise RuntimeError(res['error'])

    return res['prompt_eval_count']

  def _truncate_count_tokens(self, content):
    try:
      return self.count_tokens(content, truncate=False)
    except Exception:
      return math.inf
