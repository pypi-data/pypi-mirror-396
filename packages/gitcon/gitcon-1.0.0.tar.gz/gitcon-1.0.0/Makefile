# ------------------------------------------------------------
# GitCon – Makefile (unittest-based)
# ------------------------------------------------------------

PYTHON      ?= python3
PIP         ?= $(PYTHON) -m pip
UNITTEST    ?= $(PYTHON) -m unittest
RUFF        ?= $(PYTHON) -m ruff

SRC_DIR     := src
TEST_DIR    := tests

# Ensure src/ is on PYTHONPATH
export PYTHONPATH := $(SRC_DIR)

.DEFAULT_GOAL := help

# ------------------------------------------------------------
# Targets
# ------------------------------------------------------------

help:
	@echo "Available targets:"
	@echo "  make install        Install package in editable mode"
	@echo "  make test           Run unit tests (unittest)"
	@echo "  make test-verbose   Run unit tests with verbose output"
	@echo "  make lint           Run ruff (if installed)"
	@echo "  make clean          Remove Python cache files"

install:
	$(PIP) install -e .

test:
	$(UNITTEST) discover -s $(TEST_DIR) -p 'test_*.py'

test-verbose:
	$(UNITTEST) discover -v -s $(TEST_DIR) -p 'test_*.py'

lint:
	@command -v ruff >/dev/null 2>&1 || { \
		echo "ruff not installed, skipping lint"; \
		exit 0; \
	}
	$(RUFF) check $(SRC_DIR) $(TEST_DIR)

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
