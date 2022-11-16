
from django.contrib import admin
from django.urls import include, path

from gymclasses.views.useraddgymclass import AddGymClassToUser, \
    RemoveGymClassFromUser
from .views.addgymclass import CreateGymClass
from .views.deletegymschedule import DeleteGymSchedule
from .views.deletegymclass import DeleteGymClass
from .views.classesofstudio import ClassesofStudio

app_name = 'gymclasses'

urlpatterns = [
    path('<int:class_id>/signup/', AddGymClassToUser.as_view(), name='enrollGymClass'),
    path('<int:class_id>/drop/', RemoveGymClassFromUser.as_view(), name='dropGymClass'),
    path('<int:studio_id>/create/', CreateGymClass.as_view(), name='CreateGymClass'),
    path('schedule/<int:gym_schedule>/delete/', DeleteGymSchedule.as_view(),
         name='DeleteGymSchedule'),
    path('<int:gym_class>/delete/', DeleteGymClass.as_view(), name='DeleteGymClass'),
    path('studio/<int:studio_id>/list/', ClassesofStudio.as_view(), name='ClassesofStudio'),
]
