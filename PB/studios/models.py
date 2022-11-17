import uuid

import rest_framework.fields
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
    tgen = models.BooleanField(null=False, default=False)

    def __str__(self):
        return self.name


class ImageRep(models.Model):
    image = models.ImageField(upload_to="studios/studioimages/", null=False)
    studio = models.ForeignKey(Studio, on_delete=models.CASCADE, null=False)


class Amenity(models.Model):
    studio = models.ForeignKey(Studio, null=False, on_delete=models.CASCADE)
    type = models.CharField(null=False, max_length=255)
    quantity = models.IntegerField(null=False)
    tgen = models.BooleanField(null=False, default=False)


class StudioSearchHash(models.Model):
    hash = models.CharField(null=False, max_length=17)
    search_date = models.DateTimeField(auto_now_add=True)


class StudioSearchTemp(models.Model):  # This is so jank
    studio = models.ForeignKey(Studio, null=False, on_delete=models.CASCADE)
    searchkey = models.ForeignKey(StudioSearchHash, on_delete=models.CASCADE)
    dist = models.FloatField(null=False, default=0)


'''
Serializers
'''

class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImageRep
        fields = ['image', 'studio']

class StudioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Studio
        fields = [
            'id',
            'name',
            'address',
            'post_code',
            'geo_loc',
            'phone_num',
            'last_modified',
        ]

    def to_representation(self, instance):
        dat = super().to_representation(instance)

        imgQs = ImageRep.objects.filter(studio=instance)
        imageRepSerials = [ImageSerializer(imgRep).data for imgRep in imgQs]
        imageNames = [irs['image'] for irs in imageRepSerials]
        dat['images'] = imageNames

        return dat


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
