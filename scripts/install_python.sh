#!/usr/bin/env bash
set -euo pipefail
echo "Installing Python (attempting apt-get or Homebrew)..."
if command -v apt-get >/dev/null 2>&1; then
  sudo apt-get update && sudo apt-get install -y python3 python3-venv python3-pip
elif command -v brew >/dev/null 2>&1; then
  brew install python
else
  echo "Could not detect package manager. Please install Python 3.11+ from https://www.python.org/downloads/"
fi

echo "Done. Verify with: python3 --version"