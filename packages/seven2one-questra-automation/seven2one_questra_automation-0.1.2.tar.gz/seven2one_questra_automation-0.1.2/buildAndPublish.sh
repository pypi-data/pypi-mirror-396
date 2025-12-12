#!/bin/bash
set -e

if [ -z "$1" ]; then
    echo "Error: Token required"
    echo "Usage: $0 <token> [--pypi]"
    exit 1
fi

TOKEN="$1"

rm -rf dist/
uv sync
uv build

if [ "$2" == "--pypi" ]; then
    echo "Publishing to PyPI..."
    uv publish --token "$TOKEN"
else
    echo "Publishing to Test-PyPI..."
    uv publish --publish-url https://test.pypi.org/legacy/ --token "$TOKEN"
fi