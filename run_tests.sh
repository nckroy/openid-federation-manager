#!/bin/bash
# Copyright (c) 2025 Internet2
# Licensed under the Apache License, Version 2.0 - see LICENSE file for details

# Test runner script for OpenID Federation Manager

set -e

echo "================================"
echo "OpenID Federation Manager Tests"
echo "================================"
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Parse arguments
TEST_TYPE="${1:-all}"
VERBOSE="${2:--v}"

# Function to run tests
run_tests() {
    local marker="$1"
    local description="$2"
    
    echo -e "${YELLOW}Running $description...${NC}"
    if [ "$marker" == "all" ]; then
        python3 -m pytest tests/ $VERBOSE
    else
        python3 -m pytest tests/ $VERBOSE -m "$marker"
    fi
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ $description passed${NC}"
        return 0
    else
        echo -e "${RED}✗ $description failed${NC}"
        return 1
    fi
}

# Main test execution
case "$TEST_TYPE" in
    unit)
        run_tests "unit" "Unit Tests"
        ;;
    integration)
        run_tests "integration" "Integration Tests"
        ;;
    e2e)
        run_tests "e2e" "End-to-End Tests"
        ;;
    smoke)
        run_tests "smoke" "Smoke Tests"
        ;;
    backend)
        echo -e "${YELLOW}Running Backend Tests...${NC}"
        python3 -m pytest tests/backend/ $VERBOSE
        ;;
    all)
        echo "Running all tests..."
        run_tests "all" "All Tests"
        ;;
    *)
        echo "Usage: $0 {unit|integration|e2e|smoke|backend|all} [-v|-vv]"
        echo ""
        echo "Examples:"
        echo "  $0 unit          # Run unit tests only"
        echo "  $0 backend -vv   # Run backend tests with extra verbosity"
        echo "  $0 all           # Run all tests"
        exit 1
        ;;
esac

echo ""
echo -e "${GREEN}================================${NC}"
echo -e "${GREEN}Test run complete!${NC}"
echo -e "${GREEN}================================${NC}"
