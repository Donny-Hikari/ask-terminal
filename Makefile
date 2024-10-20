
# constant
PHRASE ?= ">>"
DOCKER_PHRASE ?= "@>"

# variables
COPY_OVERWRITE ?= false
COPY_FLAG ?= -vr
SHELL_CLIENT_DEST ?= $(HOME)/.chat-terminal/chat-terminal.sh
CONFIGS_DIR ?= $(HOME)/.config/chat-terminal
CONFIG_FILE_SOURCE ?= configs/chat_terminal.yaml


ifeq ($(COPY_OVERWRITE), false)
	COPY_FLAG += -i
endif

.SILENT:

.PHONY: setup purge clean
.PHONY: install-server install-client
.PHONY: install install-configs install-scripts pre-install-configs make-configs-dir
.PHONY: copy-prompts copy-configs copy-credentials
.PHONY: uninstall delete-all-configs delete-all-scripts

setup: install-server install-client

install-server: install install-configs

install-client: install-scripts

install:
	@echo $(PHRASE) "Installing python package..."
	pip install .

install-configs: pre-install-configs make-configs-dir copy-prompts copy-configs copy-credentials

install-scripts: shell-client/chat-terminal.sh
	@echo $(PHRASE) "Installing scripts..."
	mkdir -p "$$(dirname $(SHELL_CLIENT_DEST))"
	cp $(COPY_FLAG) shell-client/chat-terminal.sh $(SHELL_CLIENT_DEST)

pre-install-configs:
	@echo $(PHRASE) "Installing config files..."

make-configs-dir:
	mkdir -p $(CONFIGS_DIR)

copy-prompts: make-configs-dir
	cp $(COPY_FLAG) prompts $(CONFIGS_DIR)

copy-configs: make-configs-dir
	mkdir -p $(CONFIGS_DIR)/configs
	cp $(COPY_FLAG) $(CONFIG_FILE_SOURCE) $(CONFIGS_DIR)/configs/

copy-credentials: make-configs-dir
	[ -e credentials ] && cp $(COPY_FLAG) credentials $(CONFIGS_DIR) || true

uninstall: delete-all-configs delete-all-scripts
	pip uninstall -y chat-terminal

delete-all-configs:
	rm -rf $(CONFIGS_DIR)

delete-all-scripts:
	rm -f $(HOME)/.dsh/.dshrc.d/chat-terminal.dshrc

clean:
	rm -rdf build dist chat_terminal.egg-info

purge: uninstall clean

# advance targets

.PHONY: install-service

install-service:
	cp $(COPY_FLAG) services/chat-terminal-server.service $(HOME)/.config/systemd/user/
	sed -i 's|# Environment=PATH=$$PATH|Environment=PATH=$(PATH)|' $(HOME)/.config/systemd/user/chat-terminal-server.service

.PHONY: build

build:
	python -m build


# docker targets

DOCKER_IMAGE_SOURCE_BRANCH ?=  # empty means copying the whole current repo
DOCKER_FLAGS ?= --rm --net=host
SERVER_PORT ?= 16099
CLIENT_ENV ?=

.PHONY: docker-build-image docker-setup docker-run-server docker-run-client

docker-build-image:
	@echo $(DOCKER_PHRASE) "Building docker image..."
	docker image rm -f chat-terminal:latest 2>/dev/null || true
ifneq ($(DOCKER_IMAGE_SOURCE_BRANCH),)
# support building from a git branch
	mkdir -p ./tmp
	tmp_git_archive=$$(mktemp ./tmp/chat-terminal-repo-archive-XXXXXX.tar.gz) &&	\
		git archive --format=tar.gz -o $$tmp_git_archive master && \
		docker build -t chat-terminal --build-arg REPO_ARCHIVE=$$tmp_git_archive . && \
		rm $$tmp_git_archive
	rm -d ./tmp 2>/dev/null || true
else
# build from the current repo
	docker build -t chat-terminal .
endif

docker-setup: docker-build-image
	@echo $(DOCKER_PHRASE) "Running setup in docker..."

docker-run-server: docker-build-image
	@echo $(DOCKER_PHRASE) "Running server in docker..."
	docker run $(DOCKER_FLAGS) -p $(SERVER_PORT):${SERVER_PORT} chat-terminal --host 0.0.0.0 --port $(SERVER_PORT)

docker-run-client: docker-build-image
	@echo $(DOCKER_PHRASE) "Running client in docker..."
	docker run -it $(DOCKER_FLAGS) --entrypoint /bin/bash chat-terminal -c 'source ~/.chat-terminal/chat-terminal.sh && $(CLIENT_ENV) chat-terminal'
