#!/usr/bin/env bash
set -euo pipefail

root="$(git rev-parse --show-toplevel 2>/dev/null || true)"
[ -n "$root" ] || { echo "Run this inside a Git repo."; exit 1; }

cd "$root"

create() {
  file="$1"
  content="$2"

  if [ -e "$file" ]; then
    echo "Exists, skipped: $file"
  else
    mkdir -p "$(dirname "$file")"
    printf "%s\n" "$content" > "$file"
    echo "Created: $file"
  fi
}

create ".editorconfig" 'root = true

[*]
charset = utf-8
end_of_line = lf
insert_final_newline = true
trim_trailing_whitespace = true
indent_style = space
indent_size = 2

[*.py]
indent_size = 4
'

create ".gitattributes" '* text=auto eol=lf
*.sh text eol=lf
*.md text eol=lf
*.png binary
*.jpg binary
*.jpeg binary
*.gif binary
*.pdf binary
'

create ".gitignore" '# secrets
.env
.env.*
!.env.example

# OS
.DS_Store
Thumbs.db

# logs
*.log

# dependencies
node_modules/
vendor/

# Python
.venv/
venv/
__pycache__/
*.pyc

# builds
dist/
build/
coverage/
.cache/
'

create ".env.example" '# Copy to .env and fill locally.
APP_ENV=development
'

create ".github/PULL_REQUEST_TEMPLATE.md" '## What changed?

-

## Why?

-

## Checklist

- [ ] Tested
- [ ] Checked for secrets
- [ ] Updated docs if needed
'

create ".github/ISSUE_TEMPLATE/bug_report.md" '---
name: Bug report
about: Report a problem
title: "[Bug]: "
labels: bug
---

## Problem

## Steps to reproduce

## Expected behavior
'

create ".github/ISSUE_TEMPLATE/feature_request.md" '---
name: Feature request
about: Suggest an improvement
title: "[Feature]: "
labels: enhancement
---

## Goal

## Why it matters

## Suggested solution
'

echo "Repo kit installed."
