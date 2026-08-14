#!/usr/bin/env bash
set -euo pipefail

# github-master-toolkit.sh
# Command name after install: ghx
#
# Purpose:
#   A serious GitHub/Git workspace organizer:
#   - clean workspace folders
#   - repo cloning by category
#   - import old messy repos
#   - safe multi-repo sync
#   - repo status dashboard
#   - nested repo detection
#   - global Git aliases
#   - shell aliases
#   - global .gitignore
#   - hidden repo starter files
#   - pre-commit safety hook
#   - basic secret scan
#
# Works on:
#   macOS, Linux, Windows Git Bash

VERSION="1.0.0"

WORKSPACE="${WORKSPACE:-$HOME/code}"
REPOS_FILE="$WORKSPACE/repos.txt"
BIN_DIR="${BIN_DIR:-$HOME/.local/bin}"
INSTALL_NAME="ghx"

CATEGORIES=(
  "work"
  "personal"
  "learning"
  "experiments"
  "archive"
)

usage() {
  cat <<EOF
GitHub Master Toolkit v$VERSION

Usage:
  ./github-master-toolkit.sh <command>
  ghx <command>                         after install

Main commands:
  install                               full setup: workspace, ghx command, aliases, git config
  init                                  create clean workspace folders
  add <category> <repo-url> [folder]    clone repo into clean workspace and register it
  import <category> <repo-path> [name]  move an existing local repo into clean workspace
  clone-all                             clone everything listed in repos.txt
  sync                                  safely pull all clean repos
  status                                show status of all repos
  tree                                  show workspace tree
  list                                  list configured repos
  doctor                                full health check
  find-nested                           find repos accidentally cloned inside repos

Extras:
  git-defaults                          install global Git defaults and Git aliases
  shell-aliases                         install shell aliases into ~/.bashrc or ~/.zshrc
  ignore-global                         install global hidden .gitignore file
  kit                                   add hidden helper files to current repo
  hook                                  install safety pre-commit hook in current repo
  secret-scan                           basic scan for secrets in current repo
  auth                                  check GitHub auth tools and Git identity
  aliases                               print useful aliases
  help                                  show this help

Categories:
  ${CATEGORIES[*]}

Default workspace:
  $WORKSPACE

Repo list:
  $REPOS_FILE

Examples:
  ./github-master-toolkit.sh install
  ghx add personal https://github.com/user/project.git
  ghx add work https://github.com/company/api.git backend-api
  ghx import personal ~/Downloads/old-project
  ghx sync
  ghx doctor

Custom workspace:
  WORKSPACE=$HOME/dev ./github-master-toolkit.sh install
EOF
}

say() {
  printf '%s\n' "$*"
}

warn() {
  printf 'Warning: %s\n' "$*" >&2
}

die() {
  printf 'Error: %s\n' "$*" >&2
  exit 1
}

command_exists() {
  command -v "$1" >/dev/null 2>&1
}

need_git() {
  command_exists git || die "git is not installed or not in PATH."
}

repo_name_from_url() {
  local url="${1%/}"
  local name
  name="$(basename "$url")"
  name="${name%.git}"
  say "$name"
}

valid_category() {
  local category="$1"
  for c in "${CATEGORIES[@]}"; do
    [[ "$c" == "$category" ]] && return 0
  done
  return 1
}

is_git_repo() {
  local dir="${1:-.}"
  [[ -d "$dir/.git" ]] || git -C "$dir" rev-parse --is-inside-work-tree >/dev/null 2>&1
}

current_repo_root() {
  git rev-parse --show-toplevel 2>/dev/null || return 1
}

ensure_workspace() {
  mkdir -p "$WORKSPACE"

  for category in "${CATEGORIES[@]}"; do
    mkdir -p "$WORKSPACE/$category"
  done

  if [[ ! -f "$REPOS_FILE" ]]; then
    cat > "$REPOS_FILE" <<EOF
# category|repo_url|folder_name_optional
# personal|https://github.com/user/portfolio.git|
# work|https://github.com/company/api.git|backend-api
EOF
  fi
}

init_workspace() {
  need_git
  ensure_workspace

  say "Workspace ready: $WORKSPACE"
  say "Categories: ${CATEGORIES[*]}"
  say "Repo list: $REPOS_FILE"
}

install_self() {
  mkdir -p "$BIN_DIR"

  local target="$BIN_DIR/$INSTALL_NAME"
  local source="${BASH_SOURCE[0]}"

  if [[ ! -f "$source" ]]; then
    warn "Could not locate script source for self-install."
    return 0
  fi

  if [[ "$source" != "$target" ]]; then
    cp "$source" "$target"
    chmod +x "$target"
    say "Installed command: $target"
  else
    chmod +x "$target"
    say "Already installed: $target"
  fi
}

git_config_safe() {
  local key="$1"
  local value="$2"
  if git config --global "$key" "$value" >/dev/null 2>&1; then
    say "  set $key = $value"
  else
    warn "could not set $key. Your Git version may not support it."
  fi
}

install_git_defaults() {
  need_git

  say "Installing global Git defaults..."

  git_config_safe "init.defaultBranch" "main"
  git_config_safe "pull.ff" "only"
  git_config_safe "fetch.prune" "true"
  git_config_safe "rerere.enabled" "true"
  git_config_safe "push.autoSetupRemote" "true"
  git_config_safe "core.excludesfile" "$HOME/.gitignore_global"

  say "Installing global Git aliases..."

  git_config_safe "alias.st" "status --short"
  git_config_safe "alias.s" "status --short"
  git_config_safe "alias.co" "checkout"
  git_config_safe "alias.sw" "switch"
  git_config_safe "alias.br" "branch"
  git_config_safe "alias.cm" "commit -m"
  git_config_safe "alias.ca" "commit --amend"
  git_config_safe "alias.lg" "log --oneline --graph --decorate --all"
  git_config_safe "alias.last" "log -1 HEAD --stat"
  git_config_safe "alias.unstage" "reset HEAD --"
  git_config_safe "alias.undo" "reset --soft HEAD~1"
  git_config_safe "alias.save" "stash push -m"
  git_config_safe "alias.pop" "stash pop"
  git_config_safe "alias.who" "config user.email"

  say "Git defaults installed."
}

install_global_ignore() {
  local ignore="$HOME/.gitignore_global"

  cat > "$ignore" <<'EOF'
# OS noise
.DS_Store
Thumbs.db

# editor noise
.idea/
.vscode/
*.swp
*.swo

# logs
*.log
logs/

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

# secrets - keep examples, ignore real local env files
.env
.env.*
!.env.example

# private keys
*.pem
*.key
id_rsa
id_ed25519
EOF

  git config --global core.excludesfile "$ignore" >/dev/null 2>&1 || true
  say "Global ignore installed: $ignore"
}

detect_shell_rc() {
  if [[ -n "${ZSH_VERSION:-}" ]]; then
    say "$HOME/.zshrc"
  elif [[ -n "${BASH_VERSION:-}" ]]; then
    say "$HOME/.bashrc"
  elif [[ -f "$HOME/.zshrc" ]]; then
    say "$HOME/.zshrc"
  else
    say "$HOME/.bashrc"
  fi
}

install_shell_aliases() {
  ensure_workspace
  mkdir -p "$BIN_DIR"

  local rc_file
  rc_file="$(detect_shell_rc)"
  touch "$rc_file"

  local start="# >>> github-master-toolkit aliases >>>"
  local end="# <<< github-master-toolkit aliases <<<"
  local tmp
  tmp="$(mktemp)"

  awk -v start="$start" -v end="$end" '
    $0 == start {skip=1; next}
    $0 == end {skip=0; next}
    skip != 1 {print}
  ' "$rc_file" > "$tmp"

  cat >> "$tmp" <<EOF

$start
alias ghx="$BIN_DIR/$INSTALL_NAME"
alias ghcode="cd $WORKSPACE"
alias ghwork="cd $WORKSPACE/work"
alias ghpersonal="cd $WORKSPACE/personal"
alias ghlearn="cd $WORKSPACE/learning"
alias ghexp="cd $WORKSPACE/experiments"
alias gharchive="cd $WORKSPACE/archive"

alias ghs="ghx status"
alias ghsy="ghx sync"
alias ghd="ghx doctor"
alias ght="ghx tree"
alias ghn="ghx find-nested"
alias ghauth="ghx auth"

alias gs="git status --short"
alias glg="git log --oneline --graph --decorate --all"
alias gsw="git switch"
alias gcm="git commit -m"
alias gpl="git pull --ff-only"
alias gps="git push"
$end
EOF

  cp "$rc_file" "$rc_file.backup.$(date +%Y%m%d%H%M%S)" 2>/dev/null || true
  mv "$tmp" "$rc_file"

  say "Shell aliases installed in: $rc_file"
  say "Restart terminal or run:"
  say "  source $rc_file"
}

full_install() {
  init_workspace
  install_self
  install_global_ignore
  install_git_defaults
  install_shell_aliases

  say
  say "Install complete."
  say "Use:"
  say "  ghx add personal https://github.com/user/project.git"
  say "  ghx doctor"
}

add_repo() {
  need_git
  ensure_workspace

  local category="${1:-}"
  local url="${2:-}"
  local folder="${3:-}"

  [[ -n "$category" ]] || die "missing category."
  [[ -n "$url" ]] || die "missing repo URL."

  valid_category "$category" || die "invalid category '$category'. Allowed: ${CATEGORIES[*]}"

  if [[ -z "$folder" ]]; then
    folder="$(repo_name_from_url "$url")"
  fi

  local target="$WORKSPACE/$category/$folder"

  if [[ -d "$target/.git" ]]; then
    say "Already cloned: $target"
  elif [[ -e "$target" ]]; then
    die "target exists but is not a git repo: $target"
  else
    say "Cloning into: $target"
    git clone "$url" "$target"
  fi

  if ! grep -Fq "$category|$url|$folder" "$REPOS_FILE" 2>/dev/null; then
    echo "$category|$url|$folder" >> "$REPOS_FILE"
    say "Registered in: $REPOS_FILE"
  else
    say "Already registered."
  fi
}

import_repo() {
  need_git
  ensure_workspace

  local category="${1:-}"
  local source_path="${2:-}"
  local folder="${3:-}"

  [[ -n "$category" ]] || die "missing category."
  [[ -n "$source_path" ]] || die "missing repo path."

  valid_category "$category" || die "invalid category '$category'. Allowed: ${CATEGORIES[*]}"

  source_path="${source_path%/}"

  [[ -d "$source_path" ]] || die "path does not exist: $source_path"
  [[ -d "$source_path/.git" ]] || die "not a normal git repo folder: $source_path"

  if [[ -z "$folder" ]]; then
    folder="$(basename "$source_path")"
  fi

  local target="$WORKSPACE/$category/$folder"

  [[ "$source_path" != "$target" ]] || die "source is already at target."

  if [[ -e "$target" ]]; then
    die "target already exists: $target"
  fi

  say "Moving repo:"
  say "  from: $source_path"
  say "  to:   $target"

  mv "$source_path" "$target"

  local url=""
  url="$(git -C "$target" remote get-url origin 2>/dev/null || true)"

  if [[ -n "$url" ]]; then
    if ! grep -Fq "$category|$url|$folder" "$REPOS_FILE" 2>/dev/null; then
      echo "$category|$url|$folder" >> "$REPOS_FILE"
      say "Registered remote origin in: $REPOS_FILE"
    fi
  else
    warn "No origin remote found. Repo moved but not registered with a URL."
  fi

  say "Import complete."
}

clone_all() {
  need_git
  ensure_workspace

  while IFS='|' read -r category url folder; do
    [[ -z "${category// }" ]] && continue
    [[ "$category" =~ ^# ]] && continue

    valid_category "$category" || {
      warn "Skipping invalid category: $category"
      continue
    }

    [[ -n "$url" ]] || {
      warn "Skipping empty URL line."
      continue
    }

    if [[ -z "${folder:-}" ]]; then
      folder="$(repo_name_from_url "$url")"
    fi

    local target="$WORKSPACE/$category/$folder"

    if [[ -d "$target/.git" ]]; then
      say "Already cloned: $target"
    elif [[ -e "$target" ]]; then
      warn "Conflict: exists but not a git repo: $target"
    else
      say "Cloning: $url -> $target"
      git clone "$url" "$target"
    fi
  done < "$REPOS_FILE"
}

for_each_repo() {
  ensure_workspace
  find "$WORKSPACE" -type d -name .git -prune | while IFS= read -r gitdir; do
    dirname "$gitdir"
  done
}

sync_repos() {
  need_git
  ensure_workspace

  say "Safely syncing repos under: $WORKSPACE"
  say

  for_each_repo | while IFS= read -r repo; do
    say "--- $repo"

    (
      cd "$repo"

      if [[ -n "$(git status --porcelain)" ]]; then
        say "Local changes found. Skipping pull to protect your work."
        git status --short
      else
        local branch
        branch="$(git branch --show-current || true)"

        if [[ -z "$branch" ]]; then
          say "Detached HEAD. Skipping."
        elif git rev-parse --abbrev-ref --symbolic-full-name "@{u}" >/dev/null 2>&1; then
          git pull --ff-only || warn "Pull failed. Fix manually in: $repo"
        else
          say "No upstream tracking branch. Skipping pull."
        fi
      fi
    )

    say
  done
}

status_repos() {
  need_git
  ensure_workspace

  say "Repo status under: $WORKSPACE"
  say

  for_each_repo | while IFS= read -r repo; do
    (
      cd "$repo"
      local branch remote changes
      branch="$(git branch --show-current || echo 'unknown')"
      remote="$(git remote get-url origin 2>/dev/null || echo 'no-origin')"
      changes="$(git status --porcelain)"

      say "--- $repo"
      say "Branch: $branch"
      say "Origin: $remote"

      if [[ -z "$changes" ]]; then
        say "Status: clean"
      else
        say "Status: has local changes"
        git status --short
      fi

      say
    )
  done
}

list_repos() {
  ensure_workspace

  say "Configured repos in: $REPOS_FILE"
  say

  grep -v '^#' "$REPOS_FILE" | grep -v '^$' || say "No repos configured yet."
}

show_tree() {
  ensure_workspace

  say "$WORKSPACE/"

  for category in "${CATEGORIES[@]}"; do
    say "  $category/"

    if [[ -d "$WORKSPACE/$category" ]]; then
      find "$WORKSPACE/$category" -mindepth 1 -maxdepth 1 -type d | sort | while IFS= read -r dir; do
        if [[ -d "$dir/.git" ]]; then
          say "    $(basename "$dir")/  [git]"
        else
          say "    $(basename "$dir")/"
        fi
      done
    fi
  done
}

find_nested_repos() {
  need_git
  ensure_workspace

  say "Checking for nested repos under: $WORKSPACE"
  say

  local printed="false"

  for_each_repo | while IFS= read -r repo; do
    local parent
    parent="$(dirname "$repo")"

    while [[ "$parent" != "$WORKSPACE" && "$parent" != "/" && -n "$parent" ]]; do
      if [[ -d "$parent/.git" ]]; then
        say "Nested repo found:"
        say "  Parent repo: $parent"
        say "  Nested repo: $repo"
        say
        printed="true"
        break
      fi
      parent="$(dirname "$parent")"
    done
  done

  say "Nested check finished."
}

create_if_missing() {
  local file="$1"
  local content="$2"

  if [[ -e "$file" ]]; then
    say "Exists, skipped: $file"
  else
    mkdir -p "$(dirname "$file")"
    printf '%s\n' "$content" > "$file"
    say "Created: $file"
  fi
}

repo_kit() {
  need_git

  local root
  root="$(current_repo_root)" || die "run this inside a git repo."

  cd "$root"

  create_if_missing ".editorconfig" 'root = true

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

  create_if_missing ".gitattributes" '* text=auto eol=lf
*.sh text eol=lf
*.md text eol=lf
*.png binary
*.jpg binary
*.jpeg binary
*.gif binary
*.pdf binary
'

  create_if_missing ".gitignore" '# local secrets
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

  create_if_missing ".env.example" '# Copy this file to .env and fill values locally.
# Never commit real secrets.

APP_ENV=development
'

  create_if_missing "README.md" '# Project Name

## Purpose

Write what this project does.

## Setup

```bash
# install dependencies
```

## Run

```bash
# run project
```

## Notes

Keep this README updated.
'

  create_if_missing ".github/PULL_REQUEST_TEMPLATE.md" '## What changed?

-

## Why?

-

## Checklist

- [ ] I tested the change
- [ ] I checked for secrets
- [ ] I updated docs if needed
'

  create_if_missing ".github/ISSUE_TEMPLATE/bug_report.md" '---
name: Bug report
about: Report a problem
title: "[Bug]: "
labels: bug
---

## Problem

## Steps to reproduce

## Expected behavior

## Screenshots / logs
'

  create_if_missing ".github/ISSUE_TEMPLATE/feature_request.md" '---
name: Feature request
about: Suggest an improvement
title: "[Feature]: "
labels: enhancement
---

## Goal

## Why it matters

## Suggested solution
'

  say
  say "Hidden repo kit installed in: $root"
}

install_hook() {
  need_git

  local root
  root="$(current_repo_root)" || die "run this inside a git repo."

  cd "$root"

  local hooks_dir
  hooks_dir="$(git rev-parse --git-path hooks)"
  mkdir -p "$hooks_dir"

  cat > "$hooks_dir/pre-commit" <<'EOF'
#!/usr/bin/env bash
set -euo pipefail

if [[ "${SKIP_GHX_HOOK:-}" == "1" ]]; then
  exit 0
fi

blocked_files='(^|/)\.env($|\.)|(^|/)id_rsa$|(^|/)id_ed25519$|\.pem$|\.key$'
secret_patterns='AKIA[0-9A-Z]{16}|ghp_[A-Za-z0-9_]{30,}|github_pat_[A-Za-z0-9_]{40,}|BEGIN (RSA|OPENSSH|DSA|EC) PRIVATE KEY|api[_-]?key[[:space:]]*=|password[[:space:]]*=|secret[[:space:]]*='

if git diff --cached --name-only | grep -E "$blocked_files" >/dev/null 2>&1; then
  echo "Blocked commit: staged files look like secrets/private keys."
  echo "To bypass only if you know exactly why:"
  echo "  SKIP_GHX_HOOK=1 git commit"
  exit 1
fi

if git diff --cached --text | grep -E "$secret_patterns" >/dev/null 2>&1; then
  echo "Blocked commit: staged diff contains possible secret patterns."
  echo "Review your staged changes."
  echo "To bypass only if false positive:"
  echo "  SKIP_GHX_HOOK=1 git commit"
  exit 1
fi

exit 0
EOF

  chmod +x "$hooks_dir/pre-commit"
  say "Safety pre-commit hook installed:"
  say "  $hooks_dir/pre-commit"
}

secret_scan() {
  need_git

  local root
  root="$(current_repo_root)" || die "run this inside a git repo."

  cd "$root"

  say "Basic secret scan in: $root"
  say "This is not perfect. It catches common mistakes."
  say

  local pattern='AKIA[0-9A-Z]{16}|ghp_[A-Za-z0-9_]{30,}|github_pat_[A-Za-z0-9_]{40,}|BEGIN (RSA|OPENSSH|DSA|EC) PRIVATE KEY|api[_-]?key[[:space:]]*=|password[[:space:]]*=|secret[[:space:]]*='

  if grep -RInE \
    --exclude-dir=.git \
    --exclude-dir=node_modules \
    --exclude-dir=.venv \
    --exclude-dir=venv \
    --exclude-dir=dist \
    --exclude-dir=build \
    "$pattern" .; then
    say
    warn "Possible secrets found. Review carefully."
    return 1
  else
    say "No obvious secrets found."
  fi
}

auth_check() {
  need_git

  say "Git identity:"
  say "  user.name:  $(git config --global user.name || echo 'not set')"
  say "  user.email: $(git config --global user.email || echo 'not set')"
  say

  if command_exists gh; then
    say "GitHub CLI found. Checking auth:"
    gh auth status || true
  else
    warn "GitHub CLI 'gh' is not installed."
  fi

  say
  say "SSH config check:"
  if [[ -f "$HOME/.ssh/id_ed25519.pub" || -f "$HOME/.ssh/id_rsa.pub" ]]; then
    say "  SSH public key exists."
  else
    warn "No common SSH public key found in ~/.ssh."
  fi
}

doctor() {
  need_git
  ensure_workspace

  say "GitHub Workspace Doctor"
  say "Version: $VERSION"
  say "Workspace: $WORKSPACE"
  say

  say "1. Required tools"
  say "  git: $(git --version)"
  if command_exists gh; then
    say "  gh:  $(gh --version | head -n 1)"
  else
    say "  gh:  not installed"
  fi

  say
  say "2. Categories"
  for category in "${CATEGORIES[@]}"; do
    if [[ -d "$WORKSPACE/$category" ]]; then
      say "  OK: $category"
    else
      say "  Missing: $category"
    fi
  done

  say
  say "3. Repos"
  local count
  count="$(for_each_repo | wc -l | tr -d ' ')"
  say "  Git repos found: $count"

  say
  say "4. Dirty repos"
  local dirty_found="false"
  for_each_repo | while IFS= read -r repo; do
    (
      cd "$repo"
      if [[ -n "$(git status --porcelain)" ]]; then
        say "  Dirty: $repo"
        git status --short
      fi
    )
  done

  say
  say "5. Missing origin/upstream"
  for_each_repo | while IFS= read -r repo; do
    (
      cd "$repo"
      if ! git remote get-url origin >/dev/null 2>&1; then
        say "  No origin: $repo"
      elif ! git rev-parse --abbrev-ref --symbolic-full-name "@{u}" >/dev/null 2>&1; then
        say "  No upstream: $repo"
      fi
    )
  done

  say
  say "6. Nested repos"
  find_nested_repos

  say
  say "Doctor finished."
}

print_aliases() {
  cat <<EOF
Shell aliases installed by 'ghx shell-aliases':

Workspace:
  ghcode       cd $WORKSPACE
  ghwork       cd $WORKSPACE/work
  ghpersonal   cd $WORKSPACE/personal
  ghlearn      cd $WORKSPACE/learning
  ghexp        cd $WORKSPACE/experiments
  gharchive    cd $WORKSPACE/archive

Toolkit:
  ghx          run GitHub Master Toolkit
  ghs          ghx status
  ghsy         ghx sync
  ghd          ghx doctor
  ght          ghx tree
  ghn          ghx find-nested
  ghauth       ghx auth

Git:
  gs           git status --short
  glg          git log --oneline --graph --decorate --all
  gsw          git switch
  gcm          git commit -m
  gpl          git pull --ff-only
  gps          git push

Git aliases installed by 'ghx git-defaults':

  git st       git status --short
  git s        git status --short
  git co       git checkout
  git sw       git switch
  git br       git branch
  git cm       git commit -m
  git ca       git commit --amend
  git lg       pretty graph log
  git last     last commit with stats
  git unstage  unstage files
  git undo     soft undo last commit
  git save     stash with message
  git pop      stash pop
  git who      show repo/global email
EOF
}

main() {
  local command="${1:-help}"

  case "$command" in
    install)
      full_install
      ;;
    init)
      init_workspace
      ;;
    add|clone)
      shift
      add_repo "$@"
      ;;
    import|move)
      shift
      import_repo "$@"
      ;;
    clone-all)
      clone_all
      ;;
    sync)
      sync_repos
      ;;
    status)
      status_repos
      ;;
    tree)
      show_tree
      ;;
    list)
      list_repos
      ;;
    doctor)
      doctor
      ;;
    find-nested)
      find_nested_repos
      ;;
    git-defaults)
      install_git_defaults
      ;;
    shell-aliases)
      install_shell_aliases
      ;;
    ignore-global)
      install_global_ignore
      ;;
    kit)
      repo_kit
      ;;
    hook)
      install_hook
      ;;
    secret-scan)
      secret_scan
      ;;
    auth)
      auth_check
      ;;
    aliases)
      print_aliases
      ;;
    help|--help|-h)
      usage
      ;;
    version|--version|-v)
      say "$VERSION"
      ;;
    *)
      say "Unknown command: $command"
      say
      usage
      exit 1
      ;;
  esac
}

main "$@"
