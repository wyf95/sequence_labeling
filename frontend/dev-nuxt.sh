#!/usr/bin/env bash

set -o errexit

root="$(dirname "$0")/.."
app="${root}/frontend"

cd "${app}"

(
  echo "Installing dependencies"
  npm install --registry https://registry.npm.taobao.org

  echo "Starting frontend server"
  npm run dev
)