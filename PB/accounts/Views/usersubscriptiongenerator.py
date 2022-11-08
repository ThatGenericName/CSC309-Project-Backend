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

from accounts.models import UserExtension, UserPaymentData, UserSubscription
from subscriptions.models import Subscription

TIMES = (1, 10, 1 * 24, 10 * 24)
PAYMENT_NUM = 2

class AdminCreateUSubs(APIView):

    parser_classes = [
        rest_framework.parsers.JSONParser,
        rest_framework.parsers.FormParser,
        rest_framework.parsers.MultiPartParser
    ]

    permission_classes = [IsAdminUser]

    def delete(self, request):
        subs = Subscription.objects.filter(tgen=True)
        for sub in subs:
            sub.delete()

        usubs = UserSubscription.objects.filter(tgen=True)
        for s in usubs:
            s.delete()

        upds = UserPaymentData.objects.filter(tgen=True)
        for upd in upds:
            upd.delete()

        return Response(status=200)

    generationParams = None

    def get(self, request, *args, **kwargs):
        self.rand = Random()

        reqDat = request.data
        num = int(reqDat['num'])
        direct = int(reqDat['dir'])
        uid = int(reqDat['user'])
        recur = bool(reqDat['recur'])

        self.generationParams = {
            'num': num,
            'dir': direct,
            'uid': uid,
            'recur': recur
        }

        if direct != 1:
            recur = False

        self.targetUser = User.objects.get(pk=uid)
        self.targetUserExt = UserExtension.objects.get(user=self.targetUser)

        self.ClearUserSubscriptions()
        self.ClearUserPaymentMethods()

        self.ClearTemporaryGeneratedObjects()
        self.GenerateTemporarySubscriptions()
        self.GenerateTemporaryPaymentMethods()

        # Security isn't a focus for this test function,
        # non-true random doesn't matter

        sub = self.rand.choice(self.generatedSubscriptions)
        now = timezone.now()
        pm = self.rand.choice(self.generatedPaymentMethod)

        dat1 = {
            'user': self.targetUser,
            'subscription': sub,
            'start_time': now,
            'payment_time': now,
            'end_time': now + sub.duration,
            'payment_detail': pm,
            'recurring': recur,
            'tgen': True
        }

        usub = UserSubscription.objects.create(**dat1)
        usub.save()
        pm.active = True
        pm.save()
        self.targetUserExt.active_subscription = usub
        self.generationParams['last_sub'] = usub
        if direct == 0 or direct == 1:
            self.GeneratePastSubscriptions(num)
        if direct == 0 or direct == 2:
            self.GenerateFutureSubscriptions(num)
        if direct == 1 and recur:
            t2 = now + sub.duration
            dat2 = {
            'user': self.targetUser,
            'subscription': sub,
            'start_time': t2,
            'payment_time': t2,
            'end_time': t2 + sub.duration,
            'payment_detail': pm,
            'recurring': recur,
            'tgen': True
            }
            usub2 = UserSubscription.objects.create(**dat2)
            usub2.save()
        self.targetUserExt.save()
        self.targetUser.save()
        return Response()

    rand = None
    targetUser = None
    targetUserExt = None

    def ClearUserSubscriptions(self):
        subs = UserSubscription.objects.filter(user=self.targetUser)
        for sub in subs:
            sub.delete()

    def ClearUserPaymentMethods(self):
        upds = UserPaymentData.objects.filter(user=self.targetUser)
        for upd in upds:
            if (upd.active):
                pass
            upd.active = False

    def GenerateFutureSubscriptions(self, n):

        lastSub = self.generationParams['last_sub']
        pm = lastSub.payment_detail
        for i in range(n):
            sub = self.rand.choice(self.generatedSubscriptions)
            pm = pm
            recur = sub.pk == lastSub.pk
            startDT = lastSub.end_time
            dat1 = {
                'user': self.targetUser,
                'subscription': sub,
                'start_time': startDT,
                'payment_time': None,
                'end_time': startDT + sub.duration,
                'payment_detail': pm,
                'recurring': recur,
                'tgen': True
            }
            lastSub = UserSubscription.objects.create(**dat1)
            lastSub.save()
        pass

    def GeneratePastSubscriptions(self, n):
        lastSub = self.generationParams['last_sub']
        recur = self.generationParams['recur']
        for i in range(n):
            sub = self.rand.choice(self.generatedSubscriptions)
            pm = self.rand.choice(self.generatedPaymentMethod)
            endDT = lastSub.start_time
            dat1 = {
                'user': self.targetUser,
                'subscription': sub,
                'start_time': endDT - sub.duration,
                'payment_time': endDT - sub.duration,
                'end_time': endDT,
                'payment_detail': pm,
                'recurring': recur,
                'tgen': True
            }
            lastSub = UserSubscription.objects.create(**dat1)
            lastSub.save()
        pass

    def GenerateTemporaryPaymentMethods(self):
        pm = []
        for i in range(PAYMENT_NUM):
            data = {}
            cn = f"{i}000"
            for n in range(12):
                cn += str(self.rand.randint(0, 9))
            data['card_num'] = cn
            data[
                "card_name"] = f"{self.targetUser.first_name} {self.targetUser.last_name}"
            data["card_type"] = 'credit'
            data['exp_month'] = 1
            data['exp_year'] = 2100
            data['active'] = False
            data['user'] = self.targetUser
            data['tgen'] = True
            upd = UserPaymentData.objects.create(**data)
            upd.save()
            pm.append(upd)
        self.generatedPaymentMethod = pm

    generatedPaymentMethod = None
    generatedSubscriptions = None


    def GenerateTemporarySubscriptions(self):
        '''
        This will an n number of subscriptions corresponding
        to TIMES
        :return:
        '''
        genSubs = []
        for dur in TIMES:
            price = 1
            name = f"TGEN Subscription {self.targetUser.username} - {dur} hours"
            desc = f"TGEN Subscription Description, {self.targetUser.username}, {dur} hours "
            dt = timedelta(hours=dur)
            sub = Subscription.objects.create(
                name=name,
                description=desc,
                price=price,
                duration=dt,
                available=False,
                tgen=True
            )
            sub.save()
            genSubs.append(sub)
        self.generatedSubscriptions = genSubs

    def ClearTemporaryGeneratedObjects(self):
            usubs = UserSubscription.objects.filter(user=self.targetUser, tgen=True)
            for s in usubs:
                s.delete()

            upds = UserPaymentData.objects.filter(user=self.targetUser, tgen=True)
            for upd in upds:
                upd.delete()
