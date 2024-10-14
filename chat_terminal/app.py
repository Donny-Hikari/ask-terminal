import random
import logging

from fastapi import FastAPI, WebSocket
import uvicorn

from .chat_terminal import ChatTerminal
from .settings import Settings, SettingsChatTerminal

_logger = logging.getLogger(__name__)


app = FastAPI()

settings = Settings()
chat_pool = {}

@app.websocket('/chat_ws')
async def chat(websocket: WebSocket):
  await websocket.accept()
  while True:
    data = await websocket.receive_json()
    _logger.debug(f"data: {data}")

@app.post('/chat/{conversation_id}/init')
async def init(conversation_id: str, init_cfg: SettingsChatTerminal=None):
  if conversation_id in chat_pool:
    return {"error": "conversation already exists"}

  chat_settings = settings.model_copy()
  if init_cfg is not None:
    chat_settings.chat_terminal = init_cfg

  try:
    chat_pool[conversation_id] = ChatTerminal(chat_settings)
  except ValueError as e:
    return {"error": str(e)}

  return {"success": True}

def set_settings(_settings: Settings):
  global settings
  settings = _settings
