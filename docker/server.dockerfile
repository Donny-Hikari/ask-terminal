ARG BASE_IMAGE=python:3.10
FROM ${BASE_IMAGE}

ARG REPO_ARCHIVE=.

WORKDIR /chat-terminal

ADD ${REPO_ARCHIVE} ./

RUN make install-server

ENTRYPOINT ["chat-terminal-server"]