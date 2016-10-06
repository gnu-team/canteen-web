from django.contrib.auth.models import User
from django.db import models

class Report(models.Model):
    date = models.DateTimeField('date created')
    creator = models.ForeignKey(User, related_name='reports')
    location = models.CharField(max_length=512)
    type = models.CharField(max_length=64)
    condition = models.CharField(max_length=64)

class PurityReport(models.Model):
    date = models.DateTimeField('date created')
    creator = models.ForeignKey(User)
    location = models.CharField(max_length=512)
    condition = models.IntegerField()
    virus_ppm = models.IntegerField()
    contaminant_ppm = models.IntegerField()
