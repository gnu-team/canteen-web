from django.conf.urls import url
from canteen_browser import views

# Set namespace
app_name = 'canteen_browser'

urlpatterns = [
    url(r'^(?:(?P<active_screen>reports)/)?$', views.map, name='map'),
]
