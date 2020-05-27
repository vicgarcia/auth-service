**auth-service** is a proof-of-concept project for an authentication service.

At a previous job, I built an authentication service based around the [django-oauth-toolkit](https://github.com/jazzband/django-oauth-toolkit) to work within our microservice architecture. My goal with this project was to expand on ideas I've had since for customizing the User model and using JWT tokens that could be utilized by other services.

Some of the features in this project :

The User model utilizes email addresses as the identifier for an account instead of a username. The email address is stored case sensitive and uniqueness of email address is enforced in a case-insensitive fashion using Postgres-specific features exposed by Django.

The User model utilizes a Postgres JSONField 'profile'. This allows an arbitrary JSON object to be stored as the user profile data. When JWT tokens are issued, this object is encrypted as part of the token and can be utilized from the token by other services.

The User model has only the typical 'is_staff' field, and does not also have the typical 'is_superuser' feature. This was done to make the custom user model compatible with the DRF 'IsAdminUser' permission while eliminating the notion of admin/superuser which is largely relevant to integration with the Django admin system.

Tokens are issued when a user provides a valid email/password login or exchanges a valid refresh token. A access and refresh token pair (a tokenset) is issued. The access token is a json object encoded using RSA-256 public/private key encryption. The encoded payload contains token/session data and user profile data. The access token is intended to be sent on requests to seperate microservices, which would be able to decrypt the token (utilizing the RSA public key), validate the token, then access user profile data within the token.

Access tokens have a configurable short lifetime (defaulted to one hour and configured in the Django settings). Access tokens are issued with refresh tokens, which are longer lived (default has no expiration, this is after all a proof of concept), and are only used to request a new access token. Once a refresh token has been used to retrieve a new token set, that refresh token will no longer be valid.

Endpoints are provided for signup, management of account (change email, password, update profile), partial implementations of email verification and password reset, login + issue token, exchange refresh token for new tokenset, and revoke tokenset.

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

import the insomnia.json file and configure environment

https://insomnia.rest/

using the provided insomnia.yaml file has all of the api routes setup to make requests with the REST client.


## APIs


#### /account/signup/

provide an email address and password to create a new account

authentication is not required

request is a POST with json body
```
{
  "email": "test@example.com",
  "password": "password1234"
}
```

response is a 200 with json body on success
```
{
  "user": "2618f1bb-24e7-45ce-83c1-269043acf392"
}
```

response is a 400 with json body on error
```
{
  "email": [
    "The email address 'test@example.com' is already in use."
  ],
  "password": [
    "This password is too short. It must contain at least 12 characters."
  ]
}
```

---


#### /account/manage/

allow user to update email, password, and profile

authentication required via access token in header

GET request returns 200 response with json body
```
{
  "id": "54a802c7-d4ba-4cdf-aaee-b1e6b0e8b8a6",
  "email": "test@example.com",
  "verified": false,
  "profile": {
    "name": "Test User",
    "hometown": "Miami, Florida"
  },
  "status": "active"
}
```

POST request is made with json body
```
{
  "email": "test@example.com",
  "password": "password1234",
  "profile": {
    ... arbitrary json object ...
  }
}
```

all fields are optional, any combination can be provided

response is a 200 with json body on success
```
success response matches that of the GET request
```

response is a 400 with json body on error
```
{
  "email": [
    "The email address 'test@example.com' is already in use."
  ],
  "password": [
    "This password is too short. It must contain at least 12 characters."
  ]
}
```

---


#### /account/verify/

provide endpoints for user email address verification

authentication required via access token in header

to perform verification, an email would be sent with a verification code to the user's email address. the code would ideally be used with a link that would return the code in the url for use by a web app to make the second step request.

this feature is only partially implemented in this project

GET request returns 200 response with json body
```
{
  "success": "verification link sent"
}
```

once the verification code is created, a request is made to return the code. when the returned code is valid, the user will be updated to verified = true.

POST request is made with json body
```
{
  "verify_code": "IjU0YTgwMmM3LWQ0YmEtNGNkZi1hYWVlLWIxZTZiMGU4YjhhNiI.XecpVg.hWK0T4BiqZptt2TPaVv4_rdU1uw"
}
```

response is a 200 with json body on success
```
{
  "success": "email verified"
}
```

response is a 400 with json body on error
```
{
  "error": "invalid request"
}
```

---


#### /account/reset/

provide endpoints for password reset flow

this feature is only partially implemented in this project

authentication is not required

the first POST request is made with a json body
```
{
  "email": "test@example.com"
}
```


to perform verification, an email would be sent with a verification code to the user's email address. the code would ideally be used with a link that would return the code in the url for use by a web app to make the second step request.

response is a 200 with json body on success
```
{
  "success": "reset code sent"
}
```

this request will trigger sending of

response is a 400 with json body on error
```
{
  "error": "invalid request"
}
```

the second POST request is made with a json body
```
{
  "code": "IjU0YTgwMmM3LWQ0YmEtNGNkZi1hYWVlLWIxZTZiMGU4YjhhNiI.Xecrrg.tPwO4M7xwh_PKFJQVrBn17VP1ww",
  "password": "password1234"
}
```

successful when provided a proper code and valid password

---


#### /token/login/

provide an email address + password to receive an auth tokenset

authentication is not required

request is a POST with json body
```
{
  "email": "test@example.com",
  "password": "password1234"
}
```

response is a 200 with json body on success
```
{
  "user": "959dbe04-e60f-47f5-9c3b-77067f585315",
  "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJ0b2tlbiI6IjkyMGQ4ZTA5LWRjYTEtNGZlYy1hMzRiLTk3NGEzODc2NjkzYyIsImV4cGlyZXMiOjE1NzU3Nzc4OTMsInVzZXIiOiI5NTlkYmUwNC1lNjBmLTQ3ZjUtOWMzYi03NzA2N2Y1ODUzMTUiLCJwcm9maWxlIjp7Im5hbWUiOiJUZXN0IFVzZXIiLCJob21ldG93biI6Ik1pYW1pLCBGbG9yaWRhIn0sInN1cGVydXNlciI6ZmFsc2V9.LGE8M6mBUP_zNhy6OJuUATJCaiK86xkWygH-Oz0sYfJLkvEAkXU78J31S3OqqJFe_dNOOAcomcZYfIgygvV3UBQ9OZAl26vV4VSXrlXQhIkWdFViKtOBA61JRLRF4I1COChp7vfJ_hRGBeJpd_FE7IERjLdjS0VmqCN3siJ6v_pYEAfIGR5T1HQjkNu8Qng_macszPO5K9C16nOSOv1md105y7uusRq4uoSN1A1D6BfDNce2JEOMNReTfCfhVHbiEPQUvLmUmjzq0lBym3VA2PKWlRleyTFOtmtJK7ircLjt2OC0RwhUYv0Lxk1PrtEYdDrMhvTeyjlHe6xfy37WijfocVc4_gT9xyft1DoKcH0OcdWFwG9bpjZB_za2aPfvV1Y3jeQEQEsgRQrVgZLzEn2BUsZfkSz2ggFhrk8pbMICnAoLboT4mSFoNb1JrgX-y10oevLhJmx3NT0hDvKFEviMSKB7NakZkBXUOCj9Na-GtV3fnJLArJIOkPVMo_aynNnQPuBrbi5aPGEXeA56BEEy76YMNsr066s7D5V8ycpVtMRlWP56ZkXiRWwXDB8TFnykN8n9DSnXZwojfsT6Uh7KDPuJuJDogu3E094G-x7CVS84650MuZpGjal6gdG9c_-BL4T6wLPQcfdheadx6JEyAJUNupXhdb8vHm4Nvtw",
  "expires": 1575777893,
  "refresh": "SOU8gzlkLZN0YhE8ctNmEOkRwS7TKPz6hhmLikmTCv6zKthSx76uDCeGdC6tz2Tt"
}
```

response is a 400 with json body on error
```
{
  "error": "invalid login"
}
```

---


#### /token/refresh/

provide a refresh token to receive a renewed auth tokenset

authentication is not required

request is a POST with json body
```
{
  "refresh": "g0TyhaNxCNn8nxTu6ffthdRpe1sFTAPf1s7AsP5hCQNsNH0BogEYI99eXvqEf9uE"
}
```

response is a 200 with json body on success
```
{
  "user": "959dbe04-e60f-47f5-9c3b-77067f585315",
  "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJ0b2tlbiI6IjExZTdjMTllLWI3YjItNGYzZC05MmVjLTUwMTJjZmY0Y2IzNiIsImV4cGlyZXMiOjE1NzU3Nzc4OTYsInVzZXIiOiI5NTlkYmUwNC1lNjBmLTQ3ZjUtOWMzYi03NzA2N2Y1ODUzMTUiLCJwcm9maWxlIjp7Im5hbWUiOiJUZXN0IFVzZXIiLCJob21ldG93biI6Ik1pYW1pLCBGbG9yaWRhIn0sInN1cGVydXNlciI6ZmFsc2V9.vYejyeKe5dGQVdTQiNNXq-VOm4f8hywIw87iQSkamoiqrh1fQ-9Dxtg11kWjVah9XsuTGfLlEqAE3SWfZ1KfeTOvbuYPyRBk8m55c2UTTgWHaHr1StJzTZwBObq4Kc95gBIEk9vq3vLX4wuxeRx1lSL3D41p0dZ8Q803HzNr-iCfBaqXdFB682Fqg7omOkED9sJ2QSS8cRUPhJLFk7FZx5vrK03EQfIil9GKRnBpJKiXF4XZmr6Gz1qWJUMrN18V99IYr4KKtyEzDHmWUaZUEaOEoEs3fTPFL3Fx3RPzZhgw5yjE1lWZF46QY8Ac9z_u3aqKs2HxLR7YjkrUqMztg3rOxO13lGlXY8SuscILYgoWwDuHr7vWZz2F9XZpEUk5IxEVf5tOb8pyK7pX92XzkxUDJi1wnbWyZFIf0WbAym8H3jj9TL6u0CB6QYaQG9ZXuuflbcMp1mStP_SWu1O6dgJQpnYL-KTW7xtAllmpyIxLIoOZNdgMQrJLv7In7RNgTBwwqPQWOuvqkGHF0RhApB-qrOfppNtWaUCz0NySMUUfYfvYfrqtjKH9EOFHMzkjI5Q-g297aZgHGHjOqNhSFO1XLjiUC72tPXGXVT_rGkHJVswPH07g0fxO6eDcQlUSWT8QRrHo_a64bqdCoJL8TMVFxytBDYeKhB5Gf4FeF_Y",
  "expires": 1575777896,
  "refresh": "f0TzHTY9jglQygRrcUitiuaN6njiNtO1uXc27vjEsCkeGdg5Pu9PADoK8TdyDKnq"
}
```

response is a 400 with json body on error
```
{
  "error": "invalid refresh"
}
```

---


#### /token/revoke/

provide a refresh token to revoke an auth tokenset

authentication is not required

request is a POST with json body
```
{
  "refresh": "g0TyhaNxCNn8nxTu6ffthdRpe1sFTAPf1s7AsP5hCQNsNH0BogEYI99eXvqEf9uE"
}
```

response is a 200 with json body on success
```
{
  "success": "token revoked"
}
```

response is a 400 with json body on error
```
{
  "error": "invalid revoke"
}
```

---


#### /token/inspect/

provide a jwt access token to validate it's expire time

authentication is not required

request is a POST with json body
```
{
  "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJ0b2tlbiI6IjAyMTU1ZTlkLTkwODItNDJmYS1iZGQ3LTdhZGMzZGQ4NThiMCIsImV4cGlyZXMiOjE1NzU3Nzc3NDksInVzZXIiOiI5NTlkYmUwNC1lNjBmLTQ3ZjUtOWMzYi03NzA2N2Y1ODUzMTUiLCJwcm9maWxlIjp7Im5hbWUiOiJUZXN0IFVzZXIiLCJob21ldG93biI6Ik1pYW1pLCBGbG9yaWRhIn0sInN1cGVydXNlciI6ZmFsc2V9.i-Lsl5NAJb9CSHNkSOnMqy61TC2ijJxoZRHuEm3rNhFmDBKZvnZ9_PFy_ngr0kgXYI3a8DkYJ3RY_1lzZgiP1qAG0Nqj1KM4i2syWxtOJnFxXUXOAuIdlka_NWMoghvDmfn_f7sabaCM3uBaUFwe65voXwuo3juMdzHJxfDTunuE76BixKY0KeBbH2kfk16NaioH7hsHmiJbcM37Hq_05tgK2YOYuca5HX8o7RjJ891OXyISpchDkCrK7rwH03DqHZPBqK57W6uBNJTsq7xPjipMI_tdKH3oyQmS3qqc3EebIZcg52jId-Gg1wdtziHyE-LP3ZGTTeVV2Tn4Ia9y9zxIOP6nrOGY7a8sW8R_B8ox7FgLj5FliPrHZLv9iZCB36WwMUCOArvBIDTsUSf28_Vq4twu2NNZL8Ps_kitKleuDvVOaOrY64z2J4OeSf8_UnsTtTKK5kiDf4rKgSHNQ0vOA7H0nkkc-TVC_bTQN8KyJ2-0-CdqpIpQVdp1c8iKcwh-Z6KDIDNk1JJQGCUlkPyyK2klssCHkvTysTxNZjhVGFp0CRrbfEAkmA2ysuD7cPb-4gXjuJTbWBUhswzyqdwaFIfuRmUPLzd6lNGf-LqDD3yACkXVbFX3CfNtTaEHQoxnQ1KrkE-B72EFLxsSjIKWT3JNI70fPO5RbNBALAs"
}
```

response is a 200 with json body on success

when a token is valid
```
{
  "active": true,
  "expires": 1575777749
}
```

when a token is not valid
```
{
  "active": false
}
```

response is a 400 with json body on error
```
{
  "error": "invalid token"
}
```

---


#### /admin/users/

allow admin users to query users

authentication required via access token in header

endpoint is restricted to accounts with the is_staff = True flag

accounts with this permission can only be created using the 'createsuperuser' django manage.py command

GET request returns 200 response with json body
```
{
  "limit": 10,
  "offset": 0,
  "count": 4,
  "results": [
    {
      "id": "1cc73d71-9e0d-4ffb-ba85-f028b83d49ec",
      "email": "teSt@example.com",
      "verified": false,
      "status": "active",
      "last_login": null
    },
    ...
  ]
}
```

results are paginated, pagination is controlled via 'limit' and 'offset' query parameters

users can be searched by email address using the 'search' query parameter

response is a 403 with json body on error
```
{
  "detail": "You do not have permission to perform this action."
}
```

---


#### /admin/users/{user_id}/

allow admin users to retrieve and manage users

authentication required via access token in header

endpoint is restricted to accounts with the is_staff = True flag

GET request returns 200 response with json body
```
{
  "id": "c66ef82f-b7b8-43a3-a7a1-295c2b258396",
  "email": "test@example.com",
  "verified": false,
  "profile": {
    "name": "Some User",
    "hometown": "Miami, Florida"
  },
  "status": "active",
  "last_login": "2019-12-19 03:14:23",
  "is_staff": false
}
```

PATCH request is made with json body
```
{
  "email": "admin@example.com",
  "profile": {
    "name": "Some User",
    "hometown": "Chicago, Illinois"
  }
}
```

the 'email', 'status', and 'profile' fields can be updated

all fields are optional, any combination can be provided

response is a 200 with json body on success
```
success response matches that of the GET request
```

response is a 400 with json body on error
```
{
  "email": [
    "A user with this email already exists."
  ]
}
```

---


#### /admin/tokens/

allow admin users to query tokens

authentication required via access token in header

endpoint is restricted to accounts with the is_staff = True flag

GET request returns 200 response with json body
```
{
  "limit": 10,
  "offset": 0,
  "count": 9,
  "results": [
    {
      "id": "e7b1e11c-9616-4409-9008-3c604081f8b4",
      "user": "c66ef82f-b7b8-43a3-a7a1-295c2b258396",
      "ip": "172.21.0.1",
      "issued": "2019-12-19 02:48:31",
      "expires": "2019-12-19 02:53:31",
      "revoked": null,
      "renewed": null,
      "source": null
    },
    ...
  ]
}
```

results are paginated, pagination is controlled via 'limit' and 'offset' query parameters

tokes for a user can be searched by email address using the 'search' query parameter

response is a 403 with json body on error
```
{
  "detail": "You do not have permission to perform this action."
}
```

---


#### /admin/tokens/{token_id}/

allow admin users to retrieve and manage tokens

authentication required via access token in header

endpoint is restricted to accounts with the is_staff = True flag

GET request returns 200 response with json body
```
{
  "id": "e7b1e11c-9616-4409-9008-3c604081f8b4",
  "user": "c66ef82f-b7b8-43a3-a7a1-295c2b258396",
  "ip": "172.21.0.1",
  "issued": "2019-12-19 02:48:31",
  "expires": "2019-12-19 02:53:31",
  "revoked": "2019-12-19 03:03:31",
  "renewed": null,
  "source": null
}
```

DELETE request returns 204 response with empty body

tokens will be marked as revoked (not deleted)

---


### reference

https://docs.djangoproject.com/en/3.0/ref/contrib/auth/

https://docs.djangoproject.com/en/3.0/topics/auth/customizing/

https://docs.djangoproject.com/en/3.0/ref/contrib/postgres/fields/#citext-fields

https://docs.djangoproject.com/en/3.0/topics/auth/passwords/

https://github.com/django/django/blob/master/django/contrib/auth/base_user.py

https://github.com/django/django/blob/master/django/contrib/auth/models.py

https://stackoverflow.com/questions/51327584/how-to-generate-key-pair-for-php-jwt
