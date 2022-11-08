from django.contrib import admin

from accounts.models import UserExtension, UserSubscription
from subscriptions.models import Subscription


# Register your models here.
@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'name', 'duration', 'price', 'subscribed_members',
                    'total_subscriptions', 'available')

    actions = ['set_hidden', 'set_visible']

    def subscribed_members(self, obj):
        a = UserExtension.objects.filter(active_subscription__subscription=obj)
        b = a.count()
        return b

    def total_subscriptions(self, obj):
        a = UserSubscription.objects.filter(subscription=obj).count()
        return a

    def set_hidden(self, request, queryset):
        queryset.update(available=False)

    def set_visible(self, request, queryset):
        queryset.update(available=True)
