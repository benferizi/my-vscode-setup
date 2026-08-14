#!/usr/bin/env bash
set -euo pipefail

CODE_HOME="${CODE_HOME:-$HOME/code}"

category="${1:-}"
name="${2:-}"

if [ -z "$category" ] || [ -z "$name" ]; then
  echo "Usage: ./scripts/make-project.sh <category> <project-name>"
  echo "Example: ./scripts/make-project.sh personal my-new-app"
  exit 1
fi

case "$category" in
  work|personal|learning|experiments|archive) ;;
  *) echo "Invalid category"; exit 1 ;;
esac

target="$CODE_HOME/$category/$name"

if [ -e "$target" ]; then
  echo "Already exists: $target"
  exit 1
fi

mkdir -p "$target"
cd "$target"
git init

"$(dirname "$0")/repo-kit.sh" || true

echo "# $name" > README.md
git add .
git commit -m "initial project setup" || true

echo "Created project: $target"
