from django.contrib.auth.models import User
from django.db import models

class Report(models.Model):
    TYPE_CHOICES = (
        (0, 'Bottled'),
        (1, 'Well'),
        (2, 'Stream'),
        (3, 'Lake'),
        (4, 'Spring'),
        (5, 'Other'),
    )
    CONDITION_CHOICES = (
        (0, 'Waste'),
        (1, 'Treatable-Clear'),
        (2, 'Treatable-Muddy'),
        (3, 'Potable'),
    )

    date = models.DateTimeField('date created')
    creator = models.ForeignKey(User, related_name='reports')
    latitude = models.FloatField()
    longitude = models.FloatField()
    type = models.IntegerField(choices=TYPE_CHOICES)
    condition = models.IntegerField(choices=CONDITION_CHOICES)
    description = models.CharField(max_length=256, default='')

    class Meta:
        permissions = (
            ('view_report', 'Can view report'),
        )

    def __str__(self):
        return '{} {}: {}, {}{}'.format(dict(self.CONDITION_CHOICES)[self.condition],
                                  dict(self.TYPE_CHOICES)[self.type],
                                  self.latitude, self.longitude,
                                  ". " + self.description if self.description else "")

class PurityReport(models.Model):
    date = models.DateTimeField('date created')
    creator = models.ForeignKey(User)
    location = models.CharField(max_length=512)
    condition = models.IntegerField()
    virus_ppm = models.IntegerField()
    contaminant_ppm = models.IntegerField()

    class Meta:
        permissions = (
            ('view_purityreport', 'Can view purity report'),
        )

    def __str__(self):
        return '{} {}/{}, {}'.format(self.condition, self.virus_ppm,
                                     self.contaminant_ppm, self.location)
