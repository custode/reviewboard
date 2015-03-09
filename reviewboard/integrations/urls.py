from __future__ import unicode_literals

from django.conf.urls import patterns, url

import reviewboard.integrations.views as views

urlpatterns = patterns(
    '',

    url(r'^$', views.integration_list),
    )