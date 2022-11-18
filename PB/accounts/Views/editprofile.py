import rest_framework.parsers
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
import rest_framework.parsers

from PB.utility import ValidatePhoneNumber
from accounts.models import UserExtension

# Create your views here.

KEYS = [
    'password1',
    'password2',
    'first_name',
    'last_name',
    'email',
    'phone_num'
]

EXT_DATA_FIELDS = (
    'phone_num'
)


class EditProfile(APIView):
    '''
    edits a specific profile
    '''

    parser_classes = [
        rest_framework.parsers.JSONParser,
        rest_framework.parsers.FormParser,
        rest_framework.parsers.MultiPartParser
    ]

    permission_classes = [IsAuthenticated]

    def post(self, request: Request, format=None):
        errors = self.ValidateData(request.data.dict())

        if len(errors):
            return Response(errors, status=400)

        user = request.user
        userExt = UserExtension.objects.get(user=user)
        data = self.cleanedData

        if 'password1' in data:
            user.set_password(data['password1'])
            data.pop('password1')
            if 'password2' in data:
                data.pop('password2')

        for (k, v) in data.items():
            if len(v):
                if k == 'phone_num':
                    setattr(userExt, k, v)
                else:
                    setattr(user, k, v)

        user.save()
        userExt.save()

        return Response({'detail': 'account successfully modified'}, status=200)

    cleanedData = {}

    def ValidateData(self, data: dict) -> dict:
        errors = {}
        for k in KEYS:
            if k not in data:
                errors[k] = 'This field is required'

        if len(errors):
            return errors

        if 'password1' in data:
            if 'password2' not in data:
                errors['password2'] = 'password1 was provided but password2 is missing'
            else:
                if data['password1'] != data['password2']:
                    errors['password2'] = 'The passwords do not match'

            if len(data['password1']) < 8:
                errors['password1'] = "This password is too short"

        if 'email' in data:
            if len(data['email']):
                email = data['email']
                try:
                    validate_email(email)
                except ValidationError as e:
                    errors['email'] = "Enter a valid email address"

        if 'phone_num' in data:
            if len(data['phone_num']):
                if not ValidatePhoneNumber(data['phone_num']):
                    errors['phone_num'] = 'Enter a valid phone number'

        if 'password1' in data and not len(data['password1']):
            data.pop('password1')
            if 'password2' in data:
                data.pop('password2')

        self.cleanedData = data

        return errors
