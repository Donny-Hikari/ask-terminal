# Ask-terminal

Get things done by asking your terminal to generate and execute complex commands for you, using just natural language (thanks to LLM).

It works right in your shell, and the commands generated are in your shell history for easy reference.

![Demo1](./demo/demo1.gif)

- [Examples](#examples)
- [Installation](#installation)
- [Usage](#usage)
- [Text Completion Endpoints](#text-completion-endpoints)
- [Shell Client Options](#shell-client-options)
- [Server Options](#server-options)
- [More Examples](#more-examples)
- [About Prompt Template](#about-prompt-template)

## Examples

```console
$ ask which program is using the most cpu resource
% Initialized conversation: 35b95f19-2fda-4bda-970e-f1240234c5f2
Thoughts> This is a classic question to determine resource usage. We can use `top` command to get real-time data, or use `ps` and `grep` commands to find out the process with the highest CPU usage.
Command> ps -eo %cpu,pid,comm | sort -k 1 -rn
% Execute the command? (y/[N]) y
2337567 ollama_llama_se 21.2
2025836 ollama_llama_se  3.6
2104826 code             2.7
2104513 code             2.4
   3777 firefox          1.3
2322053 code             1.2
<...OMITTED...>
% Command finished
Reply> The program using the most cpu resource is "ollama_llama_se". Its pid and percentage of cpu usage are 2337567 and 21.2 respectively.
```

## Installation

There are three ways to install `ask-terminal`:

- [Run Server in Docker, and Client Locally](#run-server-in-docker-and-client-locally)
- [Full Local Setup](#full-local-setup)
- [Run Client in Docker](#run-client-in-docker)

It is recommended to use *Run Server in Docker, and Client Locally* method. But if you don't have docker installed, you can use *Full Local Setup* method.

### Run Server in Docker, and Client Locally

Start the server in docker with command:

```shell
$ make docker-run-server DOCKER_SERVER_FLAGS=--net=host\ -d\ -e\ OPENAI_API_KEY=<YOUR_API_KEY>
```

This will (re)build the image (with name `ask-terminal`) and run the server in the background (with container name `ask-terminal-server`).

Replace `<YOUR_API_KEY>` with your OpenAI API key.

> **Note:** You may use a credential file as well. See [OpenAI](#openai) in the [Text Completion Endpoint](#text-completion-endpoint) section for more information on how to obtain an OpenAI API key and how to use a credential file.

Then install the client locally with:

```shell
$ make install-client
```

Add ask-terminal to your shell config file by running:

```shel
$ make install-shell-rc
```

You may edit the shell config file yourself (`~/.bashrc` or `~/.zshrc`). Add these lines:

```shell
source $HOME/.ask-terminal/ask-terminal.sh
alias ask=ask-terminal
```

Start a new terminal, and run `ask-terminal` or `ask`. Enjoy!

> **Note:** You may use other text completion endpoints, such as `llama-cpp`, `ollama`, `anthropic`, etc. See [Text Completion Endpoint](#text-completion-endpoint) for more information.

> **Note:** If you use online API endpoints such as `OpenAI` and `Anthropic`, and want to prevent sending the output of your commands to the server, you can set the environment variable `ASK_TERMINAL_USE_REPLY=false` in your client to turn off the replying-to-result feature.
>
> It is recommended to use a local endpoint instead, such as [Ollama](#ollama) or [Llama-cpp](#llama-cpp).

### Full Local Setup

First install the server and the client with this command:

```shell
$ make setup
```

Start the server:

```shell
$ OPENAI_API_KEY=<YOUR_API_KEY> ask-terminal-server
```

Replace `<YOUR_API_KEY>` with your OpenAI API key.

> **Note:** You may use a credential file as well. See [OpenAI](#openai) in the [Text Completion Endpoint](#text-completion-endpoint) section for more information on how to obtain an OpenAI API key and how to use a credential file.

Add ask-terminal to your shell config file by running:

```shel
$ make install-shell-rc
```

You may edit the shell config file yourself (`~/.bashrc` or `~/.zshrc`). Add these lines:

```shell
source $HOME/.ask-terminal/ask-terminal.sh
alias ask=ask-terminal
```

Start a new terminal, and run `ask-terminal` or `ask`. Enjoy!

Refer to [Start Ask-terminal Server at Startup (Locally)](#start-ask-terminal-server-at-startup-locally) if you want to run the server at startup.

> **Note:** You may use other text completion endpoints other than `openai`, such as `llama-cpp`, `ollama`, `anthropic`, etc. See [Text Completion Endpoint](#text-completion-endpoint) for more information.

> **Note:** If you use online API endpoints such as `OpenAI` and `Anthropic`, and want to prevent sending the output of your commands to the server, you can set the environment variable `ASK_TERMINAL_USE_REPLY=false` in your client to turn off the replying-to-result feature.
>
> It is recommended to use a local endpoint instead, such as [Ollama](#ollama) or [Llama-cpp](#llama-cpp).

### Run Client in Docker

You may run the client in docker as well. This can help prevent unwanted command execution on your local machine, but at the cost of not having accces to your local environment and hinder the purpose of Ask-terminal - to help you find and execute commands in your environment. Therefore this method is mainly for test purpose.

```shell
$ make docker-run-client CLIENT_ENV=ASK_TERMINAL_USE_BLACKLIST=true
```

`ASK_TERMINAL_USE_BLACKLIST=true` allows the client to run commands that are not in the blacklist without confirmation. Use `ASK_TERMINAL_BLACKLIST_PATTERN` to set the blacklist pattern (grep pattern matching).

## Usage

Chat with your terminal with the command `ask-terminal`:

```console
$ ask-terminal go home
% Initialized conversation: 931a4474-384c-4fdf-8c3b-934c95ee48ed
Thought> The user wants to change the current directory. I should use the `cd` command.
Command> cd ~/
% Execute the command? (y/[N]) y
% Command finished
Reply> The system has changed its current folder to your home directory.
$ pwd
/home/username
```

Or simply `ask` (if you have set the alias):

```console
$ ask find the keybindings file for vscode
Thought> The user may have stored his keybindings in a variety of places like '.vscode/keybindings.json', 'keybindings.json' or even '$HOME/.config/vscode/keybindings.json'.
Command> find ~/.config -name "keybindings.json"
% Execute the command? (y/[N]) y
/home/username/.config/Code/User/keybindings.json
% Command finished
Reply> The keybindings file is "/home/username/.config/Code/User/keybindings.json".
```

Ask-terminal can do a lot for you and if it fails, you can ask it to fix. Go creative.

Some examples:

1. Ask it to merge git branches for you.
2. Check system status.
3. Convert images or videos (ffmpeg is too hard for me):

[![demo2.mp4](./demo/demo2.jpg)](https://github.com/user-attachments/assets/a8f922b4-2481-426f-a954-efbb4e94254b)

4. Clone git repo and run:

[![deme3.mp4](./demo/demo3.jpg)](https://github.com/user-attachments/assets/d58a0d4e-c466-418b-9268-cf65836f8d5d)

### Interactive Mode

Run the command `ask-terminal` or `ask` without arguments to enter interactive mode:

```console
$ ask-terminal
% Initialized conversation: d7370783-ce14-4f13-9901-dfffbb5990f3
> which program is using port 16099
Thought> The user might want to find the process that occupies this port. We can use the `netstat` command.
Command> netstat -tlnp | grep 16099
% Execute the command? (y/[N]) y
(eval):1: command not found: netstat
% Command finished
Reply> The 'netstat' command is not available in this zsh environment. We can replace it with the `ss` command.
Let me try again.
> do it
Thought> No problem, let's find the process that occupies port 16099 using ss command instead of netstat.
Command> ss -tlnp | grep 16099
% Execute the command? (y/[N]) y
LISTEN 0      2048       127.0.0.1:16099      0.0.0.0:*    users:(("ask-terminal-s",pid=207732,fd=6))
% Command finished
Reply> The program using port 16099 is "ask-terminal-s".
>
```

### Start Ask-terminal Server at Startup (Locally)

[services/ask-terminal-server.service](./services/ask-terminal-server.service) offers a template for starting Ask-terminal Server as a systemd service.

> **Note:** If you [run the server in docker](#run-server-in-docker-and-client-locally) with `make docker-run-server`, you don't need to worry about this section as by default the server container is set to start automatically on startup.

To install the service, first run:

```shell
$ make install-service
```

Then edit `~/.config/systemd/user/ask-terminal-server.service` as you need.

Finally, enable (and start) the service with:

```shell
$ systemctl --user daemon-reload
$ systemctl --user enable --now ask-terminal-server.service
```

### Configuration

Refers to [Shell Client Options](#shell-client-options) and [Server Options](#server-options) for more options to configure.

### Reset Chat Session

You can reset the chat session with the following command:

```shell
$ ask-terminal-reset
```

The next time you start `ask-terminal`, it will create a new conversation session.

> **Note:** Some client environment variables require a `ask-terminal-reset` to take effect, such as `ASK_TERMINAL_ENDPOINT` and `ASK_TERMINAL_MODEL`.

## Text Completion Endpoints

The following text completion endpoints are supported:

- [Ollama](#ollama)
- [Llama-cpp](#llama-cpp)
- [OpenAI](#openai)
- [Anthropic](#anthropic)

There are two ways to configure the endpoints:

1. Change th endpoint in the server configuration file `~/.config/ask-terminal/configs/ask_terminal.yaml`. This will be the default endpoint for all chat sessions.
2. Set the environment variable `ASK_TERMINAL_ENDPOINT` for the client. This will overwrite the default one specified in the server configuration file. You can change the endpoint flexibly for different chat sessions.

### Ollama

Change the endpoint to `ollama` in file `~/.config/ask-terminal/configs/ask_terminal.yaml` to use ollama for text completion.

```yaml
ask_terminal:
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

Change the endpoint to `local-llama` in file `~/.config/ask-terminal/configs/ask_terminal.yaml` to use [llama-cpp](https://github.com/ggerganov/llama.cpp) for text completion.

```yaml
ask_terminal:
  endpoint: local-llama
```

By default, llama-cpp server is expected at `http://127.0.0.1:40080`. `text_completion_endpoints.local-llama` contains the configuration for this endpoint.

```yaml
text_completion_endpoints:
  local-llama:
    server_url: "http://127.0.0.1:40080"
    # ... other configuration options
```

### OpenAI

Change the endpoint to `openai` in file `~/.config/ask-terminal/configs/ask_terminal.yaml` to use openai for text completion.

```yaml
ask_terminal:
  endpoint: openai
```

You may set your API key via environment variable `OPENAI_API_KEY`, or use a credential file at `~/.config/ask-terminal/credentials/openai.yaml`.

To use credential file, first create it with the following content:

```yaml
api_key: <YOUR_API_KEY>
```

Then add the credential file to `~/.config/ask-terminal/configs/ask_terminal.yaml`:

```yaml
text_completion_endpoints:
  openai:
    model: gpt-3.5-turbo
    credential_file: credentials/openai.yaml  # it will search ~/.config/ask-terminal; you can specify the full path as well
    # ... other configuration options
```

For how to get an API key, see [Quickstart tutorial - OpenAI API](https://platform.openai.com/docs/quickstart).

### Anthropic

Setup of Anthropic is similar to [OpenAI](#openai). The name of the endpoint is `anthropic`. The API key is stored in environment variable `ANTHROPIC_API_KEY`, or in credential file `~/.config/ask-terminal/credentials/anthropic.yaml`.

For how to get an API key, see [Build with Claude \\ Anthropic](https://www.anthropic.com/api).

## Shell Client Options

The following environment variables can be used to configure the shell client:

```shell
ASK_TERMINAL_SERVER_URL="http://localhost:16099"  # url of the ask-terminal-server
ASK_TERMINAL_ENDPOINT=  # text completion endpoint, default is what specified in the server config file
ASK_TERMINAL_MODEL=  # text completion model if the endpoint supports setting the model, default is what specified in the server config file
ASK_TERMINAL_USE_BLACKLIST=false  # use blacklist for command, true to execute command by default except those matching ASK_TERMINAL_BLACKLIST_PATTERN
ASK_TERMINAL_BLACKLIST_PATTERN="\b(rm|sudo)\b"  # pattern to confirm before execution; patterns are matched using `grep -E`; use with ASK_TERMINAL_USE_BLACKLIST
ASK_TERMINAL_USE_REPLY=true  # send the output of command to the server to get a reply
ASK_TERMINAL_USE_STREAMING=true  # stream the output
ASK_TERMINAL_USE_CLARIFICATION=true  # ask for clarification when refusing a command
ASK_TERMINAL_COMMAND_HISTORY=true   # add commands to the shell history
ASK_TERMINAL_REFUSED_COMMAND_HISTORY=true   # add commands to the shell history even if it gets refused
```

You may use `export ASK_TERMINAL_*=...` before hand or prepend the environment variables `ASK_TERMINAL_*=...` to the client `ask-terminal` (or `ask`) command to use them.

```shell
$ ASK_TERMINAL_ENDPOINT=ollama ASK_TERMINAL_MODEL=llama3.2 ask who am i
```

## Server Options

Options for the Ask-terminal server is provided via the `ask_terminal` section in the config file `~/.config/ask-terminal/configs/ask_terminal.yaml`.

You can find all available options and their defaults in the `SettingsAskTerminal` class in [ask_terminal/settings.py](./ask_terminal/settings.py).

```yaml
ask_terminal:
  endpoint: "local-llama"  # default text completion endpoint
  model_name: null  # default model name, if the endpoint supports setting model; this will overwrite the endpoint's `model` field in `text_completion_endpoints`
  prompt: "prompts/ask-terminal.mext"  # prompt template
  use_thinking: True  # think before composing the command or not (chain of thought)
  max_observation_tokens: 1024  # truncate the output of command to this length before asking for a reply
  max_reply_tokens: 2048  # the maximum number of tokens to generate for a reply

  user: "User"  # name of the user
  agent: "Assistant"  # name of the agent
```

## More examples

```console
$ ask which program answers the meaning of life
Thought> Since the user is looking for something related to "meaning of life", I'll think about programs or data that could possibly be related.
Command> echo -n '42' | xargs python3 -c "import this; print(this.s)"
% Execute the command? (y/[N]) y
The Zen of Python, by Tim Peters

Beautiful is better than ugly.
Explicit is better than implicit.
Simple is better than complex.
Complex is better than complicated.
Flat is better than nested.
Sparse is better than dense.
Readability counts.
Special cases aren't special enough to break the rules.
Although practicality beats purity.
Errors should never pass silently.
Unless explicitly silenced.
In the face of ambiguity, refuse the temptation to guess.
There should be one-- and preferably only one --obvious way to do it.
Although that way may not be obvious at first unless you're Dutch.
Now is better than never.
Although never is often better than *right* now.
If the implementation is hard to explain, it's a bad idea.
If the implementation is easy to explain, it may be a good idea.
Namespaces are one honking great idea -- let's do more of those!
Gur Mra bs Clguba, ol Gvz Crgref

Ornhgvshy vf orggre guna htyl.
Rkcyvpvg vf orggre guna vzcyvpvg.
Fvzcyr vf orggre guna pbzcyrk.
Pbzcyrk vf orggre guna pbzcyvpngrq.
Syng vf orggre guna arfgrq.
Fcnefr vf orggre guna qrafr.
Ernqnovyvgl pbhagf.
Fcrpvny pnfrf nera'g fcrpvny rabhtu gb oernx gur ehyrf.
Nygubhtu cenpgvpnyvgl orngf chevgl.
Reebef fubhyq arire cnff fvyragyl.
Hayrff rkcyvpvgyl fvyraprq.
Va gur snpr bs nzovthvgl, ershfr gur grzcgngvba gb thrff.
Gurer fubhyq or bar-- naq cersrenoyl bayl bar --boivbhf jnl gb qb vg.
Nygubhtu gung jnl znl abg or boivbhf ng svefg hayrff lbh'er Qhgpu.
Abj vf orggre guna arire.
Nygubhtu arire vf bsgra orggre guna *evtug* abj.
Vs gur vzcyrzragngvba vf uneq gb rkcynva, vg'f n onq vqrn.
Vs gur vzcyrzragngvba vf rnfl gb rkcynva, vg znl or n tbbq vqrn.
Anzrfcnprf ner bar ubaxvat terng vqrn -- yrg'f qb zber bs gubfr!
% Command finished
Reply> 42 is the answer to the meaning of life according to The Hitchhiker's Guide to the Galaxy. However, it seems that there are multiple answers provided by 'import this'. I'll consider other possible programs related to the meaning of life.
```

> **Author Note:** I don't even know there is a builtin package called `this` in Python, let alone the poem.

## About Prompt Template

This project use [Mext](https://github.com/Donny-Hikari/mext) for composing the prompt template.
It is a powerful text template language designed for crafting prompts for LLM.
