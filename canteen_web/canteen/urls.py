from django.conf.urls import url
from rest_framework import routers
from canteen.views import ReportViewSet, PurityReportViewSet, UserViewSet

router = routers.DefaultRouter()
router.register('reports', ReportViewSet)
router.register('purity_reports', PurityReportViewSet)
router.register('users', UserViewSet)

urlpatterns = router.urls
