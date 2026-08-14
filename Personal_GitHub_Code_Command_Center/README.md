# Personal GitHub Code Command Center

This is a complete personal coding workspace system.

It is made for one purpose:

> Keep GitHub, VS Code, scripts, secrets, repo folders, and daily workflow clean forever.

This bundle gives you:

- VS Code workspace
- Clean repo categories
- Doctor checks
- Secret scanner
- Safe Git sync
- GitHub repo starter kit
- GitHub Actions workflow
- VS Code tasks
- VS Code settings
- Recommended extensions
- Shell aliases
- JSON configs
- Markdown docs
- Templates

---

## Folder system

Use this structure:

```text
~/code/
  work/
  personal/
  learning/
  experiments/
  archive/
```

Repos go inside categories:

```text
~/code/personal/my-project/
~/code/work/company-api/
~/code/learning/react-course/
```

Do not clone repos inside repos.

Wrong:

```text
my-app/
  other-repo/
```

Correct:

```text
personal/
  my-app/
  other-repo/
```

---

## First-time setup

From inside this bundle folder:

```bash
chmod +x scripts/*.sh
./scripts/setup.sh
```

Then open the VS Code workspace:

```bash
code Personal_GitHub_Command_Center.code-workspace
```

---

## Main commands

Run these from the bundle folder:

```bash
./scripts/doctor.sh
./scripts/secret-scan.sh
./scripts/sync-all.sh
./scripts/find-nested-repos.sh
```

Or in VS Code:

Open Command Palette:

```text
Ctrl+Shift+P
Tasks: Run Task
```

Then choose:

```text
Doctor
Secret Scan
Sync All Repos
Find Nested Repos
Workspace Tree
```

---

## Clone new repos cleanly

Personal repo:

```bash
./scripts/repo.sh add personal https://github.com/user/project.git
```

Work repo:

```bash
./scripts/repo.sh add work https://github.com/company/project.git
```

Custom folder name:

```bash
./scripts/repo.sh add work https://github.com/company/api.git backend-api
```

---

## Add repo starter files

Go inside any repo:

```bash
cd ~/code/personal/my-project
/path/to/Personal_GitHub_Code_Command_Center/scripts/repo-kit.sh
```

This creates safe starter files:

```text
.editorconfig
.gitattributes
.gitignore
.env.example
.github/PULL_REQUEST_TEMPLATE.md
.github/ISSUE_TEMPLATE/
```

It does not overwrite existing files.

---

## Install safety hook in a repo

Inside a repo:

```bash
/path/to/Personal_GitHub_Code_Command_Center/scripts/install-hook.sh
```

This blocks common secret mistakes before commit.

---

## Daily workflow

```bash
cd ~/code/personal/project
git status
code .
```

Work:

```bash
git add .
git commit -m "clear message"
git push
```

Health check:

```bash
./scripts/doctor.sh
```

Sync safely:

```bash
./scripts/sync-all.sh
```

---

## Rule

Stop improvising.

Use the same structure every time:

```text
workspace/category/repo
```

This is how your GitHub setup stays clean.
