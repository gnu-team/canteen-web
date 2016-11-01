from datetime import datetime, timezone
from rest_framework import generics, permissions, response, viewsets
from django.shortcuts import render
from django.contrib.auth.models import User
from canteen.models import Report, PurityReport
from canteen_api.permissions import DjangoModelPermissionsWithView, IsAdminOrPost
from canteen_api.serializers import ReportSerializer, PurityReportSerializer, UserSerializer

class ReportViewSet(viewsets.ModelViewSet):
    queryset = Report.objects.all().order_by('type');
    serializer_class = ReportSerializer
    permission_classes = (DjangoModelPermissionsWithView,)

    def perform_create(self, serializer):
        serializer.save(date=datetime.now(timezone.utc), creator=self.request.user)

class PurityReportViewSet(viewsets.ModelViewSet):
    queryset = PurityReport.objects.all();
    serializer_class = PurityReportSerializer
    permission_classes = (DjangoModelPermissionsWithView,)

    def perform_create(self, serializer):
        serializer.save(date=datetime.now(timezone.utc), creator=self.request.user)

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all();
    serializer_class = UserSerializer
    permission_classes = (IsAdminOrPost,)

class CurrentUserView(generics.GenericAPIView):
    serializer_class = UserSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        self.check_permissions(request)
        serializer = self.get_serializer(request.user)
        return response.Response(serializer.data)

    def put(self, request, *args, **kwargs):
        self.check_permissions(request)

        partial = kwargs.pop('partial', False)
        serializer = self.get_serializer(request.user, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return response.Response(serializer.data)

    def patch(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return self.put(request, *args, **kwargs)

class NearbyPurityReportsView(generics.ListAPIView):
    serializer_class = PurityReportSerializer
    permission_classes = (permissions.DjangoModelPermissions,)

    def get_queryset(self):
        urlComponents = self.request.resolver_match.kwargs
        latitude = float(urlComponents['latitude'])
        longitude = float(urlComponents['longitude'])

        return PurityReport.objects.filter(latitude=float(latitude), longitude=float(longitude))
