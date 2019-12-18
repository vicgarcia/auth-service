#!/bin/sh

# change to application root
cd /code

# install dependencies
pipenv install --dev

# wait for postgres container to start
while ! nc -z auth-service-postgres-local 5432; do
    echo "postgres is unavailable. waiting ..." && sleep 20
done
echo "postgres is up" && sleep 10

# run migrations
pipenv run python manage.py migrate

# start dev server
pipenv run python debug.py runserver 0.0.0.0:8000
