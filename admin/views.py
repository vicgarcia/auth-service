from django.utils.timezone import now
from rest_framework.response import Response
from rest_framework.routers import SimpleRouter
from rest_framework.filters import SearchFilter
from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import (ListModelMixin,
                                   RetrieveModelMixin,
                                   UpdateModelMixin,
                                   DestroyModelMixin)
from users.models import User
from tokens.authentication import TokenAuthentication, IsAdminUser
from tokens.models import Token
from .pagination import LimitOffsetPagination
from .serializers import UserListSerializer, UserDetailSerializer, TokenDetailSerializer


class UserViewSet(GenericViewSet, ListModelMixin, RetrieveModelMixin, UpdateModelMixin):
    """
        api for managing users

        provides list, retrieve, update

        exposed only to staff
    """

    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAdminUser,)

    queryset = User.objects.all().order_by('-join_date')
    serializer_class = UserDetailSerializer
    pagination_class = LimitOffsetPagination
    filter_backends = (SearchFilter,)
    search_fields = ('email',)

    def list(self, request, *args, **kwargs):
        self.serializer_class = UserListSerializer
        return super().list(request, *args, **kwargs)

user_router = SimpleRouter()
user_router.register('', UserViewSet, basename='users')


class TokenViewSet(GenericViewSet, ListModelMixin, RetrieveModelMixin, DestroyModelMixin):
    """
        api for managing tokens

        provides list, retrieve, revoke

        exposed only to staff
    """

    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAdminUser,)

    queryset = Token.objects.all().order_by('-issued')
    serializer_class = TokenDetailSerializer
    pagination_class = LimitOffsetPagination
    filter_backends = (SearchFilter,)
    search_fields = ('user__email',)

    def perform_destroy(self, instance):
        # revoke the token
        instance.revoked = now()
        instance.save(update_fields=['revoked'])

token_router = SimpleRouter()
token_router.register('', TokenViewSet, basename='tokens')
