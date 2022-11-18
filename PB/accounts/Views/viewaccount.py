from django.core.exceptions import ObjectDoesNotExist
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.models import UserExtendedSerializer, UserExtension, \
    UserPaymentData, UserPaymentDataSerializer


# Create your views here.

class ViewAccount(APIView):
    '''
    Views a specific account
    '''

    permission_classes = [IsAuthenticated]
    def get(self, request: Request, format=None):
        user = request.user
        ext = UserExtension.objects.get(user=user)
        s = UserExtendedSerializer(ext).data
        s1 = s['user']
        s.pop('user')
        for (k, v) in s1.items():
            s[k] = v

        try:
            upd = UserPaymentData.objects.get(user=user, active=True)
            upddat = UserPaymentDataSerializer(upd).data
        except ObjectDoesNotExist:
            upddat = None

        s['current_payment_data'] = upddat

        return Response(s)

