from rest_framework.pagination import LimitOffsetPagination as BaseLimitOffsetPagination
from rest_framework.response import Response


class LimitOffsetPagination(BaseLimitOffsetPagination):

    default_limit = 10

    def get_paginated_response(self, results):
        return Response({
            'limit': self.limit,
            'offset': self.offset,
            'count': self.count,
            'results': results,
        })
