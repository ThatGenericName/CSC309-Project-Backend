from django.db import models

# Create your models here.

class Studio(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    post_code = models.CharField(max_length=255) # doesn't this fall under address?
    geo_loc = models.CharField(max_length=255)
    phone_num = models.CharField(max_length=20)
    last_modified = models.DateTimeField(auto_now=True)
    studio_imgs = models.ManyToManyField("ImageRep")

class ImageRep(models.Model):
    id = models.IntegerField(primary_key=True)
    image = models.ImageField(upload_to="StudioImages/", null=False)

class Amenity(models.Model):
    id = models.IntegerField(primary_key=True)
    studio = models.ForeignKey(Studio, null=False, on_delete=models.CASCADE)
    type = models.CharField(null=False, max_length=255)
    quantity = models.IntegerField(null=False)
