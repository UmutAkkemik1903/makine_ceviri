#!/usr/bin/env zsh
# Makine Çeviri - Başlatma scripti

PROJE_KOKU="$(cd "$(dirname "$0")" && pwd)"
FRONTEND="$PROJE_KOKU/frontend"
VENV="$FRONTEND/.venv"

# Venv yoksa oluştur ve bağımlılıkları yükle
if [ ! -d "$VENV" ]; then
    echo "[INFO] Virtual environment oluşturuluyor..."
    /opt/homebrew/bin/python3.13 -m venv "$VENV"
    "$VENV/bin/pip" install -r "$FRONTEND/requirements.txt" -q
fi

echo "[INFO] Frontend başlatılıyor..."
cd "$FRONTEND" && "$VENV/bin/python" "$FRONTEND/main.py"
