#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CODE_HOME="${CODE_HOME:-$HOME/code}"

echo "Setting up Personal GitHub Code Command Center..."
echo "Root: $ROOT"
echo "Code home: $CODE_HOME"

mkdir -p "$CODE_HOME"/{work,personal,learning,experiments,archive}
mkdir -p "$ROOT/workspace"/{work,personal,learning,experiments,archive}

# Link local workspace folders to ~/code categories when possible.
for category in work personal learning experiments archive; do
  target="$CODE_HOME/$category"
  link="$ROOT/workspace/$category"

  if [ -d "$link" ] && [ ! -L "$link" ] && [ -z "$(find "$link" -mindepth 1 -maxdepth 1 2>/dev/null)" ]; then
    rmdir "$link"
  fi

  if [ ! -e "$link" ]; then
    ln -s "$target" "$link" 2>/dev/null || mkdir -p "$link"
  fi
done

git config --global init.defaultBranch main || true
git config --global pull.ff only || true
git config --global fetch.prune true || true
git config --global push.autoSetupRemote true || true
git config --global rerere.enabled true || true
git config --global core.excludesfile "$HOME/.gitignore_global" || true

cat > "$HOME/.gitignore_global" <<'EOF'
.DS_Store
Thumbs.db
.idea/
.vscode/
*.log
node_modules/
.venv/
venv/
__pycache__/
*.pyc
dist/
build/
coverage/
.cache/
.env
.env.*
!.env.example
*.pem
*.key
id_rsa
id_ed25519
EOF

chmod +x "$ROOT/scripts/"*.sh

echo
echo "Setup complete."
echo "Open workspace:"
echo "  code \"$ROOT/Personal_GitHub_Command_Center.code-workspace\""
