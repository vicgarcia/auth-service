from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK


class StatusView(APIView):

    def get(self, request, *args, **kwargs):
        return Response(status=HTTP_200_OK)
