# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.conf.urls import url
from . import views


urlpatterns = [
    url(r'^start/?$', views.start, name='start_service'),
    url(r'^stop/?$', views.stop, name='stop_service'),
    url(r'^toggle/?$', views.toggle, name='toggle_service'),
    url(r'^status/?$', views.status, name='service_status'),
]
