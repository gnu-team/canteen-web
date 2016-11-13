from django.shortcuts import render
from rest_framework.renderers import JSONRenderer

from canteen import models
from canteen_api import serializers

def map(request):
    reports = models.Report.objects.all()
    serializer = serializers.ReportSerializer(reports, many=True,
                                              context={'request': request})
    reports_json = JSONRenderer().render(serializer.data)

    ctx = {
        'reports_json': reports_json,
    }

    return render(request, 'canteen_browser/map.html', ctx)
