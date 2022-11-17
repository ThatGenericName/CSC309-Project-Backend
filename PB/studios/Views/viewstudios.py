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
from gymclasses.models import GymClassSchedule
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

        qn = []
        for n in self.qStudioName:
            qn.append(qs.filter(name__contains=n).distinct())
        if len(qn):
            q.append(reduce(operator.or_, qn))

        qa = []
        for at in self.qAmenitiesType:
            qa.append(qs.filter(amenity__type__contains=at).distinct())
        if len(qa):
            q.append(reduce(operator.or_, qa))

        qcln = []
        for cln in self.qClassName:
            qcln.append(qs.filter(gymclass__name__contains=cln).distinct())
        if len(qcln):
            q.append(reduce(operator.or_, qcln))

        qchn = []
        for chn in self.qCoachName:
            qs = Studio.objects.all()
            qsfn = qs.filter(
                gymclass__gymclassschedule__coach__first_name__contains=chn[0]).distinct()
            qsln = qs.filter(
                gymclass__gymclassschedule__coach__last_name__contains=chn[1]).distinct()
            qsn = qsfn & qsln
            qchn.append(qsn)
        if len(qchn):
            q.append(reduce(operator.or_, qchn))

        if len(q):
            f = reduce(operator.and_, q)
        else:
            f = qs
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
            self.qStudioName = [i for i in a if len(i)]
        else:
            self.qStudioName = []

        if 'a' in params:
            a = params['a'].split(',')
            self.qAmenitiesType = [i for i in a if len(i)]
        else:
            self.qAmenitiesType = []

        if 'cln' in params:
            a = params['cln'].split(',')
            self.qClassName = [i for i in a if len(i)]
        else:
            self.qClassName = []

        if 'chn' in params:
            a = params['chn'].split(',')
            fl = []
            for name in a:
                ns = name.split(' ')
                fn = ns[0] if len(ns[0]) else ''
                ln = ns[1] if len(ns) > 1 and len(ns[1]) else ''
                if len(fn) or len(ln):
                    fl.append((fn, ln))
            self.qCoachName = fl
        else:
            self.qCoachName = []

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
                dist = 0
                if len(studio.geo_loc):
                    a = studio.geo_loc.split(',')
                    studioLoc = (float(a[0]), float(a[1]))
                    dist = GD(studioLoc, self.location).km
                sst = StudioSearchTemp.objects.create(
                    studio=studio,
                    dist=dist,
                    searchkey=ssh
                )
                sst.save()

        self.search_hash_obj = ssh


def IsFloat(num):
    try:
        float(num)
        return True
    except ValueError:
        return False




