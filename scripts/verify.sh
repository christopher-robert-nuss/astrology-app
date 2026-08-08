#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

export PATH="/home/chris/.config/nvm/versions/node/v24.12.0/bin:$PATH"
PYTHON_BIN="${PYTHON_BIN:-/home/chris/.pyenv/versions/3.14.2/bin/python3}"

"$PYTHON_BIN" -m pytest backend/tests
(cd frontend && npm run test:run)
(cd frontend && npm run build)
