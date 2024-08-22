from django.db import models


class Record(models.Model):
    num = models.IntegerField()
    mismatch_count = models.IntegerField()
    mismatch_percentage = models.FloatField()
    last_modified = models.DateTimeField(auto_now=True)
