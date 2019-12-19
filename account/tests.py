import unittest
from time import sleep
from rest_framework import status
from rest_framework.test import APITestCase
from users.models import User
from .functions import encode_verification, decode_verification


class SignUpViewTest(APITestCase):

    def setUp(self):
        self.valid_signup_request = {
            'email': 'test@example.com',
            'password': 'password1234',
        }
        self.invalid_email_signup_request = {
            'email': 'test@example',
            'password': 'password1234',
        }
        self.invalid_password_signup_request = {
            'email': 'test@example.com',
            'password': 'pass',
        }
        self.valid_mixed_case_signup_request = {
            'email': 'TeSt.USeR@eXAMple.com',
            'password': 'password1234',
        }

    def test_signup_with_valid_user(self):
        response = self.client \
            .post('/account/signup/', self.valid_signup_request, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_signup_error_on_existing_user(self):
        existing_user = User.objects.create_user(**self.valid_signup_request)
        response = self.client \
            .post('/account/signup/', self.valid_signup_request, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_signup_error_on_invalid_email_address(self):
        response = self.client \
            .post('/account/signup/', self.invalid_email_signup_request, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_signup_error_on_short_character_password(self):
        # assumes password validation is set to > 4 characters, default is 12
        response = self.client \
            .post('/account/signup/', self.invalid_password_signup_request, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_case_retained_in_mailbox_name(self):
        # signup with mixed case
        response = self.client \
            .post('/account/signup/', self.valid_mixed_case_signup_request, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # the signup response contains the user id, check database
        user_id = response.json()['user']
        test_user = User.objects.get(id=user_id)
        email_parts = test_user.email.split('@')
        original_parts = self.valid_mixed_case_signup_request['email'].split('@')
        self.assertEqual(email_parts[0], original_parts[0])  # email should match
        self.assertEqual(email_parts[1].lower(), original_parts[1].lower())

    def test_case_insensitive_email_duplicate(self):
        # signup with mixed case
        response = self.client \
            .post('/account/signup/', self.valid_mixed_case_signup_request, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # attempt signup with lowercase equivilent
        failing_signup_request = {
            'email': self.valid_mixed_case_signup_request['email'].lower(),
            'password': self.valid_mixed_case_signup_request['password'],
        }
        failing_signup_response = self.client \
            .post('/account/signup/', failing_signup_request, format='json')
        self.assertEqual(failing_signup_response.status_code, status.HTTP_400_BAD_REQUEST)


class ManageViewTest(APITestCase):

    def setUp(self):
        self.test_user_login = {
            'email': 'test@example.com',
            'password': 'password1234',
        }
        self.test_user = User.objects.create_user(**self.test_user_login)
        duplicate_user_login = {
            'email': 'test@example.com',
            'password': 'password1234',

        }

    def test_manage_view_requires_auth_header(self):
        # request with no auth header / token returns a 401
        resp = self.client.post('/account/manage/', {}, format='json')
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

    def _get_access_token(self, login_request):
        auth_response = response = self.client \
            .post('/token/login/', login_request, format='json')
        access_token = auth_response.json()['token']
        return access_token

    def test_password_change(self):
        # get an access token for the manage request
        access_token = self._get_access_token(self.test_user_login)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + access_token)
        # make request to update our password
        update_password_request = { 'password': 'password5678' }
        update_password_response = self.client \
            .post('/account/manage/', update_password_request, format='json')
        self.assertEqual(update_password_response.status_code, status.HTTP_200_OK)
        # unset the credentials from above
        self.client.credentials()
        # test login with new password
        new_login_request = {
            'email': self.test_user_login['email'],
            'password': update_password_request['password'],
        }
        new_login_response = response = self.client \
            .post('/token/login/', new_login_request, format='json')
        self.assertEqual(new_login_response.status_code, status.HTTP_200_OK)

    def test_profile_update(self):
        # get an access token for the manage request
        access_token = self._get_access_token(self.test_user_login)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + access_token)
        # ensure profile doesn't match prior to update
        update_profile_request = {
            'profile': {
                'name': 'Some User',
                'hometown': 'Chicago, Illinois',
            }
        }
        manage_get_response = self.client.get('/account/manage/', format='json')
        self.assertNotEqual(
            manage_get_response.json()['profile'], update_profile_request['profile']
        )
        # make request to update the profile
        update_profile_response = self.client \
            .post('/account/manage/', update_profile_request, format='json')
        self.assertEqual(update_profile_response.status_code, status.HTTP_200_OK)
        # ensure profile does match after the update
        manage_get_response = self.client.get('/account/manage/', format='json')
        self.assertEqual(
            manage_get_response.json()['profile'], update_profile_request['profile']
        )

    def test_valid_email_update(self):
        # get an access token for the manage request
        access_token = self._get_access_token(self.test_user_login)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + access_token)
        # ensure email doesn't match prior to update
        update_profile_request = { 'email': 'test.user@example.com' }
        manage_get_response = self.client.get('/account/manage/', format='json')
        self.assertNotEqual(
            manage_get_response.json()['email'], update_profile_request['email']
        )
        # make request to update the email
        update_profile_response = self.client \
            .post('/account/manage/', update_profile_request, format='json')
        self.assertEqual(update_profile_response.status_code, status.HTTP_200_OK)
        # ensure email does match after the update
        manage_get_response = self.client.get('/account/manage/', format='json')
        self.assertEqual(
            manage_get_response.json()['email'], update_profile_request['email']
        )

    def test_duplicate_email_update(self):
        # insert a user with a duplicate email to test against
        duplicate_user_login = {
            'email': 'test.user@example.com',
            'password': 'password1234',
        }
        duplicate_user = User.objects.create_user(**duplicate_user_login)
        # get an access token for the manage request
        access_token = self._get_access_token(self.test_user_login)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + access_token)
        # make request to attempt to update the email (fails)
        update_email_request = { 'email'}
        update_email_response = self.client \
            .post('/account/manage/', update_email_request, format='json')
        self.assertEqual(update_email_response.status_code, status.HTTP_400_BAD_REQUEST)


class VerificationFunctionsTest(APITestCase):

    def setUp(self):
        self.test_user_login = {
            'email': 'test@example.com',
            'password': 'password1234',
        }
        self.test_user = User.objects.create_user(**self.test_user_login)

    def test_encode_decode(self):
        salt = 'verify_email'
        # encode accepts a user id and salt, such as 'verify_email'
        verify_string = encode_verification(self.test_user.id, salt)
        # decode accepts string + salt, returns user id
        decode_user_id = decode_verification(verify_string, salt)
        # assert that the decoded user id matches
        self.assertEqual(decode_user_id, str(self.test_user.id))

    def test_decode_ttl(self):
        salt = 'reset_password'
        # encode the verify string
        verify_string = encode_verification(self.test_user.id, salt)
        # sleep for 10 seconds
        sleep(10)
        # decode accepts a ttl in seconds
        decode_user_id = decode_verification(verify_string, salt, ttl=5)
        # because ttl is 5 and 10 seconds elapsed, it should fail
        self.assertEqual(decode_user_id, None)


class VerifyViewTest(APITestCase):

    def setUp(self):
        self.test_user_login = {
            'email': 'test@example.com',
            'password': 'password1234',
        }
        self.test_user = User.objects.create_user(**self.test_user_login)

    def test_verify_view_requires_auth_header(self):
        # request with no auth header / token returns a 401
        resp = self.client.post('/account/verify/', {}, format='json')
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

    def test_valid_verifcation(self):
        # make sure the test user is unverified
        self.assertEqual(self.test_user.verified, False)
        # get an access token for the verify request
        auth_response = response = self.client \
            .post('/token/login/', self.test_user_login, format='json')
        access_token = auth_response.json()['token']
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + access_token)
        # generate a verify code
        verify_code = encode_verification(self.test_user.id, 'verify_email')
        # make verify request
        verify_request = {'verify_code': verify_code}
        resp = self.client.post('/account/verify/', verify_request, format='json')
        # check if we verified
        test_user = User.objects.get(id=self.test_user.id)
        self.assertEqual(test_user.verified, True)


class ResetView(APITestCase):

    def setUp(self):
        self.lost_credentials = {
            'email': 'test@example.com',
            'password': 'lostpassword1234',
        }
        self.test_user = User.objects.create_user(**self.lost_credentials)
        self.new_credentials = {
            'email': 'test@example.com',
            'password': 'password5678',
        }

    def test_valid_reset_password(self):
        # verify that the new password doesnt work
        login_fail = response = self.client \
            .post('/token/login/', self.new_credentials, format='json')
        self.assertEqual(login_fail.status_code, status.HTTP_400_BAD_REQUEST)
        # generate a verify code
        verify_code = encode_verification(self.test_user.id, 'reset_password')
        # make reset password request
        reset_password_request = {
            'code': verify_code,
            'password': self.new_credentials['password'],
        }
        reset_password_response = self.client \
            .post('/account/reset/', reset_password_request, format='json')
        self.assertEqual(reset_password_response.status_code, status.HTTP_200_OK)
        # verify that the new password works
        login_sucess = response = self.client \
            .post('/token/login/', self.new_credentials, format='json')
        self.assertEqual(login_sucess.status_code, status.HTTP_200_OK)
