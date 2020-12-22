#!/usr/bin/env bash

set -o errexit

root="$(dirname "$0")/.."
app="${root}/frontend"

cd "${app}"


if [[ ! -d node_modules/tui-editor ]]; then
  echo "Installing dependencies"
  npm install --save nuxt

  ls
  
  echo "Modiry tui-editor-Editor.js"
  rm node_modules/tui-editor/dist/tui-editor-Editor.js
  cp static/tui-editor-Editor.js node_modules/tui-editor/dist/
fi

echo "Starting frontend server"
npm run dev