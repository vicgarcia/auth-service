from django.conf import settings
from django.contrib.auth import password_validation
from rest_framework import serializers
from users.models import User


class PasswordField(serializers.CharField):
    """
        customer serializer field with validation for passwords
        includes validation against django password validation framework
    """

    def __init__(self, *args, **kwargs):
        kwargs['write_only'] = True
        self.user = None
        super().__init__(*args, **kwargs)

    def get_user(self):
        """
            get the user from the request in the serializer context

            this allows password validations to be run against a given user
            maitains compatibility with django password validation framework
        """
        if self.context:
            request = self.context.get('request')
            if request.user.is_authenticated():
                self.user = request.user
        return self.user

    def to_internal_value(self, data):
        password_validation.validate_password(data, user=self.get_user())
        return super().to_internal_value(data)


class SignupSerializer(serializers.Serializer):
    """
        serializer for use with account signup api
    """

    email = serializers.EmailField()
    password = PasswordField()

    def validate_email(self, value):
        if User.objects.filter(email__iexact=value.lower()).exists():
            error_message = f"The email address '{value}' is already in use."
            raise serializers.ValidationError(error_message)
        return value

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user


class ManageSerializer(serializers.ModelSerializer):
    """
        serializer for use with account managment api
    """

    password = PasswordField(required=False)

    def validate_email(self, value):
        unique_email_excluding_current_user_query = User.objects \
            .filter(email__iexact=value.lower()) \
            .exclude(id=self.instance.id)
        if unique_email_excluding_current_user_query.exists():
            error_message = f"The email address '{value}' is already in use."
            raise serializers.ValidationError(error_message)
        return value

    def update(self, user, validated_data):
        # update the password
        password = validated_data.pop('password', None)
        if password:
            user.set_password(password)
        # update user fields
        for attr, value in validated_data.items():
            setattr(user, attr, value)
            # when changing email, reset the verified flag
            if attr == 'email':
                user.verified = False
        # save and return
        user.save()
        return user

    # todo: validate profile dict w/ json schema

    class Meta:
        model = User
        fields = (
            'id',
            'email',
            'verified',
            'profile',
            'status',
            'password',
            'is_staff',
        )
        read_only_fields = (
            'id',
            'verified',
            'status',
            'is_staff',
        )
        extra_kwargs = {
            'email': {
                'required': False,
            },
            'profile': {
                'required': False,
            }
        }


class ResetEmailSerializer(serializers.Serializer):
    """
        serializer for use with password reset api
    """

    email = serializers.EmailField()


class ResetPasswordSerializer(serializers.Serializer):
    """
        serializer for use with password reset api
    """

    code = serializers.CharField()
    password = PasswordField()
