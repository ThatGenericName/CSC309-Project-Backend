from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from django.utils import timezone

import datetime

import rest_framework.parsers

from PB.utility import ValidateInt, ValidatePicture, VerifyPayment
from accounts.models import GetUserExtension, InternalUserPaymentDataSerializer, \
    UserExtension, \
    UserPaymentData, \
    UserPaymentDataSerializer, UserSubscription, UserSubscriptionSerializer
from subscriptions.models import Subscription

RECURRENCE_BUFFER = 3


# Create your views here.

class AddSubscription(APIView):
    '''
    Adds a subscription
    '''

    parser_classes = [
        rest_framework.parsers.JSONParser,
        rest_framework.parsers.FormParser,
        rest_framework.parsers.MultiPartParser
    ]

    permission_classes = [IsAuthenticated]

    req = ('id', 'pin')

    cleaned_data = None

    def ValidateData(self, data: dict) -> dict:
        errors = {}
        for k in self.req:
            if k not in data or not len(data[k]):
                errors[k] = 'This field is required'

        if len(errors):
            return errors

        res = ValidateInt(data['id'])
        if res.error:
            errors['id'] = "Please enter a valid number"
        else:
            data['id'] = res.value

        res2 = ValidateInt(data['pin'])
        if res2.error:
            errors['pin'] = "Please enter a valid pin"
        else:
            data['pin'] = res.value

        self.cleaned_data = data

        return errors

    def post(self, request: Request, ):

        errors = self.ValidateData(request.data.dict())
        if len(errors):
            return Response(errors, status=200)

        id = self.cleaned_data['id']
        recurring = 'do_not_renew' not in request.data
        pin = self.cleaned_data['pin']

        try:
            sub = Subscription.objects.get(id=id)
            if not sub.available:
                return Response("Subscription is not available", status=401)
        except ObjectDoesNotExist:
            return Response("Subscription does not exist", status=404)

        # get payment data
        try:
            userPaymentDetail = UserPaymentData.objects.get(user=request.user, active=True)
            dat = InternalUserPaymentDataSerializer(userPaymentDetail).data
            dat['pin'] = pin
            res = VerifyPayment(dat)
            if not res:
                raise ObjectDoesNotExist() # im too lazy to set this up properly
        except ObjectDoesNotExist:
            return Response({'detail': "Your payment information is invalid, please check your payment information on your profile"}, status=401)

        uext = UserExtension.objects.get(user=request.user)

        if uext.active_subscription is None:
            # user does not have existing subscription
            now = timezone.now()
            next = now + sub.duration()

            dat1 = {
                'user': request.user,
                'subscription': sub,
                'payment_time': now,
                'start_time': now,
                'end_time': next,
                'recurring': recurring,
                'payment_detail': userPaymentDetail
            }
            uSub1 = UserSubscription.objects.create(**dat1)
            uext.active_subscription = uSub1
            uSub1.save()
            uext.save()

            for n in range(RECURRENCE_BUFFER):
                now = next
                next = next + sub.duration
                dat = {
                    'user': request.user,
                    'subscription': sub,
                    'payment_time': None,
                    'start_time': now,
                    'end_time': next,
                    'recurring': recurring,
                    'payment_detail': userPaymentDetail
                }
                uSub = UserSubscription.objects.create(**dat)
                uSub.save()
        else:
            # User already has an active subscription
            activeSub = uext.active_subscription
            now, left = RemoveAndShiftUserSubs(request.user, activeSub.end_time)
            next = now + sub.duration
            dat = {
                'user': request.user,
                'subscription': sub,
                'payment_time': None,
                'start_time': now,
                'end_time': next,
                'recurring': recurring,
                'payment_detail': userPaymentDetail
            }
            buf = RECURRENCE_BUFFER - left - 1
            if buf > 0:
                for n in range(buf):
                    now = next
                    next = now + sub.duration
                    dat = {
                        'user': request.user,
                        'subscription': sub,
                        'payment_time': None,
                        'start_time': now,
                        'end_time': next,
                        'recurring': recurring,
                        'payment_detail': userPaymentDetail
                    }
                    uSub = UserSubscription.objects.create(**dat)
                    uSub.save()

        return Response({'detail': 'Thank you for your purchase'}, status=200)

def RemoveAndShiftUnpaidSubs(user, start_date) -> (datetime, int):
    '''
    Removes all future recurring and unpaid subscriptions and
    shifts any paid and non-recurring subscriptions down
    :param user:
    :param start_date:
    :return:
    '''
    usubs = UserSubscription.objects.filter(
        start_time__gt=timezone.now(),
        user=user).order_by('start_time')

    subsList = []

    for sub in usubs:
        if sub.payment_time is None:
            sub.delete()
        else:
            subsList.append(sub)

    nextDate = start_date
    for sub in subsList:
        sub.start_time = nextDate
        dur = sub.subscription.duration
        nextDate = nextDate + dur
        sub.end_time = nextDate
        sub.save()

    return nextDate, len(subsList)

def RemoveAndShiftUserSubs(user, start_date) -> (datetime, int):
    '''
    Removes all future recurring and unpaid subscriptions and
    shifts any paid and non-recurring subscriptions down
    :param user:
    :param start_date:
    :return:
    '''
    usubs = UserSubscription.objects.filter(
        start_time__gt=timezone.now(),
        user=user).order_by('start_time')

    subsList = []

    for sub in usubs:
        if sub.recurring and sub.payment_time is None:
            sub.delete()
        else:
            subsList.append(sub)

    nextDate = start_date
    for sub in subsList:
        sub.start_time = nextDate
        dur = sub.subscription.duration
        nextDate = nextDate + dur
        sub.end_time = nextDate
        sub.save()

    ResetActiveSubscription(user)
    return nextDate, len(subsList)

def ResetActiveSubscription(user: User):
    now = timezone.now()
    uext = GetUserExtension(user)
    userSubs = UserSubscription.objects\
        .filter(user=user, start_time__lte=now)\
        .order_by('-start_time')

    active = userSubs.first()
    if active is not None:
        uext.active_subscription = active
        uext.save()

class CanceAllSubscriptions(APIView):

    parser_classes = [
        rest_framework.parsers.JSONParser,
        rest_framework.parsers.FormParser,
        rest_framework.parsers.MultiPartParser
    ]

    permission_classes = [IsAuthenticated]

    def get(self, request):
        usubs = UserSubscription.objects.filter(
            start_time__gt=timezone.now(),
            user=request.user)

        for sub in usubs:
            if sub.payment_time is not None:
                # In theory, since a user would be able to pay for future
                # subscriptions, we also need to process refunds if a
                # subscription was already paid for
                pass
            sub.delete()

        return Response({'details': 'future subscriptions successfully cancelled'}, status=200)


class GetSubscription(APIView):

    parser_classes = [
        rest_framework.parsers.JSONParser,
        rest_framework.parsers.FormParser,
        rest_framework.parsers.MultiPartParser
    ]

    permission_classes = [IsAuthenticated]

    model = Subscription
    serializer_class = UserSubscriptionSerializer
    queryset = Subscription.objects.all()

    def get(self, request, *args, **kwargs):
        subId = kwargs['pk']
        try:
            sub = UserSubscription.objects.get(id=subId)
        except ObjectDoesNotExist:
            return Response('User Subscription does not exist', status=404)

        if sub.user.pk != request.user.pk:
            return Response('User Subscription does not exist', status=404)

        a = UserSubscriptionSerializer(sub).data

        return Response(a, status=200)


    def delete(self, request, *args, **kwargs):

        subId = kwargs['pk']
        try:
            sub = UserSubscription.objects.get(id=subId)
        except ObjectDoesNotExist:
            return Response('User Subscription does not exist', status=404)
        if sub.user.pk != request.user.pk:
            return Response('User Subscription does not exist', status=404)

        now = timezone.now()
        if sub.start_time < now:
            return Response({'detail': 'User Subscription has already begun'}, status=401)

        sd = sub.start_time
        sub.delete()

        RemoveAndShiftUserSubs(sub.user, sd)

        return Response({'detail': 'Subscription successfully cancelled'},status=200)


class UserSubscriptionPagination(PageNumberPagination):
    page_size = 10

class GetAllUserSubscriptions(ListAPIView):
    parser_classes = [
        rest_framework.parsers.JSONParser,
        rest_framework.parsers.FormParser,
        rest_framework.parsers.MultiPartParser
    ]

    permission_classes = [IsAuthenticated]
    pagination_class = UserSubscriptionPagination
    model = UserSubscription
    serializer_class = UserSubscriptionSerializer

    def get_queryset(self):
        self.ProcessRequestParams()
        qs = UserSubscription.objects\
            .filter(user=self.request.user)

        if self.requestParams[0] == 0:
            qs = qs.order_by('start_time')
        else:
            qs = qs.order_by('-start_time')

        searchTime = timezone.now()

        user = self.request.user
        uext = GetUserExtension(user)
        if uext.active_subscription is not None:
            searchTime = uext.active_subscription.start_time

        if self.requestParams[1] == 1:
            qs = qs.filter(start_time__lt=searchTime)
        elif self.requestParams[1] == 2:
            qs = qs.filter(start_time__gte=searchTime)

        return qs

    requestParams = None

    def ProcessRequestParams(self):
        p = []
        dat = self.request.data
        sort = 1
        if 'sort' in dat:
            if dat['sort'].lower() == 'asc':
                sort = 0

        filt = 0
        if 'filter' in dat:
            if dat['filter'] == 'past':
                filt = 1
            elif dat['filter'] == 'future':
                filt = 2

        p.append(sort)
        p.append(filt)

        self.requestParams = p
