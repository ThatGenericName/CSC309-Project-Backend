import rest_framework.parsers
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
# from rest_framework_simplejwt import authentication
from django.core.validators import validate_email
from PIL import Image

from PB.utility import ValidatePhoneNumber, ValidatePicture
from accounts.models import UserExtension



class RegisterAccount(APIView):
    '''
    Views a specific account
    '''

    parser_classes = [
        rest_framework.parsers.JSONParser,
        rest_framework.parsers.FormParser,
        rest_framework.parsers.MultiPartParser
    ]
    permission_classes = []

    def post(self, request: Request, format=None):
        errors = self.ValidateData(request.data)
        if len(errors):
            return Response(errors, status=400)
        data = request.data
        user = User.objects.create_user(
            username=data['username'],
            email=data['email'],
            first_name=data['first_name'],
            last_name=data['last_name'],
            password=data['password1']
        )
        user.save()
        userExt = UserExtension.objects.create(
            user=user,
            phone_num=data['phone_num'],
        )
        userExt.save()
        return Response({"detail": 'account registered'}, status=200)

    keys = [
        'username',
        'password1',
        'password2',
        'first_name',
        'last_name',
        'email',
        'phone_num'
    ]

    req = [0, 1, 2, 3, 4, 5]

    validated_data = None

    def ValidateData(self, data) -> dict:
        errors = {}
        for i, k in enumerate(self.keys):
            if k not in data:
                if i in self.req:
                    errors[k] = "Missing Key"
                else:
                    data[k] = ""
            elif i in self.req and not len(data[k]):
                errors[k] = "This field is required"

        if 'username' not in errors:
            try:
                User.objects.get(username=data['username'])
                errors['username'] = "This username is already taken"
            except ObjectDoesNotExist:
                pass

        if 'password1' not in errors:
            if len(data['password1']) < 8:
                errors['password1'] = "Password is too short, must be at least 8 characters"
            if 'password2' not in errors:
                if data['password2'] != data['password1']:
                    errors['password2'] = "Passwords does not match"

        if 'email' not in errors:
            email = data['email']
            try:
                validate_email(email)
            except ValidationError as e:
                errors['email'] = "Enter a valid email address"

        if len(data['phone_num']):
            if not ValidatePhoneNumber(data['phone_num']):
                errors['phone_num'] = 'Enter a valid phone number'

        return errors









