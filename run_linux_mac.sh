#!/usr/bin/env bash
# Запуск розрахункової моделі в Linux / macOS:  bash run_linux_mac.sh
set -e
cd "$(dirname "$0")"

PY=$(command -v python3 || command -v python || true)
if [ -z "$PY" ]; then
  echo "[ПОМИЛКА] Python 3 не знайдено. Встановіть його: https://www.python.org/downloads/"
  exit 1
fi
echo "[1/3] Python: $($PY --version)"

if ! $PY -c "import numpy, scipy, matplotlib" 2>/dev/null; then
  echo "[2/3] Встановлення бібліотек..."
  $PY -m pip install -r requirements.txt
else
  echo "[2/3] Бібліотеки вже встановлено."
fi

echo "[3/3] Виконується розрахунок..."
$PY main.py --figures > results.txt
echo
echo "Готово! Таблиці: results.txt, рисунки: папка figures/"
