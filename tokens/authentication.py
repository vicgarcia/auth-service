from rest_framework.authentication import get_authorization_header, BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from .models import Token


class TokenAuthentication(BaseAuthentication):

    keyword = 'Token'
    error_message = 'invalid token'

    def authenticate(self, request):
        # extract the jwt token from the request
        jwt = self.extract_jwt(request)
        if jwt:
            # fail if token is invalid, expired, or revoked
            token = Token.decode_and_lookup(jwt)
            if not token or token.expired or token.revoked:
                raise AuthenticationFailed(self.error_message)
            # successful, return user and token tuple
            return token.user, token

    def extract_jwt(self, request):
        # check the auth header for a token, proceed to next auth class if no token
        auth_header = get_authorization_header(request).split()
        if not auth_header or auth_header[0].lower() != self.keyword.lower().encode():
            return None
        # fail if header is not in proper '<keyword> <token>' format
        if len(auth_header) != 2:
            raise AuthenticationFailed(self.error_message)
        # fail if the header contains invalid characters
        try:
            token = auth_header[1].decode()
        except UnicodeError:
            raise AuthenticationFailed(self.error_message)
        # return the token string
        return token
