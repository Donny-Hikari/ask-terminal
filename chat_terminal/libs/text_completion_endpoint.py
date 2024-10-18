import json
import openai
import requests
import os
import time
import logging

class LLamaTextCompletion:
  def __init__(self, server_url, logger=None):
    self.server_url = server_url
    self.logger = logger

  def tokenize(self, content):
    data = {
      "content": content,
    }

    res = requests.post(f"{self.server_url}/tokenize", json=data)
    return len(json.loads(res.content)['tokens'])

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

class OpenAITextCompletion:
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
           messages=None, params={}, prompt=None,
           cb=None, max_retries=5):
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
    while n_retries < max_retries:
      n_retries += 1
      try:
        response = self.client.chat.completions.create(
          **params,
          model=self.model_name,
          messages=messages,
          stream=True,
        )
        for chunk in response:
            content = chunk.choices[0].delta.content
            stop = chunk.choices[0].finish_reason is not None
            if not stop:
              reply += content
            if cb is not None:
              cb(content=content, stop=stop, res=chunk)
        break
      except openai.RateLimitError as e:
        if n_retries == 1:
          if self.logger:
            self.logger.warning("Encounter rate limit.")
        elif n_retries == max_retries:
          raise e
        # wait 1 5 13 29 60 120 ...
        time.sleep(int(4.5*(1.94**n_retries)-3))

    return reply

class OllamaTextCompletion:
  def __init__(self, server_url, model_name, logger=None):
    self.server_url = server_url
    self.model_name = model_name
    self.logger = logger

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

