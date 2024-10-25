ARG BASE_IMAGE=python:3.10
FROM ${BASE_IMAGE}

ARG REPO_ARCHIVE=.

WORKDIR /chat-terminal

ADD ${REPO_ARCHIVE} ./

RUN apt-get update
RUN apt-get install -y jq uuid-runtime

RUN make install-client install-shell-rc

ENV CLIENT_ENV=

CMD ["bash", "-ic", "export ${CLIENT_ENV}; chat-terminal"]
