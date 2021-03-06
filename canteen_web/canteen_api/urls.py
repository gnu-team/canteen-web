from django.conf.urls import url
from rest_framework import routers
from canteen_api.views import ReportViewSet, PurityReportViewSet, UserViewSet, CurrentUserView, NearbyPurityReportsView

router = routers.DefaultRouter()
router.register('reports', ReportViewSet)
router.register('purity_reports', PurityReportViewSet)
router.register('users', UserViewSet)

custom_urls = [
    url(r'^users/me/$', CurrentUserView.as_view()),
    url(r'^purity_reports/near/(?P<latitude>-?\d+\.\d+),(?P<longitude>-?\d+\.\d+)/$', NearbyPurityReportsView.as_view()),
]

urlpatterns = custom_urls + router.urls
