#!/usr/bin/env python3
from typing import Dict, List

from pydantic import BaseModel, Field

class SettingsChatTerminal(BaseModel):
  endpoint: str = "local-llama"

  prompt: str = "prompts/chat-terminal.txt"
  user: str = "User"
  agent: str = "Assistant"

  use_black_list: bool = False
  black_list_pattern: str = r"\b(rm|sudo)\b"

class Settings(BaseModel):
  chat_terminal: SettingsChatTerminal = SettingsChatTerminal()
  text_completion_endpoints: Dict[str, Dict] = {}
