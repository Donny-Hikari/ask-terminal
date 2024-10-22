#!/usr/bin/env python3
from typing import Dict, List

from pydantic import BaseModel, Field

class SettingsChatTerminal(BaseModel):
  endpoint: str = "local-llama"  # default text completion endpoint
  prompt: str = "prompts/chat-terminal.mext"  # prompt template
  use_thinking: bool = True  # think before composing the command or not (chain of thought)
  max_observation_tokens: int = 1024  # truncate the output of command to this length before asking for a reply
  max_reply_tokens: int = 2048  # the maximum number of tokens to generate for a reply

  user: str = "User"  # name of the user
  agent: str = "Assistant"  # name of the agent

class Settings(BaseModel):
  chat_terminal: SettingsChatTerminal = SettingsChatTerminal()
  text_completion_endpoints: Dict[str, Dict] = {}
