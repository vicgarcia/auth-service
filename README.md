**auth-service** is a proof-of-concept project for an authentication service.

At a previous job, I built an authentication service based around the [django-oauth-toolkit](https://github.com/jazzband/django-oauth-toolkit) to work within our microservice architecture. My goal with this project was to expand on ideas I've had since then for customizing the User model and using JWT tokens that could be better utilized by other services.

Some of the features in this project :

The User model utilizes email addresses as the identifier for an account instead of a username. The email address is stored case sensitive and uniqueness of email address is enforced in a case-insensitive fashion using Postgres-specific features exposed by Django.

The User model utilizes a Postgres JSONField 'profile'. This allows an arbitrary JSON object to be stored as the user profile data. When tokens are issued, this object is encrypted as part of the token and can be utilized from the token by other services.

The User model has only the 'is_staff' field, and does not also have the 'is_superuser' field typically used by Django. This was done to make the custom user model compatible with the DRF 'IsAdminUser' permission while eliminating the notion of admin/superuser which is only really relevant to integration with the Django admin system.

Tokens are issued when a user provides a valid email/password login or exchanges a valid refresh token. A access and refresh token pair (a tokenset) is issued. The access token is a json object encoded using RSA-256 public/private key encryption. The encoded payload contains token/session data and user profile data. The access token is intended to be sent on requests to seperate microservices, which would be able to decrypt the token (utilizing the RSA public key), validate the token, then access user profile data within the token.

Access tokens have a configurable short lifetime (defaulted to one hour and configured in the Django settings). Access tokens are issued with refresh tokens, which are longer lived (default has no expiration, this is after all a proof of concept), and are only used to request a new access token. Once a refresh token has been used to retrieve a new token set, that refresh token will no longer be valid.

Endpoints are provided for signup, management of account (change email, password, update profile), partial implementations of email verification and password reset, login + issue token, exchange refresh token for new tokenset, and revoke tokenset. Complete documentation of all available API endpoints can be found (here). This repository also includes a configuration file that can be imported and used with the Insomnia REST client.

The User model uses an 'is_staff' field to designate admin users. User accounts with this set to true are created using the 'createsuperuser' django manage.py command. Users with this is_staff=True flag will have access to the /admin/ APIs which can be used to manage users and tokens.

The clients subdirectory in the root of the repository contains components for use with another Django application (microservice) that would utilize tokens being issued by this service.  The TokenAuthentication component is for use with Django Rest Framework, for use as a views 'authentication_classes' value, and will populate the request.user object with an instance of the TokenUser component hydrated from the provided auth token.

### Running the Project Locally w/ Docker

clone the repository
```
git clone git@github.com:vicgarcia/auth-service.git
```

copy .env template and setup local .env file
```
cp .env.template .env
```

generate rsa key set
```
openssl genrsa -out jwt.private.key 2048
openssl rsa -in jwt.private.key -outform PEM -pubout -out jwt.public.key
```

start the development docker environment
```
docker-compose build
docker-compose up -d
```

use the django manage command to create a admin user
```
./docker/local/cli/manage createsuperuser --email admin@example.com
```

run pipenv inside of the docker container
```
./docker/local/cli/pipenv <command arguments>
```

run psql inside of the Docker environment
```
./docker/local/cli/psql
```

run tests inside of the Docker environment
```
./docker/local/cli/pytest
```

using the provided insomnia.yaml (https://insomnia.rest/) file has all of the api routes setup to make requests with the REST client

browse [documentation](https://github.com/vicgarcia/auth-service/blob/master/API.md) for the various api endpoints provided by this application

### reference

https://docs.djangoproject.com/en/3.0/ref/contrib/auth/

https://docs.djangoproject.com/en/3.0/topics/auth/customizing/

https://docs.djangoproject.com/en/3.0/ref/contrib/postgres/fields/#citext-fields

https://docs.djangoproject.com/en/3.0/topics/auth/passwords/

https://github.com/django/django/blob/master/django/contrib/auth/base_user.py

https://github.com/django/django/blob/master/django/contrib/auth/models.py

https://stackoverflow.com/questions/51327584/how-to-generate-key-pair-for-php-jwt
