#!/usr/bin/env sh

CHAT_TERMINAL_SERVER_URL="http://localhost:16099"
CHAT_TERMINAL_USE_BLACKLIST=false
CHAT_TERMINAL_BLACKLIST_PATTERN="\b(rm|sudo)\b"
CHAT_TERMINAL_ENDPOINT=

_conversation_id=
_MESSAGE_PREFIX="%"


# handy functions

_print_response() {
  echo "$1> $2"
}

_advance_read() {
  if [[ -n $BASH_VERSION ]]; then
    read -e "$@"
  elif [[ -n $ZSH_VERSION ]]; then
    vared -e "$@"
  else
    read "$@"
  fi
}

# APIs

_get_env() {
  local shell_name="${SHELL##*/}"

  echo "{ \
    \"shell\": \"$shell_name\" \
  }"
}

_curl_server() {
  local url="$1"
  local data="$2"

  curl -s \
    -X POST "${CHAT_TERMINAL_SERVER_URL}${url}" \
    -H "Content-Type: application/json" \
    -d "$data"
}

_init_conversation() {
  local data="{"
  if [[ -n "$CHAT_TERMINAL_ENDPOINT" ]]; then
    data+="\"endpoint\": \"$CHAT_TERMINAL_ENDPOINT\""
  fi
  data+="}"

  _curl_server "/chat/${_conversation_id}/init" "$data"
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
  local executed="$1"
  local observation="$2"
  local data

  observation=$(echo -ne "$observation" | python3 -c "import sys, json; print(json.dumps(sys.stdin.read()))")

  data="{ \
    \"command_executed\": $executed, \
    \"message\": $(echo -E "$observation"), \
    \"env\": $(_get_env)
  }"

  _curl_server "/chat/${_conversation_id}/query_reply" "$data"
}

# core functions

_confirm_command_execution() {
  echo -n $_MESSAGE_PREFIX "Execute the command? (y/[N]) "
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
  local line

  result=$(_query_command "$query")
  _status=$(echo -E "$result" | jq -r ".status")
  if [[ $_status != "success" ]]; then
    echo $_MESSAGE_PREFIX "Failed to generate command: $result"
    return 1
  fi

  thinking=$(echo -E "$result" | jq -r '.payload.thinking')
  _command=$(echo -E "$result" | jq -r '.payload.command')
  _print_response "Thought" "$thinking"
  _print_response "Command" "$_command"

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

  if $exec_command; then
    # ensure execution in current shell
    # use /dev/shm to avoid wearing the disk
    memfile=$(mktemp /dev/shm/chat-terminal-XXXXXX)
    if [[ -n $BASH_VERSION ]]; then
      { tail -n +1 -f $memfile & } 2>/dev/null
    elif [[ -n $ZSH_VERSION ]]; then
      (tail -n +1 -f $memfile ) &!
    else
      (tail -n +1 -f $memfile) &
    fi
    display_job=$!
    eval "$_command" 1>$memfile 2>&1
    sleep 1  # wait for tail to display all contents
    if [[ -n $BASH_VERSION ]]; then
      { kill $display_job && wait $display_job; } 2>/dev/null
    elif [[ -n $ZSH_VERSION ]]; then
      kill $display_job
    fi
    observation=$(cat $memfile)
    rm $memfile
    echo $_MESSAGE_PREFIX "Command finished"
  else
    _advance_read -p "Clarification: " observation
  fi

  result=$(_query_reply "$exec_command" "$observation")
  _status=$(echo -E "$result" | jq -r ".status")
  if [[ $_status != "success" ]]; then
    echo $_MESSAGE_PREFIX "Failed to generate reply: $result"
    return 1
  fi

  reply=$(echo -E "$result" | jq -r '.payload.reply')
  _print_response "Reply" "$reply"
}

chat-terminal-reset() {
  _conversation_id=
}

chat-terminal() {
  local query="$@"
  local result
  local _status

  if [[ -z "$_conversation_id" ]]; then
    # generate a UUID as conversation ID
    _conversation_id=$(uuidgen)
    result=$(_init_conversation)
    _status=$(echo -E "$result" | jq -r ".status")
    if [[ $_status != "success" ]]; then
      if [[ -z "$result" ]]; then
        result="server not online"
      fi
      echo $_MESSAGE_PREFIX "Failed to initialize converstaion: ${result}"
      _conversation_id=
      return 1
    fi
    echo $_MESSAGE_PREFIX "Initialized conversation: $_conversation_id"
    if [[ -n "$CHAT_TERMINAL_ENDPOINT" ]]; then
      echo $_MESSAGE_PREFIX "Using endpoint: $CHAT_TERMINAL_ENDPOINT"
    fi
  fi

  if [[ -n "$query" ]]; then
    _chat_once "$query"
  else
    while true; do
      _advance_read -p "> " query
      if [[ $? -eq 1 ]]; then
        # EOF
        break
      fi
      if [[ -n $query ]]; then
        _chat_once "$query"
      fi
    done
  fi
}
