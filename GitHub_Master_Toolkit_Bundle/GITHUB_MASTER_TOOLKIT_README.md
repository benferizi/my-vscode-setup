# GitHub Master Toolkit

This is your clean GitHub system.

You were using GitHub for a long time, but the problem was not GitHub.  
The problem was folder chaos, no repeatable workflow, and no safety checks.

This toolkit fixes that.

---

## What this gives you

- One clean workspace: `~/code`
- Categories: `work`, `personal`, `learning`, `experiments`, `archive`
- One command to clone repos cleanly
- One command to import old messy repos
- One command to sync all repos safely
- One command to check repo health
- Detection for repos accidentally cloned inside other repos
- Git aliases
- Shell aliases
- Global hidden `.gitignore`
- Hidden helper files for each repo
- Pre-commit hook to block accidental secrets
- Basic secret scanner

---

## Files in this bundle

```text
github-master-toolkit.sh
GITHUB_MASTER_TOOLKIT_README.md
```

After install, the script becomes available as:

```bash
ghx
```

---

## First-time install

Put `github-master-toolkit.sh` somewhere safe, then run:

```bash
chmod +x github-master-toolkit.sh
./github-master-toolkit.sh install
```

Then restart your terminal.

Or run:

```bash
source ~/.bashrc
```

For Zsh/macOS:

```bash
source ~/.zshrc
```

---

## Your clean structure

The script creates:

```text
~/code/
  work/
  personal/
  learning/
  experiments/
  archive/
```

Correct:

```text
~/code/personal/my-project/
~/code/work/company-api/
~/code/learning/react-practice/
```

Wrong:

```text
~/code/my-project/other-repo/
```

Repos should be siblings, not nested.

---

## Clone a new repo

Personal:

```bash
ghx add personal https://github.com/user/project.git
```

Work:

```bash
ghx add work https://github.com/company/project.git
```

Custom folder name:

```bash
ghx add work https://github.com/company/api.git backend-api
```

---

## Import old messy repos

If you already have an old repo somewhere:

```bash
ghx import personal ~/Downloads/old-project
```

For work:

```bash
ghx import work ~/Desktop/company-api
```

This moves the repo into the clean workspace.

---

## Sync everything safely

```bash
ghx sync
```

This only pulls repos that are clean.

If a repo has local changes, it skips it so your work does not get damaged.

---

## Check status of all repos

```bash
ghx status
```

---

## Full health check

```bash
ghx doctor
```

This checks:

- Git installation
- GitHub CLI if installed
- workspace folders
- repo count
- dirty repos
- missing remotes
- missing upstream branches
- nested repos

---

## Show workspace tree

```bash
ghx tree
```

---

## Find nested repos

```bash
ghx find-nested
```

If it prints nested repos, fix them.  
Do not keep repos inside repos unless you intentionally use submodules.

---

## Install hidden helper files inside a repo

Go inside a repo:

```bash
cd ~/code/personal/my-project
ghx kit
```

This creates files like:

```text
.editorconfig
.gitattributes
.gitignore
.env.example
README.md
.github/PULL_REQUEST_TEMPLATE.md
.github/ISSUE_TEMPLATE/
```

It does not overwrite existing files.

---

## Install safety pre-commit hook

Inside a repo:

```bash
ghx hook
```

This helps block accidental commits of:

- `.env`
- private keys
- common token patterns
- obvious secret patterns

To bypass only for a false positive:

```bash
SKIP_GHX_HOOK=1 git commit
```

Do not use bypass as a habit.

---

## Basic secret scan

Inside a repo:

```bash
ghx secret-scan
```

This is not perfect, but it catches common mistakes.

---

## Useful shell aliases

After install:

```bash
ghcode       # cd ~/code
ghwork       # cd ~/code/work
ghpersonal   # cd ~/code/personal
ghlearn      # cd ~/code/learning
ghexp        # cd ~/code/experiments

ghs          # ghx status
ghsy         # ghx sync
ghd          # ghx doctor
ght          # ghx tree
ghn          # ghx find-nested

gs           # git status --short
glg          # git log --oneline --graph --decorate --all
gpl          # git pull --ff-only
gps          # git push
```

---

## Useful Git aliases

After install:

```bash
git st
git sw
git br
git cm "message"
git lg
git last
git unstage file.txt
git undo
git save "message"
git pop
```

---

## Normal daily workflow

Clone:

```bash
ghx add personal https://github.com/user/project.git
```

Work:

```bash
cd ~/code/personal/project
code .
```

Check:

```bash
gs
```

Commit:

```bash
git add .
git cm "clean update"
git push
```

Sync all repos:

```bash
ghsy
```

Health check:

```bash
ghd
```

---

## Important rule

Do not improvise folder placement every time.

Use:

```text
workspace/category/repo
```

Every time.

That is the system.
