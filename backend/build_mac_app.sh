#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

rm -rf build dist

pip install --upgrade pyinstaller pywebview

pyinstaller desktop_main.py \
  --name "NovaMind" \
  --onedir --windowed \
  --add-data "app/static:app/static" \
  --hidden-import "uvicorn.logging" \
  --hidden-import "uvicorn.loops.auto" \
  --hidden-import "uvicorn.protocols.http.auto" \
  --hidden-import "passlib.handlers.bcrypt" \
  --hidden-import "bcrypt" \
  --hidden-import "email_validator" \
  --hidden-import "cryptography" \
  --hidden-import "jose" \
  --clean

xattr -cr dist/NovaMind.app
echo "Done."
