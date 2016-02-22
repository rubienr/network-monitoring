from django.conf.urls import url
from . import views


urlpatterns = [
    url(r'^pi/?$', views.pingProbesCountChart),
    url(r'^line/?$', views.pingProbesTimeLineChart),
    url(r'^transferline/?$', views.transferProbesTimeLineChart),
    url(r'^servers/?$', views.getClosestServers),
    url(r'^transferdl/?$', views.dlTransferProbesCountPieChart),
    url(r'^transferul/?$', views.ulTransferProbesCountPieChart),
    url(r'^transfer/?$', views.transferProbesCountPieChart),
]
