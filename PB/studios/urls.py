
from django.contrib import admin
from django.urls import include, path
from .Views.createstudio import *
from .Views.addamenity import *
from .Views.editstudio import EditStudio
from .Views.listamenity import *
from .Views.studiogenerator import AdminGenerateStudios
from .Views.viewstudios import ViewStudios
from .Views.getimages import ImageView

app_name = 'studios'

urlpatterns = [
    path('create/', CreateStudio.as_view(), name='CreateStudio'),
    path('studioimages/<str:image>', ImageView.as_view(), name='ImageView'),
    path('<int:pk>/amenities/add/', AddAmenity.as_view(), name='AddAmenity'),
    path('<int:pk>/amenities/', ListAmenity.as_view(), name='ListAmenity'),
    path('', ViewStudios.as_view(), name='viewStudios'),
    path('admingenerate/', AdminGenerateStudios.as_view(), name='generateStudios'),
    path('<int:pk>/edit/', EditStudio.as_view(), name='editStudio')
]
