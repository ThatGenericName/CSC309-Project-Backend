from django.core.exceptions import ObjectDoesNotExist
from django.http import FileResponse
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from PB.utility import ValidatePicture
from accounts.management.commands.runapscheduler import \
    CheckForSubscriptionRenewals
from accounts.models import UserExtension

import os
from django.conf import settings
import base64


# Create your views here.

class AdminRenew(APIView):

    permission_classes = []
    '''
    Views a specific profile picture
    '''

    def get(self, request, *args, **kwargs):
        CheckForSubscriptionRenewals()

        return Response()

