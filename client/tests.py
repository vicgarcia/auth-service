import unittest
from time import sleep
from django.conf import settings
from django.test.client import RequestFactory
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework.exceptions import AuthenticationFailed
from users.models import User
from .authentication import TokenUser, TokenAuthentication


class TokenClientTests(APITestCase):

    def setUp(self):
        self.requst_factory = RequestFactory()
        self.admin_user_credentials = {
            'email': 'admin@example.com',
            'password': 'password1234',
        }
        self.admin_user = User.objects.create_superuser(**self.admin_user_credentials)
        self.test_user_credentials = {
            'email': 'test@example.com',
            'password': 'password1234',
        }
        self.test_user = User.objects.create_user(**self.test_user_credentials)

    def test_hydrate_user_from_jwt_token(self):
        # get a token from the auth service
        auth_response = self.client \
            .post('/token/login/', self.test_user_credentials, format='json')
        token = auth_response.json()['token']
        # setup a fake request with the token in header
        auth_header = f'Token {token}'
        fake_request = self.requst_factory.get('/', {}, HTTP_AUTHORIZATION=auth_header)
        # use authentication component on fake request
        token_result = TokenAuthentication().authenticate(fake_request)
        self.assertEqual(type(token_result), tuple)
        # assert user is TokenUser type, token matches input
        user, _ = token_result
        self.assertEqual(type(user), TokenUser)
        # assert that hydrated values match the test user
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token)
        user_detail_response = self.client.get('/account/manage/', format='json')
        user_detail = user_detail_response.json()
        self.assertEqual(str(user.id), user_detail['id'])
        self.assertEqual(user.is_staff, user_detail['is_staff'])
        self.assertEqual(user.profile, user_detail['profile'])

    def test_hydrate_admin_user_from_jwt_token(self):
        # get a token from the auth service
        auth_response = self.client \
            .post('/token/login/', self.admin_user_credentials, format='json')
        token = auth_response.json()['token']
        # setup a fake request with the token in header
        auth_header = f'Token {token}'
        fake_request = self.requst_factory.get('/', {}, HTTP_AUTHORIZATION=auth_header)
        # use authentication component on fake request
        token_result = TokenAuthentication().authenticate(fake_request)
        self.assertEqual(type(token_result), tuple)
        # assert user is TokenUser type, token matches input
        user, _ = token_result
        self.assertEqual(type(user), TokenUser)
        # assert that hydrated user is an admin
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token)
        user_detail_response = self.client.get('/account/manage/', format='json')
        user_detail = user_detail_response.json()
        self.assertEqual(str(user.id), user_detail['id'])
        self.assertEqual(user.is_staff, True)

    def test_expired_token_is_rejected(self):
        # modify the settings directly to drop the token expire time to 5 seconds
        settings.AUTH_TOKEN_EXPIRE_TIME = 5
        # get a token from the auth service
        auth_response = self.client \
            .post('/token/login/', self.test_user_credentials, format='json')
        token = auth_response.json()['token']
        # wait 10 seconds for the token to expire
        sleep(10)
        # setup a fake request with the token in header
        auth_header = f'Token {token}'
        fake_request = self.requst_factory.get('/', {}, HTTP_AUTHORIZATION=auth_header)
        # use authentication component on fake request expecting failure exception
        with self.assertRaises(AuthenticationFailed):
            token_result = TokenAuthentication().authenticate(fake_request)

    def test_fail_on_invalid_token(self):
        # setup a fake request with an invalid token
        auth_header = f'Token invalid-token-string-is-not-anything'
        fake_request = self.requst_factory.get('/', {}, HTTP_AUTHORIZATION=auth_header)
        # an invalid token will throw an error
        with self.assertRaises(AuthenticationFailed):
            token_result = TokenAuthentication().authenticate(fake_request)

    def test_return_none_on_no_auth(self):
        # setup a fake request with no auth header
        auth_header = f'Token invalid-token-string-is-not-anything'
        fake_request = self.requst_factory.get('/')
        # a request without the auth header will return none
        token_result = TokenAuthentication().authenticate(fake_request)
        self.assertEqual(token_result, None)
