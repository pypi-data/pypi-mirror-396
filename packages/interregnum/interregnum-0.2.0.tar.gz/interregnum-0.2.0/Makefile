# SPDX-FileCopyrightText: 2025 wmj <wmj.py@gmx.com>
#
# SPDX-License-Identifier: LGPL-3.0-or-later

PYTHON=python
SETUP=pyproject.toml
UPTOOL=twine

PROJECT=interregnum

VERSION := $(shell python -m setuptools_scm)
DIST_FILES := \
	dist/$(PROJECT)-$(VERSION)-py3-none-any.whl \
	dist/$(PROJECT)-$(VERSION).tar.gz

.PHONY: clean-version upload doc upload-doc

test: $(SETUP) tox.ini
	$(PYTHON) -m tox -r

local-test: $(SETUP) tox.ini
	$(PYTHON) -m tox -e "py310,twine,reuse,black"

local-test-rebuild: $(SETUP) tox.ini
	$(PYTHON) -m tox -r -e "py310,twine,reuse,black"

clean: clean-pyco clean-cache clean-pycache

clean-pyco:
	@-find . -name "*.py[co]" -type f -delete

clean-cache:
	@-find . -name ".cache" -type d -ls -exec rm -rv {} \;

clean-pycache:
	@-find . -name "__pycache__" -type d -ls -exec rm -rv {} \;

clean-dist:
	-(mkdir -p dist.old && mv dist/* dist.old/)

clean-version:
	-rm -fr build/
	-rm -fr $(PROJECT).egg-info/

bdist: $(SETUP) clean clean-version
	$(PYTHON) -m build

doc:
	(cd doc && make clean && make html)

dist: local-test-rebuild clean-version clean-dist bdist

dist/$(PROJECT)-$(VERSION)-py3-none-any.whl: bdist

dist/$(PROJECT)-$(VERSION).tar.gz: bdist

twine-check: $(DIST_FILES)
	$(UPTOOL) check --strict $(DIST_FILES)

upload: $(SETUP) local-test-rebuild twine-check $(DIST_FILES)
	$(UPTOOL) upload $(DIST_FILES)
