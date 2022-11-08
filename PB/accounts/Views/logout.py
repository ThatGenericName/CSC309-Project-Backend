from django.core.exceptions import ObjectDoesNotExist
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

# Create your views here.

class Logout(APIView):
    '''
    Views a specific account
    '''

    permission_classes = [IsAuthenticated]

    def get(self, request: Request, format=None):
        try:
            request.user.auth_token.delete()
        except ObjectDoesNotExist:
            pass
        return Response(status=200)
