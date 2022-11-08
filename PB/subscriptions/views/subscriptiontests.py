from datetime import timedelta
from random import Random

import rest_framework.parsers
from rest_framework.generics import ListAPIView
from rest_framework.permissions import AllowAny, IsAdminUser
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from subscriptions.models import Subscription, SubscriptionSerializer


class AdminCreate(APIView):

    parser_classes = [
        rest_framework.parsers.JSONParser,
        rest_framework.parsers.FormParser,
        rest_framework.parsers.MultiPartParser
    ]

    permission_classes = [IsAdminUser]

    def get(self, *args, **kwargs):
        count = kwargs['count']

        qs = Subscription.objects.filter(tgen=True)
        for s in qs:
            qs.delete()

        rand = Random()

        for i in range(count):
            a = rand.random()
            b = 2 ** i
            price = a * b
            name = f"Subscription {i}"
            desc = f"Subscription {i} Description"
            dt = timedelta(days=b)
            sub = Subscription.objects.create(
                name=name,
                description=desc,
                price=price,
                duration=dt,
                tgen=True
            )
            sub.save()

        return Response()


class AdminClearTgen(APIView):

    def get(self, *args, **kwargs):
        qs = Subscription.objects.filter(tgen=True)
        i = 0
        for q in qs:
            q.delete()
            i += 1
        return Response(f"cleared {i} test subscriptions", status=200)
