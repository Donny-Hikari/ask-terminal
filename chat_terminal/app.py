import random
import logging
from typing import Dict, Optional

from fastapi import FastAPI, WebSocket
from pydantic import BaseModel

from .chat_terminal import ChatTerminal, ChatQueryEnvModel
from .settings import Settings

_logger = logging.getLogger(__name__)


class ChatInitModel(BaseModel):
  endpoint: Optional[str] = None

class ChatQueryModel(BaseModel):
  message: str
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

@app.post('/chat/{conversation_id}/query_command')
async def query_command(conversation_id: str, query: ChatQueryCommandModel):
  if conversation_id not in chat_pool:
    return {
      "status": "error",
      "error": "Conversation does not exist",
    }
  conversation = chat_pool[conversation_id]

  try:
    response = await conversation.query_command(query.message, env=query.env)
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
async def query_reply(conversation_id: str, query: ChatQueryReplyModel):
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


