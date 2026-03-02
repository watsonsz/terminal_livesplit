#!/usr/bin/env bash
set -euo pipefail

echo "== Seriphai Terminal Livesplit (Ubuntu/Debian) installer =="

sudo apt update
sudo apt install -y python3 python3-venv python3-pip

python3 -m venv venv
source venv/bin/activate

python -m pip install --upgrade pip
pip install -r requirements.txt

echo
echo "Done."
echo "Run:"
echo "  source venv/bin/activate"
echo "  python terminal_livesplit.py"
