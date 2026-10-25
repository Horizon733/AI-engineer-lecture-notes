#!/usr/bin/env bash
# Activate the shared prompt-tools venv (bash/zsh).
# Usage:  source ./activate.sh
HERE="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")" && pwd)"
# shellcheck disable=SC1091
source "$HERE/.venv/bin/activate"
echo "prompt-tools venv active -> $HERE/.venv"
