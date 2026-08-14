#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CODE_HOME="${CODE_HOME:-$HOME/code}"

echo "Personal GitHub Workspace Doctor"
echo "================================"
echo "Command Center: $ROOT"
echo "Code home:      $CODE_HOME"
echo

echo "1. Tools"
if command -v git >/dev/null 2>&1; then
  echo "  git: OK - $(git --version)"
else
  echo "  git: MISSING"
fi

if command -v gh >/dev/null 2>&1; then
  echo "  gh:  OK - $(gh --version | head -n 1)"
else
  echo "  gh:  not installed"
fi

if command -v code >/dev/null 2>&1; then
  echo "  code: OK"
else
  echo "  code: not in PATH"
fi

echo
echo "2. Git identity"
echo "  user.name:  $(git config --global user.name || echo 'not set')"
echo "  user.email: $(git config --global user.email || echo 'not set')"

echo
echo "3. Workspace folders"
for category in work personal learning experiments archive; do
  if [ -d "$CODE_HOME/$category" ]; then
    echo "  OK: $CODE_HOME/$category"
  else
    echo "  Missing: $CODE_HOME/$category"
  fi
done

echo
echo "4. Repo count"
count="$(find "$CODE_HOME" -type d -name .git -prune 2>/dev/null | wc -l | tr -d ' ')"
echo "  repos found: $count"

echo
echo "5. Dirty repos"
found_dirty=0
while IFS= read -r gitdir; do
  repo="$(dirname "$gitdir")"
  if [ -n "$(git -C "$repo" status --porcelain)" ]; then
    found_dirty=1
    echo "  Dirty: $repo"
    git -C "$repo" status --short
  fi
done < <(find "$CODE_HOME" -type d -name .git -prune 2>/dev/null)

if [ "$found_dirty" = "0" ]; then
  echo "  none"
fi

echo
echo "6. Nested repo check"
"$ROOT/scripts/find-nested-repos.sh"

echo
echo "Doctor finished."
