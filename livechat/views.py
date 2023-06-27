from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView


class MainView(APIView):
    def get(self, request):
        pass


class RoomView(APIView):
    def post(self, request):
        pass