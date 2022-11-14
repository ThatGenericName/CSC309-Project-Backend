from geopy.geocoders import Nominatim

import rest_framework.parsers
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.permissions import IsAdminUser
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from ..models import Studio, ImageRep

from PB.utility import ValidatePhoneNumber, ValidatePostalCode, ValidatePicture


class CreateStudio(APIView):
    parser_classes = [
        rest_framework.parsers.JSONParser,
        rest_framework.parsers.FormParser,
        rest_framework.parsers.MultiPartParser
    ]

    # permission_classes = [IsAdminUser]

    keys = [
        'name',
        'address',
        'post_code',
        'phone_num'
    ]

    def post(self, request: Request, format=None):
        errors = self.ValidateData(request.data)

        if len(errors):
            return Response(errors)

        data = request.data

        geolocator = Nominatim(user_agent="studios")
        map_location = geolocator.geocode(data["address"], timeout=10)

        studio = Studio(
            name=data['name'],
            address=data['address'],
            post_code=data['post_code'],
            geo_loc=map_location,
            phone_num=data['phone_num'])

        studio.save()

        for f in request.FILES.getlist('images'):
            if ValidatePicture(f):
                image = ImageRep.objects.create(image=f,
                                                studio=Studio.objects.get(name=data['name']))
                image.save()

        return Response({"success": True})

    def ValidateData(self, data) -> dict:
        errors = {}
        for key in self.keys:
            if key not in data:
                errors[key] = "Missing Key"
        if 'images' not in data:
            errors['images'] = "Missing Key"

        if 'name' not in errors:
            try:
                Studio.objects.get(name=data['name'])
                errors['name'] = "This Studio name is already taken"
            except ObjectDoesNotExist:
                pass

        if 'phone_num' not in errors:
            if not ValidatePhoneNumber(data['phone_num']):
                errors['phone_num'] = 'Enter a valid phone number'

        if 'post_code' not in errors:
            if not ValidatePostalCode(data['post_code']):
                errors['post_code'] = 'Enter a Valid Postal Code'

        if 'address' not in errors:
            geolocator = Nominatim(user_agent="studios")
            map_location = geolocator.geocode(data["address"])

            if map_location is None:
                errors['address'] = 'Enter a Valid Address'

        return errors
