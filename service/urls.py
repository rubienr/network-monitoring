from django.conf.urls import url
from . import views
#from service.Scheduler import  startScheduler

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^pi/?$', views.piChart, name='pi'),
    url(r'^line/?$', views.lineWithFocusChart, name='line'),
]

#startScheduler()