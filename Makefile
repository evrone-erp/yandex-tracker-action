format:
	black .
	isort .

lint:
	black --check .
	isort --check .
	flake8 --inline-quotes '"' --exclude=.venv
	pylint $(shell git ls-files '*.py')
	PYTHONPATH=/ mypy --namespace-packages --show-error-codes . --check-untyped-defs --ignore-missing-imports --show-traceback

dep-vulnerabilities:
	pip-audit
