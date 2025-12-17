.PHONY: all build test clean check publish

all: build

build:
	@uv sync --reinstall-package cynn

test:
	@uv run pytest

wheel:
	@uv build --wheel

check:
	@uv run twine check dist/*

publish:
	@uv run twine upload dist/*

cmake:
	@mkdir -p build && cd build && cmake .. && cmake --build . --config Release

clean:
	@rm -rf build dist src/*.egg-info
	@rm -f *.so
