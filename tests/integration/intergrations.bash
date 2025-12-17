#!/bin/bash

# Integration test script for mdxcanvas
# Runs the processor on both the base and modifications test suites

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Test suites to run
TESTS=(
"base"
#"modifications"
)

# Configuration
COURSE_INFO="$SCRIPT_DIR/testing_course_info.json"

# Load environment variables
source ~/.env

echo "========================================"
echo "  MDX Canvas Integration Tests"
echo "========================================"
echo ""

# Counters
PASSED=0
FAILED=0

# Run each test suite
for test in "${TESTS[@]}"; do
    echo "Running test suite: $test"

    TEST_DIR="$SCRIPT_DIR/$test"
    COURSE_FILE="$TEST_DIR/course.canvas.md.xml.jinja"
    GLOBALS_FILE="$TEST_DIR/globals.yaml"

    cd "$PROJECT_ROOT"

    if python -m mdxcanvas.main \
        --course-info "$COURSE_INFO" \
        --global-args "$GLOBALS_FILE" \
        "$COURSE_FILE"; then
        echo "✓ $test passed"
        ((PASSED++))
    else
        echo "✗ $test failed"
        ((FAILED++))
    fi

    echo ""
done

# Summary
echo "========================================"
echo "  Summary"
echo "========================================"
echo "Passed: $PASSED"
echo "Failed: $FAILED"
echo ""

if [ $FAILED -gt 0 ]; then
    echo "Some tests failed!"
    exit 1
else
    echo "All tests passed!"
    exit 0
fi
