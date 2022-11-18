
from django.contrib import admin
from django.urls import include, path

from gymclasses.views.useraddgymclass import AddGymClassSessionToUser, \
    AddGymClassToUser, DropAllClasses, RemoveGymClassFromUser, \
    RemoveGymClassSessionFromUser
from .views.addgymclass import CreateGymClass
from .views.deletegymschedule import DeleteGymSchedule
from .views.deletegymclass import DeleteGymClass
from .views.classesofstudio import ClassesofStudio
from .views.searchgymclassschedules import ViewGymClassSchedule

app_name = 'gymclasses'

urlpatterns = [
    path('session/<int:session_id>/signup/', AddGymClassSessionToUser.as_view(), name='enrollGymClassSession'),
    path('session/<int:session_id>/drop/', RemoveGymClassSessionFromUser.as_view(), name='dropGymClassSession'),
    path('<int:class_id>/signup/', AddGymClassToUser.as_view(), name='enrollGymClass'),
    path('<int:class_id>/drop/', RemoveGymClassFromUser.as_view(), name='dropGymClass'),
    path('dropclasses/', DropAllClasses.as_view(), name='dropAllClasses'),
    path('<int:studio_id>/create/', CreateGymClass.as_view(), name='CreateGymClass'),
    path('schedule/<int:gym_schedule>/delete/', DeleteGymSchedule.as_view(),
         name='DeleteGymSchedule'),
    path('<int:gym_class>/delete/', DeleteGymClass.as_view(), name='DeleteGymClass'),
    path('studio/<int:studio_id>/list/', ClassesofStudio.as_view(), name='ClassesofStudio'),
    path('', ViewGymClassSchedule.as_view(), name='ViewGymClassSchedule'),
]
