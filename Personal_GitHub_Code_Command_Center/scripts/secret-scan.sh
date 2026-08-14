#!/usr/bin/env bash
set -euo pipefail

SCAN_ROOT="${1:-$(pwd)}"

echo "Secret scan"
echo "==========="
echo "Scanning: $SCAN_ROOT"
echo

pattern='AKIA[0-9A-Z]{16}|ghp_[A-Za-z0-9_]{30,}|github_pat_[A-Za-z0-9_]{40,}|BEGIN (RSA|OPENSSH|DSA|EC) PRIVATE KEY|api[_-]?key[[:space:]]*=|password[[:space:]]*=|secret[[:space:]]*=|token[[:space:]]*='

if grep -RInE \
  --exclude-dir=.git \
  --exclude-dir=node_modules \
  --exclude-dir=.venv \
  --exclude-dir=venv \
  --exclude-dir=dist \
  --exclude-dir=build \
  --exclude-dir=coverage \
  "$pattern" "$SCAN_ROOT"; then
  echo
  echo "Possible secrets found. Review before committing."
  exit 1
else
  echo "No obvious secrets found."
fi
