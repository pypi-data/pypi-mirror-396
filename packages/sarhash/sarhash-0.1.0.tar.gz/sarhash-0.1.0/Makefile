.PHONY: build test run clean

build:
	maturin develop

test: build
	pytest

run: build
	python tests/basic_usage.py

clean:
	cargo clean
	rm -rf .pytest_cache
	rm -rf python/sarhash/__pycache__
	rm -rf tests/__pycache__
	rm -rf target
