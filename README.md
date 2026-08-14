# Ultimate GitHub + VS Code Setup

This repository now includes the **final merged version** of your environment automation.

It combines and replaces both legacy bundles:

- `GitHub_Master_Toolkit_Bundle/`
- `Personal_GitHub_Code_Command_Center/`

Both legacy folders are intentionally kept as reference.

## Quick start

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
| `python setup.py restore` | Full restore flow (install + extensions + next steps) |

## Restore after PC format

1. Install **VS Code**, **Python 3.8+**, and **Git**
2. Clone this repository
3. Run:
   ```bash
   python setup.py restore
   ```
4. Open `ultimate.code-workspace`
5. Sign in to GitHub in VS Code

After sign-in, enable/confirm Settings Sync and Copilot Pro+.
