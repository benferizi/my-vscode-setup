#!/usr/bin/env bash
set -euo pipefail

root="$(git rev-parse --show-toplevel 2>/dev/null || true)"
[ -n "$root" ] || { echo "Run this inside a Git repo."; exit 1; }

hooks_dir="$(git -C "$root" rev-parse --git-path hooks)"
mkdir -p "$hooks_dir"

cat > "$hooks_dir/pre-commit" <<'EOF'
#!/usr/bin/env bash
set -euo pipefail

if [ "${SKIP_PERSONAL_HOOK:-}" = "1" ]; then
  exit 0
fi

blocked_files='(^|/)\.env($|\.)|(^|/)id_rsa$|(^|/)id_ed25519$|\.pem$|\.key$'
secret_patterns='AKIA[0-9A-Z]{16}|ghp_[A-Za-z0-9_]{30,}|github_pat_[A-Za-z0-9_]{40,}|BEGIN (RSA|OPENSSH|DSA|EC) PRIVATE KEY|api[_-]?key[[:space:]]*=|password[[:space:]]*=|secret[[:space:]]*=|token[[:space:]]*='

if git diff --cached --name-only | grep -E "$blocked_files" >/dev/null 2>&1; then
  echo "Blocked commit: staged files look like secrets/private keys."
  echo "Bypass only if false positive:"
  echo "  SKIP_PERSONAL_HOOK=1 git commit"
  exit 1
fi

if git diff --cached --text | grep -E "$secret_patterns" >/dev/null 2>&1; then
  echo "Blocked commit: staged diff contains possible secrets."
  echo "Bypass only if false positive:"
  echo "  SKIP_PERSONAL_HOOK=1 git commit"
  exit 1
fi

exit 0
EOF

chmod +x "$hooks_dir/pre-commit"
echo "Installed pre-commit hook: $hooks_dir/pre-commit"
