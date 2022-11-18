from django.contrib import admin

from gymclasses.models import GymClass, GymClassSchedule


# Register your models here.

@admin.register(GymClass)
class GymclassAdmin(admin.ModelAdmin):

    pass

@admin.register(GymClassSchedule)
class GymclassScheduleAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'parent_class', 'start_time')
    pass
