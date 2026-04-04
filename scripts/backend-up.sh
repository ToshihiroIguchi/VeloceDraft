#!/bin/bash
set -e
cd "$(dirname "$0")/../app_build/backend"
../../.venv/bin/python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
