ARG BASE_IMAGE=python:3.10
FROM ${BASE_IMAGE}

ARG REPO_ARCHIVE=.

WORKDIR /ask-terminal

ADD ${REPO_ARCHIVE} ./

RUN make install-server

ENTRYPOINT ["ask-terminal-server"]