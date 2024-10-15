
CONFIGS_DIR = $(HOME)/.config/chat-terminal

setup: install install-configs install-script

install:
	pip install .

install-configs: make-configs-dir copy-prompts copy-configs copy-credentials

install-script:
	cp -i shell-client/chat-terminal.sh $(HOME)/.dsh/.dshrc.d/chat-terminal.dshrc

make-configs-dir:
	mkdir -p $(CONFIGS_DIR)

copy-prompts:
	cp -ivr prompts $(CONFIGS_DIR)

copy-configs:
	cp -ivr configs $(CONFIGS_DIR)

copy-credentials:
	[ -e credentials ] && cp -ivr credentials $(CONFIGS_DIR) || true

uninstall: delete-all-configs delete-all-scripts
	pip uninstall -y chat-terminal

delete-all-configs:
	rm -rf $(CONFIGS_DIR)

delete-all-scripts:
	rm -f $(HOME)/.dsh/.dshrc.d/chat-terminal.dshrc

clean: uninstall
	rm -rdf build dist chat_terminal.egg-info
