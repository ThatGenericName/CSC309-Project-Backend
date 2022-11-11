
from django.contrib import admin
from django.urls import include, path
from .Views.createstudio import *
from .Views.addamenity import *
from .Views.listamenity import *

app_name = 'studios'

urlpatterns = [
    path('create/', CreateStudio.as_view(), name='CreateStudio'),
    path('<int:pk>/amenities/add/', AddAmenity.as_view(), name='AddAmenity'),
    path('<int:pk>/amenities/', ListAmenity.as_view(), name='ListAmenity'),
]
