from django.conf.urls import patterns, include, url
from django.contrib import admin
from service.Scheduler import startScheduler
from constance import config
import logging


urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
    url(r"service/", include("service.urls")),
    url(r"vis/", include("data_vis.urls")),
]
