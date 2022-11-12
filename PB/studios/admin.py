from django.contrib import admin

from studios.models import Amenity, Studio, StudioSearchHash, StudioSearchTemp


# Register your models here.


@admin.register(Studio)
class StudioAdmin(admin.ModelAdmin):
    pass

@admin.register(Amenity)
class AmenityAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'studio', 'type')
    pass

@admin.register(StudioSearchTemp)
class SSTAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'studio', 'dist')
    pass

@admin.register(StudioSearchHash)
class SSHAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'hash', 'search_date')
    pass
