from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST
from users.models import User
from tokens.authentication import TokenAuthentication, IsAuthenticated
from .serializers import SignupSerializer, ManageSerializer, \
                         ResetEmailSerializer, ResetPasswordSerializer
from .functions import encode_verification, decode_verification, \
                       send_verify_email, send_reset_email


class SignupView(APIView):
    """
        api for new user account signups

        provide an email address and password to create a new account
    """

    authentication_classes = ()
    permission_classes = ()

    def post(self, request, *args, **kwargs):
        serializer = SignupSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response({"user": user.id}, status=HTTP_200_OK)


class ManageView(APIView):
    """
        api to manage a user account

        allow user to update email, password, and profile
    """

    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        serializer = ManageSerializer(instance=request.user)
        return Response(serializer.data, status=HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        serializer = ManageSerializer(instance=request.user, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=HTTP_200_OK)


class VerifyView(APIView):
    """
        api for user email verification

        allow user to complete email verification
    """

    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        # GET request will trigger sending of verification email
        verification_string = encode_verification(request.user.id, 'verify_email')
        send_verify_email(request.user.email, verification_string)
        return Response({'success': 'verification link sent'}, status=HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        # POST request is used to return the verification code
        if 'verify_code' in request.data and type(request.data['verify_code']) == str:
            user_id = decode_verification(request.data['verify_code'], 'verify_email')
            if str(request.user.id) == user_id:
                request.user.verified = True
                request.user.save()
                success_response = {'success': 'email verified'}
                return Response(success_response, status=HTTP_200_OK)
        error_message = {'error': 'invalid request'}
        return Response(error_message, status=HTTP_400_BAD_REQUEST)


class ResetView(APIView):
    """
        api for user password reset

        allow user to complete password reset
    """

    authentication_classes = ()
    permission_classes = ()

    def get_user_by_email(self, email):
        try:
            return User.objects.get(email__iexact=email.lower(), status=User.STATUS_ACTIVE)
        except User.DoesNotExist:
            pass

    def get_user_by_id(self, user_id):
        try:
            return User.objects.get(pk=user_id, status=User.STATUS_ACTIVE)
        except User.DoesNotExist:
            pass

    def post(self, request, *args, **kwargs):
        # on the first request of the password reset flow provide 'email' to trigger reset email
        if 'email' in request.data:
            serializer = ResetEmailSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            user = self.get_user_by_email(serializer.validated_data['email'])
            if user:
                verification_string = encode_verification(user.id, 'reset_password')
                send_reset_email(user.email, verification_string)
                return Response({'success': 'reset code sent'}, status=HTTP_200_OK)
        # on the second request of the reset flow provide 'verification_code' and 'password'
        elif 'code' in request.data and type(request.data['code']) == str:
            serializer = ResetPasswordSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            user_id = decode_verification(serializer.validated_data['code'], 'reset_password')
            if user_id:
                user = self.get_user_by_id(user_id)
                if user:
                    user.set_password(serializer.validated_data['password'])
                    user.save()
                    return Response({'success': 'password updated'}, status=HTTP_200_OK)
        # return a general error message response
        error_message = {'error': 'invalid request'}
        return Response(error_message, status=HTTP_400_BAD_REQUEST)
