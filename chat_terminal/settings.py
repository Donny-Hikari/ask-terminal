#!/usr/bin/env python3
from typing import Dict, List, Optional

from pydantic import BaseModel, Field

class SettingsChatTerminal(BaseModel):
  endpoint: str = Field("local-llama", help="default text completion endpoint")
  model_name: Optional[str] = Field(None, help="default model name, if the endpoint supports setting model; this will overwrite the endpoint's `model` field in `text_completion_endpoints`")
  prompt: str = Field("prompts/chat-terminal.mext", help="prompt template")
  use_thinking: bool = Field(True, help="think before composing the command or not (chain of thought)")
  max_observation_tokens: int = Field(1024, help="truncate the output of command to this length before asking for a reply")
  max_reply_tokens: int = Field(2048, help="the maximum number of tokens to generate for a reply")

  user: str = Field("User", help="name of the user")
  agent: str = Field("Assistant", help="name of the agent")

  class Config:
      protected_namespaces = ()

class Settings(BaseModel):
  chat_terminal: SettingsChatTerminal = SettingsChatTerminal()
  text_completion_endpoints: Dict[str, Dict] = {}
