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

Note: You may use other text completion endpoints other than `openai`, such as `llama-cpp` and `ollama`. See [Text Completion Endpoint](#text-completion-endpoint) for more information.

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
