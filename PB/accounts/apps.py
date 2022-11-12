from django.apps import AppConfig
import time




class AccountsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'accounts'

    def ready(self):
        from django.contrib.auth.models import Group
        new_group, created = Group.objects.get_or_create(name='Coach')
        print("Group Ready")
