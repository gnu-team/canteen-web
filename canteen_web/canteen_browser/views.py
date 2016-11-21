from django.shortcuts import redirect, render
from rest_framework.renderers import JSONRenderer
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required

from canteen import models
from canteen_api import serializers
from canteen_browser.forms import RegisterForm

# Return the JavaScript REST API client with the given screen active
@login_required(login_url='/login/')
def map(request, active_screen=None):
    reports = models.Report.objects.all()
    serializer = serializers.ReportSerializer(reports, many=True,
                                              context={'request': request})
    reports_json = JSONRenderer().render(serializer.data)

    if request.user.has_perm('canteen.view_purityreport'):
        purity_reports = models.PurityReport.objects.all()
        serializer = serializers.PurityReportSerializer(purity_reports, many=True,
                                                        context={'request': request})
        purity_reports_json = JSONRenderer().render(serializer.data)
    else:
        purity_reports_json = None

    ctx = {
        'reports_json': reports_json,
        'purity_reports_json': purity_reports_json,
        'active': active_screen or 'map',
    }

    return render(request, 'canteen_browser/map.html', ctx)

def register(request):
    form = RegisterForm(request.POST if request.method == 'POST' else None)

    if request.method == 'POST' and form.is_valid():
        user = form.save()
        login(request, user)
        return redirect('canteen_browser:map')
    else:
        ctx = {
            'form': form,
        }

        return render(request, 'registration/register.html', ctx)
