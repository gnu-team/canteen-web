from datetime import datetime, timezone
from rest_framework import viewsets
from django.shortcuts import render
from django.contrib.auth.models import User
from canteen.serializers import ReportSerializer, UserSerializer
from canteen.permissions import DjangoModelPermissionsWithView, IsAdminOrPost
from canteen.models import Report

class ReportViewSet(viewsets.ModelViewSet):
    queryset = Report.objects.all().order_by('type');
    serializer_class = ReportSerializer
    permission_classes = (DjangoModelPermissionsWithView,)

    def perform_create(self, serializer):
        serializer.save(date=datetime.now(timezone.utc), creator=self.request.user)

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all();
    serializer_class = UserSerializer
    permission_classes = (IsAdminOrPost,)
