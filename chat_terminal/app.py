import random
import logging
from typing import Dict, Literal, Optional

from fastapi import FastAPI, WebSocket
from pydantic import BaseModel

from .chat_terminal import ChatTerminal
from .settings import Settings, SettingsChatTerminal

_logger = logging.getLogger(__name__)


app = FastAPI()

settings = Settings()
chat_pool: Dict[str, ChatTerminal] = {}

def set_settings(_settings: Settings):
  global settings
  settings = _settings

@app.post('/chat/{conversation_id}/init')
async def init(conversation_id: str, init_cfg: SettingsChatTerminal=None):
  if conversation_id in chat_pool:
    return {
      "status": "error",
      "error": "conversation already exists",
    }

  chat_settings = settings.model_copy()
  if init_cfg is not None:
    chat_settings.chat_terminal = init_cfg

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

class ChatQueryEnvModel(BaseModel):
  shell: Optional[Literal["bash", "zsh"]] = None

class ChatQueryModel(BaseModel):
  message: str
  env: ChatQueryEnvModel = ChatQueryEnvModel()

class ChatQueryReplyModel(ChatQueryModel):
  command_executed: bool

@app.post('/chat/{conversation_id}/query_command')
async def query_command(conversation_id: str, query: ChatQueryModel):
  if conversation_id not in chat_pool:
    return {
      "status": "error",
      "error": "conversation does not exist",
    }
  conversation = chat_pool[conversation_id]

  response = conversation.query_command(query.message, env=query.env.model_dump())

  return {
      "status": "success",
      "payload": response,
    }

@app.post('/chat/{conversation_id}/query_reply')
async def query_reply(conversation_id: str, query: ChatQueryReplyModel):
  if conversation_id not in chat_pool:
    return {
      "status": "error",
      "error": "conversation does not exist",
    }
  conversation = chat_pool[conversation_id]

  response = conversation.query_reply(
    command_refused=not query.command_executed,
    observation=query.message,
    env=query.env.model_dump(),
  )

  return {
      "status": "success",
      "payload": response,
    }


