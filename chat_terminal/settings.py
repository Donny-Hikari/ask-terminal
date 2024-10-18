#!/usr/bin/env python3
from typing import Dict, List

from pydantic import BaseModel, Field

class SettingsChatTerminal(BaseModel):
  endpoint: str = "local-llama"
  prompt: str = "prompts/chat-terminal.mext"
  use_thinking: bool = True
  max_observation_tokens: int = 1024
  max_reply_tokens: int = 2048

  user: str = "User"
  agent: str = "Assistant"

class Settings(BaseModel):
  chat_terminal: SettingsChatTerminal = SettingsChatTerminal()
  text_completion_endpoints: Dict[str, Dict] = {}
