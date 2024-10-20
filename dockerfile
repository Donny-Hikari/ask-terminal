FROM ubuntu:20.04
FROM python:3.10

ARG REPO_ARCHIVE=.

WORKDIR /chat-terminal

ADD ${REPO_ARCHIVE} ./
RUN mkdir -p ./locals
COPY locals/chat_terminal.yaml ./locals/

RUN apt-get update

CMD ["make", "setup"]