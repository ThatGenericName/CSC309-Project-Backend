
from django.contrib import admin
from django.urls import include, path

from gymclasses.views.useraddgymclass import AddGymClassToUser, \
    RemoveGymClassFromUser

app_name = 'gymclasses'

urlpatterns = [
    path('<int:class_id>/signup/', AddGymClassToUser.as_view(), name='enrollGymClass'),
    path('<int:class_id>/drop/', RemoveGymClassFromUser.as_view(), name='dropGymClass'),
]
