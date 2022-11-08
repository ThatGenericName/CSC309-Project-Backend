from datetime import timedelta

import rest_framework.parsers
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.generics import CreateAPIView, ListAPIView, RetrieveAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny, IsAdminUser
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from PB.utility import ValidateBool, ValidateFloat, ValidateInt
from subscriptions.models import Subscription, SubscriptionSerializer

class SubscriptionPagination(PageNumberPagination):
    page_size = 10

class ViewSubscriptions(ListAPIView):

    parser_classes = [
        rest_framework.parsers.JSONParser,
        rest_framework.parsers.FormParser,
        rest_framework.parsers.MultiPartParser
    ]
    permission_classes = []
    pagination_class = SubscriptionPagination
    model = Subscription
    serializer_class = SubscriptionSerializer
    queryset = Subscription.objects.order_by('-price')

    def filter_queryset(self, queryset):
        a = queryset.filter(available=True).values()
        return a


class GetSubscription(RetrieveAPIView):

    parser_classes = [
        rest_framework.parsers.JSONParser,
        rest_framework.parsers.FormParser,
        rest_framework.parsers.MultiPartParser
    ]
    permission_classes = [IsAdminUser]
    model = Subscription
    serializer_class = SubscriptionSerializer
    queryset = Subscription.objects.all()

    def check_permissions(self, request):
        if (request.method == 'GET'):
            return True
        else:
            return super().check_permissions(request)

    def delete(self, request, *args, **kwargs):
        subId = kwargs['pk']

        dat = request.data
        remove = False
        if 'remove' in dat:
            val = ValidateBool(dat['remove'])
            if not val.error:
                remove = val

        try:
            sub = Subscription.objects.get(id=subId)
        except ObjectDoesNotExist:
            return Response("Subscription does not exist", status=404)

        if remove:
            sub.delete()
            return Response('Subscription successfully deleted')
        else:
            sub.available = False
            sub.save()
            return Response('Subscription successfully hidden')



class CreateSubscription(CreateAPIView):
    parser_classes = [
        rest_framework.parsers.JSONParser,
        rest_framework.parsers.FormParser,
        rest_framework.parsers.MultiPartParser
    ]
    permission_classes = [IsAdminUser]
    model = Subscription
    serializer_class = SubscriptionSerializer
    queryset = Subscription.objects.all()

    def post(self, request, *args, **kwargs):
        data = request.data
        errors = self.validateData(data)
        if len(errors):
            return Response(errors)
        ndat = self.cleaned_data
        sub = Subscription.objects.create(
            name=ndat['name'],
            description=ndat['description'],
            price=ndat['price'],
            duration=ndat['duration'],
            tgen=ndat['tgen']
        )
        sub.save()
        return Response()

    keys = [
        'name',
        'description',
        'price',
        'days',
        'hours'
    ]

    req = [
        0, 2, 3, 4
    ]

    cleaned_data = None

    def validateData(self, data: dict) -> dict:

        dat = data.dict()
        errors = {}
        for i, k in enumerate(self.keys):
            if k not in dat:
                errors[k] = "This field is missing"

        if 'available' in dat:
            a = ValidateBool(dat['available'])
            if a.error:
                dat['available'] = True
            else:
                dat['available'] = a.value

        if 'tgen' not in dat:
            dat['tgen'] = False

        if not len(dat['name']):
            errors['name'] = "This field is required"

        pf = None
        p = dat['price']
        if isinstance(p, str):
            if not len(p):
                errors['price'] = 'This field is required'
            else:
                try:
                    pf = float(p)
                except ValueError:
                    errors['price'] = 'Enter a valid price'
        elif isinstance(p, str) or isinstance(p, str):
            pf = float(p)

        df = None
        d = dat['days']
        if isinstance(d, str):
            if not len(d):
                errors['days'] = 'This field is required'
            else:
                try:
                    df = int(float(d))
                except ValueError:
                    errors['days'] = 'Enter a valid number'
        elif isinstance(d, float) or isinstance(d, int):
            df = int(float(d))

        hf = None
        h = dat['hours']
        if isinstance(h, str):
            if not len(h):
                errors['hours'] = 'This field is required'
            else:
                try:
                    hf = float(h)
                except ValueError:
                    errors['hours'] = 'Enter a valid number'
        elif isinstance(h, float) or isinstance(h, int):
            hf = float(h)

        if len(errors):
            return errors

        duration = timedelta(days=df, hours=hf)

        dat.pop('days')
        dat.pop('hours')
        dat['price'] = pf
        dat['duration'] = duration

        self.cleaned_data = dat
        return errors


class EditSubscription(APIView):
    parser_classes = [
        rest_framework.parsers.JSONParser,
        rest_framework.parsers.FormParser,
        rest_framework.parsers.MultiPartParser
    ]
    permission_classes = [IsAdminUser]
    model = Subscription
    serializer_class = SubscriptionSerializer
    queryset = Subscription.objects.all()

    def post(self, request, *args, **kwargs):
        try:
            sub = Subscription.objects.get(id=kwargs['pk'])
        except ObjectDoesNotExist:
            return Response("Subscription does not exist", status=404)

        data = request.data.dict()
        errors = self.validateData(data)
        if len(errors):
            return Response(errors)
        ndat = self.cleaned_data

        for (k, v) in ndat.items():
            setattr(sub, k, v)

        sub.save()

        return Response()

    keys = [
        'name',
        'description',
        'price',
        'days',
        'hours',
        'available',
        'tgen'
    ]

    req = [

    ]

    cleaned_data = None

    def validateData(self, data: dict) -> dict:
        errors = {}
        dat = data
        for i, k in enumerate(self.keys):
            if k not in dat:
                dat[k] = None

        if 'available' in dat:
            a = ValidateBool(dat['available'])
            if a.error:
                dat['available'] = True
            else:
                dat['available'] = a.value

        if dat['tgen'] is not None:
            validate = ValidateBool(dat['tgen'])
            if not validate.error:
                dat['tgen'] = validate.value
            else:
                errors['tgen'] = 'Enter a valid boolean'

        if dat['price'] is not None:
            validate = ValidateFloat(dat['price'])
            if not validate.error:
                dat['price'] = validate.value
            else:
                errors['price'] = 'Enter a valid price'

        di = 0
        if dat['days'] is not None:
            validate = ValidateInt(dat['days'])
            if not validate.error:
                di = validate.value
            else:
                errors['days'] = 'Enter a value number'

        hi = 0
        if dat['hours'] is not None:
            validate = ValidateInt(dat['hours'])
            if not validate.error:
                hi = validate.value
            else:
                errors['hours'] = 'Enter a value number'

        if len(errors):
            return errors

        duration = timedelta(days=di, hours=hi)

        dat.pop('days')
        dat.pop('hours')
        dat['duration'] = duration

        newDat = {}
        for (k, v) in dat.items():
            if v is not None:
                newDat[k] = v

        self.cleaned_data = newDat
        return errors


