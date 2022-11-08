import rest_framework.parsers
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.core.validators import validate_email
from django.utils import timezone
from rest_framework.generics import RetrieveAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
import rest_framework.parsers

from PB.utility import ValidatePhoneNumber
from accounts.models import GetUserExtension, UserExtension, UserPaymentData, \
    UserPaymentDataSerializer, UserSubscription

# Create your views here.

KEYS = [
    'card_type',
    'card_num',
    'card_name',
    'exp_month',
    'exp_year'
]


class AddPaymentInformation(APIView):
    '''
    edits a specific profile
    '''

    parser_classes = [
        rest_framework.parsers.JSONParser,
        rest_framework.parsers.FormParser,
        rest_framework.parsers.MultiPartParser
    ]

    permission_classes = [IsAuthenticated]

    def post(self, request: Request):
        errors = self.ValidateData(request.data.dict())

        if len(errors):
            return Response(errors, status=200)

        try:
            upd = UserPaymentData.objects.get(user=request.user, active=True)
            upd.active = False
            cn = upd.card_num
            a = len(cn)
            b = a - 4
            cns = f"{'*' * b}{cn[b-1:]}"
            upd.card_num = cns
            #upd.user = None
            upd.save()

        except ObjectDoesNotExist:
            pass

        nupd = UserPaymentData.objects.create(**self.cleanedData)
        nupd.user = request.user
        nupd.active = True
        nupd.save()

        self.UpdateFutureSubscriptions(nupd)

        return Response({"success": True}, status=200)

    cleanedData = {}

    ct = ('credit', 'debit')

    def ValidateData(self, data: dict) -> dict:
        errors = {}
        for k in KEYS:
            if k not in data or not len(data[k]):
                errors[k] = 'This field is required'

        if len(errors):
            return errors

        if data['card_type'].lower() not in self.ct:
            errors['card_type'] = 'Enter a valid card type'
        else:
            data['card_type'] = data['card_type'].lower()

        if not data['card_num'].isnumeric() or len(data['card_num']) < 12 or len(data['card_num']) > 16:
            data['card_num'] = 'Enter a valid number'

        if not all(x.isalpha() or x.isspace() for x in data['card_name']):
            errors['card_name'] = 'enter a valid name'

        mf = None
        m = data['exp_month']
        if isinstance(m, str):
            if not len(m):
                errors['exp_month'] = 'This field is required'
            else:
                try:
                    mf = int(float(m))
                except ValueError:
                    errors['exp_month'] = 'Enter a valid number'
        elif isinstance(m, float) or isinstance(m, int):
            mf = int(m)

        if mf < 1 or mf > 12:
            errors['exp_month'] = 'Enter a valid month'

        yf = None
        y = data['exp_year']
        if isinstance(y, str):
            if not len(y):
                errors['exp_year'] = 'This field is required'
            else:
                try:
                    yf = int(float(y))
                except ValueError:
                    errors['exp_year'] = 'Enter a valid number'
        elif isinstance(y, float) or isinstance(y, int):
            yf = int(y)

        if yf < 0:
            errors['exp_year'] = 'Enter a valid year'

        data['exp_year'] = yf
        data['exp_month'] = mf

        self.cleanedData = data

        return errors


    def UpdateFutureSubscriptions(self, payment_data):
        now = timezone.now()
        qs = UserSubscription.objects.filter(start_time__gt=now)
        for q in qs:
            if q.payment_time is None:
                q.payment_detail = payment_data
                q.save()

class RemovePaymentInformation(APIView):
    '''
    edits a specific profile
    '''

    parser_classes = [
        rest_framework.parsers.JSONParser,
        rest_framework.parsers.FormParser,
        rest_framework.parsers.MultiPartParser
    ]

    permission_classes = [IsAuthenticated]


    def delete(self, request: Request):

        user = request.user

        upds = UserPaymentData.objects.filter(user=user, active=True)
        for upd in upds:
            upd.active = False
            cn = upd.card_num
            a = len(cn)
            b = a - 4
            cns = f"{'*' * b}{cn[b - 1:]}"
            upd.card_num = cns
            upd.save()

        self.UpdateFutureSubscriptions(user)

        return Response({"success": True}, status=200)

    def UpdateFutureSubscriptions(self, user):
        now = timezone.now()
        qs = UserSubscription.objects.filter(start_time__gt=now)
        for q in qs:
            if q.payment_time is None:
                q.delete()
        qs2 = UserSubscription.objects\
            .filter(start_time__gt=now)\
            .order_by('start_time')

        nextT = GetUserExtension(user).active_subscription.end_time

        for q in qs2:
            q.start_time = nextT
            nextT = nextT + q.subscription.duration
            q.end_time = nextT
            q.save()


class GetPaymentInformation(APIView):
    '''
    edits a specific profile
    '''

    parser_classes = [
        rest_framework.parsers.JSONParser,
        rest_framework.parsers.FormParser,
        rest_framework.parsers.MultiPartParser
    ]

    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        try:
            paymentDat = UserPaymentData.objects.get(user=request.user, active=True)
        except ObjectDoesNotExist:
            return Response("You do not have a payment method", status=200)
        dat = UserPaymentDataSerializer(paymentDat).data

        return Response(dat, status=200)
