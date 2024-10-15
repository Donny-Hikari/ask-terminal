#!/usr/bin/env python3
from typing import Dict, List

from pydantic import BaseModel, Field

class SettingsChatTerminal(BaseModel):
  endpoint: str = "local-llama"
  use_thinking: bool = True
  use_black_list: bool = False
  black_list_pattern: str = r"\b(rm|sudo)\b"

  prompt: str = "prompts/chat-terminal.mext"
  user: str = "User"
  agent: str = "Assistant"

class Settings(BaseModel):
  chat_terminal: SettingsChatTerminal = SettingsChatTerminal()
  text_completion_endpoints: Dict[str, Dict] = {}
