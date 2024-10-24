ARG BASE_IMAGE=python:3.10
FROM ${BASE_IMAGE}

ARG REPO_ARCHIVE=.

WORKDIR /chat-terminal

ADD ${REPO_ARCHIVE} ./
RUN mkdir -p ./locals
COPY locals/chat_terminal.yaml ./locals/

RUN apt-get update
RUN apt-get install -y jq uuid-runtime

RUN make setup

ENTRYPOINT ["chat-terminal-server"]