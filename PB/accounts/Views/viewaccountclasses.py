import rest_framework.parsers
from django.utils import timezone
from requests import Response
from rest_framework.generics import ListAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated

from accounts.models import GetUserExtension, UserExtension


class AccountClassesPagination(PageNumberPagination):
    page_size = 10

class ViewAccountClasses(ListAPIView):

    parser_classes = [
        rest_framework.parsers.JSONParser,
        rest_framework.parsers.FormParser,
        rest_framework.parsers.MultiPartParser
    ]

    permission_classes = [IsAuthenticated]
    pagination_class = AccountClassesPagination

    def get(self, request, *args, **kwargs):


        return Response()

    requestParams = None

    def ProcessRequestParams(self):
        p = []
        dat = self.request.data
        sort = 0
        if 'sort' in dat:
            if dat['sort'].lower() == 'des':
                sort = 1

        filt = 0
        if 'filter' in dat:
            if dat['filter'] == 'past':
                filt = 1
            elif dat['filter'] == 'future':
                filt = 2

        p.append(sort)
        p.append(filt)

        self.requestParams = p

    def get_queryset(self):
        self.ProcessRequestParams()
        user = self.request.user
        uext = GetUserExtension(user)
        now = timezone.now()
        if self.request[1] == 0:
            qs = uext.enrolled_classes
        elif self.request[1] == 1:
            qs = uext.enrolled_classes.filter(start_time__lt=now)
        else:
            qs = uext.enrolled_classes.filter(start_time__gte=now)

        if self.request[0] == 0:
            qs = qs.order_by('start_time')
        else:
            qs = qs.order_by('-start_time')

        return qs
