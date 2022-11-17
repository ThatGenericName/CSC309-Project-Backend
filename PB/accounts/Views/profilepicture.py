import rest_framework.parsers
from django.core.exceptions import ObjectDoesNotExist
from django.http import FileResponse
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from PB.utility import ValidatePicture
from accounts.models import UserExtension

import os
from django.conf import settings


# Create your views here.

class AddProfilePicture(APIView):
    '''
    Adds a profile picture to an authenticated user
    '''

    parser_classes = [
        rest_framework.parsers.JSONParser,
        rest_framework.parsers.FormParser,
        rest_framework.parsers.MultiPartParser
    ]

    permission_classes = [IsAuthenticated]

    def post(self, request: Request, ):

        if 'avatar' not in request.FILES:
            return Response({'detail': 'Image was not provided'}, status=400)

        f = request.FILES['avatar']

        if ValidatePicture(f):
            userExt = UserExtension.objects.get(user=request.user)
            oldf = userExt.profile_pic
            if oldf:
                fp = oldf.path
                if os.path.exists(fp):
                    os.remove(fp)
            userExt.profile_pic = f
            userExt.save()
            fn = userExt.profile_pic.path.split(os.sep)[-1]
            return Response({'detail': {'fileName': fn}}, status=200)
        else:
            return Response({'detail': "Submit a valid picture"}, status=400)

PROFILE_PICTURE_PATH = "accounts" + os.sep + "icon" + os.sep

class ViewProfilePicture(APIView):

    permission_classes = []
    '''
    Views a specific profile picture
    '''

    def get(self, request, *args, **kwargs):

        fn = kwargs['image_name']
        fp1 = os.path.join(PROFILE_PICTURE_PATH, fn)

        fp = os.path.join(settings.BASE_DIR, fp1)
        try:
            f = open(fp, 'rb')
            return FileResponse(f, status=200)
        except FileNotFoundError as e:
            print(e)
            return Response({'detail': "file does not exist"}, status=404)

class ClearProfilePicture(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request, *args):
        userExt = UserExtension.objects.get(user=request.user)
        f = userExt.profile_pic
        fp = f.path
        userExt.profile_pic = None
        userExt.save()
        if os.path.exists(fp):
            os.remove(fp)

        return Response({'detail': 'profile picture cleared'}, status=200)
