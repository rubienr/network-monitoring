# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.conf.urls import url
from . import views


urlpatterns = [
    url(r'^start/?$', views.start, name='index'),
    url(r'^stop/?$', views.stop, name='index'),
    url(r'^toggle/?$', views.toggle, name='index'),
    url(r'^status/?$', views.status, name='index'),
]
