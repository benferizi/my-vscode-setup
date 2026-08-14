#!/usr/bin/env bash
set -euo pipefail

echo "GitHub auth check"
echo "================="
echo

echo "Git identity:"
echo "  user.name:  $(git config --global user.name || echo 'not set')"
echo "  user.email: $(git config --global user.email || echo 'not set')"
echo

if command -v gh >/dev/null 2>&1; then
  echo "GitHub CLI:"
  gh auth status || true
else
  echo "GitHub CLI not installed."
fi

echo
echo "SSH keys:"
if [ -f "$HOME/.ssh/id_ed25519.pub" ] || [ -f "$HOME/.ssh/id_rsa.pub" ]; then
  echo "  SSH public key exists."
else
  echo "  No common SSH public key found."
fi
