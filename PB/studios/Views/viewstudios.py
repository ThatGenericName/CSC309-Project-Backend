import uuid
from datetime import timedelta

from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone
from rest_framework.generics import ListAPIView
from rest_framework.pagination import PageNumberPagination
from functools import reduce
import operator
from django.db.models import Q, QuerySet

from PB.utility import ClearOldDateCalculations, GenerateQObjectsContainsAnd
from accounts.models import UserExtendedSerializer, UserExtension, \
    UserPaymentData, UserPaymentDataSerializer
from studios.models import Amenity, Studio, StudioSearchHash, StudioSearchTemp, \
    StudioSerializer
from geopy.distance import geodesic as GD


SEARCH_GAP_DURATION = timedelta(days=2)

# Create your views here.

class StudioPagination(PageNumberPagination):
    page_size = 10

class ViewStudios(ListAPIView):
    '''
    Searches Studios
    '''

    permission_classes = []
    pagination_class = StudioPagination
    model = Studio
    serializer_class = StudioSerializer


    def get(self, request, *args, **kwargs):
        self.ProcessParams(request.query_params)
        if self.location is not None:
            self.CalculateDistance()
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        if self.location is None:
            qs = Studio.objects.order_by('name')
        else:
            qs = Studio.objects. \
                filter(studiosearchtemp__searchkey=self.search_hash_obj). \
                order_by('studiosearchtemp__dist')

        return qs

    def filter_queryset(self, qs: QuerySet):
        #qs = Studio.objects.all()
        q = []
        for n in self.qStudioName:
            q.append(qs.filter(name__contains=n).distinct())

        for at in self.qAmenitiesType:
            q.append(qs.filter(amenity__type__contains=at).distinct())

        # for cln in self.qClassName:
        #     q.append(qs.filter(gymclass__name__contains=cln).distinct())
        #
        # for chn in self.qCoachName:
        #     q.append(qs.filter(
        #         gymclass__gymclassoccurence__coach__first_name=chn[0],
        #         gymclass__gymclassoccurence__coach__last_name=chn[1]
        #     ))

        f = reduce(operator.and_, q)
        return f

    qStudioName = None
    qAmenitiesType = None
    qClassName = None
    qCoachName = None
    location = None

    def ProcessParams(self, params):

        #General Search Query

        if 'n' in params:
            a = params['n'].split(',')
            #q = GenerateQObjectsContainsAnd('name', *a)
            self.qStudioName = a

        if 'a' in params:
            a = params['a'].split(',')
            #q = GenerateQObjectsContainsAnd('amenity__type', *a)
            self.qAmenitiesType = a

        if 'cln' in params:
            a = params['cln'].split(',')
            #q = GenerateQObjectsContainsAnd('gymclass__name', *a)
            self.qClassName = a

        if 'chn' in params:
            a = params['chn'].split(',')
            fl = []
            for name in a:
                ns = name.split(' ')
                fn = ns[0] if len(ns[0]) else ''
                ln = ns[1] if len(ns) > 1 and len(ns[1]) else ''
                fl.append((fn, ln))
            #qObj = Q(gymclass__gymclassoccurence__coach__first_name=fn, gymclass__gymclassoccurence__coach__last_name=ln)
            self.qCoachName = fl

        # location data:
        if 'location' in self.request.data:
            a = self.request.data['location'].split(',')
            if not (IsFloat(a[0]) and IsFloat(a[1])):
                self.location = None
            else:
                self.location = (float(a[0]), float(a[1]))

    search_hash_obj = None

    def CalculateDistance(self, ):
        search_hash = f"{self.location[0].__round__(3)},{self.location[1].__round__(3)}"

        try:
            ssh = StudioSearchHash.objects.get(hash=search_hash)
            dur = timezone.now() - ssh.search_date
            if dur > SEARCH_GAP_DURATION:
                ClearOldDateCalculations(ssh)
                ssh = None
        except ObjectDoesNotExist:
            ssh = None

        if ssh is None:
            ssh = StudioSearchHash.objects.create(hash=search_hash)
            q = Studio.objects.all()
            for studio in q:
                a = studio.geo_loc.split(',')
                studioLoc = (float(a[0]), float(a[1]))
                dist = GD(studioLoc, self.location).km
                StudioSearchTemp.objects.create(
                    studio=studio,
                    dist=dist,
                    searchkey=ssh
                )

        self.search_hash_obj = ssh


def IsFloat(num):
    try:
        float(num)
        return True
    except ValueError:
        return False




