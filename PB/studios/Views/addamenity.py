import time

import rest_framework.parsers
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.core.validators import validate_email
from django.utils import timezone
from rest_framework.generics import RetrieveAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
import rest_framework.parsers

from PB.utility import *

from ..models import *


class AddAmenity(APIView):
    '''
    adds amenity to db
    '''

    parser_classes = [
        rest_framework.parsers.JSONParser,
        rest_framework.parsers.FormParser,
        rest_framework.parsers.MultiPartParser
    ]
    keys = [
        'type',
        'quantity'
    ]

    # permission_classes = [IsAuthenticated]

    def post(self, request: Request, *args, **kwargs):
        errors = self.ValidateData(request.data)

        if len(errors):
            return Response(errors)
        data = request.data

        pk = kwargs['pk']
        amenity = Amenity.objects.create(studio=Studio.objects.get(pk=pk), type=data['type'],
                                         quantity=data['quantity'])

        amenity.save()

        return Response({"success": True})

    def ValidateData(self, data) -> dict:
        errors = {}
        for key in self.keys:
            if key not in data:
                errors[key] = "Missing Key"

        return errors
