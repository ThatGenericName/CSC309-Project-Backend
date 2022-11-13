from django.apps import AppConfig




class SubscriptionsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'subscriptions'

    def ready(self):
        # from django.contrib.auth.models import Group
        # new_group, created = Group.objects.get_or_create(name='Coach')
        # print("Group Ready")

        pass
