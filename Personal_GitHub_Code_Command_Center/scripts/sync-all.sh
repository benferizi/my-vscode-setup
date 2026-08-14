#!/usr/bin/env bash
set -euo pipefail

CODE_HOME="${CODE_HOME:-$HOME/code}"

echo "Safe sync all repos"
echo "==================="
echo "Root: $CODE_HOME"
echo

find "$CODE_HOME" -type d -name .git -prune 2>/dev/null | while IFS= read -r gitdir; do
  repo="$(dirname "$gitdir")"
  echo "--- $repo"

  if [ -n "$(git -C "$repo" status --porcelain)" ]; then
    echo "Local changes found. Skipping pull."
    git -C "$repo" status --short
  else
    branch="$(git -C "$repo" branch --show-current || true)"

    if [ -z "$branch" ]; then
      echo "Detached HEAD. Skipping."
    elif git -C "$repo" rev-parse --abbrev-ref --symbolic-full-name "@{u}" >/dev/null 2>&1; then
      git -C "$repo" pull --ff-only || echo "Pull failed. Fix manually."
    else
      echo "No upstream tracking branch. Skipping."
    fi
  fi

  echo
done
