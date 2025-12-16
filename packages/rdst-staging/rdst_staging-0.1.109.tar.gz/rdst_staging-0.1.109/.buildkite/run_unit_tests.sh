#!/bin/bash
set -euo pipefail

# RDST Test Runner Script
# Runs unit tests and generates JUnit XML reports

echo "=== Setting up Python environment ==="
cd "$(dirname "$0")/.."  # Navigate to rdst directory

python3 -m venv venv
source venv/bin/activate

echo "=== Installing test dependencies ==="
pip install --upgrade pip
pip install -r tests/requirements.txt

echo "=== Creating test results directory ==="
mkdir -p test-results

echo "=== Running unit tests ==="
pytest tests/unit -v --tb=short --junitxml=test-results/unit-tests.xml

# Future: Add integration tests here
# echo "=== Running integration tests ==="
# pytest tests/integration -v --tb=short --junitxml=test-results/integration-tests.xml

echo "=== Test run complete ==="
