#!/usr/bin/env bash
# Wypchnięcie repo na GitHub (konto: backloghero-lang).
# 1) Utwórz PUSTE repo na https://github.com/new  (nazwa: bunkhouse-trainer, bez README).
# 2) Uruchom ten skrypt w folderze repo:
set -e
REPO_URL="https://github.com/backloghero-lang/bunkhouse-trainer.git"
git init -q 2>/dev/null || true
git add -A
git commit -m "Bunkhouse Final Table Trainer (engine + web app)" 2>/dev/null || true
git branch -M main
git remote remove origin 2>/dev/null || true
git remote add origin "$REPO_URL"
git push -u origin main
echo "Gotowe: $REPO_URL"
