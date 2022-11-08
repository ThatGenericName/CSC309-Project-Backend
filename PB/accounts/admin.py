from django.contrib import admin

from accounts.models import UserExtension, UserPaymentData, UserSubscription


# Register your models here.

@admin.register(UserExtension)
class UserExtAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone_num', 'last_modified')

@admin.register(UserSubscription)
class UserSubAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'user', 'subscription', 'start_time', 'payment_detail')
    list_filter = ('user', 'subscription')

@admin.register(UserPaymentData)
class UserSubAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'user', 'card_num', 'card_name', 'active')
