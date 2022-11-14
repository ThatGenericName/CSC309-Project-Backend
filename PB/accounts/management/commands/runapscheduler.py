
import logging
from datetime import datetime, timedelta

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.date import DateTrigger
from django.conf import settings

from apscheduler.triggers.cron import CronTrigger
from django.core.exceptions import ObjectDoesNotExist
from django.core.management.base import BaseCommand
from django_apscheduler.jobstores import DjangoJobStore
from django_apscheduler.models import DjangoJobExecution
from django_apscheduler import util
from django.contrib.auth.models import User
from django.utils import timezone
from PB.utility import VerifyPayment
from accounts.models import InternalUserPaymentDataSerializer, \
    UserExtension, \
    UserPaymentData, UserSubscription
from studios.models import StudioSearchHash

logger = logging.getLogger(__name__)

REFRESH_DUR = timedelta(hours=16)
SSH_DUR = timedelta(hours=24)

@util.close_old_connections
def ClearOldSearchHash():
    minH = timezone.now() - SSH_DUR
    StudioSearchHash.objects.filter(search_date__lt=minH).delete()


@util.close_old_connections
def CheckForSubscriptionRenewals():

    print('checking for subscriptions that need renewals')
    now = timezone.now()
    range = now + REFRESH_DUR
    users = User.objects.all()
    for user in users:
        print(f'checking {user.username}')
        uext = user.userextension
        activeSub = uext.active_subscription
        if activeSub is not None and activeSub.end_time < range:
            print(f'{user.username} has an active subscription')
            futureSubs = UserSubscription.objects.filter(
                user=user,
                start_time__gt=now
            ).order_by('start_time')

            if futureSubs.count():
                print(f'{user.username} has future subscriptions, activating')
                nextSub = futureSubs.first()

                if (nextSub.payment_time is not None):
                    continue

                upd = UserPaymentData.objects.get(user=user, active=True)
                dat = InternalUserPaymentDataSerializer(upd).data
                dat['pin'] = '0000'
                if VerifyPayment(dat):
                    nextSub.payment_time = activeSub.end_time
                    nextSub.payment_detail = upd
                    nextSub.save()
                else:
                    print(f'{user.username}\'s payment failed, cancelling subscriptions')
                    RemoveAndShiftUnpaidSubs(user, now)
            elif activeSub.recurring:
                print(f'{user.username} has a recurring subscription and does not have further subscriptions')
                try:
                    upd = UserPaymentData.objects.get(user=user, active=True)
                except ObjectDoesNotExist:
                    # user has no payment method, do not renew
                    continue
                dat = InternalUserPaymentDataSerializer(upd).data
                dat['pin'] = '0000'
                if VerifyPayment(dat):
                    dat1 = {
                        'user': user,
                        'subscription': activeSub.subscription,
                        'payment_time': now,
                        'start_time': activeSub.end_time,
                        'end_time': activeSub.end_time + activeSub.subscription.duration,
                        'recurring': True,
                        'payment_detail': upd
                    }
                    a = UserSubscription.objects.create(**dat1)
                    a.save()

@util.close_old_connections
def AutoCreateCoachGroup():
    '''
    A startup task that creates the Coach usergroup.
    '''
    from django.contrib.auth.models import Group
    new_group, created = Group.objects.get_or_create(name='Coach')
    print("Coach Usergroup Ready")

'''
The Below code is largely taken from the documentation for the
django-apscheduler library, a library that does some integration
of the apscheduler library with django.



'''


# The `close_old_connections` decorator ensures that database connections, that have become
# unusable or are obsolete, are closed before and after your job has run. You should use it
# to wrap any jobs that you schedule that access the Django database in any way.
@util.close_old_connections
def delete_old_job_executions(max_age=604_800):
    """
    This job deletes APScheduler job execution entries older than `max_age` from the database.
    It helps to prevent the database from filling up with old historical records that are no
    longer useful.

    :param max_age: The maximum length of time to retain historical job execution records.
                    Defaults to 7 days.
    """
    DjangoJobExecution.objects.delete_old_job_executions(max_age)


class Command(BaseCommand):
    help = "Runs APScheduler."

    def handle(self, *args, **options):
        InitScheduler()

SCHEDULER = None
def InitScheduler():
    global SCHEDULER
    if SCHEDULER is None:
        SCHEDULER = BackgroundScheduler(timezone=settings.TIME_ZONE)

    SCHEDULER.add_jobstore(DjangoJobStore(), "default")

    SCHEDULER.add_job(
        CheckForSubscriptionRenewals,
        trigger=CronTrigger(hour="*/12"),
        id="AutoRenewalCheck",
        max_instances=1,
        replace_existing=True,
    )
    logger.info("Added job 'AutoRenewalCheck'.")

    SCHEDULER.add_job(
        ClearOldSearchHash,
        trigger=CronTrigger(hour="*/12"),
        id="ClearOldSearchHash",
        max_instances=1,
        replace_existing=True,
    )
    logger.info("Added job 'ClearOldSearchHash'.")

    tz = datetime.now().astimezone().tzinfo
    SCHEDULER.add_job(
        AutoCreateCoachGroup,
        trigger=DateTrigger(
            run_date=datetime.now() + timedelta(seconds=30),
            timezone=tz
        ),
        id="CoachUsergroupCheck",
        max_instances=1,
        replace_existing=True
    )
    logger.info("Added job 'CoachUsergroupCheck'.")

    SCHEDULER.add_job(
        delete_old_job_executions,
        trigger=CronTrigger(
            day_of_week="mon", hour="00", minute="00"
        ),  # Midnight on Monday, before start of the next work week.
        id="delete_old_job_executions",
        max_instances=1,
        replace_existing=True,
    )
    logger.info(
        "Added weekly job: 'delete_old_job_executions'."
    )

    try:
        logger.info("Starting scheduler...")
        SCHEDULER.start()
    except KeyboardInterrupt:
        logger.info("Stopping scheduler...")
        SCHEDULER.shutdown()
        logger.info("Scheduler shut down successfully!")


