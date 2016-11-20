from django.shortcuts import render
from rest_framework.renderers import JSONRenderer
from django.contrib.auth.decorators import login_required

from canteen import models
from canteen_api import serializers

# Return the JavaScript REST API client with the given screen active
@login_required(login_url='/login/')
def map(request, active_screen=None):
    reports = models.Report.objects.all()
    serializer = serializers.ReportSerializer(reports, many=True,
                                              context={'request': request})
    reports_json = JSONRenderer().render(serializer.data)

    ctx = {
        'reports_json': reports_json,
        'active': active_screen or 'map',
    }

    return render(request, 'canteen_browser/map.html', ctx)
