import random
from datetime import timedelta
from random import Random

import rest_framework.parsers
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from django.utils import timezone

from PB.utility import ClearAllDistCalculations
from accounts.models import UserExtension, UserPaymentData, UserSubscription
from studios.models import Amenity, Studio
from subscriptions.models import Subscription

AMENITIES = [
    'treadmill',
    'benchpress',
    'freeweights',
    'rowers',
    'bikes'
]

START = (43.66730190391905, -79.44288327717946)

END = (43.650480562434645, -79.36391443704902)

class AdminGenerateStudios(APIView):

    parser_classes = [
        rest_framework.parsers.JSONParser,
        rest_framework.parsers.FormParser,
        rest_framework.parsers.MultiPartParser
    ]

    permission_classes = [IsAdminUser]

    generationParams = None

    rand = None

    def delete(self, request, *args, **kwargs):
        ClearAllDistCalculations()
        a = Studio.objects.filter(tgen=True)
        a.delete()
        Amenity.objects.filter(tgen=True).delete()
        return Response()

    def get(self, request, *args, **kwargs):
        ClearAllDistCalculations()
        self.rand = Random()
        n = request.data['n']
        n = int(n)

        xSep = END[0] - START[0]
        ySep = END[1] - START[1]

        for i in range(n):
            amens = self.rand.sample(AMENITIES, 3)
            stdName = f"Studio {i}"

            xLoc = (self.rand.random() * xSep) + START[0]
            yLoc = (self.rand.random() * ySep) + START[1]
            locfstr = f"{xLoc},{yLoc}"
            print(locfstr)
            std = Studio.objects.create(
                name=stdName,
                tgen=True,
                geo_loc=locfstr
            )
            std.save()
            for a in amens:
                amen = Amenity.objects.create(
                    studio=std,
                    type=a,
                    quantity=1,
                    tgen=True
                )
                amen.save()

        return Response()
