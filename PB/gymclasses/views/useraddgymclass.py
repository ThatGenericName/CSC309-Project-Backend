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
from accounts.models import GetUserExtension, UserExtension
from gymclasses.models import GymClass, GymClassSchedule

# Create your views here.

KEYS = [
    'password1',
    'password2',
    'first_name',
    'last_name',
    'email',
    'phone_num'
]

class AddGymClassSessionToUser(APIView):

    parser_classes = [
        rest_framework.parsers.JSONParser,
        rest_framework.parsers.FormParser,
        rest_framework.parsers.MultiPartParser
    ]

    permission_classes = [IsAuthenticated]

    def get(self, request: Request, *args, **kwargs):

        classId = kwargs['session_id']
        try:
            gclasssched = GymClassSchedule.objects.get(id=classId)
        except ObjectDoesNotExist:
            return Response({'details': 'class session was not found'}, status=404)

        now = timezone.now()

        if gclasssched.end_time < now:
            return Response({'details': 'This class session has already ended'}, status=401)

        user = request.user
        uext = UserExtension.objects.get(user=user)
        if gclasssched.userextension_set.filter(user=user).exists():
            return Response({'details': 'You are already enrolled in this class session'}, status=200)

        if gclasssched.enrollment_count < gclasssched.enrollment_capacity:
            uext.enrolled_classes.add(gclasssched)
            gclasssched.enrollment_count += 1
            gclasssched.save()
            uext.save()
            return Response({'details': 'You have successfully enrolled in this class session'}, status=200)

        return Response({'details': 'This class is full'}, status=401)


class RemoveGymClassSessionFromUser(APIView):
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

        classId = kwargs['session_id']

        try:
            gclass = GymClassSchedule.objects.get(id=classId)
        except ObjectDoesNotExist:
            return Response({'details': 'class session was not found'}, status=404)

        now = timezone.now()
        if gclass.end_time < now:
            return Response({'details': 'This class session has already ended'}, status=401)

        user = request.user
        uext = UserExtension.objects.get(user=user)
        if gclass.userextension_set.filter(user=user).exists():
            uext.enrolled_classes.remove(gclass)
            gclass.enrollment_count -= 1
            uext.save()
            gclass.save()
            return Response(
                {'details': 'You have successfully dropped this class session'},
                status=200)

        return Response({'details': 'You are not enrolled in this class session'}, status=200)


class AddGymClassToUser(APIView):
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
            return Response({'details': 'Class was not found'}, status=404)
        now = timezone.now()
        gcsq = GymClassSchedule.objects.filter(parent_class=gclass, start_time__gt=now)
        fullClasses = []

        uext = GetUserExtension(request.user)

        for gcs in gcsq:
            # gcs = GymClassSchedule()
            if gcs.enrollment_count < gcs.enrollment_capacity:
                if not uext.enrolled_classes.all().filter(id=gcs.id).exists():
                    gcs.enrollment_count += 1
                    uext.enrolled_classes.add(gcs)
                    gcs.save()
            else:
                fullClasses.append(gcs.id)

        uext.save()
        return Response({'details': {'full_classes': fullClasses}}, status=200)

class RemoveGymClassFromUser(APIView):
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
            return Response({'details': 'Class was not found'}, status=404)
        now = timezone.now()

        uext = GetUserExtension(request.user)
        gcsq = uext.enrolled_classes.all().filter(parent_class=gclass, start_time__gt=now)

        for gcs in gcsq:
            # gcs = GymClassSchedule()
            uext.enrolled_classes.remove(gcs)
            gcs.enrollment_count -= 1
            gcs.save()

        uext.save()

        return Response({'details': 'class successfully unenrolled'}, status=200)


class DropAllClasses(APIView):
    parser_classes = [
        rest_framework.parsers.JSONParser,
        rest_framework.parsers.FormParser,
        rest_framework.parsers.MultiPartParser
    ]

    permission_classes = [IsAuthenticated]

    def get(self, request: Request, *args, **kwargs):

        now = timezone.now()

        uext = GetUserExtension(request.user)
        gcsq = uext.enrolled_classes.all().filter(start_time__gt=now)

        for gcs in gcsq:
            uext.enrolled_classes.remove(gcs)
            gcs.enrollment_count -= 1
            gcs.save()

        uext.save()
        return Response({'details': 'classes successfully unenrolled'}, status=200)
