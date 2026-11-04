#!/usr/bin/env bash
# eng-os one-command installer and updater for macOS, Linux and WSL.
#
#   ( [ -d ~/.eng-os ] || git clone https://github.com/tcbinfotechpvtltd/claude-development-skills.git ~/.eng-os ) && bash ~/.eng-os/install.sh
#
# Works for a private repo (git uses your GitHub login; run `gh auth login` once if git asks) and a public one.
# Installs the latest release into ~/.claude, so it applies to Claude Code in VS Code, the desktop app and the
# terminal alike. Safe to re-run: on a machine that already has eng-os it updates to the latest release.
# Optional: ENG_OS_NAME / ENG_OS_EMAIL (commit identity), ENG_OS_DIR (where the repo is kept), ENG_OS_REPO.
set -euo pipefail

REPO_URL="${ENG_OS_REPO:-https://github.com/tcbinfotechpvtltd/claude-development-skills.git}"
PAGE="https://github.com/tcbinfotechpvtltd/claude-development-skills"
say() { printf '\033[1m%s\033[0m\n' "$*"; }
die() { printf 'eng-os: %s\n' "$*" >&2; exit 1; }

command -v git >/dev/null 2>&1 || die "git is required (macOS: run 'xcode-select --install' first)"
PY="$(command -v python3 || true)"
[ -n "$PY" ] || die "python3 (3.9 or newer) is required"
"$PY" -c 'import sys; sys.exit(0 if sys.version_info >= (3, 9) else 1)' || die "python3 3.9 or newer is required"

# Reuse the repo an earlier install recorded; otherwise keep it in ~/.eng-os.
RECORDED="$("$PY" -c 'import json,os,sys; print(json.load(open(os.path.expanduser("~/.claude/eng-os/manifest.json"))).get("repo",""))' 2>/dev/null || true)"
DIR="${ENG_OS_DIR:-${RECORDED:-$HOME/.eng-os}}"

FRESH=0
if [ -d "$DIR/.git" ]; then
  say "Updating eng-os in $DIR"
  [ -z "$(git -C "$DIR" status --porcelain)" ] || die "$DIR has local changes; commit or remove them, then run this again"
  git -C "$DIR" fetch --tags --quiet origin
else
  [ ! -e "$DIR" ] || die "$DIR exists but is not an eng-os clone; move it away or set ENG_OS_DIR"
  say "Downloading eng-os into $DIR"
  git clone --quiet "$REPO_URL" "$DIR"
  FRESH=1
fi
TAG="$(git -C "$DIR" tag --list 'v*' --sort=-v:refname | head -n 1)"
[ -n "$TAG" ] || die "no release found in $REPO_URL"
# An existing clone with unreleased work of its own (another branch, or commits not on origin/main) is a
# maintainer's working copy: leave it alone. Everything else is switched to the latest release.
BRANCH="$(git -C "$DIR" symbolic-ref --quiet --short HEAD 2>/dev/null || true)"
if [ "$FRESH" = 0 ] && [ -n "$BRANCH" ] \
   && { [ "$BRANCH" != "main" ] || [ -n "$(git -C "$DIR" log --oneline origin/main..HEAD 2>/dev/null)" ]; }; then
  die "$DIR has unreleased work on branch $BRANCH (a maintainer copy), so it was left as it is. Install it with: $PY $DIR/bin/eng-os install"
fi
git -C "$DIR" checkout --quiet "$TAG"
say "Release $TAG"

# Commit identity: kept from an earlier install, else taken from git or asked once.
IDENTITY=()
if [ -n "${ENG_OS_NAME:-}" ] || [ -n "${ENG_OS_EMAIL:-}" ] || [ ! -f "$HOME/.claude/eng-os/user.json" ]; then
  NAME="${ENG_OS_NAME:-$(git config --global user.name 2>/dev/null || true)}"
  EMAIL="${ENG_OS_EMAIL:-$(git config --global user.email 2>/dev/null || true)}"
  if { [ -z "$NAME" ] || [ -z "$EMAIL" ]; } && (: < /dev/tty) 2>/dev/null; then
    if [ -z "$NAME" ]; then printf 'Your full name (used for your git commits): ' > /dev/tty; read -r NAME < /dev/tty; fi
    if [ -z "$EMAIL" ]; then printf 'Your work email (used for your git commits): ' > /dev/tty; read -r EMAIL < /dev/tty; fi
  fi
  [ -n "$NAME" ] && [ -n "$EMAIL" ] || die "your name and email are needed: set ENG_OS_NAME and ENG_OS_EMAIL, or run git config --global user.name / user.email"
  IDENTITY=(--name="$NAME" --email="$EMAIL")
fi

say "Running the self-tests"
"$PY" "$DIR/bin/eng-os" test >/dev/null || die "self-tests failed on $TAG, so nothing was installed (details: $PY $DIR/bin/eng-os test)"
"$PY" "$DIR/bin/eng-os" install ${IDENTITY[@]+"${IDENTITY[@]}"}

cat <<EOF

$(say "eng-os $TAG is installed.")
Next:
  1. Restart Claude Code (in VS Code: reload the window) so every chat picks it up.
  2. On an individual Claude plan, turn Model Improvement off: https://claude.ai/settings/data-privacy-controls
  3. Read the engineering policy: $PAGE/blob/main/docs/ENGINEERING-POLICY.md
To update later, run the same command again.
EOF
