from django.apps import AppConfig

class AccountsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'accounts'

    def ready(self):
        # from django.contrib.auth.models import Group
        # new_group, created = Group.objects.get_or_create(name='Coach')
        # print("Group Ready")
        from accounts.management.commands.runapscheduler import InitScheduler
        InitScheduler()
        pass

