import unittest
from rest_framework import status
from rest_framework.test import APITestCase
from users.models import User


class LoginViewTest(APITestCase):

    def setUp(self):
        self.valid_login_request = {
            'email': 'test@example.com',
            'password': 'password1234',
        }
        self.test_user = User.objects.create_user(**self.valid_login_request)
        self.invalid_login_request = {
            'email': 'test@example.com',
            'password': 'password5678',
        }

    def test_valid_login(self):
        response = self.client \
            .post('/token/login/', self.valid_login_request, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_invalid_login(self):
        response = self.client \
            .post('/token/login/', self.invalid_login_request, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class RefreshViewTest(APITestCase):

    def setUp(self):
        self.valid_login_request = {
            'email': 'test@example.com',
            'password': 'password1234',
        }
        self.test_user = User.objects.create_user(**self.valid_login_request)

    def test_valid_refresh(self):
        # login to get a token
        response = self.client \
            .post('/token/login/', self.valid_login_request, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        token = response.json()
        # refresh the token
        refresh_request = { 'refresh': token['refresh'] }
        response = self.client \
            .post('/token/refresh/', refresh_request, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_invalid_refresh(self):
        # login to get a token
        response = self.client \
            .post('/token/login/', self.valid_login_request, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        token = response.json()
        # refresh w/ a mangled token
        refresh_request = { 'refresh': token['refresh'] + 'xxx' }
        response = self.client \
            .post('/token/refresh/', refresh_request, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class RevokeViewTest(APITestCase):

    def setUp(self):
        self.valid_login_request = {
            'email': 'test@example.com',
            'password': 'password1234',
        }
        self.test_user = User.objects.create_user(**self.valid_login_request)

    def test_valid_revoke(self):
        # login to get a token
        response = self.client \
            .post('/token/login/', self.valid_login_request, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        token = response.json()
        # revoke the token
        revoke_request = { 'refresh': token['refresh'] }
        response = self.client \
            .post('/token/revoke/', revoke_request, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_invalid_refresh(self):
        # login to get a token
        response = self.client \
            .post('/token/login/', self.valid_login_request, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        token = response.json()
        # refresh w/ a mangled token
        revoke_request = { 'refresh': token['refresh'] + 'xxx' }
        response = self.client \
            .post('/token/refresh/', revoke_request, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class InspectViewTest(APITestCase):

    def setUp(self):
        self.valid_login_request = {
            'email': 'test@example.com',
            'password': 'password1234',
        }
        self.test_user = User.objects.create_user(**self.valid_login_request)

    def test_valid_inspect(self):
        # login to get a token
        login_response = self.client \
            .post('/token/login/', self.valid_login_request, format='json')
        self.assertEqual(login_response.status_code, status.HTTP_200_OK)
        auth = login_response.json()
        # inspect the token
        inspect_request = { 'token': auth['token'] }
        inspect_response = self.client \
            .post('/token/inspect/', inspect_request, format='json')
        self.assertEqual(inspect_response.status_code, status.HTTP_200_OK)
        self.assertTrue('valid' in inspect_response.json())
