
# constant
PHRASE ?= ">>"

# variables
COPY_OVERWRITE ?= false
COPY_FLAG ?= -vr
SHELL_CLIENT_DIR ?= $(HOME)/.chat-terminal
CONFIGS_DIR ?= $(HOME)/.config/chat-terminal
CONFIG_FILE_SOURCE ?= configs/chat_terminal.yaml
DOCKER_IMAGE_SOURCE_BRANCH ?=  # empty means copying the whole current repo

ifeq ($(COPY_OVERWRITE), false)
	COPY_FLAG += -i
endif

.SILENT:

.PHONY: setup clean
.PHONY: install install-configs install-scripts make-configs-dir
.PHONY: copy-prompts copy-configs copy-credentials
.PHONY: uninstall delete-all-configs delete-all-scripts

setup: install install-configs install-scripts

install:
	@echo $(PHRASE) "Installing python package..."
	pip install .

install-configs: pre-install-configs make-configs-dir copy-prompts copy-configs copy-credentials

install-scripts: shell-client/chat-terminal.sh
	@echo $(PHRASE) "Installing scripts..."
	mkdir -p $(SHELL_CLIENT_DIR)
	cp $(COPY_FLAG) shell-client/chat-terminal.sh $(SHELL_CLIENT_DIR)/chat-terminal.dshrc

pre-install-configs:
	@echo $(PHRASE) "Installing config files..."

make-configs-dir:
	mkdir -p $(CONFIGS_DIR)

copy-prompts:
	cp $(COPY_FLAG) prompts $(CONFIGS_DIR)

copy-configs:
	mkdir -p $(CONFIGS_DIR)/configs
	cp $(COPY_FLAG) $(CONFIG_FILE_SOURCE) $(CONFIGS_DIR)/configs/

copy-credentials:
	[ -e credentials ] && cp $(COPY_FLAG) credentials $(CONFIGS_DIR) || true

build:
	python -m build

uninstall: delete-all-configs delete-all-scripts
	pip uninstall -y chat-terminal

delete-all-configs:
	rm -rf $(CONFIGS_DIR)

delete-all-scripts:
	rm -f $(HOME)/.dsh/.dshrc.d/chat-terminal.dshrc

clean:
	rm -rdf build dist chat_terminal.egg-info

purge: uninstall clean

install-service:
	cp $(COPY_FLAG) services/chat-terminal-server.service $(HOME)/.config/systemd/user/
	sed -i 's|# Environment=PATH=$$PATH|Environment=PATH=$(PATH)|' $(HOME)/.config/systemd/user/chat-terminal-server.service

docker-build-image:
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
	docker run --rm chat-terminal
