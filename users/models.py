import uuid
from django.conf import settings
from django.db import models
from django.utils.timezone import now
from django.contrib.postgres import fields as postgres
from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager


class UserManager(BaseUserManager):

    use_in_migrations = True

    def _create_user(self, email, password):
        email = self.normalize_email(email)
        user = self.model(email=email)
        user.set_password(password)
        return user

    def create_user(self, email, password):
        user = self._create_user(email, password)
        user.save()
        return user

    # auth-service utilizes the 'createsuperuser' manage.py command
    # however, the custom User model only uses the is_staff flag

    def create_superuser(self, email, password):
        user = self._create_user(email, password)
        user.is_staff = True
        user.save()
        return user


class User(AbstractBaseUser):
    """
        user model

        id is a unique generated UUID

        email is used as the account identifier

        verfied is set to true when email address is verified

        profile is stored as a json object
        the format of this object is described by a json schema

        status is an enumerated value, one of : active, locked, disabled

        is_staff is boolean if the user can use user management apis

        join_date / last_login / updated_at are timestamps as described

    """

    # account status choices
    STATUS_ACTIVE = 'active'
    STATUS_LOCKED = 'locked'
    STATUS_DISABLED = 'disabled'

    STATUS_CHOICES = [
        (STATUS_ACTIVE, STATUS_ACTIVE),
        (STATUS_LOCKED, STATUS_LOCKED),
        (STATUS_DISABLED, STATUS_DISABLED),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = postgres.CIEmailField(unique=True)
    verified = models.BooleanField(default=False)
    profile = postgres.JSONField(default=dict)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=STATUS_ACTIVE)
    is_staff = models.BooleanField(default=False)
    join_date = models.DateTimeField(default=now)
    last_login = models.DateTimeField(null=True, default=None)
    updated_at = models.DateTimeField(auto_now=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    EMAIL_FIELD = 'email'
    REQUIRED_FIELDS = []

    @property
    def is_active(self):
        return self.status == self.STATUS_ACTIVE

    def __str__(self):
        return str(self.id)

    def update_last_login(self):
        self.last_login = now()
        self.save(update_fields=['last_login'])

    # todo: can we access profile thru a property to auto-merge it with schema

    # todo: override save() method to merge with json schema
