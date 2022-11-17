import rest_framework.parsers
from django.contrib.auth.models import Group, User
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.core.validators import validate_email
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
import rest_framework.parsers

from PB.utility import ValidatePhoneNumber
from accounts.models import UserExtension

# Create your views here.


class SetUserCoach(APIView):
    '''
    edits a specific profile
    '''

    parser_classes = [
        rest_framework.parsers.JSONParser,
        rest_framework.parsers.FormParser,
        rest_framework.parsers.MultiPartParser
    ]

    permission_classes = [IsAdminUser]

    def get(self, request: Request, *args, **kwargs):
        userId = kwargs['user_id']

        try:
            user = User.objects.get(id=userId)
            group, created = Group.objects.get_or_create(name='Coach')
            group.user_set.add(user)
        except ObjectDoesNotExist:
            return Response({"error": "User does not exist"}, status=404)

        return Response({'detail': "User has been set as a coach"}, status=200)

    def delete(self, request, *args, **kwargs):
        userId = kwargs['user_id']

        try:
            user = User.objects.get(id=userId)
            group, created = Group.objects.get_or_create(name='Coach')
            group.user_set.remove(user)
        except ObjectDoesNotExist:
            return Response({"detail": "User does not exist"}, status=404)

        return Response({'detail': 'User has been removed as a coach'}, status=200)
