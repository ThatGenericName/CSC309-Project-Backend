from django.contrib.auth.management.commands import createsuperuser
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand, CommandError

from accounts.models import UserExtension


class Command(BaseCommand):
    help = 'Creates a default admin user'

    def add_arguments(self, parser):
        parser.add_argument('--username',
                            dest='username',
                            help='if this is not set or is invalid, username will be "PBAdmin"',
                            type=str,
                            default="PBAdmin"
                            )
        parser.add_argument('--password',
                            dest='password',
                            help='if this is not set or is invalid, password will be "PBAdmin"',
                            type=str,
                            default="PBAdmin"
                            )



    def handle(self, *args, **options):

        username = options.get('username')
        password = options.get('password')

        if User.objects.filter(username=username).exists():
            print('default superuser already exists')
        else:
            user = User.objects.create_user(username=username, password=password)
            user.is_staff = True
            user.is_superuser = True
            user.save()
            uext = UserExtension.objects.create(user=user)
            uext.save()




