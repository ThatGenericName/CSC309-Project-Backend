from django.core.exceptions import ObjectDoesNotExist
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from ..models import *

# Create your views here.

class ViewStudio(APIView):
    '''
    Views a specific account
    '''

    # permission_classes = [IsAuthenticated]

    def get(self, request: Request, format=None, *args, **kwargs):

        try:
            Studio.objects.get(id=kwargs["studio_id"])
        except ObjectDoesNotExist:
            Response({"Studio Does not exist"})

        studio = Studio.objects.get(id=kwargs["studio_id"])
        lat, long = studio.geo_loc.split(",")

        s = StudioSerializer(studio).data
        s["direction"] = "https://maps.google.com/?q=" + lat + "," + long




        return Response(s)

