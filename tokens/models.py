import uuid
import jwt
import random
import string
from ipware import get_client_ip
from datetime import timedelta
from django.utils.timezone import now
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.db import models, IntegrityError


ALPHABET = string.ascii_uppercase + string.ascii_lowercase + string.digits


class Token(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey('users.User', related_name='+', on_delete=models.CASCADE)
    ip = models.GenericIPAddressField(null=True)
    issued = models.DateTimeField()
    expires = models.DateTimeField()
    refresh = models.CharField(max_length=64, unique=True)
    revoked = models.DateTimeField(null=True)
    renewed = models.DateTimeField(null=True)
    source = models.ForeignKey('tokens.Token', related_name='+', on_delete=models.DO_NOTHING, null=True)

    def __str__(self):
        return str(self.id)

    @property
    def expired(self):
        return now() > self.expires

    @property
    def is_valid(self):
        if self.expired:
            return False
        if self.revoked is not None:
            return False
        if self.renewed is not None:
            return False
        return True

    def encode_payload(self):
        payload = {
            'token': str(self.id),
            'expires': int(self.expires.strftime('%s')),
            'user': str(self.user.id),
            'profile': self.user.profile,
            'staff': self.user.is_staff,
        }
        encoded = jwt.encode(payload, settings.JWT_PRIVATE_KEY, algorithm='RS256')
        return encoded.decode()

    def auth_response(self):
        return {
            'user': str(self.user.id),
            'token': self.encode_payload(),
            'expires': int(self.expires.strftime('%s')),
            'refresh': self.refresh,
        }

    @classmethod
    def decode_payload(cls, token):
        try:
            return jwt.decode(token, settings.JWT_PUBLIC_KEY, algorithms=['RS256'])
        except jwt.exceptions.InvalidTokenError:
            return None

    @classmethod
    def decode_and_lookup(cls, token):
        try:
            payload = cls.decode_payload(token)
            return cls.objects.select_related('user').get(id=payload['token'])
        except (KeyError, TypeError, ObjectDoesNotExist):
            pass
        return None

    @classmethod
    def generate(cls, request, user, source=None):
        try:
            refresh = ''.join(random.SystemRandom().choice(ALPHABET) for _ in range(64))
            issued = now()
            expires = issued + timedelta(seconds=settings.AUTH_TOKEN_EXPIRE_TIME)
            ip, _ = get_client_ip(request)
            return cls.objects.create(
                user=user,
                issued=issued,
                expires=expires,
                ip=ip,
                refresh=refresh,
                source=source,
            )
        except IntegrityError:
            return cls.generate(request, user)

    @classmethod
    def renew(cls, request, refresh):
        try:
            token = cls.objects.select_related('user').get(refresh=refresh)
            if token.revoked is None and token.renewed is None:
                token.renewed = now()
                token.save()
                return cls.generate(request, token.user, token)
        except ObjectDoesNotExist:
            pass
