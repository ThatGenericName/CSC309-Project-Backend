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
            upd = UserPaymentData.objects.get(user=request.user, active=True)
            dat = InternalUserPaymentDataSerializer(upd).data
            dat['pin'] = pin
            res = VerifyPayment(dat)
            if not res:
                raise ObjectDoesNotExist() # im too lazy to set this up properly
        except ObjectDoesNotExist:
            return Response("Your payment information is invalid, please check your payment information on your profile", status=200)

        now = timezone.now()
        nextPayment = now + sub.duration
        nextAfter = nextPayment + sub.duration

        uext = UserExtension.objects.get(user=request.user)

        if uext.active_subscription is None:
            # user does not have existing subscription
            dat1 = {
                'user': request.user,
                'subscription': sub,
                'payment_time': now,
                'start_time': now,
                'end_time': nextPayment,
                'recurring': recurring,
                'payment_detail': upd
            }

            dat2 = {
                'user': request.user,
                'subscription': sub,
                'payment_time': None,
                'start_time': nextPayment,
                'end_time': nextAfter,
                'recurring': recurring,
                'payment_detail': upd
            }

            uSub1 = UserSubscription.objects.create(**dat1)
            uSub2 = UserSubscription.objects.create(**dat2)

            uext.active_subscription = uSub1

            uSub1.save()
            uSub2.save()
            uext.save()
        else:
            activ = UserSubscription()
            activ = uext.active_subscription
            activ.recurring = False

            date = activ.end_time
            # removes recurring (automatic) subscriptions and shifts
            # non-recurring subscriptions downwards
            last_date = (request.user, date)
            end = last_date + sub.duration
            dat1 = {
                'user': request.user,
                'subscription': sub,
                'payment_time': None,
                'start_time': last_date,
                'end_time': end,
                'recurring': recurring,
                'payment_detail': upd
            }
            uSub1 = UserSubscription.objects.create(**dat1)
            uSub1.save()

        return Response({'Thank you for your purchase'}, status=200)


def ShiftUserSubs(user, start_date) -> datetime:
    usubs = UserSubscription.objects.filter(
        start_time__gt=timezone.now(),
        user=user).order_by('start_time')

    subsList = []

    for sub in usubs:
        if sub.recurring:
            sub.delete()
        else:
            subsList.append(sub)

    nextDate = start_date
    for sub in subsList:
        sub.start_time = nextDate
        dur = sub.subscription.duration
        nextDate = nextDate + dur
        sub.save()

    return nextDate


class CancelSubscription(APIView):

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
            sub.delete()

        # In theory, since a user would be able to pay for future
        # subscriptions, we also need to process refunds if a
        # subscription was already paid for

        return Response(status=200)


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
        sd = sub.start_time
        sub.delete()

        ShiftUserSubs(sub.user, sd)

        return Response(status=200)


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
            .filter(user=self.request.user)\
            .order_by(self.requestParams[0])

        if self.requestParams[2] == 1:
            uext = GetUserExtension(self.request.user)
            active = uext.active_subscription
            if active is None:
                date = timezone.now()
            else:
                date = active.start_time
            qs = qs.filter(start_time__lt=date)
        elif self.requestParams[2] == 2:
            uext = GetUserExtension(self.request.user)
            active = uext.active_subscription
            if active is None:
                date = timezone.now()
            else:
                date = active.start_time
            qs = qs.filter(start_time__gte=date)

        return qs

    requestParams = None

    def ProcessRequestParams(self):
        p = []
        dat = self.request.data
        sort = '-start_time'
        if 'sort' in dat:
            if dat['sort'].lower() == 'asc':
                p.append('start_time')

        filt = 0
        if 'filter' in dat:
            if dat['filter'] == 'past':
                filt = 1
            elif dat['filter'] == 'future':
                filt = 2

        p.append(sort)
        p.append(filt)

        self.requestParams = p
