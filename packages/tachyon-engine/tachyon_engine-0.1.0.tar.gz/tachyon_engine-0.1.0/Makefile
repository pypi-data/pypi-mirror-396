.PHONY: help build develop test test-rust test-python bench clean install

help:
	@echo "Tachyon Engine - Development Commands"
	@echo ""
	@echo "  make build        Build release version"
	@echo "  make develop      Build development version and install"
	@echo "  make test         Run all tests"
	@echo "  make test-rust    Run Rust tests"
	@echo "  make test-python  Run Python tests"
	@echo "  make bench        Run benchmarks"
	@echo "  make clean        Clean build artifacts"
	@echo "  make install      Install in current environment"

build:
	maturin build --release

develop:
	maturin develop

test: test-rust test-python

test-rust:
	cargo test

test-python:
	pytest tests/ -v

bench:
	cargo bench
	python benchmarks/benchmark_vs_starlette.py

clean:
	cargo clean
	rm -rf target/
	rm -rf dist/
	rm -rf *.egg-info
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

install:
	maturin develop --release

