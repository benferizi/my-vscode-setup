#!/usr/bin/env bash
#
# One-command full automation install for my-vscode-setup.
#
# Usage after a fresh PC format (single command, no chat history needed):
#
#   curl -fsSL https://raw.githubusercontent.com/benferizi/my-vscode-setup/main/install.sh | bash
#
# Or, if you already cloned the repo:
#
#   bash install.sh
#
# What it does:
#   1. Clones (or updates) the repo into ~/code/personal/my-vscode-setup
#   2. Runs the full restore: workspace layout, git aliases, global gitignore,
#      VS Code extensions, dev tools (npm globals + Python packages),
#      config restore (if a backup exists) and a setup summary.

set -euo pipefail

REPO_URL="https://github.com/benferizi/my-vscode-setup.git"
TARGET_DIR="$HOME/code/personal/my-vscode-setup"

info() { printf '\033[34m[INFO]\033[0m %s\n' "$*"; }
ok()   { printf '\033[32m[OK]\033[0m %s\n' "$*"; }
err()  { printf '\033[31m[ERROR]\033[0m %s\n' "$*" >&2; }

# --- Check prerequisites ---------------------------------------------------
for tool in git python3; do
    if ! command -v "$tool" >/dev/null 2>&1; then
        err "'$tool' is required. Install it first (e.g. sudo apt install $tool) and re-run."
        exit 1
    fi
done

# --- Get the repo ----------------------------------------------------------
# If this script is being run from inside an existing clone, use that clone.
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]:-.}")" 2>/dev/null && pwd)" || SCRIPT_DIR=""
if [ -n "$SCRIPT_DIR" ] && [ -f "$SCRIPT_DIR/setup.py" ]; then
    TARGET_DIR="$SCRIPT_DIR"
    info "Using existing clone: $TARGET_DIR"
elif [ -d "$TARGET_DIR/.git" ]; then
    info "Repo already cloned. Updating: $TARGET_DIR"
    git -C "$TARGET_DIR" pull --ff-only || info "Could not fast-forward. Continuing with the current version."
else
    info "Cloning $REPO_URL into $TARGET_DIR"
    mkdir -p "$(dirname "$TARGET_DIR")"
    git clone "$REPO_URL" "$TARGET_DIR"
fi

# --- Run the full automated setup ------------------------------------------
cd "$TARGET_DIR"
info "Running full restore (install + dev tools + config restore + summary)..."
python3 setup.py restore --full

ok "All done!"
echo
echo "Next steps:"
echo "  1. Open the workspace:  code $TARGET_DIR/ultimate.code-workspace"
echo "  2. Sign in to GitHub in VS Code (Accounts menu)."
echo "  3. Optional GitHub setup: python3 setup.py github-setup --name 'Your Name' --email 'you@example.com' --ssh"
