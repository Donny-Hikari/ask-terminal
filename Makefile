
CONFIGS_DIR = $(HOME)/.config/chat-terminal

setup: install install-configs

install:
	pip install .

install-configs: make-configs-dir copy-prompts copy-configs copy-credentials

make-configs-dir:
	mkdir -p $(CONFIGS_DIR)

copy-prompts:
	cp -ivr prompts $(CONFIGS_DIR)

copy-configs:
	cp -ivr configs $(CONFIGS_DIR)

copy-credentials:
	[ -e credentials ] && cp -ivr credentials $(CONFIGS_DIR) || true

uninstall: delete-all-configs
	pip uninstall -y chat-terminal

delete-all-configs:
	rm -rf $(CONFIGS_DIR)

clean: uninstall
	rm -rdf build dist chat_terminal.egg-info
