
# constant
PHRASE ?= ">>"
DOCKER_PHRASE ?= "@>"

# variables
COPY_OVERWRITE ?= false
COPY_FLAG ?= -vr
SHELL_CLIENT_DEST ?= $(HOME)/.ask-terminal/ask-terminal.sh
SHELL_RCFILE ?= $(HOME)/.bashrc
CONFIGS_DIR ?= $(HOME)/.config/ask-terminal
CONFIG_FILE_SOURCE ?= configs/ask_terminal.yaml


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

install-scripts: shell-client/ask-terminal.sh
	@echo $(PHRASE) "Installing scripts..."
	mkdir -p "$$(dirname $(SHELL_CLIENT_DEST))"
	cp $(COPY_FLAG) shell-client/ask-terminal.sh $(SHELL_CLIENT_DEST)

install-shell-rc:
	@echo $(PHRASE) "Appending to shell runtime configuration..."
	echo >> $(SHELL_RCFILE)
	echo "# added by ask-terminal" >> $(SHELL_RCFILE)
	echo "source \"$(SHELL_CLIENT_DEST)\"" >> $(SHELL_RCFILE)
	echo "alias ask=ask-terminal" >> $(SHELL_RCFILE)

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

uninstall:
	pip uninstall -y ask-terminal

delete-all-configs:
	rm -rf "$(CONFIGS_DIR)"

delete-all-scripts:
	rm -f $(SHELL_CLIENT_DEST)
	client_dir=$$(dirname $(SHELL_CLIENT_DEST)) && \
		[ -d $${client_dir} ] && \
		! ( find "$${client_dir}" -mindepth 1 | grep -qE '.' ) && \
		rm -df "$${client_dir}" && \
		echo "Empty shell client directory \"$${client_dir}\" removed" \
		|| true

clean:
	rm -rdf build dist ask_terminal.egg-info

purge: uninstall delete-all-configs delete-all-scripts

# advance targets

.PHONY: install-service

install-service:
	cp $(COPY_FLAG) services/ask-terminal-server.service $(HOME)/.config/systemd/user/
	sed -i 's|# Environment=PATH=$$PATH|Environment=PATH=$(PATH)|' $(HOME)/.config/systemd/user/ask-terminal-server.service

.PHONY: build

build:
	python -m build


# docker targets

DOCKER_IMAGE_SOURCE_BRANCH ?=  # empty means copying the whole current repo
DOCKER_BUILD_FLAGS ?=
DOCKER_SERVER_FLAGS ?= --net=host -d
DOCKER_CLIENT_FLAGS ?= --net=host --rm
SERVER_RESTART ?= always
SERVER_PORT ?= 16099
CLIENT_ENV ?=

DOCKER_SERVER_FILE ?= docker/server.dockerfile
DOCKER_CLIENT_FILE ?= docker/client.dockerfile
DOCKER_SERVER_IMAGE_NAME ?= ask-terminal-server
DOCKER_CLIENT_IMAGE_NAME ?= ask-terminal-client
DOCKER_SERVER_CONTAINER_NAME ?= ask-terminal-server
DOCKER_CLIENT_CONTAINER_NAME ?= ask-terminal-client

.PHONY: docker-build-image docker-setup docker-run-server docker-rm-server docker-run-client

docker-build-image:
	if [ -z "$(DOCKER_IMAGE_NAME)" ]; then \
		echo "Please specify DOCKER_IMAGE_NAME"; exit 1; \
	fi
	@echo $(DOCKER_PHRASE) "Building docker image..."
	docker image rm -f $(DOCKER_IMAGE_NAME) 2>/dev/null || true
ifneq ($(DOCKER_IMAGE_SOURCE_BRANCH),)
# support building from a git branch
	mkdir -p ./tmp
	tmp_git_archive=$$(mktemp ./tmp/ask-terminal-repo-archive-XXXXXX.tar.gz) &&	\
		git archive --format=tar.gz -o $$tmp_git_archive master && \
		docker build -t $(DOCKER_IMAGE_NAME) --build-arg REPO_ARCHIVE=$$tmp_git_archive $(DOCKER_BUILD_FLAGS) -f $(DOCKER_FILE) . && \
		rm $$tmp_git_archive
	rm -d ./tmp 2>/dev/null || true
else
# build from the current repo
	docker build -t $(DOCKER_IMAGE_NAME) $(DOCKER_BUILD_FLAGS) -f $(DOCKER_FILE) .
endif

docker-setup: docker-build-image
	@echo $(DOCKER_PHRASE) "Running setup in docker..."

docker-run-server: DOCKER_FILE = $(DOCKER_SERVER_FILE)
docker-run-server: DOCKER_IMAGE_NAME = $(DOCKER_SERVER_IMAGE_NAME)
docker-run-server: docker-rm-server docker-build-image
	@echo $(DOCKER_PHRASE) "Running server in docker..."
	docker run --name $(DOCKER_SERVER_CONTAINER_NAME) $(DOCKER_SERVER_FLAGS) --restart $(SERVER_RESTART) -p $(SERVER_PORT):$(SERVER_PORT) $(DOCKER_IMAGE_NAME) --host 0.0.0.0 --port $(SERVER_PORT)

docker-rm-server:
	if $$(docker ps -a -q --filter "name=$(DOCKER_SERVER_CONTAINER_NAME)" | grep -q .); then \
		echo $(DOCKER_PHRASE) "Removing old server container..."; \
		docker rm -f $(DOCKER_SERVER_CONTAINER_NAME) >/dev/null; \
	fi

docker-run-client: DOCKER_FILE = $(DOCKER_CLIENT_FILE)
docker-run-client: DOCKER_IMAGE_NAME = $(DOCKER_CLIENT_IMAGE_NAME)
docker-run-client: docker-build-image
	@echo $(DOCKER_PHRASE) "Running client in docker..."
	docker run --name $(DOCKER_CLIENT_CONTAINER_NAME) -it $(DOCKER_CLIENT_FLAGS) -e CLIENT_ENV="$(CLIENT_ENV)" $(DOCKER_IMAGE_NAME)
