NAME := vigirrd
all: build

install:
	$(PYTHON) setup.py install --single-version-externally-managed --root=$(DESTDIR) --record=INSTALLED_FILES
	mkdir -p $(DESTDIR)$(HTTPD_DIR)
	ln -f -s $(SYSCONFDIR)/vigilo/$(NAME)/$(NAME).conf $(DESTDIR)$(HTTPD_DIR)/
	echo $(HTTPD_DIR)/$(NAME).conf >> INSTALLED_FILES
	mkdir -p $(DESTDIR)/var/log/vigilo/$(NAME)

include buildenv/Makefile.common

MODULE := $(NAME)
CODEPATH := $(NAME)

lint: lint_pylint
tests: tests_nose
clean: clean_python
	rm -rf data/img
