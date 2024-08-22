from django.db import models


class InvalidImage(models.Model):
    image_id = models.CharField(max_length=255)


class Record(models.Model):
    num = models.IntegerField()
    mismatch_count = models.IntegerField()
    mismatch_percentage = models.FloatField()
    invalid_images = models.ManyToManyField(InvalidImage)
    last_modified = models.DateTimeField(auto_now=True)
