#!/usr/bin/env bash
set -euo pipefail

CODE_HOME="${CODE_HOME:-$HOME/code}"
REPOS_FILE="$CODE_HOME/repos.txt"
CATEGORIES="work personal learning experiments archive"

usage() {
  cat <<EOF
Repo helper

Usage:
  ./scripts/repo.sh add <category> <repo-url> [folder-name]
  ./scripts/repo.sh list

Examples:
  ./scripts/repo.sh add personal https://github.com/user/project.git
  ./scripts/repo.sh add work https://github.com/company/api.git backend-api
EOF
}

repo_name_from_url() {
  name="$(basename "${1%/}")"
  name="${name%.git}"
  echo "$name"
}

valid_category() {
  case " $CATEGORIES " in
    *" $1 "*) return 0 ;;
    *) return 1 ;;
  esac
}

mkdir -p "$CODE_HOME"/{work,personal,learning,experiments,archive}
touch "$REPOS_FILE"

cmd="${1:-help}"

case "$cmd" in
  add)
    category="${2:-}"
    url="${3:-}"
    folder="${4:-}"

    [ -n "$category" ] || { echo "Missing category"; exit 1; }
    [ -n "$url" ] || { echo "Missing repo URL"; exit 1; }

    valid_category "$category" || { echo "Invalid category: $category"; exit 1; }

    if [ -z "$folder" ]; then
      folder="$(repo_name_from_url "$url")"
    fi

    target="$CODE_HOME/$category/$folder"

    if [ -d "$target/.git" ]; then
      echo "Already cloned: $target"
    elif [ -e "$target" ]; then
      echo "Target exists but is not a git repo: $target"
      exit 1
    else
      git clone "$url" "$target"
    fi

    line="$category|$url|$folder"
    if ! grep -Fq "$line" "$REPOS_FILE"; then
      echo "$line" >> "$REPOS_FILE"
    fi

    echo "Done: $target"
    ;;
  list)
    cat "$REPOS_FILE"
    ;;
  *)
    usage
    ;;
esac
