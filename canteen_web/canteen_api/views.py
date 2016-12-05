from datetime import datetime, timezone, timedelta
from rest_framework import generics, permissions, response, viewsets
from django.shortcuts import render
from django.contrib.auth.models import User
from django.utils.dateparse import parse_date
from django.contrib.gis.geos import Point
from canteen.models import Report, PurityReport
from canteen_api.permissions import DjangoModelPermissionsWithView, IsAdminOrPost
from canteen_api.serializers import ReportSerializer, PurityReportSerializer, UserSerializer

class ReportViewSet(viewsets.ModelViewSet):
    queryset = Report.objects.all()
    serializer_class = ReportSerializer
    permission_classes = (DjangoModelPermissionsWithView,)

    def perform_create(self, serializer):
        serializer.save(date=datetime.now(timezone.utc), creator=self.request.user)

class PurityReportViewSet(viewsets.ModelViewSet):
    queryset = PurityReport.objects.all()
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
    NEARBY_METERS = 1500
    serializer_class = PurityReportSerializer
    permission_classes = (permissions.DjangoModelPermissions,)

    def get_queryset(self):
        urlComponents = self.request.resolver_match.kwargs
        point = Point(float(urlComponents['longitude']), float(urlComponents['latitude']))
        filter_ = dict(
            loc__dwithin=(point, self.NEARBY_METERS),
        )

        # Parse a date from ISO 8601 form (YYYY-MM-DD) into a
        # timezone-aware UTC datetime. parse_date() is a Django utility
        # method that returns a datetime.date, which we can convert into
        # a timezone-aware datetime.datetime marked to use UTC. This is
        # necessary because unlike datetime.datetime objects, plain
        # date.date objects apparently have no tzdata, which is
        # annoying.
        getdate = lambda iso8601: datetime(*parse_date(iso8601).timetuple()[:3],
                                           tzinfo=timezone.utc)

        # If specified in the querystring, use startDate and endDate to
        # limit reports specified to an inclusive calendar-date range.
        # Since datetime objects describe an instant in time, not a
        # calendar day, some thought is required here.
        if 'startDate' in self.request.GET:
            # Limit results to reports posted at or after the instant
            # this datetime represents
            filter_['date__gte'] = getdate(self.request.GET['startDate'])
        if 'endDate' in self.request.GET:
            # Limit results to reports posted before the first instant
            # of the day after the given end date (this makes the end
            # date inclusive)
            filter_['date__lt'] = getdate(self.request.GET['endDate']) + timedelta(days=1)

        return PurityReport.objects.filter(**filter_)
