import rest_framework.parsers
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

    permission_classes = [IsAuthenticated]

    def get(self, request: Request, *args, **kwargs):

        pk = kwargs['pk']
        if not Studio.objects.filter(id=pk):
            return Response({"Wrong Studio Id"})

        lst = []

        amenity = Amenity.objects.filter(studio_id=pk)

        for item in amenity:
            lst.append({
                "type": item.type,
                "quantity": item.quantity
            })

        return Response(lst)
