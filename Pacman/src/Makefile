SCRIPT = pac-man.py

SHELL := /bin/bash

SRC = *.py src/pacman/*.py

all: env install run clean

clean:
	@rm -rf .mypy_cache __pycache__ tempCodeRunnerFile.py

run:
	@.env/bin/python3 $(SCRIPT)

install:
	@.env/bin/pip install mazegenerator-00001-py3-none-any.whl
	@.env/bin/pip install flake8
	@.env/bin/pip install mypy
	@.env/bin/pip install pygame
	@.env/bin/pip install build

debug:
	@.env/bin/python -m pdb $(SCRIPT)

lint:
	@flake8 $(SRC) && mypy $(SRC) --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

lint-strict:
	@flake8 $(SRC) && mypy $(SRC) --strict

env:
	@python -m venv .env

