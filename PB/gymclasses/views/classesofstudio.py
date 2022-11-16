import datetime
from itertools import chain
import pytz
from django.utils import timezone
import rest_framework.parsers
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from rest_framework.generics import ListAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
import rest_framework.parsers

from PB.utility import ValidateInt, ValidatePhoneNumber
from accounts.models import UserExtension, User
from gymclasses.models import *
from studios.models import Studio

# Create your views here.

DAYS = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']


class ClassesofStudioPagination(PageNumberPagination):
    page_size = 10


class ClassesofStudio(ListAPIView):
    '''
    edits a specific profile
    '''

    parser_classes = [
        rest_framework.parsers.JSONParser,
        rest_framework.parsers.FormParser,
        rest_framework.parsers.MultiPartParser
    ]

    # permission_classes = [IsAuthenticated]
    pagination_class = ClassesofStudioPagination
    model = GymClassSchedule
    serializer_class = GymClassScheduleSerializer

    def get_queryset(self):

        studio_id = self.kwargs['studio_id']

        try:
            studio = Studio.objects.get(id=studio_id)
        except ObjectDoesNotExist:
            return Response({'error': 'Studio Class was not found'}, status=404)

        classes = GymClassSchedule.objects.filter(parent_class__studio=studio)

        qs = classes.filter(start_time__gt=timezone.now())
        qs = qs.filter(end_time__gt=timezone.now())
        qs = qs.filter(is_cancelled=False)

        return qs
