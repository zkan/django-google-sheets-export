from django.conf.urls import url

from .views import index, auth_return


urlpatterns = [
    url(r'^$', index, name='index'),
    url(r'oauth2callback/$', auth_return, name='return'),
]
