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
python setup.py restore
```

6. Open `ultimate.code-workspace`
7. Sign in to GitHub in VS Code (Settings Sync + Copilot)

## 4) Command guide

## Workspace and setup

- `python setup.py install`  
  Create `~/code/{work,personal,learning,experiments,archive}`, configure git defaults/aliases/global ignore, install extensions.

- `python setup.py restore`  
  Run full restore flow and print next steps.

- `python setup.py extensions`  
  Install or verify recommended extensions.

- `python setup.py cleanup-old`  
  Scan old legacy folders (dry run).

- `python setup.py cleanup-old --execute`  
  Move found legacy folders to backup.

## Repo operations

- `python setup.py add <category> <git-url> [name]`  
  Clone a repository into the chosen category.

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
