from django.db import models

# Create your models here.
from rest_framework import serializers


class Studio(models.Model):
    name = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    post_code = models.CharField(max_length=255)  # doesn't this fall under address?
    geo_loc = models.CharField(max_length=255)
    phone_num = models.CharField(max_length=20)
    last_modified = models.DateTimeField(auto_now=True)


class ImageRep(models.Model):
    image = models.ImageField(upload_to="StudioImages/", null=False)
    studio = models.ForeignKey(Studio, on_delete=models.CASCADE, null=False)


class Amenity(models.Model):
    studio = models.ForeignKey(Studio, null=False, on_delete=models.CASCADE)
    type = models.CharField(null=False, max_length=255)
    quantity = models.IntegerField(null=False)


'''
Serializers
'''


class StudioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Studio
        fields = [
            'name',
            'address',
            'post_code',
            'geo_loc',
            'phone_num',
            'last_modified',
        ]


class ImageRepSerializer(serializers.ModelSerializer):
    studio = StudioSerializer
    class Meta:
        model = ImageRep
        fields = [
            'studio',
            'image',
        ]

class AmenitySerializer(serializers.ModelSerializer):
    studio = StudioSerializer
    class Meta:
        model = Amenity
        fields = [
            'type',
            'quantity',
        ]
