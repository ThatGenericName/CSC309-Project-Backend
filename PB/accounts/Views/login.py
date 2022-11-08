import rest_framework.parsers
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token


class Login(APIView):

    parser_classes = [
        rest_framework.parsers.JSONParser,
        rest_framework.parsers.FormParser,
        rest_framework.parsers.MultiPartParser
    ]

    permission_classes = []

    def post(self, request: Request, format=None):
        errors = self.ValidateData(request.data)

        if len(errors):
            return Response(errors)
        data = request.data

        user = authenticate(
            username=data['username'],
            password=data['password']
        )
        if user is None:
           return Response({"error": "The Username or Password is invalid"})

        if request.auth is not None:
            request.auth.delete()

        try:
            user.auth_token.delete()
        except ObjectDoesNotExist:
            pass

        token = Token.objects.create(user=user)

        return Response({"token": token.key})

    def ValidateData(self, data) -> dict:
        errors = {}
        if "username" not in data or not len(data['username']):
            errors['username'] = "This field is required"
        if "password" not in data or not len(data['password']):
            errors['password'] = 'this field is required'

        return errors

