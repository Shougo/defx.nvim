install:
	pip install --upgrade -r test/requirements.txt

install-user:
	pip install --user --upgrade -r test/requirements.txt

lint:
	vint --version
	vint plugin
	vint autoload
	flake8 --version
	flake8 rplugin
	mypy --version
	mypy --ignore-missing-imports --follow-imports=skip --strict rplugin/python3/defx

test:
	pytest --version
	pytest

.PHONY: install lint test
