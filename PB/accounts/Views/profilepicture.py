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
import base64


# Create your views here.

class AddProfilePicture(APIView):
    '''
    Adds a profile picture to an authenticated user
    '''

    permission_classes = [IsAuthenticated]

    def post(self, request: Request, ):
        f = request.FILES['avatar']

        if ValidatePicture(f):
            userExt = UserExtension.objects.get(user=request.user)
            oldf = userExt.profile_pic
            if oldf is not None:
                fp = oldf.path
                if os.path.exists(fp):
                    os.remove(fp)
            userExt.profile_pic = f
            userExt.save()
            return Response(status=200)
        else:
            return Response({"Submit a valid picture"}, status=200)

PROFILE_PICTURE_PATH = "accounts/icon/"

class ViewProfilePicture(APIView):

    permission_classes = []
    '''
    Views a specific profile picture
    '''

    def get(self, request, *args, **kwargs):

        fn = kwargs['image_uuid']
        fp1 = PROFILE_PICTURE_PATH + fn

        fp = os.path.join(settings.BASE_DIR, fp1)
        try:
            f = open(fp, 'rb')
            return FileResponse(f, status=200)
        except FileNotFoundError as e:
            print(e)
            return Response({"file does not exist"}, status=404)

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

        return Response(status=200)
