import os
from geopy.geocoders import Nominatim

import rest_framework.parsers
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.permissions import IsAdminUser
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from ..models import Studio, ImageRep

from PB.utility import ValidatePhoneNumber, ValidatePostalCode, ValidatePicture


class EditStudio(APIView):
    parser_classes = [
        rest_framework.parsers.JSONParser,
        rest_framework.parsers.FormParser,
        rest_framework.parsers.MultiPartParser
    ]

    permission_classes = [IsAdminUser]

    keys = [
        'name',
        'address',
        'post_code',
        'phone_num'
    ]

    def post(self, request: Request, *args, **kwargs):

        pk = kwargs['pk']

        if not Studio.objects.filter(id=pk):
            return Response({"Wrong Studio Id"}, status=404)
        errors = self.ValidateData(request.data)

        if len(errors):
            return Response(errors, status=400)

        data = request.data
        studio = Studio.objects.get(id=pk)

        for (k, v) in data.items():
            if k in self.keys and len(v):
                setattr(studio, k, v)

        if data['address']:
            geolocator = Nominatim(user_agent="studios")
            map_location = geolocator.geocode(data["address"], timeout=10)
            geo_loc = str(map_location.latitude) + "," + str(map_location.longitude)
            setattr(studio, "geo_loc", geo_loc)

        studio.save()

        if request.FILES.getlist('images'):
            for item in ImageRep.objects.filter(studio_id=pk):
                old_pic = item.image
                if old_pic is not None:
                    path = old_pic.path
                    if os.path.exists(path):
                        os.remove(path)
            ImageRep.objects.filter(studio_id=pk).delete()

            for f in request.FILES.getlist('images'):
                if ValidatePicture(f):
                    image = ImageRep.objects.create(image=f,
                                                    studio=studio)
                    image.save()

        return Response(status=200)

    def ValidateData(self, data) -> dict:
        errors = {}
        for key in self.keys:
            if key not in data:
                errors[key] = "Missing Key"
        if 'images' not in data:
            errors['images'] = "Missing Key"

        if 'name' not in errors and data['name']:
            try:
                Studio.objects.get(name=data['name'])
                errors['name'] = "This Studio name is already taken"
            except ObjectDoesNotExist:
                pass

        if 'phone_num' not in errors and data['phone_num']:
            if not ValidatePhoneNumber(data['phone_num']):
                errors['phone_num'] = 'Enter a valid phone number'

        if 'post_code' not in errors and data['post_code']:
            if not ValidatePostalCode(data['post_code']):
                errors['post_code'] = 'Enter a Valid Postal Code'

        if 'address' not in errors and data["address"]:
            geolocator = Nominatim(user_agent="studios")
            map_location = geolocator.geocode(data["address"], timeout=10)

            if map_location is None:
                errors['address'] = 'Enter a Valid Address'

        return errors
