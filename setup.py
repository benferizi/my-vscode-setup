#!/usr/bin/env python3
import argparse
from datetime import datetime
import json
import re
import shutil
import subprocess
import sys
import os
from pathlib import Path

VERSION = "1.0.0"
CATEGORIES = ("work", "personal", "learning", "experiments", "archive")
WORKSPACE = Path.home() / "code"
GLOBAL_GITIGNORE = Path.home() / ".gitignore_global"
SCRIPT_ROOT = Path(__file__).resolve().parent
LEGACY_DIR_NAMES = ("GitHub_Master_Toolkit_Bundle", "Personal_GitHub_Code_Command_Center")

EXTENSIONS = [
    "github.vscode-github-actions",
    "eamodio.gitlens",
    "github.vscode-pull-request-github",
    "editorconfig.editorconfig",
    "ms-azuretools.vscode-docker",
    "redhat.vscode-yaml",
    "davidanson.vscode-markdownlint",
    "esbenp.prettier-vscode",
    "streetsidesoftware.code-spell-checker",
    "github.copilot",
    "github.copilot-chat",
    "ms-python.python",
]

BLOCKED_FILES_PATTERN = r"(^|/)\.env($|\.)|(^|/)id_rsa$|(^|/)id_ed25519$|\.pem$|\.key$"
SECRET_PATTERN = (
    r"AKIA[0-9A-Z]{16}|"
    r"ghp_[A-Za-z0-9_]{30,}|"
    r"github_pat_[A-Za-z0-9_]{40,}|"
    r"BEGIN (RSA|OPENSSH|DSA|EC) PRIVATE KEY|"
    r"api[_-]?key\s*=|"
    r"password\s*=|"
    r"secret\s*=|"
    r"token\s*="
)

IGNORE_DIRS = {".git", "node_modules", ".venv", "venv", "dist", "build", "coverage", "__pycache__"}


class Color:
    def __init__(self):
        self.enabled = self._enable_windows_ansi_if_possible() and self._supports_ansi()
        self.codes = {
            "reset": "\033[0m",
            "blue": "\033[34m",
            "green": "\033[32m",
            "yellow": "\033[33m",
            "red": "\033[31m",
            "bold": "\033[1m",
        }

    def _supports_ansi(self):
        if not sys.stdout.isatty():
            return False
        if os.name != "nt":
            return True
        return bool(os.environ.get("ANSICON") or os.environ.get("WT_SESSION") or os.environ.get("TERM"))

    def _enable_windows_ansi_if_possible(self):
        if os.name != "nt":
            return True
        try:
            import ctypes

            kernel32 = ctypes.windll.kernel32
            handle = kernel32.GetStdHandle(-11)
            mode = ctypes.c_uint32()
            if kernel32.GetConsoleMode(handle, ctypes.byref(mode)):
                kernel32.SetConsoleMode(handle, mode.value | 0x0004)
            return True
        except Exception:
            return False

    def wrap(self, text, color=None, bold=False):
        if not self.enabled:
            return text
        parts = []
        if bold:
            parts.append(self.codes["bold"])
        if color:
            parts.append(self.codes[color])
        parts.append(text)
        parts.append(self.codes["reset"])
        return "".join(parts)


COLOR = Color()


def run(cmd, check=True, capture_output=True, cwd=None):
    return subprocess.run(
        cmd,
        check=check,
        text=True,
        capture_output=capture_output,
        cwd=cwd,
    )


def print_info(message):
    print(COLOR.wrap(message, "blue"))


def print_ok(message):
    print(COLOR.wrap(message, "green"))


def print_warn(message):
    print(COLOR.wrap(message, "yellow"))


def print_error(message):
    print(COLOR.wrap(message, "red", bold=True), file=sys.stderr)


def ensure_workspace():
    WORKSPACE.mkdir(parents=True, exist_ok=True)
    for category in CATEGORIES:
        (WORKSPACE / category).mkdir(parents=True, exist_ok=True)


def check_tool(name):
    return shutil.which(name) is not None


def run_git_config(key, value):
    try:
        run(["git", "config", "--global", key, value])
        print_ok(f"set {key} = {value}")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print_warn(f"could not set {key}")


def install_global_gitignore():
    content = """# OS noise
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

# secrets
.env
.env.*
!.env.example

# private keys
*.pem
*.key
id_rsa
id_ed25519
"""
    GLOBAL_GITIGNORE.write_text(content, encoding="utf-8")
    run_git_config("core.excludesfile", str(GLOBAL_GITIGNORE))
    print_ok(f"Global gitignore installed: {GLOBAL_GITIGNORE}")


def install_git_aliases_and_defaults():
    if not check_tool("git"):
        raise RuntimeError("git is not installed or not in PATH.")

    print_info("Installing global Git defaults...")
    run_git_config("init.defaultBranch", "main")
    run_git_config("pull.ff", "only")
    run_git_config("fetch.prune", "true")
    run_git_config("rerere.enabled", "true")
    run_git_config("push.autoSetupRemote", "true")

    print_info("Installing global Git aliases...")
    aliases = {
        "alias.st": "status --short",
        "alias.sw": "switch",
        "alias.br": "branch",
        "alias.cm": "commit -m",
        "alias.lg": "log --oneline --graph --decorate --all",
        "alias.last": "log -1 HEAD --stat",
        "alias.unstage": "reset HEAD --",
        "alias.undo": "reset --soft HEAD~1",
        "alias.save": "stash push -m",
        "alias.pop": "stash pop",
    }
    for key, value in aliases.items():
        run_git_config(key, value)


def repo_name_from_url(url):
    name = url.rstrip("/").split("/")[-1]
    if name.endswith(".git"):
        name = name[:-4]
    return name


def validate_category(category):
    if category not in CATEGORIES:
        raise ValueError(f"Invalid category '{category}'. Allowed: {', '.join(CATEGORIES)}")


def is_git_repo(path):
    return (path / ".git").exists()


def iter_git_repos(root):
    root = root.resolve()
    if not root.exists():
        return
    for current, dirs, _files in os.walk(root):
        current_path = Path(current)
        if ".git" in dirs:
            yield current_path
            dirs[:] = [d for d in dirs if d != ".git"]


def add_repo(args):
    ensure_workspace()
    validate_category(args.category)
    if not check_tool("git"):
        raise RuntimeError("git is not installed or not in PATH.")

    folder = args.name or repo_name_from_url(args.git_url)
    target = WORKSPACE / args.category / folder

    if is_git_repo(target):
        print_warn(f"Already cloned: {target}")
        return
    if target.exists():
        raise RuntimeError(f"Target exists but is not a git repo: {target}")

    print_info(f"Cloning into: {target}")
    run(["git", "clone", args.git_url, str(target)], check=True, capture_output=False)
    print_ok("Clone complete.")


def import_repo(args):
    ensure_workspace()
    validate_category(args.category)

    source_path = Path(args.path).expanduser().resolve()
    if not source_path.exists():
        raise RuntimeError(f"Path does not exist: {source_path}")
    if not is_git_repo(source_path):
        raise RuntimeError(f"Not a normal git repo folder: {source_path}")

    folder = args.name or source_path.name
    target = (WORKSPACE / args.category / folder).resolve()

    if source_path == target:
        raise RuntimeError("Source is already at target.")
    if target.exists():
        raise RuntimeError(f"Target already exists: {target}")

    print_info(f"Moving:\n  from: {source_path}\n  to:   {target}")
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.move(str(source_path), str(target))
    print_ok("Import complete.")


def sync_repos(_args):
    if not check_tool("git"):
        raise RuntimeError("git is not installed or not in PATH.")
    ensure_workspace()

    print_info(f"Safely syncing repos under: {WORKSPACE}")
    for repo in iter_git_repos(WORKSPACE):
        print(COLOR.wrap(f"--- {repo}", bold=True))
        status = run(["git", "-C", str(repo), "status", "--porcelain"]).stdout.strip()
        if status:
            print_warn("Local changes found. Skipping pull.")
            print(status)
            print()
            continue

        branch = run(["git", "-C", str(repo), "branch", "--show-current"]).stdout.strip()
        if not branch:
            print_warn("Detached HEAD. Skipping.")
            print()
            continue

        upstream = run(
            ["git", "-C", str(repo), "rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{u}"],
            check=False,
        )
        if upstream.returncode != 0:
            print_warn("No upstream tracking branch. Skipping.")
            print()
            continue

        pull = run(["git", "-C", str(repo), "pull", "--ff-only"], check=False)
        if pull.returncode == 0:
            print_ok("Pulled successfully.")
            if pull.stdout.strip():
                print(pull.stdout.strip())
        else:
            print_warn("Pull failed. Fix manually.")
            if pull.stderr.strip():
                print(pull.stderr.strip())
        print()


def status_repos(_args):
    if not check_tool("git"):
        raise RuntimeError("git is not installed or not in PATH.")
    ensure_workspace()

    print_info(f"Repo status under: {WORKSPACE}")
    for repo in iter_git_repos(WORKSPACE):
        branch = run(["git", "-C", str(repo), "branch", "--show-current"]).stdout.strip() or "unknown"
        remote_res = run(["git", "-C", str(repo), "remote", "get-url", "origin"], check=False)
        remote = remote_res.stdout.strip() if remote_res.returncode == 0 else "no-origin"
        changes = run(["git", "-C", str(repo), "status", "--porcelain"]).stdout.strip()

        print(COLOR.wrap(f"--- {repo}", bold=True))
        print(f"Branch: {branch}")
        print(f"Origin: {remote}")
        if not changes:
            print_ok("Status: clean")
        else:
            print_warn("Status: has local changes")
            print(changes)
        print()


def find_nested_repos_data(root):
    nested = []
    root = root.resolve()
    repos = [repo.resolve() for repo in iter_git_repos(root)]
    repo_set = set(repos)

    for repo in repos:
        parent = repo.parent
        while parent != root and parent != parent.parent:
            if parent in repo_set:
                nested.append((parent, repo))
                break
            parent = parent.parent
    return nested


def find_nested_repos(_args):
    ensure_workspace()
    nested = find_nested_repos_data(WORKSPACE)
    if not nested:
        print_ok("none")
        return

    for parent, child in nested:
        print_warn("Nested repo found:")
        print(f"  Parent: {parent}")
        print(f"  Nested: {child}")
        print()


def tree(_args):
    ensure_workspace()
    print(f"{WORKSPACE}/")
    for category in CATEGORIES:
        category_path = WORKSPACE / category
        print(f"  {category}/")
        if not category_path.exists():
            continue
        for item in sorted([p for p in category_path.iterdir() if p.is_dir()], key=lambda p: p.name.lower()):
            marker = " [git]" if is_git_repo(item) else ""
            print(f"    {item.name}/{marker}")


def doctor(_args):
    ensure_workspace()

    print(COLOR.wrap("Workspace Doctor", bold=True))
    print(f"Workspace: {WORKSPACE}")
    print()

    print("1. Tools")
    if check_tool("git"):
        git_version = run(["git", "--version"]).stdout.strip()
        print_ok(f"  git: {git_version}")
    else:
        print_error("  git: MISSING")

    if check_tool("gh"):
        gh_line = run(["gh", "--version"]).stdout.splitlines()[0]
        print_ok(f"  gh:  {gh_line}")
    else:
        print_warn("  gh:  not installed")

    if check_tool("code"):
        print_ok("  code: available")
    else:
        print_warn("  code: not in PATH")

    print("\n2. Workspace folders")
    for category in CATEGORIES:
        category_path = WORKSPACE / category
        if category_path.exists():
            print_ok(f"  OK: {category_path}")
        else:
            print_warn(f"  Missing: {category_path}")

    repos = list(iter_git_repos(WORKSPACE))
    print("\n3. Repo count")
    print(f"  repos found: {len(repos)}")

    print("\n4. Dirty repos")
    dirty_any = False
    for repo in repos:
        changes = run(["git", "-C", str(repo), "status", "--porcelain"]).stdout.strip()
        if changes:
            dirty_any = True
            print_warn(f"  Dirty: {repo}")
            print(changes)
    if not dirty_any:
        print_ok("  none")

    print("\n5. Missing remotes/upstream")
    issue_any = False
    for repo in repos:
        origin = run(["git", "-C", str(repo), "remote", "get-url", "origin"], check=False)
        if origin.returncode != 0:
            issue_any = True
            print_warn(f"  No origin: {repo}")
            continue

        upstream = run(
            ["git", "-C", str(repo), "rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{u}"],
            check=False,
        )
        if upstream.returncode != 0:
            issue_any = True
            print_warn(f"  No upstream: {repo}")
    if not issue_any:
        print_ok("  none")

    print("\n6. Nested repos")
    nested = find_nested_repos_data(WORKSPACE)
    if not nested:
        print_ok("  none")
    else:
        for parent, child in nested:
            print_warn(f"  Parent: {parent}")
            print_warn(f"  Nested: {child}")


def current_repo_root():
    result = run(["git", "rev-parse", "--show-toplevel"], check=False)
    if result.returncode != 0:
        raise RuntimeError("Run this command inside a Git repo.")
    return Path(result.stdout.strip()).resolve()


def create_if_missing(path, content):
    if path.exists():
        print_warn(f"Exists, skipped: {path}")
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    print_ok(f"Created: {path}")


def kit(_args):
    root = current_repo_root()

    create_if_missing(
        root / ".editorconfig",
        """root = true

[*]
charset = utf-8
end_of_line = lf
insert_final_newline = true
trim_trailing_whitespace = true
indent_style = space
indent_size = 2

[*.py]
indent_size = 4
""",
    )

    create_if_missing(
        root / ".gitattributes",
        """* text=auto eol=lf
*.sh text eol=lf
*.md text eol=lf
*.png binary
*.jpg binary
*.jpeg binary
*.gif binary
*.pdf binary
""",
    )

    create_if_missing(
        root / ".gitignore",
        """# local secrets
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
""",
    )

    create_if_missing(
        root / ".env.example",
        """# Copy this file to .env and fill values locally.
# Never commit real secrets.

APP_ENV=development
""",
    )

    create_if_missing(
        root / "README.md",
        """# Project Name

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
""",
    )

    create_if_missing(
        root / ".github" / "PULL_REQUEST_TEMPLATE.md",
        """## What changed?

-

## Why?

-

## Checklist

- [ ] I tested the change
- [ ] I checked for secrets
- [ ] I updated docs if needed
""",
    )


def hook(_args):
    root = current_repo_root()
    hooks_dir = Path(
        run(["git", "-C", str(root), "rev-parse", "--git-path", "hooks"]).stdout.strip()
    )
    hooks_dir.mkdir(parents=True, exist_ok=True)

    hook_content = f"""#!/usr/bin/env bash
set -euo pipefail

if [ "${{SKIP_GHX_HOOK:-}}" = "1" ]; then
  exit 0
fi

blocked_files='{BLOCKED_FILES_PATTERN}'
secret_patterns='{SECRET_PATTERN}'

if git diff --cached --name-only | grep -E "$blocked_files" >/dev/null 2>&1; then
  echo "Blocked commit: staged files look like secrets/private keys."
  echo "Bypass only if false positive:"
  echo "  SKIP_GHX_HOOK=1 git commit"
  exit 1
fi

if git diff --cached --text | grep -E "$secret_patterns" >/dev/null 2>&1; then
  echo "Blocked commit: staged diff contains possible secrets."
  echo "Bypass only if false positive:"
  echo "  SKIP_GHX_HOOK=1 git commit"
  exit 1
fi

exit 0
"""

    hook_path = hooks_dir / "pre-commit"
    hook_path.write_text(hook_content, encoding="utf-8")
    if os.name != "nt":
        hook_path.chmod(0o755)
    print_ok(f"Installed pre-commit hook: {hook_path}")


def is_binary_file(path):
    try:
        with path.open("rb") as f:
            chunk = f.read(1024)
        return b"\x00" in chunk
    except OSError:
        return True


def secret_scan(_args):
    root = current_repo_root()
    pattern = re.compile(SECRET_PATTERN)

    hits = []
    for current, dirs, files in os.walk(root):
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]
        current_path = Path(current)
        for file_name in files:
            file_path = current_path / file_name
            rel_path = file_path.relative_to(root)

            if re.search(BLOCKED_FILES_PATTERN, str(rel_path).replace("\\", "/")):
                hits.append((rel_path, "blocked filename pattern"))
                continue

            if is_binary_file(file_path):
                continue
            try:
                text = file_path.read_text(encoding="utf-8", errors="ignore")
            except OSError:
                continue

            for idx, line in enumerate(text.splitlines(), start=1):
                if pattern.search(line):
                    hits.append((rel_path, f"line {idx}"))

    if hits:
        print_error("Possible secrets found:")
        for rel_path, detail in hits:
            print(f"  {rel_path} ({detail})")
        raise RuntimeError("Secret scan failed.")

    print_ok("No obvious secrets found.")


def extensions(_args):
    if not check_tool("code"):
        print_warn("VS Code CLI 'code' is not in PATH. Skipping extension installation.")
        return

    installed = set(run(["code", "--list-extensions"]).stdout.splitlines())
    for ext in EXTENSIONS:
        if ext in installed:
            print_ok(f"Already installed: {ext}")
            continue
        print_info(f"Installing: {ext}")
        res = run(["code", "--install-extension", ext], check=False)
        if res.returncode == 0:
            print_ok(f"Installed: {ext}")
        else:
            print_warn(f"Failed: {ext}")
            if res.stderr.strip():
                print(res.stderr.strip())


def install(_args):
    ensure_workspace()
    install_git_aliases_and_defaults()
    install_global_gitignore()
    extensions(_args)
    print_ok("Install complete.")


def restore(_args):
    install(_args)
    print()
    print_ok("Restore complete.")
    print("Next steps:")
    print("1. Open 'ultimate.code-workspace' in VS Code.")
    print("2. Sign in to GitHub in VS Code.")
    print("3. Enable Settings Sync and verify Copilot Pro+ is active.")


def find_legacy_paths():
    roots = {
        SCRIPT_ROOT,
        Path.cwd().resolve(),
        Path.home().resolve(),
    }
    found = set()
    for root in roots:
        for name in LEGACY_DIR_NAMES:
            candidate = (root / name).resolve()
            if candidate.exists() and candidate.is_dir():
                found.add(candidate)
    return sorted(found, key=lambda p: str(p))


def cleanup_old(args):
    found = find_legacy_paths()
    if not found:
        print_ok("No legacy folders found in the standard scan locations.")
        return

    print_info("Legacy folders found:")
    for path in found:
        print(f"  - {path}")

    backup_dir = Path(args.backup_dir).expanduser().resolve()
    if not args.execute:
        print()
        print_warn("Dry run only. Nothing moved.")
        print(f"Run with --execute to move these folders into: {backup_dir}")
        return

    backup_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")

    for path in found:
        target = backup_dir / f"{path.name}-{timestamp}"
        counter = 1
        while target.exists():
            target = backup_dir / f"{path.name}-{timestamp}-{counter}"
            counter += 1
        shutil.move(str(path), str(target))
        print_ok(f"Moved: {path} -> {target}")

    print_ok("Legacy cleanup complete.")


def print_json_extensions(_args):
    print(json.dumps(EXTENSIONS, indent=2))


def build_parser():
    parser = argparse.ArgumentParser(
        description="Ultimate merged GitHub + VS Code workspace toolkit",
    )
    parser.add_argument("--version", action="version", version=f"setup.py {VERSION}")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("install", help="First-time setup").set_defaults(func=install)

    add_p = sub.add_parser("add", help="Clone a repo into a category")
    add_p.add_argument("category", choices=CATEGORIES)
    add_p.add_argument("git_url")
    add_p.add_argument("name", nargs="?")
    add_p.set_defaults(func=add_repo)

    import_p = sub.add_parser("import", help="Move an existing local repo into workspace")
    import_p.add_argument("category", choices=CATEGORIES)
    import_p.add_argument("path")
    import_p.add_argument("name", nargs="?")
    import_p.set_defaults(func=import_repo)

    sub.add_parser("sync", help="Safe pull all repos").set_defaults(func=sync_repos)
    sub.add_parser("status", help="Status of all repos").set_defaults(func=status_repos)
    sub.add_parser("doctor", help="Workspace health check").set_defaults(func=doctor)
    sub.add_parser("tree", help="Print workspace tree").set_defaults(func=tree)
    sub.add_parser("find-nested", help="Detect nested repos").set_defaults(func=find_nested_repos)
    sub.add_parser("kit", help="Install helper files into current repo").set_defaults(func=kit)
    sub.add_parser("hook", help="Install safety pre-commit hook").set_defaults(func=hook)
    sub.add_parser("secret-scan", help="Basic secret scan in current repo").set_defaults(func=secret_scan)
    sub.add_parser("extensions", help="Install/verify VS Code extensions").set_defaults(func=extensions)
    sub.add_parser("restore", help="Full restore after PC format").set_defaults(func=restore)
    cleanup_p = sub.add_parser("cleanup-old", help="Scan and move old legacy bundles to backup")
    cleanup_p.add_argument(
        "--backup-dir",
        default="~/my-vscode-setup-backup",
        help="Backup directory where legacy folders are moved",
    )
    cleanup_p.add_argument(
        "--execute",
        action="store_true",
        help="Actually move the legacy folders (default is dry run)",
    )
    cleanup_p.set_defaults(func=cleanup_old)
    sub.add_parser("extensions-json", help=argparse.SUPPRESS).set_defaults(func=print_json_extensions)

    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()
    try:
        args.func(args)
    except (RuntimeError, ValueError) as exc:
        print_error(str(exc))
        sys.exit(1)


if __name__ == "__main__":
    main()
