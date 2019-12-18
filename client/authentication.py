import jwt
from django.conf import settings
from django.utils.timezone import now
from django.contrib.auth.models import AnonymousUser
from rest_framework.authentication import BaseAuthentication, get_authorization_header
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.permissions import IsAuthenticated, IsAdminUser


class TokenUser(AnonymousUser):
    """
        user model for use w/ JWT token auth
        used in place of the Django database-backed model
        user is populated based on content of the jwt token
    """

    def __init__(self, jwt_payload):
        self.id = jwt_payload['user']
        self.profile = jwt_payload['profile']
        self.payload = jwt_payload

    @property
    def is_authenticated(self):
        return True

    @property
    def is_anonymous(self):
        return False

    @property
    def is_active(self):
        return True

    @property
    def is_staff(self):
        return self.payload['staff'] == True


class TokenAuthentication(BaseAuthentication):
    """
        DRF authentication component for use with JWT tokens provided by auth-service server
        The component validates the JWT token and attaches a TokenUser user model to request.user
    """

    token_prefix_string = 'Token'
    invalid_token_error_message = 'invalid token'
    authentication_failed_error_message = 'authentication failed'

    def authenticate_header(self, request):
        return 'Authorization'

    def authenticate(self, request):
        token = self.extract_token(request)
        if token:
            payload = self.decode_token(token)
            if payload:
                if not self.token_is_expired(payload):
                    user = self.populate_user(payload)
                    return user, payload
            raise AuthenticationFailed(self.authentication_failed_error_message)

    def extract_token(self, request):
        # check the auth header for a token, proceed to next auth class if no token
        auth_header = get_authorization_header(request).split()
        if not auth_header or auth_header[0].lower() != self.token_prefix_string.lower().encode():
            return None
        # fail if header is not in proper '<keyword> <token>' formate
        if len(auth_header) != 2:
            raise AuthenticationFailed(self.invalid_token_error_message)
        # fail if the header contains invalid data
        try:
            token = auth_header[1].decode()
        except UnicodeError:
            raise AuthenticationFailed(self.invalid_token_error_message)
        # return the token
        return token

    def decode_token(self, token):
        try:
            return jwt.decode(token, settings.JWT_PUBLIC_KEY, algorithms=['RS256'])
            # todo: catch the correct exception types here
        except Exception:
            return None

    def token_is_expired(self, decoded_token):
        current_timestamp = int(now().strftime('%s'))
        if decoded_token['expires'] < current_timestamp:
            return True
        return False

    def populate_user(self, decoded_token):
        return TokenUser(decoded_token)



"""
The TokenUser and TokenAuthentication components are inteded for use in an external repository.

For a microservice that would be consuming the auth tokens for identifying users, the database for
this application would have no user model of it's own. The token would be use to hydrate the
TokenUser as a replacement for the Django User model.
"""
