import random
import logging
import asyncio
import json
from functools import wraps
from typing import Dict, Optional

from fastapi import FastAPI, WebSocket
from fastapi.exceptions import RequestValidationError
from fastapi.responses import StreamingResponse, JSONResponse
from pydantic import BaseModel

from .chat_terminal import ChatTerminal, ChatQueryEnvModel
from .settings import Settings

_logger = logging.getLogger(__name__)


class ChatInitModel(BaseModel):
  endpoint: Optional[str] = None
  model_name: Optional[str] = None

  class Config:
      protected_namespaces = ()

class ChatQueryModel(BaseModel):
  message: str
  stream: bool = False
  env: ChatQueryEnvModel = ChatQueryEnvModel()

class ChatQueryCommandModel(ChatQueryModel):
  pass

class ChatQueryReplyModel(ChatQueryModel):
  command_executed: bool


app = FastAPI()

settings = Settings()
chat_pool: Dict[str, ChatTerminal] = {}

def set_settings(_settings: Settings):
  global settings
  settings = _settings

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
  _logger.error("Error occurred", exc_info=exc)
  return JSONResponse(
    status_code=500,
    content={
      "status": "error",
      "error": "Something went wrong. Please try again.",
    },
  )

@app.exception_handler(RequestValidationError)
async def request_validation_exception_handler(request, exc):
  _logger.error("Request validation error", exc_info=exc)
  return JSONResponse(
    status_code=400,
    content={
      "status": "error",
      "error": "Bad request",
    },
  )

@app.post('/chat/{conversation_id}/init')
async def init(conversation_id: str, init_cfg: ChatInitModel=ChatInitModel()):
  if conversation_id in chat_pool:
    return {
      "status": "error",
      "error": "Conversation already exists",
    }

  chat_settings = settings.model_copy(deep=True)
  for prop in init_cfg.model_fields_set:
    setattr(chat_settings.chat_terminal, prop, getattr(init_cfg, prop))

  try:
    chat_pool[conversation_id] = ChatTerminal(chat_settings)
  except ValueError as e:
    return {
      "status": "error",
      "error": str(e),
    }

  return {
    "status": "success",
  }

def conditional_query_streaming_response(num_sections=1):
  def decorator(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
      stream = False
      if 'query' in kwargs:
        query: ChatQueryModel = kwargs.get('query')
        stream = query.stream

      q_response = asyncio.Queue()

      async def receive_response(content, stop, res, section):
        await q_response.put((section, content, stop))

      async def stream_response(producer_task: asyncio.Task):
        sections_left = num_sections
        while True:
          get_response_task = asyncio.create_task(q_response.get())
          done, pending = await asyncio.wait([producer_task, get_response_task], return_when=asyncio.FIRST_COMPLETED)
          if get_response_task in done:
            section, content, stop = get_response_task.result()
          else:
            get_response_task.cancel()
            break  # stop early on error

          s_res = json.dumps({
            'section': section,
            'content': content if content is not None else '',
            'finished': stop,
          }, ensure_ascii=False)
          yield s_res + '\n'
          if stop:
            sections_left -= 1
            if sections_left == 0:
              break

        final_response = await producer_task
        final_response = json.dumps(final_response, ensure_ascii=False)
        yield final_response + '\n'

      kwargs['streaming_cb'] = receive_response if stream else None
      producer_task = asyncio.create_task(func(*args, **kwargs))

      if not stream:
        return await producer_task
      else:
        return StreamingResponse(stream_response(producer_task), media_type="text/plain")

    return wrapper

  return decorator

@app.post('/chat/{conversation_id}/query_command')
@conditional_query_streaming_response(num_sections=2)
async def query_command(conversation_id: str, query: ChatQueryCommandModel, streaming_cb=None):
  if conversation_id not in chat_pool:
    return {
      "status": "error",
      "error": "Conversation does not exist",
    }
  conversation = chat_pool[conversation_id]

  try:
    response = await conversation.query_command(
      query.message,
      env=query.env,
      stream=query.stream,
      cb=streaming_cb,
    )
  except Exception as e:
    _logger.error(f'Error while querying command: {e}')
    return {
      "status": "error",
      "error": "Failed to communicate with upstream endpoint"
    }

  return {
      "status": "success",
      "payload": response,
    }

@app.post('/chat/{conversation_id}/query_reply')
@conditional_query_streaming_response()
async def query_reply(conversation_id: str, query: ChatQueryReplyModel, streaming_cb=None):
  if conversation_id not in chat_pool:
    return {
      "status": "error",
      "error": "Conversation does not exist",
    }
  conversation = chat_pool[conversation_id]

  try:
    response = await conversation.query_reply(
      command_refused=not query.command_executed,
      observation=query.message,
      env=query.env,
      stream=query.stream,
      cb=streaming_cb,
    )
  except Exception as e:
    _logger.error(f'Error while querying command: {e}')
    return {
      "status": "error",
      "error": "Failed to communicate with upstream endpoint"
    }

  return {
      "status": "success",
      "payload": response,
    }


