.PHONY: setup-dev ruff isort isort-fix pyright lint build clean

NAME = ytrssil

setup-dev:
	uv sync

ruff:
	ruff check

isort:
	@uv run isort -c .

isort-fix:
	@uv run isort .

pyright:
	@uv run basedpyright

lint: ruff isort pyright

build:
	uv build

clean:
	rm -rf $(CURDIR)/build
	rm -rf $(CURDIR)/dist
	rm -rf $(CURDIR)/$(NAME).egg-info

publish:
	@git checkout $(shell git tag | sort -V | tail -n1)
	@$(MAKE) clean
	@$(MAKE) build
	@uv publish
	@$(MAKE) clean
	@git switch main
