#!/bin/bash
set -e

# Python環境準備
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# Flutter環境準備
bash flutter_env.sh
flutter pub get

echo "✅ Setup complete."
