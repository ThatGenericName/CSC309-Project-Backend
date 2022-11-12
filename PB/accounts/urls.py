from django.urls import path

from accounts.Views.accountsubscription import AddSubscription, \
    CanceAllSubscriptions, GetAllUserSubscriptions, GetSubscription
from accounts.Views.paymentinformation import AddPaymentInformation, \
    RemovePaymentInformation
from accounts.Views.editprofile import EditProfile
from accounts.Views.login import Login
from accounts.Views.logout import Logout
from accounts.Views.paymentinformation import GetPaymentInformation
from accounts.Views.profilepicture import AddProfilePicture, \
    ClearProfilePicture, ViewProfilePicture
from accounts.Views.register import RegisterAccount
from accounts.Views.usersubscriptiongenerator import AdminCreateUSubs
from accounts.Views.viewaccount import ViewAccount

app_name = 'accounts'

urlpatterns = [
    path('view/', ViewAccount.as_view(), name='viewAccount'),
    path('register/', RegisterAccount.as_view(), name='register'),
    path('login/', Login.as_view(), name='login'),
    path('logout/', Logout.as_view(), name='logout'),
    path('edit/', EditProfile.as_view(), name='edit'),
    path('icon/set/', AddProfilePicture.as_view(), name="addPicture"),
    path('icon/<str:image_uuid>', ViewProfilePicture.as_view(), name='viewPicture'),
    path('icon/clear/', ClearProfilePicture.as_view(), name='clearPicture'),
    path('subscriptions/add/', AddSubscription.as_view(), name='addSubscription'),
    path('subscriptions/cancel/', CanceAllSubscriptions.as_view(), name='cancelSubscriptions'),
    path('subscriptions/<int:pk>/', GetSubscription.as_view(), name='getSubscription'),
    path('subscriptions/', GetAllUserSubscriptions.as_view(), name='getAllSubscriptions'),
    path('payment/', GetPaymentInformation.as_view(), name='getPaymentInfo'),
    path('payment/add/', AddPaymentInformation.as_view(), name='addPaymentInfo'),
    path('payment/remove/', RemovePaymentInformation.as_view(), name='removePaymentInfo'),
    # Below are the admin debug calls
    path('admin/generatesubscriptions/', AdminCreateUSubs.as_view(), name='adminCreateUSubs')
]
