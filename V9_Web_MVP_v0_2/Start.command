#!/bin/zsh
set -e
v9_app_dir="$(cd -- "$(dirname -- "$0")" && pwd)"
cd "$v9_app_dir"
if [[ ! -x .venv/bin/python ]]; then
  print 'First-time setup is needed. Follow the Python 3.12 instructions in README.md.'
  print 'Press Return to close.'
  read -r
  exit 1
fi
print 'Glovo Partner Insights — starting your local workspace.'
print 'Keep this window open while you use the app. Control-C stops it.'
if command -v lsof >/dev/null 2>&1 && lsof -nP -iTCP:8501 -sTCP:LISTEN >/dev/null 2>&1; then
  print 'Port 8501 is already used by another local app.'
  print 'Stop the other app with Control-C, then run this launcher again.'
  print 'Press Return to close.'
  read -r
  exit 1
fi
exec .venv/bin/python -m streamlit run app.py --server.port 8501 --server.showEmailPrompt false --browser.gatherUsageStats false
