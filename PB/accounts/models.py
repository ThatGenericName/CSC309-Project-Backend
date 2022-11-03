from django.db import models
from django.contrib.auth.models import User

from gymclasses.models import GymClassOccurence
from subscriptions.models import Subscription

# Create your models here.
class UserExtension(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    phone_num = models.CharField(max_length=12, null=False)
    profile_pic = models.ImageField(upload_to="ProfileImages/")
    last_modified = models.DateTimeField(auto_now=True)
    enrolled_classes = models.ManyToManyField(GymClassOccurence)
    active_subscription = models.OneToOneField("UserSubscription", null=True, on_delete=models.SET_NULL)


class UserSubscription(models.Model):
    user = models.ForeignKey(User, null=False, on_delete=models.CASCADE)
    current_subscription = models.ForeignKey(Subscription, null=True, on_delete=models.SET_NULL)
    payment_time = models.DateTimeField(null=False, auto_now_add=False, auto_now=False)
    start_time = models.DateTimeField(null=False, auto_now_add=True, auto_now=False)
    end_time = models.DateTimeField(null=False, auto_now_add=False, auto_now=False)

class UserPaymentData(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    card_type = models.CharField(null=False, max_length=6)
    card_num = models.CharField(null=False, max_length=16)
    card_name = models.CharField(null=False, max_length=255)
    exp_month = models.IntegerField(null=False)
    exp_year = models.IntegerField(null=False)
