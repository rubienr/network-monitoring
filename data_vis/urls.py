from django.conf.urls import url
from . import views
from service.Scheduler import startScheduler
from constance import config
import logging


urlpatterns = [
    url(r'^pi/?$', views.piChart, name='pi'),
    url(r'^line/?$', views.lineWithFocusChart, name='line'),
]
