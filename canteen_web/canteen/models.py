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
    description = models.CharField(max_length=256, default='', blank=True)

    class Meta:
        permissions = (
            ('view_report', 'Can view report'),
        )

    def __str__(self):
        fmt = '{} {}: {}, {}{}'
        return fmt.format(dict(self.CONDITION_CHOICES)[self.condition],
                          dict(self.TYPE_CHOICES)[self.type],
                          self.latitude, self.longitude,
                          ". " + self.description if self.description else "")

class PurityReport(models.Model):
    CONDITION_CHOICES = (
        (0, 'Safe'),
        (1, 'Treatable'),
        (2, 'Unsafe'),
    )

    date = models.DateTimeField('date created')
    creator = models.ForeignKey(User, related_name='purity_reports')
    latitude = models.FloatField()
    longitude = models.FloatField()
    virusPPM = models.FloatField('virus PPM')
    contaminantPPM = models.FloatField('contaminant PPM')
    condition = models.IntegerField(choices=CONDITION_CHOICES)
    description = models.CharField(max_length=256, default='', blank=True)

    class Meta:
        permissions = (
            ('view_purityreport', 'Can view purity report'),
        )

    def __str__(self):
        fmt = '{} {}vppm/{}cppm: {}, {}{}'
        return fmt.format(dict(self.CONDITION_CHOICES)[self.condition],
                          self.virusPPM, self.contaminantPPM,
                          self.latitude, self.longitude,
                          ". " + self.description if self.description else "")
