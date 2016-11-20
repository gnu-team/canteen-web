from django.conf.urls import url
from django.contrib.auth import views as auth_views
from canteen_browser import views

# Set namespace
app_name = 'canteen_browser'

urlpatterns = [
    url(r'^(?:(?P<active_screen>reports)/)?$', views.map, name='map'),
    url(r'^login/$', auth_views.login, name='login'),
    url(r'^logout/$', auth_views.logout, name='logout'),
]
