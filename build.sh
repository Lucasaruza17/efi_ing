#!/usr/bin/env bash
set -o errexit

pip install -r requirements.txt

python manage.py collectstatic --no-input
python manage.py migrate --no-input

# Datos de ejemplo (idempotente: no duplica) y usuario cliente_demo / demo1234
python populate.py

# Superusuario staff para administrar productos desde el front (usa DJANGO_SUPERUSER_*)
python manage.py createsuperuser --noinput || true
