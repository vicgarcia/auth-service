from django.contrib.auth.backends import ModelBackend
from .models import User


class AuthenticationBackend(ModelBackend):
    """
        django authentication backend for login w/ email and password

        https://docs.djangoproject.com/en/3.0/topics/auth/customizing/#writing-an-authentication-backend
    """

    def authenticate(self, request, email=None, password=None, *args, **kwargs):
        try:
            user = User.objects.get(email__iexact=email.lower())
            if user.is_active and user.check_password(password):
                user.update_last_login()
                return user
        except User.DoesNotExist:
            pass

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except ObjectDoesNotExist:
            pass
