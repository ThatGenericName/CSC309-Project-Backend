from django.urls import path

from accounts.Views.register import RegisterAccount
from accounts.Views.viewaccount import ViewAccount

app_name = 'accounts'

urlpatterns = [
    path('view/', ViewAccount.as_view()),
    path('register/', RegisterAccount.as_view())
]
