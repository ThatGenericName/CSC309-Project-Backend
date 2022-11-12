import rest_framework.parsers
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
import rest_framework.parsers

from PB.utility import *

from ..models import *


class EditAmenity(APIView):
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

    permission_classes = [IsAuthenticated]

    def post(self, request: Request, *args, **kwargs):

        if not Amenity.objects.filter(pk=kwargs['pk']):
            return Response({"Amenity Does not Exist"})

        errors = self.ValidateData(request.data)

        if len(errors):
            return Response(errors)

        amenity = Amenity.objects.get(pk=kwargs['pk'])

        data = request.data
        amenity.quantity = data['quantity']
        amenity.type = data['type']
        amenity.studio = amenity.studio

        amenity.save()
        return Response({"success": True})

    def ValidateData(self, data) -> dict:
        """
        Function to validate the input data

        """
        errors = {}
        for key in self.keys:
            if key not in data:
                errors[key] = "Missing Key"
            elif not data[key]:
                errors[key] = "This Field is required"

        return errors
