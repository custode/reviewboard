from __future__ import unicode_literals

from django.conf.urls import patterns, url

import reviewboard.integrations.views as views


urlpatterns = patterns(
    '',
    url(r'^new/(?P<integration_class>\w+)/', views.configure_integration,
        name='new-integration'),
    url(r'(?P<config_id>\d+)/', views.configure_integration,
        name='configure-integration'),
    url(r'^$', views.integration_list),
)
