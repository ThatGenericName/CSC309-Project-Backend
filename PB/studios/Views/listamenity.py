import rest_framework.parsers
from rest_framework.generics import ListAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
import rest_framework.parsers

from PB.utility import *

from ..models import *


class ListAmenityPagination(PageNumberPagination):
    page_size = 10


class ListAmenity(ListAPIView):
    '''
    adds amenity to db
    '''

    parser_classes = [
        rest_framework.parsers.JSONParser,
        rest_framework.parsers.FormParser,
        rest_framework.parsers.MultiPartParser
    ]

    permission_classes = [IsAuthenticated]
    pagination_class = ListAmenityPagination
    model = Amenity
    serializer_class = AmenitySerializer


    def get_queryset(self):

        pk = self.kwargs['pk']
        qs = Amenity.objects.filter(studio_id=pk)

        return qs
