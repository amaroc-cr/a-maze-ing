VENV := venv
PYTHON := $(VENV)/bin/python3
PIP := $(VENV)/bin/pip

.PHONY: install run debug clean lint lint-strict build

install: $(VENV)/bin/activate

$(VENV)/bin/activate: requirements.txt pyproject.toml
	python3 -m venv $(VENV)
	$(PIP) install -r requirements.txt
	touch $(VENV)/bin/activate

build: install
	$(PYTHON) -m build
	cp dist/mazegen-*.whl dist/mazegen-*.tar.gz .

run: install
	python3 a_maze_ing.py config.txt

debug: install
	python3 -m pdb a_maze_ing.py config.txt

lint: install
	flake8 .
	mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

lint-strict:
	flake8 .
	mypy . --strict

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
	rm -rf dist build *.egg-info
