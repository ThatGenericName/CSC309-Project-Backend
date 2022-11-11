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


class ListAmenity(APIView):
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

    def get(self, request: Request, *args, **kwargs):

        data = request.data

        pk = kwargs['pk']
        lst = []

        amenity = Amenity.objects.filter(studio_id=pk)

        for item in amenity:
            lst.append({
                "type": item.type,
                "quantity": item.quantity
            })

        # amenity.save()

        return Response(lst)
