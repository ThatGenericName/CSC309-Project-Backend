import os

from django.conf import settings
from django.http import FileResponse
from geopy.geocoders import Nominatim

import rest_framework.parsers
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.permissions import IsAdminUser
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from ..models import Studio, ImageRep

from PB.utility import ValidatePhoneNumber, ValidatePostalCode, ValidatePicture

STUDIO_PICTURE_PATH = os.path.join('studios', 'studioimages')


class ImageView(APIView):
    permission_classes = []
    '''
    Views a specific profile picture
    '''

    def get(self, request, *args, **kwargs):

        fn = kwargs['image']
        fp1 = os.path.join(STUDIO_PICTURE_PATH, fn)

        fp = os.path.join(settings.BASE_DIR, fp1)
        try:
            f = open(fp, 'rb')
            return FileResponse(f, status=200)
        except FileNotFoundError as e:
            print(e)
            return Response({'error': "file does not exist"}, status=404)
