
COPY_OVERWRITE := false
CONFIGS_DIR := $(HOME)/.config/chat-terminal
COPY_FLAG := -vr
PHRASE := ">>"

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

install-scripts:
	@echo $(PHRASE) "Installing scripts..."
	cp $(COPY_FLAG) shell-client/chat-terminal.sh $(HOME)/.dsh/.dshrc.d/chat-terminal.dshrc

pre-install-configs:
	@echo $(PHRASE) "Installing config files..."

make-configs-dir:
	mkdir -p $(CONFIGS_DIR)

copy-prompts:
	cp $(COPY_FLAG) prompts $(CONFIGS_DIR)

copy-configs:
	cp $(COPY_FLAG) configs $(CONFIGS_DIR)

copy-credentials:
	[ -e credentials ] && cp $(COPY_FLAG) credentials $(CONFIGS_DIR) || true

uninstall: delete-all-configs delete-all-scripts
	pip uninstall -y chat-terminal

delete-all-configs:
	rm -rf $(CONFIGS_DIR)

delete-all-scripts:
	rm -f $(HOME)/.dsh/.dshrc.d/chat-terminal.dshrc

clean: uninstall
	rm -rdf build dist chat_terminal.egg-info
