import os

import rest_framework.parsers
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from ..models import Amenity, Studio, ImageRep



class DeleteStudio(APIView):
    parser_classes = [
        rest_framework.parsers.JSONParser,
        rest_framework.parsers.FormParser,
        rest_framework.parsers.MultiPartParser
    ]

    permission_classes = [IsAdminUser]

    def post(self, request: Request, *args, **kwargs):

        pk = kwargs['pk']

        if not Studio.objects.filter(id=pk):
            return Response({"Wrong Studio Id"})

        if ImageRep.objects.filter(studio_id=pk):
            for item in ImageRep.objects.filter(studio_id=pk):
                old_pic = item.image
                if old_pic is not None:
                    path = old_pic.path
                    if os.path.exists(path):
                        os.remove(path)
            ImageRep.objects.filter(studio_id=pk).delete()

        Amenity.objects.filter(studio_id=pk).delete()

        Studio.objects.get(id=pk).delete()

        return Response(status=200)
