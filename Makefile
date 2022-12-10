PYTHON=python
VENV_NAME=.venv
PYLINT=pylint
HTML_DIR=docs/sphinx/build/html

_BLUE=\033[34m
_END=\033[0m

# canned recipe
define show =
echo -e "${_BLUE}============================================================${_END}" && \
echo -e "${_BLUE}[$@] ${1}${_END}" && \
echo -e "${_BLUE}============================================================${_END}"
endef

.PHONY: help
help: ## Show this help
	@egrep -h '\s##\s' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "${_BLUE}%-15s${_END} %s\n", $$1, $$2}'

docs: rm-docs lint test ## Generate sphinx docs
	cd docs/sphinx && make html

lint: lint-run lint-copy-to-docs ## Lint code
test: test-run test-copy-to-docs ## Run unit tests

rm-docs: ## Delete generated docs
	@rm -rf docs/sphinx/source/.autosummary
	@rm -rf docs/sphinx/build

lint-run:
	-@${PYLINT} pylint_report pylint_report/utest/* > .pylint_report.json || exit 0
	-@pylint_report .pylint_report.json -o .pylint_report.html

lint-copy-to-docs:
	mkdir -p $(HTML_DIR)
	rm -rf $(HTML_DIR)/.pylint_report.html
	mv -f .pylint_report.html $(HTML_DIR)
	rm .pylint_report.json

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

.PHONY: open
open: ## Open sphinx documentation
	brave-browser ${HTML_DIR}/index.html

pre-commit: ## Execute pre-commit on all files
	@pre-commit run -a

setup-venv: ## Setup empty venv
	${PYTHON} -m venv ${VENV_NAME} && \
	. ${VENV_NAME}/bin/activate && \
	pip install --upgrade pip

install-local: setup-venv ## Editable install in venv
	. ${VENV_NAME}/bin/activate && pip install -e .[dev]

dist-local: setup-venv ## Build package
	. ${VENV_NAME}/bin/activate && pip install build && ${PYTHON} -m build

publish: ## Publish to PyPi
	pip install build && ${PYTHON} -m build && pip install twine && \
	twine upload dist/* --verbose
