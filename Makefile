NAME := vigirrd
all: build

install:
	$(PYTHON) setup.py install --single-version-externally-managed --root=$(DESTDIR) --record=INSTALLED_FILES
	mkdir -p $(DESTDIR)$(HTTPD_DIR)
	ln -f -s $(SYSCONFDIR)/vigilo/$(NAME)/$(NAME).conf $(DESTDIR)$(HTTPD_DIR)/
	echo $(HTTPD_DIR)/$(NAME).conf >> INSTALLED_FILES
	install -p -m 644 -D deployment/logrotate $(DESTDIR)$(SYSCONFDIR)/logrotate.d/$(NAME)
	echo $(SYSCONFDIR)/logrotate.d/$(NAME) >> INSTALLED_FILES
	mkdir -p /var/log/vigilo/$(NAME)

include buildenv/Makefile.common

MODULE := $(NAME)
CODEPATH := $(NAME)

lint: lint_pylint
tests: tests_nose
clean: clean_python
	rm -rf data/img
