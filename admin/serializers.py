from rest_framework import serializers
from users.models import User
from tokens.models import Token


class UserListSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = (
            'id',
            'email',
            'verified',
            'status',
            'last_login',
        )


class UserDetailSerializer(serializers.ModelSerializer):

    def validate_email(self, value):
        unique_email_excluding_current_user_query = User.objects \
            .filter(email__iexact=value.lower()) \
            .exclude(id=self.instance.id)
        if unique_email_excluding_current_user_query.exists():
            error_message = f"The email address '{value}' is already in use."
            raise serializers.ValidationError(error_message)
        return value

    class Meta:
        model = User
        fields = (
            'id',
            'email',
            'verified',
            'profile',
            'status',
            'last_login',
            'is_staff',
        )
        read_only_fields = (
            'id',
            'verified',
            'last_login',
            'is_staff',
        )


class TokenListSerializer(serializers.ModelSerializer):

    class Meta:
        model = Token
        fields = (
            'id',
            'user',
            'ip',
            'issued',
        )


class TokenDetailSerializer(serializers.ModelSerializer):

    class Meta:
        model = Token
        fields = (
            'id',
            'user',
            'ip',
            'issued',
            'expires',
            'revoked',
            'renewed',
            'source',
        )
        read_only_fields = (
            'id',
            'user',
            'ip',
            'issued',
            'expires',
            'revoked',
            'renewed',
            'source',
        )
