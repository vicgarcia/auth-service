from django.conf import settings
from django.utils.timezone import now
from django.contrib.auth import authenticate
from rest_framework.views import APIView
from rest_framework.status import HTTP_200_OK, HTTP_401_UNAUTHORIZED, HTTP_400_BAD_REQUEST
from rest_framework.response import Response
from .models import Token


class LoginView(APIView):
    """
        api for login / issue token

        provide an email address + password to receive an auth tokenset
    """

    authentication_classes = ()
    permission_classes = ()

    def post(self, request, *args, **kwargs):
        email = request.data.get('email')
        password = request.data.get('password')
        if email and password:
            user = authenticate(email=email, password=password)
            if user is not None:
                token = Token.generate(request, user)
                return Response(token.auth_response(), status=HTTP_200_OK)
        return Response({'error': 'invalid login'}, status=HTTP_400_BAD_REQUEST)


class RefreshView(APIView):
    """
        api to refresh auth tokenset

        provide a refresh token to receive a renewed auth tokenset
    """

    authentication_classes = ()
    permission_classes = ()

    def post(self, request, *args, **kwargs):
        refresh = request.data.get('refresh')
        if refresh:
            token = Token.renew(request, refresh)
            if token:
                return Response(token.auth_response(), status=HTTP_200_OK)
        return Response({'error': 'invalid refresh'}, status=HTTP_400_BAD_REQUEST)


class RevokeView(APIView):
    """
        api to revoke auth tokenset

        provide a refresh token to revoke an auth tokenset
    """

    authentication_classes = ()
    permission_classes = ()

    def post(self, request, *args, **kwargs):
        refresh = request.data.get('refresh')
        if refresh:
            try:
                token = Token.objects.get(refresh=refresh)
                token.revoked = now()
                token.save()
                return Response({'success': 'token revoked'})
            except Token.DoesNotExist:
                pass
        return Response({'error': 'invalid revoke'}, status=HTTP_400_BAD_REQUEST)


class InspectView(APIView):
    """
        api to inspect a jwt access token

        provide a jwt access token to validate it's expire time
    """

    authentication_classes = ()
    permission_classes = ()

    def post(self, request, *args, **kwargs):
        # parse the jwt token provided in the request body json
        if 'token' in request.data and type(request.data['token']) == str:
            token = Token.decode_and_lookup(request.data['token'])
            # if the token was populated from the db, return a response w/ token status
            if token:
                response_json = {'valid': False}
                # when DEBUG is set, also return the decoded token payload
                if settings.DEBUG:
                    response_json['payload'] = Token.decode_payload(request.data['token'])
                if token.is_valid:
                    response_json['valid'] = True
                return Response(response_json, status=HTTP_200_OK)
        # when the token is not populated, return a 400 w/ error
        return Response({'error': 'invalid token'}, status=HTTP_400_BAD_REQUEST)
