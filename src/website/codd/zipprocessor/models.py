from django.db import models


class InvalidImage(models.Model):
    image_id = models.CharField(max_length=255)


class ContentImage(models.Model):
    image_id = models.CharField(max_length=255)


class ValidImage(models.Model):
    image_id = models.CharField(max_length=255)


class Record(models.Model):
    num = models.IntegerField()
    mismatch_count = models.IntegerField()
    mismatch_percentage = models.FloatField()
    invalid_images = models.ManyToManyField(InvalidImage)
    valid_images = models.ManyToManyField(ValidImage)
    content_images = models.ManyToManyField(ContentImage)
    last_modified = models.DateTimeField(auto_now=True)
