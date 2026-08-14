# Ultimate GitHub + VS Code Setup

This repository now includes the **final merged version** of your environment automation.

It combines and replaces both legacy bundles:

- `GitHub_Master_Toolkit_Bundle/`
- `Personal_GitHub_Code_Command_Center/`

Both legacy folders are intentionally kept as reference.

## One-command full install (after PC format)

Run this single command on a fresh machine — it clones the repo and runs the full automated setup (workspace layout, git config, VS Code extensions, dev tools, config restore, summary):

```bash
curl -fsSL https://raw.githubusercontent.com/benferizi/my-vscode-setup/main/install.sh | bash
```

Or, if you already cloned the repo (the script is *inside* the repo folder, so `cd` into it first):

```bash
cd my-vscode-setup
bash install.sh
```

> **Note:** `install.sh` only exists on `main` after this change is merged. If a fresh clone doesn't contain it, merge the PR that added it (or pull the latest `main`) first.

## Quick start

Optional cleanup first (dry run):

```bash
python setup.py cleanup-old
```

Then move old bundles to backup:

```bash
python setup.py cleanup-old --execute
```

Then run setup:

```bash
python setup.py install
```

Then open:

```bash
code ultimate.code-workspace
```

## Workspace layout

The toolkit uses:

```text
~/code/
  work/
  personal/
  learning/
  experiments/
  archive/
```

`ultimate.code-workspace` points to these folders using `~/code/...` paths. If your VS Code install does not expand `~` on your OS, edit those paths manually.

## Command reference

| Command | What it does |
|---|---|
| `python setup.py install` | First-time setup: creates workspace folders, installs Git defaults/aliases/global gitignore, installs VS Code extensions |
| `python setup.py add <category> <git-url> [name]` | Clone repo into `~/code/<category>/` |
| `python setup.py import <category> <path> [name]` | Move existing local Git repo into clean workspace |
| `python setup.py sync` | Safe sync all repos (`git pull --ff-only`), skip dirty repos |
| `python setup.py status` | Show short status for all repos |
| `python setup.py doctor` | Health checks: tools, folders, repo count, dirty repos, remotes/upstream, nested repos |
| `python setup.py tree` | Print workspace tree |
| `python setup.py find-nested` | Detect repos nested inside other repos |
| `python setup.py kit` | Add helper files in current repo without overwriting existing files |
| `python setup.py hook` | Install pre-commit hook that blocks common secret mistakes (`SKIP_GHX_HOOK=1` bypass) |
| `python setup.py secret-scan` | Basic secret scan for current repo |
| `python setup.py extensions` | Install/verify recommended VS Code extensions |
| `python setup.py github-setup [--name N] [--email E] [--ssh]` | Premium GitHub setup: gh CLI check + auth status, git identity, ed25519 SSH key, Copilot Pro+ checklist |
| `python setup.py dev-setup [--skip-npm] [--skip-python]` | Install/verify dev tools (Node, npm, Docker, VS Code), global npm packages (nodemon, express-generator, create-react-app, @vue/cli, typescript) and Python packages (django, flask, requests, numpy, pandas, matplotlib) |
| `python setup.py config backup [--backup-dir <path>]` | Backup `~/.bashrc`, `~/.bash_aliases`, `~/.gitconfig`, `~/.nanorc` and `~/Projects/personal` |
| `python setup.py config restore [--snapshot <path>]` | Restore configs and personal projects from the latest (or given) backup |
| `python setup.py repos [owner] [--limit N] [--visibility public\|private\|internal]` | List your GitHub repositories via the `gh` CLI |
| `python setup.py menu` | Interactive menu: view/edit configs, add aliases, create projects, backup/restore, list repos |
| `python setup.py summary` | Write `~/SETUP_SUMMARY.md`, a markdown summary of all logged setup/restore actions |
| `python setup.py restore` | Full restore flow (install + extensions + next steps); add `--full` to also run dev-setup, restore configs and write the summary |
| `python setup.py cleanup-old [--execute] [--backup-dir <path>]` | Scan for old legacy folders and move them to backup (dry run by default) |

## Restore after PC format

1. Install **VS Code**, **Python 3.8+**, and **Git**
2. Clone this repository
3. Run cleanup dry run:
  ```bash
  python setup.py cleanup-old
  ```
4. Move old folders to backup:
  ```bash
  python setup.py cleanup-old --execute
  ```
5. Run:
  ```bash
  python setup.py restore
  ```
6. Open `ultimate.code-workspace`
7. Sign in to GitHub in VS Code

After sign-in, enable/confirm Settings Sync and Copilot Pro+.

## Full user manual

Read the full step-by-step manual here:

- `MANUAL.md`
