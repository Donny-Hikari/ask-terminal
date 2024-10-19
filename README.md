# Chat Terminal

Chat with your terminal and get things done using natural language with the help of LLM (Large Language Model).

## Installation

First setup with this command:

```shell
$ make setup
```

Add this to your shell config file (`~/.bashrc` or `~/.zshrc`):

```shell
source ~/.chat-terminal/chat-terminal.sh
alias ask=chat-terminal
```

Start the server:

```shell
$ OPENAI_API_KEY=<YOUR_API_KEY> chat-terminal-server
```

Start a new terminal, and run `chat-terminal` or `ask`. Enjoy!

Note: You may use other text completion endpoints other than `openai`, such as `llama-cpp`, `ollama`, `anthropic`, etc. See [Text Completion Endpoint](#text-completion-endpoint) for more information.

## Text Completion Endpoint

The following text completion endpoints are supported:

- [Ollama](#ollama)
- [Llama-cpp](#llama-cpp)
- [OpenAI](#openai)
- [Anthropic](#anthropic)

### Ollama

Change the endpoint to `ollama` in file `~/.config/chat-terminal/configs/chat_terminal.yaml` to use ollama for text completion.

```yaml
chat_terminal:
  endpoint: ollama
```

Make sure the `server_url` is correct and the `model` is locally available.

```yaml
text_completion_endpoints:
  ollama:
    server_url: "http://127.0.0.1:11434"
    model: "llama3.1"
    # ... other configuration options
```

You can get Ollama [here](https://ollama.com/download). And pull `llama3.1` with:

```shell
$ ollama pull llama3.1
```

### Llama-cpp

Change the endpoint to `local-llama` in file `~/.config/chat-terminal/configs/chat_terminal.yaml` to use llama-cpp for text completion.

```yaml
chat_terminal:
  endpoint: local-llama
```

By default, llama-cpp server is expected at `http://127.0.0.1:40080`. `text_completion_endpoints.local-llama` contains the configuration for this endpoint.

### OpenAI

Change the endpoint to `openai` in file `~/.config/chat-terminal/configs/chat_terminal.yaml` to use openai for text completion.

```yaml
chat_terminal:
  endpoint: openai
```

You may set your API key via environment variable `OPENAI_API_KEY`, or use a credential file at `~/.config/chat-terminal/credentials/openai.yaml`.

To use credential file, first create it with the following content:

```yaml
api_key: <YOUR_API_KEY>
```

Then add the credential file to `~/.config/chat-terminal/configs/chat_terminal.yaml`:

```yaml
text_completion_endpoints:
  openai:
    model: gpt-3.5-turbo
    credential_file: credentials/openai.yaml  # or specify the full path
    # ... other configuration options
```

For how to get an API key, see [Quickstart tutorial - OpenAI API](https://platform.openai.com/docs/quickstart).

### Anthropic

Setup of Anthropic is similar to [OpenAI](#openai). The name of the endpoint is `anthropic`. The API key is stored in environment variable `ANTHROPIC_API_KEY`, or in credential file `~/.config/chat-terminal/credentials/anthropic.yaml`.

For how to get an API key, see [Build with Claude \\ Anthropic](https://www.anthropic.com/api).

## Start Chat Terminal Server at Startup

[services/chat-terminal-server.service](./services/chat-terminal-server.service) offers a template for starting Chat Terminal Server as a systemd service.

To install the service, first run:

```shell
$ make install-service
```

Then edit `~/.config/systemd/user/chat-terminal-server.service` as you need.

Finally, enable (and start) the service with:

```shell
$ systemctl --user daemon-reload
$ systemctl --user enable --now chat-terminal-server.service
```

## Shell Client Options

The following environment variables can be used to configure the shell client:

```shell
CHAT_TERMINAL_SERVER_URL="http://localhost:16099"  # url of the chat-terminal-server
CHAT_TERMINAL_USE_BLACKLIST=false  # use blacklist for command, true to execute command by default except those matching CHAT_TERMINAL_BLACKLIST_PATTERN
CHAT_TERMINAL_BLACKLIST_PATTERN="\b(rm|sudo)\b"  # pattern to confirm before execution, use with CHAT_TERMINAL_USE_BLACKLIST
CHAT_TERMINAL_ENDPOINT=  # text completion endpoints, default is specified in the server config file
CHAT_TERMINAL_USE_REPLY=true  # send the output of command to the server to get a reply
CHAT_TERMINAL_USE_STREAMING=true  # stream the output
```

## Chat Terminal Server Options

Options for the chat terminal server is provided via the `chat_terminal` section in the config file `~/.config/chat-terminal/configs/chat_terminal.yaml`.

You can find all available options and their defaults in `SettingsChatTerminal` class in [chat_terminal/settings.py](./chat_terminal/settings.py).

```yaml
chat_terminal:
  endpoint: "local-llama"  # text completion endpoint
  prompt: "prompts/chat-terminal.mext"  # prompt template
  use_thinking: True  # think before composing the command or not (chain of thought)
  max_observation_tokens: 1024  # truncate the output of command to this length before asking for a reply
  max_reply_tokens: 2048  # the maximum number of tokens to generate for a reply

  user: "User"  # name of the user
  agent: "Assistant"  # name of the agent
```

## About Prompt Template

[Mext](https://github.com/Donny-Hikari/mext) is a powerful text template language designed for crafting prompts for LLM. It is used for composing the prompt template.
