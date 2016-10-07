from rest_framework import viewsets, permissions
from django.shortcuts import render
from django.contrib.auth.models import User
from canteen.serializers import ReportSerializer, UserSerializer
from canteen.models import Report

class ReportViewSet(viewsets.ModelViewSet):
    queryset = Report.objects.all().order_by('type');
    serializer_class = ReportSerializer

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all();
    serializer_class = UserSerializer
    permission_classes = (permissions.IsAdminUser,)
