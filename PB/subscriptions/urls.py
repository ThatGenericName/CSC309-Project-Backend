
from django.contrib import admin
from django.urls import include, path

from subscriptions.views.subscriptiontests import AdminClearTgen, AdminCreate
from subscriptions.views.viewsubscriptions import CreateSubscription, \
    EditSubscription, GetSubscription, \
    ViewSubscriptions

app_name = 'subscriptions'

urlpatterns = [
    path('admin/create/<int:count>/', AdminCreate.as_view(), name='adminCreate'),
    path('admin/destroy/', AdminClearTgen.as_view(), name='adminDestroy'),
    path('', ViewSubscriptions.as_view(), name='viewSubscriptions'),
    path('<int:pk>/', GetSubscription.as_view(), name='viewSubscriptionDetail'),
    path('create/', CreateSubscription.as_view(), name='createSubscription'),
    path('<int:pk>/edit/', EditSubscription.as_view(), name='editSubscription')
]
