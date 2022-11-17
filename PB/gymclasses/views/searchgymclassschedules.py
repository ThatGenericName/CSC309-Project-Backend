import uuid
from datetime import timedelta
import datetime

from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone
from rest_framework.generics import ListAPIView
from rest_framework.pagination import PageNumberPagination
from functools import reduce
import operator
from django.db.models import Q, QuerySet
from rest_framework.response import Response

from ..models import *

SEARCH_GAP_DURATION = timedelta(days=2)


# Create your views here.

class GymClassSchedulePagination(PageNumberPagination):
    page_size = 10


class ViewGymClassSchedule(ListAPIView):
    '''
    Searches Studios
    '''

    permission_classes = []
    pagination_class = GymClassSchedulePagination
    model = GymClassSchedule
    serializer_class = GymClassScheduleSerializer

    gym_class_name = None
    coach_name = None
    date = []
    start_time = None
    end_time = None

    def get(self, request, *args, **kwargs):
        # print(request.query_params)
        e = self.ProcessParams(request.query_params)
        # print(self.gym_class_name, self.coach_name, self.date,
        #       self.start_time, self.end_time)
        # print("date", self.date)
        if e:
            return Response(e)
        return super().get(request, *args, **kwargs)

    def get_queryset(self):

        qs = GymClassSchedule.objects.order_by('start_time')

        return qs

    def filter_queryset(self, qs: QuerySet):
        # qs = Studio.objects.all()
        q = []

        if self.gym_class_name:
            qn = []
            for n in self.gym_class_name:
                qn.append(qs.filter(parent_class__name__contains=n).distinct())
            if len(qn):
                q.append(reduce(operator.or_, qn))

        if self.coach_name:
            qchn = []
            for chn in self.coach_name:
                qsfn = qs.filter(coach__first_name__contains=chn[0]).distinct()
                qsln = qs.filter(coach__last_name__contains=chn[1]).distinct()
                qsn = qsfn & qsln
                qchn.append(qsn)
            if len(qchn):
                q.append(reduce(operator.or_, qchn))

        if self.date:
            qn = []
            for item in self.date:
                q_day = qs.filter(date__day=item.day).distinct()
                q_month = qs.filter(date__month=item.month).distinct()
                q_year = qs.filter(date__year=item.year).distinct()
                q_date = q_day & q_month & q_year
                qn.append(q_date)
            if qn:
                q.append(reduce(operator.or_, qn))

        if self.start_time:
            qn = []
            q_hour = qs.filter(start_time__hour__gte=self.start_time.hour).distinct()
            q_minute = qs.filter(start_time__minute__gte=self.start_time.minute).distinct()
            q_time = q_hour & q_minute
            qn.append(q_time)
            if qn:
                q.append(reduce(operator.or_, qn))

        if self.end_time:
            qn = []
            q_hour = qs.filter(end_time__hour__lte=self.end_time.hour).distinct()
            q_minute = qs.filter(end_time__minute__lte=self.end_time.minute).distinct()
            q_time = q_hour & q_minute
            qn.append(q_time)
            if qn:
                q.append(reduce(operator.or_, qn))

        if len(q):
            f = reduce(operator.and_, q)
        else:
            f = qs
        return f

    def ProcessParams(self, params):

        errors = {}

        if 'name' in params and params['name']:
            a = params['name'].split(',')
            self.gym_class_name = [i for i in a if len(i)]

        if 'coach_name' in params and params["coach_name"]:
            a = params['coach_name'].split(',')
            fl = []
            for name in a:
                ns = name.split(' ')
                fn = ns[0] if len(ns[0]) else ''
                ln = ns[1] if len(ns) > 1 and len(ns[1]) else ''
                if len(fn) or len(ln):
                    fl.append((fn, ln))
            self.coach_name = fl

        if 'date' in params and params["date"]:
            a = params['date'].split(',')

            for item in a:
                try:
                    datetime.datetime.strptime(item, '%d/%m/%Y')
                except ValueError:
                    errors["date"] = {"Wrong date Format"}

                date = datetime.datetime.strptime(item, '%d/%m/%Y')
                if not errors:
                    self.date.append(date)

        if "time_range" in params and params["time_range"]:
            lst = params['time_range'].split('-')

            if lst[0]:
                try:
                    datetime.datetime.strptime(lst[0], '%H:%M')
                except ValueError:
                    errors["time_range"] = {"Wrong start date Format"}

                self.start_time = datetime.datetime.strptime(lst[0], '%H:%M')

            if lst[1]:

                try:
                    datetime.datetime.strptime(lst[1], '%H:%M')
                except ValueError:
                    errors["time_range"] = {"Wrong end date Format"}

                self.end_time = datetime.datetime.strptime(lst[1], '%H:%M')

            if self.start_time and self.end_time:
                if self.start_time >= self.end_time:
                    errors["time_range"] = {"Start Time before End Time"}

        return errors
