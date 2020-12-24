#!/usr/bin/env bash

set -o errexit

root="$(dirname "$0")/.."
app="${root}/backend"

cd "${app}"

echo "Initializing database"
python manage.py makemigrations
python manage.py migrate
python manage.py create_roles

echo "Creating admin"
if [[ -n "${ADMIN_USERNAME}" ]] && [[ -n "${ADMIN_PASSWORD}" ]] && [[ -n "${ADMIN_EMAIL}" ]]; then
  python manage.py create_admin \
    --username "${ADMIN_USERNAME}" \
    --password "${ADMIN_PASSWORD}" \
    --email "${ADMIN_EMAIL}" \
    --noinput \
  || true
fi

echo "Starting django"
gunicorn --bind="0.0.0.0:${PORT:-8000}" --workers="${WORKERS:-4}" backend.wsgi --timeout 300