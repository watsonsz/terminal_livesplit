#!/usr/bin/env bash
set -euo pipefail

echo "== Seriphai Terminal Livesplit (Arch) installer =="

sudo pacman -Syu --needed --noconfirm python python-pip

python -m venv venv
source venv/bin/activate

python -m pip install --upgrade pip
pip install -r requirements.txt

echo
echo "Done."
echo "Run:"
echo "  source venv/bin/activate"
echo "  python terminal_livesplit.py"
