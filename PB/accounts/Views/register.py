from django.contrib.auth.models import User
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework_simplejwt import authentication


# Create your views here.


class RegisterAccount(APIView):
    '''
    Views a specific account
    '''

    authentication_classes = [authentication.JWTAuthentication]

    def post(self, request, format=None):
        print(request)



