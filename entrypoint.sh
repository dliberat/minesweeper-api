#!/bin/sh

# wait for postgres to accept connections
until pg_isready --username=${DJANGO_DB_USER} --host=${DJANGO_DB_HOST}; do
    sleep 1;
done

# python manage.py collectstatic --noinput
# python manage.py makemigrations
# python manage.py migrate

exec "$@"