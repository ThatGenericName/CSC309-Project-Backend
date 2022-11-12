from django.contrib import admin

from gymclasses.models import GymClass


# Register your models here.

@admin.register(GymClass)
class GymclassAdmin(admin.ModelAdmin):
    pass
