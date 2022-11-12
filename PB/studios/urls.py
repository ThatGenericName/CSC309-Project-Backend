from django.contrib import admin
from django.urls import include, path
from .Views.createstudio import *
from .Views.addamenity import *
from .Views.listamenity import *
from .Views.editstudio import *
from .Views.editamenity import *
from .Views.deletestudio import *

app_name = 'studios'

urlpatterns = [
    path('create/', CreateStudio.as_view(), name='CreateStudio'),
    path('<int:pk>/amenities/add/', AddAmenity.as_view(), name='AddAmenity'),
    path('<int:pk>/amenities/', ListAmenity.as_view(), name='ListAmenity'),
    path('<int:pk>/edit/', EditStudio.as_view(), name='EditStudio'),
    path('amenities/<int:pk>/edit/', EditAmenity.as_view(), name='EditAmenity'),
    path('<int:pk>/delete/', DeleteStudio.as_view(), name='DeleteStudio'),
]
