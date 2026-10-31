#!/bin/bash
# Host start command:  bash start.sh   (or simply:  python app.py)
PY=$(command -v python3 || command -v python)
$PY -m pip install --upgrade pip -q
$PY -m pip install -r requirements.txt --no-cache-dir -q
exec $PY app.py
