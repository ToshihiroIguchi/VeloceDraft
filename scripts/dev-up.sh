#!/bin/bash
set -e

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
LOG_DIR="$DIR/../production_artifacts/logs"

mkdir -p "$LOG_DIR"

echo "Starting Backend..."
"$DIR/backend-up.sh" > "$LOG_DIR/backend.log" 2>&1 &
BACKEND_PID=$!

echo "Starting Frontend..."
"$DIR/frontend-up.sh" > "$LOG_DIR/frontend.log" 2>&1 &
FRONTEND_PID=$!

echo "Both processes started."
echo "Backend PID: $BACKEND_PID"
echo "Frontend PID: $FRONTEND_PID"
echo "To terminate, kill these PIDs."
