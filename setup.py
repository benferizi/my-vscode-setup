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

NPM_GLOBAL_PACKAGES = [
    "nodemon",
    "express-generator",
    "create-react-app",
    "@vue/cli",
    "typescript",
]

PYTHON_PACKAGES = [
    "django",
    "flask",
    "requests",
    "numpy",
    "pandas",
    "matplotlib",
]

CONFIG_FILES = (
    ".bashrc",
    ".bash_aliases",
    ".gitconfig",
    ".nanorc",
)

PROJECTS_PERSONAL = Path.home() / "Projects" / "personal"
BACKUP_ROOT = Path.home() / "my-vscode-setup-backup"
CONFIG_BACKUP_DIR = BACKUP_ROOT / "configs"
LOG_FILE = Path.home() / ".my-vscode-setup.log"
SUMMARY_FILE = Path.home() / "SETUP_SUMMARY.md"

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


def log_action(action, status, detail=""):
    """Append one action line to the setup log used by the summary command."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"{timestamp} | {status.upper():7} | {action}"
    if detail:
        line += f" | {detail}"
    try:
        with LOG_FILE.open("a", encoding="utf-8") as handle:
            handle.write(line + "\n")
    except OSError:
        pass


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


def github_setup(args):
    """Premium GitHub setup: gh CLI, auth, SSH key, git identity, Copilot Pro+."""
    print_info("== GitHub premium setup ==")

    if not check_tool("git"):
        raise RuntimeError("git is not installed or not in PATH.")

    if check_tool("gh"):
        print_ok("GitHub CLI (gh) is installed.")
        log_action("github-setup: gh CLI", "ok")
        auth = run(["gh", "auth", "status"], check=False)
        if auth.returncode == 0:
            print_ok("GitHub CLI is authenticated.")
            log_action("github-setup: gh auth", "ok")
        else:
            print_warn("GitHub CLI is not authenticated. Run: gh auth login")
            log_action("github-setup: gh auth", "pending", "run 'gh auth login'")
    else:
        print_warn("GitHub CLI (gh) is not installed. See: https://cli.github.com")
        log_action("github-setup: gh CLI", "missing", "install from https://cli.github.com")

    if args.name:
        run_git_config("user.name", args.name)
        log_action("github-setup: git user.name", "ok", args.name)
    if args.email:
        run_git_config("user.email", args.email)
        log_action("github-setup: git user.email", "ok", args.email)
    if not args.name and not args.email:
        current_name = run(["git", "config", "--global", "user.name"], check=False).stdout.strip()
        current_email = run(["git", "config", "--global", "user.email"], check=False).stdout.strip()
        if current_name and current_email:
            print_ok(f"Git identity already set: {current_name} <{current_email}>")
        else:
            print_warn("Git identity not fully set. Re-run with --name and --email.")

    ssh_dir = Path.home() / ".ssh"
    key_path = ssh_dir / "id_ed25519"
    if key_path.exists():
        print_ok(f"SSH key already exists: {key_path}")
        log_action("github-setup: SSH key", "ok", str(key_path))
    elif args.ssh:
        if not check_tool("ssh-keygen"):
            print_warn("ssh-keygen not found. Skipping SSH key creation.")
            log_action("github-setup: SSH key", "skipped", "ssh-keygen missing")
        else:
            ssh_dir.mkdir(mode=0o700, parents=True, exist_ok=True)
            comment = args.email or "my-vscode-setup"
            res = run(["ssh-keygen", "-t", "ed25519", "-C", comment, "-f", str(key_path), "-N", ""], check=False)
            if res.returncode == 0:
                print_ok(f"SSH key created: {key_path}")
                print_info("Add the public key to GitHub: https://github.com/settings/keys")
                log_action("github-setup: SSH key", "ok", "created")
            else:
                print_warn("SSH key creation failed.")
                log_action("github-setup: SSH key", "failed")
    else:
        print_warn("No SSH key found. Re-run with --ssh to create one.")
        log_action("github-setup: SSH key", "pending", "re-run with --ssh")

    print_info("Copilot Pro+ checklist:")
    print("  1. Verify your plan: https://github.com/settings/copilot")
    print("  2. Sign in to GitHub inside VS Code (Accounts menu).")
    print("  3. The copilot + copilot-chat extensions are installed via 'python setup.py extensions'.")
    log_action("github-setup: Copilot Pro+", "info", "manual verification at github.com/settings/copilot")
    print_ok("GitHub setup finished.")


def dev_setup(args):
    """Install/verify developer environment: core tools, npm globals, Python packages."""
    print_info("== Development environment setup ==")

    for tool, hint in (
        ("git", "https://git-scm.com"),
        ("node", "https://nodejs.org"),
        ("npm", "comes with Node.js"),
        ("docker", "https://docs.docker.com/get-docker/"),
        ("code", "https://code.visualstudio.com"),
    ):
        if check_tool(tool):
            print_ok(f"Found: {tool}")
            log_action(f"dev-setup: {tool}", "ok")
        else:
            print_warn(f"Missing: {tool} ({hint})")
            log_action(f"dev-setup: {tool}", "missing", hint)

    if check_tool("npm") and not args.skip_npm:
        print_info("Installing global npm packages...")
        for pkg in NPM_GLOBAL_PACKAGES:
            res = run(["npm", "install", "-g", pkg], check=False)
            if res.returncode == 0:
                print_ok(f"npm: {pkg}")
                log_action(f"dev-setup: npm {pkg}", "ok")
            else:
                print_warn(f"npm failed: {pkg}")
                log_action(f"dev-setup: npm {pkg}", "failed")
    elif args.skip_npm:
        print_warn("Skipping npm packages (--skip-npm).")

    if not args.skip_python:
        print_info("Installing Python packages...")
        for pkg in PYTHON_PACKAGES:
            res = run([sys.executable, "-m", "pip", "install", "--user", pkg], check=False)
            if res.returncode == 0:
                print_ok(f"pip: {pkg}")
                log_action(f"dev-setup: pip {pkg}", "ok")
            else:
                print_warn(f"pip failed: {pkg}")
                log_action(f"dev-setup: pip {pkg}", "failed")
    else:
        print_warn("Skipping Python packages (--skip-python).")

    print_ok("Development environment setup finished.")


AI_PYTHON_PACKAGES = ("openai", "python-dotenv")

ENV_EXAMPLE_CONTENT = """# Copy this file to .env and fill in your real values.
# NEVER commit .env - it is blocked by the global gitignore and pre-commit hook.
OPENAI_API_KEY=your-openai-api-key-here
"""


def ai_setup(_args):
    """One AI platform, no conflicts: OpenAI SDK + safe .env scaffold + Copilot checks."""
    print_info("== AI stack setup (Copilot Pro+ + ChatGPT Pro / OpenAI SDK) ==")

    print_info("Installing OpenAI SDK Python packages...")
    for pkg in AI_PYTHON_PACKAGES:
        res = run([sys.executable, "-m", "pip", "install", "--user", pkg], check=False)
        if res.returncode == 0:
            print_ok(f"pip: {pkg}")
            log_action(f"ai-setup: pip {pkg}", "ok")
        else:
            print_warn(f"pip failed: {pkg}")
            log_action(f"ai-setup: pip {pkg}", "failed")

    env_example = WORKSPACE / "personal" / ".env.example"
    env_example.parent.mkdir(parents=True, exist_ok=True)
    if env_example.exists():
        print_ok(f"Already exists: {env_example}")
    else:
        env_example.write_text(ENV_EXAMPLE_CONTENT, encoding="utf-8")
        print_ok(f"Created safe template: {env_example}")
        log_action("ai-setup: .env.example", "ok", str(env_example))

    if check_tool("code"):
        installed = set(run(["code", "--list-extensions"], check=False).stdout.splitlines())
        for ext in ("github.copilot", "github.copilot-chat"):
            if ext in installed:
                print_ok(f"Copilot extension installed: {ext}")
                log_action(f"ai-setup: {ext}", "ok")
            else:
                print_warn(f"Copilot extension missing: {ext} (run: python setup.py extensions)")
                log_action(f"ai-setup: {ext}", "missing")
    else:
        print_warn("VS Code CLI 'code' not found. Copilot extensions not verified.")

    print_info("How Copilot Pro+ and ChatGPT Pro work together with NO conflicts:")
    print("  - Copilot Pro+ lives in VS Code/GitHub. Config = your GitHub sign-in + extensions. Nothing local to lose.")
    print("  - ChatGPT Pro lives at chatgpt.com. All projects/chats are stored on OpenAI's servers; a PC format cannot delete them.")
    print("  - The only shared local item is OPENAI_API_KEY for the SDK. Keep it in a .env file (never committed) and in a password manager.")
    print("  - Division of labor: Copilot for in-editor completions/chat on your code; ChatGPT for research, planning and long-form work.")
    print("  - Before formatting: commit+push all repos (python setup.py status), run 'python setup.py config backup', copy the backup off-disk.")
    log_action("ai-setup: advice", "info", "Copilot Pro+ + ChatGPT Pro coexistence")
    print_ok("AI stack setup finished.")


def config_backup(args):
    """Back up key config files and ~/Projects/personal into the backup directory."""
    backup_dir = Path(args.backup_dir).expanduser().resolve()
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    target = backup_dir / timestamp
    target.mkdir(parents=True, exist_ok=True)

    copied = 0
    for name in CONFIG_FILES:
        source = Path.home() / name
        if source.exists():
            shutil.copy2(source, target / name)
            print_ok(f"Backed up: {source}")
            log_action(f"config backup: {name}", "ok")
            copied += 1
        else:
            print_warn(f"Not found, skipped: {source}")
            log_action(f"config backup: {name}", "skipped", "not found")

    if PROJECTS_PERSONAL.exists():
        dest = target / "Projects-personal"
        shutil.copytree(PROJECTS_PERSONAL, dest, ignore=shutil.ignore_patterns(*IGNORE_DIRS))
        print_ok(f"Backed up projects: {PROJECTS_PERSONAL}")
        log_action("config backup: Projects/personal", "ok")
        copied += 1
    else:
        print_warn(f"Not found, skipped: {PROJECTS_PERSONAL}")

    if copied == 0:
        print_warn("Nothing was backed up.")
    else:
        print_ok(f"Backup complete: {target}")


def latest_config_backup(backup_dir):
    if not backup_dir.exists():
        return None
    candidates = sorted((p for p in backup_dir.iterdir() if p.is_dir()), key=lambda p: p.name)
    return candidates[-1] if candidates else None


def config_restore(args):
    """Restore config files and personal projects from the latest (or given) backup."""
    backup_dir = Path(args.backup_dir).expanduser().resolve()
    source = Path(args.snapshot).expanduser().resolve() if args.snapshot else latest_config_backup(backup_dir)
    if source is None or not source.exists():
        print_warn(f"No backup snapshot found under: {backup_dir}")
        return

    print_info(f"Restoring from: {source}")
    for name in CONFIG_FILES:
        stored = source / name
        if stored.exists():
            shutil.copy2(stored, Path.home() / name)
            print_ok(f"Restored: ~/{name}")
            log_action(f"config restore: {name}", "ok")

    stored_projects = source / "Projects-personal"
    if stored_projects.exists():
        PROJECTS_PERSONAL.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(stored_projects, PROJECTS_PERSONAL, dirs_exist_ok=True)
        print_ok(f"Restored projects into: {PROJECTS_PERSONAL}")
        log_action("config restore: Projects/personal", "ok")

    print_ok("Config restore complete.")


def list_github_repos(args):
    """List your GitHub repositories using the GitHub CLI."""
    if not check_tool("gh"):
        raise RuntimeError("GitHub CLI (gh) is required. Install it from https://cli.github.com and run 'gh auth login'.")

    cmd = ["gh", "repo", "list", "--limit", str(args.limit)]
    if args.owner:
        cmd.insert(2, args.owner)
    if args.visibility:
        cmd.extend(["--visibility", args.visibility])
    res = run(cmd, check=False)
    if res.returncode != 0:
        if res.stderr.strip():
            print(res.stderr.strip(), file=sys.stderr)
        raise RuntimeError("Could not list repositories. Are you logged in? Try: gh auth login")
    output = res.stdout.strip()
    if output:
        print(output)
        log_action("repos: list", "ok")
    else:
        print_warn("No repositories found.")


def summary(_args):
    """Generate a markdown summary of everything set up / restored so far."""
    lines = [
        "# Setup & Restore Summary",
        "",
        f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "",
        "## Actions",
        "",
    ]
    if LOG_FILE.exists():
        entries = LOG_FILE.read_text(encoding="utf-8").splitlines()
        if entries:
            lines.append("| Time | Status | Action | Detail |")
            lines.append("|---|---|---|---|")
            for entry in entries:
                parts = [p.strip() for p in entry.split("|")]
                while len(parts) < 4:
                    parts.append("")
                lines.append(f"| {parts[0]} | {parts[1]} | {parts[2]} | {parts[3]} |")
        else:
            lines.append("_No logged actions yet._")
    else:
        lines.append("_No logged actions yet. Run install / restore / github-setup / dev-setup first._")

    lines += [
        "",
        "## Next steps",
        "",
        "1. Open `ultimate.code-workspace` in VS Code.",
        "2. Sign in to GitHub in VS Code.",
        "3. Verify Copilot Pro+ at https://github.com/settings/copilot",
        "",
    ]
    SUMMARY_FILE.write_text("\n".join(lines), encoding="utf-8")
    print_ok(f"Summary written to: {SUMMARY_FILE}")


def _menu_edit_config():
    print("Config files:")
    for index, name in enumerate(CONFIG_FILES, start=1):
        print(f"  {index}. ~/{name}")
    choice = input("Pick a file number (or Enter to cancel): ").strip()
    if not choice.isdigit() or not 1 <= int(choice) <= len(CONFIG_FILES):
        return
    path = Path.home() / CONFIG_FILES[int(choice) - 1]
    editor = os.environ.get("EDITOR", "nano")
    if check_tool(editor):
        subprocess.run([editor, str(path)], check=False)
    else:
        print_warn(f"Editor '{editor}' not found. File path: {path}")


def _menu_view_config():
    print("Config files:")
    for index, name in enumerate(CONFIG_FILES, start=1):
        print(f"  {index}. ~/{name}")
    choice = input("Pick a file number (or Enter to cancel): ").strip()
    if not choice.isdigit() or not 1 <= int(choice) <= len(CONFIG_FILES):
        return
    path = Path.home() / CONFIG_FILES[int(choice) - 1]
    if path.exists():
        print(path.read_text(encoding="utf-8", errors="replace"))
    else:
        print_warn(f"File does not exist: {path}")


def _menu_add_alias():
    name = input("Alias name (e.g. gs): ").strip()
    command = input("Alias command (e.g. git status): ").strip()
    if not name or not command:
        print_warn("Alias name and command are both required.")
        return
    if not re.fullmatch(r"[A-Za-z0-9_-]+", name):
        print_warn("Alias name may only contain letters, numbers, '-' and '_'.")
        return
    aliases_file = Path.home() / ".bash_aliases"
    escaped = command.replace("'", "'\\''")
    with aliases_file.open("a", encoding="utf-8") as handle:
        handle.write(f"alias {name}='{escaped}'\n")
    print_ok(f"Added alias '{name}' to ~/.bash_aliases (reload your shell to use it).")
    log_action(f"menu: alias {name}", "ok")


def _menu_create_project():
    name = input("New project name: ").strip()
    if not name or not re.fullmatch(r"[A-Za-z0-9._-]+", name):
        print_warn("Project name may only contain letters, numbers, '.', '-' and '_'.")
        return
    target = PROJECTS_PERSONAL / name
    if target.exists():
        print_warn(f"Already exists: {target}")
        return
    target.mkdir(parents=True)
    if check_tool("git"):
        run(["git", "init"], check=False, cwd=str(target))
    (target / "README.md").write_text(f"# {name}\n", encoding="utf-8")
    print_ok(f"Created project: {target}")
    log_action(f"menu: project {name}", "ok")


def menu(args):
    """Interactive shell menu for config management and project actions."""
    actions = {
        "1": ("View a config file", _menu_view_config),
        "2": ("Edit a config file", _menu_edit_config),
        "3": ("Add a shell alias", _menu_add_alias),
        "4": ("Create a personal project", _menu_create_project),
        "5": ("Backup configs", lambda: config_backup(argparse.Namespace(backup_dir=str(CONFIG_BACKUP_DIR)))),
        "6": ("Restore configs", lambda: config_restore(argparse.Namespace(backup_dir=str(CONFIG_BACKUP_DIR), snapshot=None))),
        "7": ("List my GitHub repos", lambda: list_github_repos(argparse.Namespace(limit=30, owner=None, visibility=None))),
        "8": ("Write setup summary", lambda: summary(args)),
    }
    while True:
        print()
        print_info("== my-vscode-setup menu ==")
        for key, (label, _func) in actions.items():
            print(f"  {key}. {label}")
        print("  q. Quit")
        choice = input("Choose an option: ").strip().lower()
        if choice in ("q", "quit", "exit", ""):
            return
        entry = actions.get(choice)
        if entry is None:
            print_warn("Unknown option.")
            continue
        try:
            entry[1]()
        except RuntimeError as exc:
            print_error(str(exc))


def install(_args):
    ensure_workspace()
    install_git_aliases_and_defaults()
    install_global_gitignore()
    extensions(_args)
    print_ok("Install complete.")


def restore(args):
    install(args)
    print()
    if getattr(args, "full", False):
        dev_setup(argparse.Namespace(skip_npm=False, skip_python=False))
        ai_setup(args)
        config_restore(argparse.Namespace(backup_dir=str(CONFIG_BACKUP_DIR), snapshot=None))
        summary(args)
    print_ok("Restore complete.")
    print("Next steps:")
    print("1. Open 'ultimate.code-workspace' in VS Code.")
    print("2. Sign in to GitHub in VS Code.")
    print("3. Enable Settings Sync and verify Copilot Pro+ is active.")
    if not getattr(args, "full", False):
        print("4. Run 'python setup.py restore --full' to also reinstall dev tools and restore configs.")


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
    restore_p = sub.add_parser("restore", help="Full restore after PC format")
    restore_p.add_argument("--full", action="store_true", help="Also run dev-setup, restore configs and write summary")
    restore_p.set_defaults(func=restore)

    gh_p = sub.add_parser("github-setup", help="Premium GitHub setup: gh CLI, auth, SSH key, Copilot Pro+")
    gh_p.add_argument("--name", help="Git user.name to configure globally")
    gh_p.add_argument("--email", help="Git user.email to configure globally")
    gh_p.add_argument("--ssh", action="store_true", help="Create an ed25519 SSH key if missing")
    gh_p.set_defaults(func=github_setup)

    dev_p = sub.add_parser("dev-setup", help="Install/verify dev tools, npm globals and Python packages")
    dev_p.add_argument("--skip-npm", action="store_true", help="Skip global npm packages")
    dev_p.add_argument("--skip-python", action="store_true", help="Skip Python packages")
    dev_p.set_defaults(func=dev_setup)

    sub.add_parser(
        "ai-setup",
        help="AI stack: OpenAI SDK, safe .env template, Copilot extension checks, no-conflict advice",
    ).set_defaults(func=ai_setup)

    config_p = sub.add_parser("config", help="Backup/restore key config files and personal projects")
    config_sub = config_p.add_subparsers(dest="config_command", required=True)
    backup_p = config_sub.add_parser("backup", help="Backup ~/.bashrc, ~/.bash_aliases, ~/.gitconfig, ~/.nanorc, ~/Projects/personal")
    backup_p.add_argument("--backup-dir", default=str(CONFIG_BACKUP_DIR), help="Backup directory")
    backup_p.set_defaults(func=config_backup)
    restore_cfg_p = config_sub.add_parser("restore", help="Restore configs from the latest (or given) backup snapshot")
    restore_cfg_p.add_argument("--backup-dir", default=str(CONFIG_BACKUP_DIR), help="Backup directory")
    restore_cfg_p.add_argument("--snapshot", help="Specific snapshot folder to restore from")
    restore_cfg_p.set_defaults(func=config_restore)

    repos_p = sub.add_parser("repos", help="List your GitHub repositories (requires gh CLI)")
    repos_p.add_argument("owner", nargs="?", help="Owner to list repos for (default: yourself)")
    repos_p.add_argument("--limit", type=int, default=50, help="Maximum repositories to list")
    repos_p.add_argument("--visibility", choices=("public", "private", "internal"), help="Filter by visibility")
    repos_p.set_defaults(func=list_github_repos)

    sub.add_parser("menu", help="Interactive menu: configs, aliases, projects, backups, repos").set_defaults(func=menu)
    sub.add_parser("summary", help="Write markdown summary of setup/restore actions").set_defaults(func=summary)
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
