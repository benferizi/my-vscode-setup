# Manual: How to Use the New Merged Setup

This manual explains exactly how to move from old bundles to the new final setup.

## 1) What is the new final version

Use these root files only:

- `/home/runner/work/my-vscode-setup/my-vscode-setup/setup.py`
- `/home/runner/work/my-vscode-setup/my-vscode-setup/ultimate.code-workspace`
- `/home/runner/work/my-vscode-setup/my-vscode-setup/README.md`

Legacy folders can be backed up using `cleanup-old`.

## 2) First-time setup (recommended order)

From repo root:

```bash
cd /home/runner/work/my-vscode-setup/my-vscode-setup
```

### Step A: scan old folders (safe dry run)

```bash
python setup.py cleanup-old
```

### Step B: move old folders to backup

```bash
python setup.py cleanup-old --execute
```

Default backup folder:

- `~/my-vscode-setup-backup`

Custom backup folder:

```bash
python setup.py cleanup-old --execute --backup-dir "~/Desktop/my-setup-backup"
```

### Step C: install new merged setup

```bash
python setup.py install
```

### Step D: open the workspace

```bash
code ultimate.code-workspace
```

### Step E: sign in

In VS Code, sign in to GitHub and enable Settings Sync.
Copilot Pro+ features will activate from your GitHub account.

## 3) Restore after PC format

1. Install Git
2. Install Python 3.8+
3. Install VS Code
4. Clone this repo
5. Run:

```bash
python setup.py restore --full
```

`--full` also reinstalls dev tools/packages, restores your backed-up configs and writes `~/SETUP_SUMMARY.md`.

6. Open `ultimate.code-workspace`
7. Sign in to GitHub in VS Code (Settings Sync + Copilot)
8. Optionally run `python setup.py github-setup --name "Your Name" --email you@example.com --ssh`

## 4) Command guide

## Workspace and setup

- `python setup.py install`  
  Create `~/code/{work,personal,learning,experiments,archive}`, configure git defaults/aliases/global ignore, install extensions.

- `python setup.py restore`  
  Run full restore flow and print next steps. Add `--full` to also run `dev-setup`, restore configs and write the summary.

- `python setup.py extensions`  
  Install or verify recommended extensions.

- `python setup.py github-setup [--name NAME] [--email EMAIL] [--ssh]`  
  Premium GitHub setup: check/verify `gh` CLI and auth status, configure git identity, create an ed25519 SSH key (with `--ssh`), and show the Copilot Pro+ activation checklist.

- `python setup.py dev-setup [--skip-npm] [--skip-python]`  
  Verify core dev tools (git, Node.js, npm, Docker, VS Code) and install global npm packages (nodemon, express-generator, create-react-app, @vue/cli, typescript) plus Python packages (django, flask, requests, numpy, pandas, matplotlib).

- `python setup.py config backup [--backup-dir PATH]`  
  Backup `~/.bashrc`, `~/.bash_aliases`, `~/.gitconfig`, `~/.nanorc` and `~/Projects/personal` into a timestamped snapshot (default: `~/my-vscode-setup-backup/configs`).

- `python setup.py config restore [--backup-dir PATH] [--snapshot PATH]`  
  Restore configs and personal projects from the latest (or a given) snapshot.

- `python setup.py repos [owner] [--limit N] [--visibility public|private|internal]`  
  List your GitHub repositories using the `gh` CLI (requires `gh auth login`).

- `python setup.py menu`  
  Interactive menu: view/edit config files, add shell aliases, create personal projects, backup/restore configs, list repos, write summary.

- `python setup.py summary`  
  Write `~/SETUP_SUMMARY.md`, a markdown summary of all logged setup and restore actions (log: `~/.my-vscode-setup.log`).

- `python setup.py cleanup-old`  
  Scan old legacy folders (dry run).

- `python setup.py cleanup-old --execute`  
  Move found legacy folders to backup.

## Repo operations

- `python setup.py add <category> <git-url> [name]`  
  Clone a repository into the chosen category.

- `python setup.py new-project <name> [--category <category>]`  
  Create a brand-new project in `~/code/<category>/<name>` (default category: `personal`): creates the folder, runs `git init`, adds the kit starter files (README, .gitignore, .editorconfig, .gitattributes, .env.example, PR template) and installs the secret-blocking pre-commit hook.

- `python setup.py import <category> <path> [name]`  
  Move an existing local git repo into workspace.

- `python setup.py sync`  
  Safe pull all repos (`--ff-only`), skip dirty repos.

- `python setup.py status`  
  Show branch/origin/clean-or-dirty for each repo.

- `python setup.py tree`  
  Print workspace category tree.

- `python setup.py doctor`  
  Run health checks: tools, folders, dirty repos, upstreams, nested repos.

- `python setup.py find-nested`  
  Detect nested git repos.

## Repo safety tools (run inside a repo)

- `python setup.py kit`  
  Add starter files without overwriting existing files.

- `python setup.py hook`  
  Install pre-commit protection for common secret mistakes.

- `python setup.py secret-scan`  
  Scan current repo for common secret patterns.

## 5) Notes

- `cleanup-old` scans standard locations and only moves the two known legacy folder names.
- `cleanup-old` is dry-run by default for safety.
- If VS Code CLI `code` is not in PATH, extension installation is skipped and setup continues.
