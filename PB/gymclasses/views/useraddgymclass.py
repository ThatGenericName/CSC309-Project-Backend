import rest_framework.parsers
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.core.validators import validate_email
from django.utils import timezone
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
import rest_framework.parsers

from PB.utility import ValidateInt, ValidatePhoneNumber
from accounts.models import UserExtension
from gymclasses.models import GymClass

# Create your views here.

KEYS = [
    'password1',
    'password2',
    'first_name',
    'last_name',
    'email',
    'phone_num'
]

class AddGymClassToUser(APIView):
    '''
    edits a specific profile
    '''

    parser_classes = [
        rest_framework.parsers.JSONParser,
        rest_framework.parsers.FormParser,
        rest_framework.parsers.MultiPartParser
    ]

    permission_classes = [IsAuthenticated]

    def get(self, request: Request, *args, **kwargs):

        classId = kwargs['class_id']
        try:
            gclass = GymClass.objects.get(id=classId)
        except ObjectDoesNotExist:
            return Response({'error': 'Class was not found'}, status=404)

        now = timezone.now()

        if gclass.end_datetime < now:
            return Response({'error': 'This class has already ended'})

        user = request.user
        uext = UserExtension.objects.get(user=user)
        if gclass.userextension_set.filter(user=user).exists():
            return Response({'error': 'You are already enrolled in this class'}, status=200)

        if gclass.enrollment_count < gclass.enrollment_capacity:
            uext.enrolled_classes.add(gclass)
            gclass.enrollment_count += 1
            gclass.save()
            uext.save()
            return Response({'success': 'You have successfully enrolled in this class'}, status=200)

        return Response({'error': 'This class if full'}, status=200)


class RemoveGymClassFromUser(APIView):
    '''
    edits a specific profile
    '''

    parser_classes = [
        rest_framework.parsers.JSONParser,
        rest_framework.parsers.FormParser,
        rest_framework.parsers.MultiPartParser
    ]

    permission_classes = [IsAuthenticated]

    def get(self, request: Request, *args, **kwargs):

        classId = kwargs['class_id']

        try:
            gclass = GymClass.objects.get(id=classId)
        except ObjectDoesNotExist:
            return Response({'error': 'class was not found'}, status=404)

        now = timezone.now()
        if gclass.end_datetime < now:
            return Response({'error': 'This class has already ended'})

        user = request.user
        uext = UserExtension.objects.get(user=user)
        if gclass.userextension_set.filter(user=user).exists():
            uext.enrolled_classes.remove(gclass)
            gclass.enrollment_count -= 1
            uext.save()
            gclass.save()
            return Response(
                {'success': 'You have successfully dropped this class'},
                status=200)

        return Response({'error': 'You are not enrolled in this class'}, status=200)
