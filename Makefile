.PHONY: install demo lint test artifacts package check

install:
	python -m pip install -e ".[live,dev]"

demo:
	intellicrawl demo

lint:
	ruff check .
	ruff format --check .

test:
	pytest

artifacts:
	python scripts/build_demo_artifacts.py
	git diff --exit-code -- examples

package:
	python -m pip wheel --no-deps --wheel-dir /tmp/intellicrawl-wheel .
	python -m pip check

check: lint test artifacts package
