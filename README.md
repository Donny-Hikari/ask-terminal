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
$ OPENAI_API_KEY=... chat-terminal-server
```

Start a new terminal, and run `chat-terminal` or `ask`. Enjoy!

Note: You may use other text completion endpoints other than `openai`, such as `llama-cpp`. See [Text Completion Endpoint](#text-completion-endpoint) for more information.

## Text Completion Endpoint

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

You may pass your API key via environment variable `OPENAI_API_KEY`, or use a credential file at `~/.config/chat-terminal/credentials/openai.yaml`.

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
