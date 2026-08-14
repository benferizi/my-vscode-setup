#!/usr/bin/env bash
set -euo pipefail

CODE_HOME="${CODE_HOME:-$HOME/code}"

found=0

while IFS= read -r gitdir; do
  repo="$(dirname "$gitdir")"
  parent="$(dirname "$repo")"

  while [ "$parent" != "$CODE_HOME" ] && [ "$parent" != "/" ] && [ -n "$parent" ]; do
    if [ -d "$parent/.git" ]; then
      found=1
      echo "Nested repo found:"
      echo "  Parent: $parent"
      echo "  Nested: $repo"
      echo
      break
    fi
    parent="$(dirname "$parent")"
  done
done < <(find "$CODE_HOME" -type d -name .git -prune 2>/dev/null)

if [ "$found" = "0" ]; then
  echo "  none"
fi
