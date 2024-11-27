#!/usr/bin/env bash

echo "Watching and running"


watchmedo auto-restart \
  --patterns="*.py" \
  --command='python -V' \
  .