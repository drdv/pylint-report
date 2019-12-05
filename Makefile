PYTHON=python3
VENV_NAME=.venv

.PHONY: setup-venv
setup-venv:
	${PYTHON} -m venv ${VENV_NAME} && \
	. ${VENV_NAME}/bin/activate && \
	pip install --upgrade pip && \
	pip install -r .requirements.txt

.PHONY: lint
lint:
	-@pylint pylint_report | pylint_report/pylint_report.py > .pylint_report.html
