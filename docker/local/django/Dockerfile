FROM python:3.7-alpine

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# command line + scripting tools
RUN apk add netcat-openbsd postgresql-client

# os library dependencies
RUN apk update && apk add gcc libffi-dev python3-dev py3-cryptography musl-dev postgresql-dev

# update pip and install pipenv
RUN pip install -U pip && pip install pipenv

# setup path for codebase
RUN mkdir -p /code
WORKDIR /code

# copy pipfile and install dependencies
COPY Pipfile* /code/
RUN pipenv install --dev
