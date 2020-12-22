#!/usr/bin/env bash

set -o errexit

root="$(dirname "$0")/.."
app="${root}/backend"

cd "${app}"

echo "apt installing"
sed -i s@/archive.ubuntu.com/@/mirrors.aliyun.com/@g /etc/apt/sources.list
sed -i s@/deb.debian.org/@/mirrors.aliyun.com/@g /etc/apt/sources.list
apt-get clean

apt-get update
apt-get install -y \
    netcat=1.10-41.1 \
    libpq-dev=11.9-0+deb10u1 \
    unixodbc-dev=2.3.6-0.1 \
    g++=4:8.3.0-1 \

echo "Innstalling dependencies"
pip install --upgrade --no-cache-dir pip setuptools -i https://pypi.tuna.tsinghua.edu.cn/simple
pip install --no-cache-dir -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

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