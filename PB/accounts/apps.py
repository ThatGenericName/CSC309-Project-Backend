import django
from django.apps import AppConfig
from django.utils import timezone


class AccountsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'accounts'

    def ready(self):
        # from django.contrib.auth.models import Group
        # new_group, created = Group.objects.get_or_create(name='Coach')
        # print("Group Ready")
        from django.db import connection
        at = connection.introspection.table_names()
        if 'django_apscheduler_djangojob' in at:
            from accounts.management.commands.runapscheduler import \
                InitScheduler
            InitScheduler()
        pass

