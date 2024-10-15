#!/bin/bash

CHAT_TERMINAL_SERVER_URL="http://localhost:16099"
CHAT_TERMINAL_USE_BLACKLIST=false
CHAT_TERMINAL_BLACKLIST_PATTERN="\b(rm|sudo)\b"

_conversation_id=

_curl_server() {
  local url="$1"
  local data="$2"

  curl -s \
    -X POST "${CHAT_TERMINAL_SERVER_URL}${url}" \
    -H "Content-Type: application/json" \
    -d "$data"
}

_init_conversation() {
  _curl_server "/chat/${_conversation_id}/init"
}

_get_env() {
  local shell_name="${SHELL##*/}"

  echo "{ \
    \"shell\": \"$shell_name\" \
  }"
}

_query_command() {
  local query="$1"
  local data="{ \
    \"message\": \"$query\", \
    \"env\": $(_get_env)
  }"

  _curl_server "/chat/${_conversation_id}/query_command" "$data"
}

_query_reply() {
  local observation="$1"
  local data="{ \
    \"message\": \"$(echo -E ${observation//$'\n'/\\n})\", \
    \"env\": $(_get_env)
  }"

  _curl_server "/chat/${_conversation_id}/query_reply" "$data"
}

_confirm_command_execution() {
  echo -n "Execute the command? (y/[N])"
  if [[ -n "$BASH_VERSION" ]]; then
    read -n 1 choice
  elif [[ -n "$ZSH_VERSION" ]]; then
    read -k 1 choice
  else
    read choice
  fi
  echo

  if [[ "$choice" == 'y' || "$choice" == 'Y' ]]; then
    return 0
  else
    return 1
  fi
}

_chat_once() {
  local query=$1
  local result
  local thinking
  local _command
  local exec_command
  local observation

  result=$(_query_command "$query")
  _status=$(echo -E "$result" | jq -r ".status")
  if [[ $_status != "success" ]]; then
    echo "Failed to commute with server: $result"
    return 1
  fi

  thinking=$(echo -E "$result" | jq -r '.payload.thinking')
  _command=$(echo -E "$result" | jq -r '.payload.command')
  echo "Thought> $thinking"
  echo "Command> $_command"

  exec_command=false
  if [[ "$CHAT_TERMINAL_USE_BLACKLIST" == "true" ]]; then
    echo "$_command" | grep -qE "$CHAT_TERMINAL_BLACKLIST_PATTERN"
    if [[ $? -ne 0 ]]; then
      exec_command=true
    else
      _confirm_command_execution
      if [[ $? -eq 0 ]]; then
        exec_command=true
      fi
    fi
  else
    _confirm_command_execution
    if [[ $? -eq 0 ]]; then
      exec_command=true
    fi
  fi

  if ! $exec_command; then
    return
  fi

  observation=$(eval "$_command")
  echo -e "$observation"

  result=$(_query_reply "$observation")
  _status=$(echo -E "$result" | jq -r ".status")
  if [[ $_status != "success" ]]; then
    echo "Failed to commute with server: $result"
    return 1
  fi

  reply=$(echo -E "$result" | jq -r '.payload.reply')
  echo "Reply> $reply"
}

chat_terminal() {
  local query="$@"
  local result
  local _status

  if [[ -z "$_conversation_id" ]]; then
    # generate a UUID as conversation ID
    _conversation_id=$(uuidgen)
    result=$(_init_conversation)
    _status=$(echo -E "$result" | jq -r ".status")
    if [[ $_status != "success" ]]; then
      echo "Failed to initialize converstaion: ${result}"
      return 1
    fi
    echo "Initialized conversation: $_conversation_id"
  fi

  if [[ -n "$query" ]]; then
    _chat_once "$query"
  else
    while true; do
      echo -n "> " && read query
      if [[ -n $query ]]; then
        _chat_once "$query"
      fi
    done
  fi
}
