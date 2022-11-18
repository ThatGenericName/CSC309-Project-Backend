import rest_framework.parsers
from rest_framework.permissions import IsAdminUser, IsAuthenticated
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

    permission_classes = [IsAdminUser]

    def post(self, request: Request, *args, **kwargs):

        pk = kwargs['pk']
        if not Studio.objects.filter(id=pk):
            return Response({"Wrong Studio Id"})

        errors = self.ValidateData(request.data)

        if len(errors):
            return Response(errors)
        data = request.data


        amenity = Amenity.objects.create(studio=Studio.objects.get(pk=pk), type=data['type'],
                                         quantity=data['quantity'])

        amenity.save()

        return Response({"success": True})

    def ValidateData(self, data) -> dict:
        errors = {}
        for key in self.keys:
            if key not in data:
                errors[key] = "Missing Key"
            elif not data[key]:
                errors[key] = "This Field is required"

        return errors
