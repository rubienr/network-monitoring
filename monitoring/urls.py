from django.conf.urls import patterns, include, url
from django.contrib import admin


urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
    url(r"service/", include("service.urls")),
    url(r"vis/", include("data_vis.urls")),
]
