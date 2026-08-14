#!/usr/bin/env bash
set -euo pipefail

CODE_HOME="${CODE_HOME:-$HOME/code}"

echo "$CODE_HOME/"
for category in work personal learning experiments archive; do
  echo "  $category/"
  if [ -d "$CODE_HOME/$category" ]; then
    find "$CODE_HOME/$category" -mindepth 1 -maxdepth 1 -type d 2>/dev/null | sort | while IFS= read -r dir; do
      if [ -d "$dir/.git" ]; then
        echo "    $(basename "$dir")/ [git]"
      else
        echo "    $(basename "$dir")/"
      fi
    done
  fi
done
