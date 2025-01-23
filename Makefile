PYTHON := python
PYLINT := pylint

VENV=.venv
DOCS_DIR := docs/sphinx
TMP_PYLINT_FILE=.pylint_report.json

HTML_DIR := $(DOCS_DIR)/build/html
VENV_ACTIVATE := source ${VENV}/bin/activate

help: URL := github.com/drdv/makefile-doc/releases/latest/download/makefile-doc.awk
help: DIR := $(HOME)/.local/share/makefile-doc
help: SCR := $(DIR)/makefile-doc.awk
help: ## show this help
	@test -f $(SCR) || wget -q -P $(DIR) $(URL)
	@awk -f $(SCR) $(MAKEFILE_LIST)

##@
##@----- Code quality -----
##@

docs: rm-docs lint test ## Generate sphinx docs
	cd $(DOCS_DIR) && make html
lint: lint-run lint-copy-to-docs ## Lint code
test: test-run test-copy-to-docs ## Run unit tests

lint-run:
	-@${PYLINT} pylint_report pylint_report/utest/* > ${TMP_PYLINT_FILE} || exit 0
	-@pylint_report ${TMP_PYLINT_FILE} -o .pylint_report.html

lint-copy-to-docs:
	mkdir -p $(HTML_DIR)
	rm -rf $(HTML_DIR)/.pylint_report.html
	mv -f .pylint_report.html $(HTML_DIR)
	rm ${TMP_PYLINT_FILE}

test-run:
	coverage run -m pytest -v
	coverage html

test-copy-to-docs:
	mkdir -p $(HTML_DIR)
	rm -rf $(HTML_DIR)/.htmlcov
	rm -rf $(HTML_DIR)/.utest_reports
	mv -f .htmlcov $(HTML_DIR)
	mv -f .utest_reports $(HTML_DIR)
	rm -rf .coverage .pytest_cache

## Execute pre-commit on all files
.PHONY: pre-commit
pre-commit:
	@pre-commit run -a

$(VENV):
	${PYTHON} -m venv $@ && $(VENV_ACTIVATE) && pip install --upgrade pip

##@
##@----- Installation and packaging -----
##@

## Editable install in venv
.PHONY: install
install: | $(VENV)
	$(VENV_ACTIVATE) && pip install -e .[dev]

## Build package
.PHONY: package
package: | $(VENV)
	$(VENV_ACTIVATE) && pip install build && ${PYTHON} -m build

##! Publish on PyPi
.PHONY: publish
publish: package
	$(VENV_ACTIVATE) && pip install twine && twine upload dist/* --verbose

##@
##@----- Other -----
##@

## Open sphinx documentation
.PHONY: open
open:
	xdg-open ${HTML_DIR}/index.html

##! Delete generated docs
rm-docs:
	@rm -rf $(DOCS_DIR)/source/.autosummary
	@rm -rf $(DOCS_DIR)/build

##! Clean all
.PHONY: clean
clean: rm-docs
	rm -rf pylint_report.egg-info
	rm -rf pylint_report/_version.py
	find . -name "__pycache__" | xargs rm -rf
	rm -rf .venv
