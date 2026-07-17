SCRIPT = a_maze_ing.py

all: run clean

clean:
	@rm -rf .mypy_cache __pycache__ tempCodeRunnerFile.py

install:
	@pip install mlx-2.2-py3-none-any.whl
	@pip install mazegen-1.0.0-py3-none-any.whl
	@pip install flake8
	@pip install mypy

run:
	@python3 $(SCRIPT)

debug:
	@python -m pdb $(SCRIPT)

lint:
	@flake8 . && mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

lint-strict:
	@flake8 . && mypy . --strict

env:
	@python -m venv .env
