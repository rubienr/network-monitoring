from django.conf.urls import url
from . import views
from service.Scheduler import startScheduler
from constance import config
import logging


urlpatterns = [
    url(r'^$', views.index, name='index'),
]

#try:
#    if config.ENABLE_PROBING_ON_START:
#        logger = logging.getLogger(__name__).debug("starting scheduler on service start")
#        startScheduler()
#except:
#    pass