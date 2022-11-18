import rest_framework.parsers
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
import rest_framework.parsers

from PB.utility import *

from ..models import *


class DeleteAmenity(APIView):
    '''
    edits amenity in db
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

    permission_classes = [IsAdminUser]

    def post(self, request: Request, *args, **kwargs):

        if not Amenity.objects.filter(pk=kwargs['pk']):
            return Response({"Amenity Does not Exist"})

        amenity = Amenity.objects.get(pk=kwargs['pk'])

        amenity.delete()
        return Response({"success": True})
