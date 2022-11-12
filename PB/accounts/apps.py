from django.apps import AppConfig
from apscheduler.schedulers.background import BackgroundScheduler
import time

class AccountsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'accounts'

    scheduler = BackgroundScheduler()

    def ready(self):
        # time to schedule checking to renew subscriptions
        self.scheduler.scheduled_job(
            UpdateSubscriptionRenewals,
            'cron',
            hour='7')

def UpdateSubscriptionRenewals():
    from django.contrib.auth.models import User
    from django.utils import timezone
    from PB.utility import VerifyPayment
    from accounts.models import InternalUserPaymentDataSerializer, \
        UserExtension, \
        UserPaymentData, UserSubscription

    print('checking for subscriptions that need renewals')
    now = timezone.now()
    users = User.objects.all()
    for user in users:
        uext = user.userextension
        activeSub = uext.active_subscription
        if activeSub is not None:
            futureSubs = UserSubscription.objects.filter(
                user=user,
                start_time__gt=now
            ).order_by('start_time')

            if futureSubs.count():
                nextSub = futureSubs.first()

                if (nextSub.payment_time is not None):
                    return

                upd = UserPaymentData.objects.get(user=user, active=True)
                dat = InternalUserPaymentDataSerializer(upd).data
                dat['pin'] = '0000'
                if VerifyPayment(dat):
                    nextSub.payment_time = timezone.now()
