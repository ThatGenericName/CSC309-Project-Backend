from __future__ import annotations
import os
from uuid import uuid4

from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.contrib.auth.models import Group, User
from rest_framework import serializers
from rest_framework.permissions import BasePermission

from gymclasses.models import GymClass, GymClassSchedule, \
    GymClassScheduleSerializer
from subscriptions.models import Subscription

# Create your models here.
'''
Models
'''

PATH = "accounts/icon/"


def RandomNameGen(instance, filename):
    ext = "." + filename.split('.')[-1]
    name = str(uuid4())
    fn = name + ext
    return os.path.join(PATH, fn)


class UserExtension(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE,
                                primary_key=True)
    phone_num = models.CharField(max_length=12, null=False)
    profile_pic = models.ImageField(blank=True,
                                    upload_to=RandomNameGen)
    last_modified = models.DateTimeField(auto_now=True)
    enrolled_classes = models.ManyToManyField(GymClassSchedule, blank=True)
    active_subscription = models.OneToOneField("UserSubscription", null=True,
                                               on_delete=models.SET_NULL)


def GetUserExtension(user):
    try:
        Uext = UserExtension.objects.get(user=user)
        return Uext
    except ObjectDoesNotExist:
        print(f"User {user.username} does not have an extension, creating extension")
        Uext = UserExtension.objects.create(user=user)
        Uext.save()
        return Uext


class UserSubscription(models.Model):
    user = models.ForeignKey(User, null=False, on_delete=models.CASCADE)
    subscription = models.ForeignKey(Subscription, null=True,
                                     on_delete=models.CASCADE)
    payment_time = models.DateTimeField(null=True, auto_now_add=False,
                                        auto_now=False, blank=True)
    start_time = models.DateTimeField(null=False, auto_now_add=False,
                                      auto_now=False)
    end_time = models.DateTimeField(null=False, auto_now_add=False,
                                    auto_now=False)
    payment_detail = models.ForeignKey("UserPaymentData",
                                       on_delete=models.SET_NULL, null=True,
                                       blank=True)
    recurring = models.BooleanField(null=False, default=True)
    tgen = models.BooleanField(null=False, default=False)


class UserPaymentData(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    card_type = models.CharField(null=False, max_length=6)
    card_num = models.CharField(null=False, max_length=16)
    card_name = models.CharField(null=False, max_length=255)
    exp_month = models.IntegerField(null=False)
    exp_year = models.IntegerField(null=False)
    active = models.BooleanField(null=False, default=True)
    tgen = models.BooleanField(null=False, default=False)


'''
Serializers
'''


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'username',
            'email',
            'first_name',
            'last_name',
            'is_staff',
        ]


class UserExtendedSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    enrolled_classes = GymClassScheduleSerializer()

    class Meta:
        model = UserExtension
        fields = [
            'phone_num',
            'enrolled_classes',
            'active_subscription',
            'profile_pic',
            'last_modified',
            'user'
        ]
        depth = 1

    def to_representation(self, instance):
        data = super().to_representation(instance)

        return data


class InternalUserPaymentDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserPaymentData
        fields = [
            'card_type',
            'card_num',
            'card_name',
            'exp_month',
            'exp_year',
            'active'
        ]


class UserPaymentDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserPaymentData
        fields = [
            'card_type',
            'card_num',
            'card_name',
            'exp_month',
            'exp_year',
            'active'
        ]

    def to_representation(self, instance):
        data = super().to_representation(instance)
        cn = data['card_num']
        if '*' not in cn:
            a = len(cn)
            b = a - 4
            cns = f"{'*' * b}{cn[b:]}"
            data['card_num'] = cns
        return data


class UserSubscriptionSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    payment_detail = UserPaymentDataSerializer()

    class Meta:
        model = UserSubscription
        fields = [
            'user',
            'subscription',
            'payment_time',
            'start_time',
            'end_time',
            'payment_detail',
            'recurring'
        ]
        depth = 1

    def to_representation(self, instance):
        dat = super().to_representation(instance)
        return dat


'''
Custom permission classes
'''

class IsCoach(BasePermission):

    def has_permission(self, request, view):
        """
        Return `True` if a user is part of the coach usergroup
        """
        new_group, created = Group.objects.get_or_create(name='Coach')
        if bool(request.user):
            return request.user.groups.filter(name='Coach').exists()
        return False
