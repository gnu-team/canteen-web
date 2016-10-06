from django.contrib.auth.models import User
from canteen.models import Report
from rest_framework import serializers

class ReportSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Report
        fields = ('date', 'creator', 'location', 'type', 'condition')

class UserSerializer(serializers.HyperlinkedModelSerializer):
    reports = serializers.HyperlinkedRelatedField(view_name='report-detail', many=True, queryset=Report.objects.all())

    class Meta:
        model = User
        fields = ('username', 'email', 'reports')
