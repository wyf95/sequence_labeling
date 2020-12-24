#!/usr/bin/env bash

set -o errexit

root="$(dirname "$0")/.."
app="${root}/frontend"

cd "${app}"


if [[ ! -d node_modules/tui-editor ]]; then
  echo "Installing dependencies"
  npm install --save nuxt
fi

echo "Starting frontend server"
npm run dev