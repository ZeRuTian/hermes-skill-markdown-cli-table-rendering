#!/usr/bin/env bash
set -euo pipefail

REPO="hermes-skill-markdown-cli-table-rendering"
DESC="Hermes skill for rendering Markdown pipe tables as aligned CLI box tables"

if ! command -v gh >/dev/null 2>&1; then
  echo "gh CLI not found. Install GitHub CLI first."
  exit 1
fi

if ! gh auth status >/dev/null 2>&1; then
  echo "gh is not authenticated. Run: gh auth login"
  exit 1
fi

if gh repo view "ZeRuTian/${REPO}" >/dev/null 2>&1; then
  echo "Repository already exists: ZeRuTian/${REPO}"
else
  gh repo create "ZeRuTian/${REPO}" --public --description "${DESC}"
fi

git remote remove origin 2>/dev/null || true
git remote add origin "https://github.com/ZeRuTian/${REPO}.git"
git push -u origin main

echo "Published: https://github.com/ZeRuTian/${REPO}"
