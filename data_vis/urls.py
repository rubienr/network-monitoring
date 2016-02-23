# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^servers/?$', views.getClosestServersView, name="server_list"),

    url(r'^pingpie/?$', views.DefaultChartView.as_view(
        dataSource="ping",
        view="pie"),
        name="ping_count_pie"),
    url(r'^transferpiedownload/?$', views.DefaultChartView.as_view(
        dataSource="transfer",
        view="pie",
        direction="download"),
        name="transfer_count_pie_download"),
    url(r'^transferpieupload/?$', views.DefaultChartView.as_view(
        dataSource="transfer",
        view="pie",
        direction="upload"),
        name="transfer_count_pie_upload"),
    url(r'^transferpie/?$', views.DefaultChartView.as_view(
        dataSource="transfer",
        view="pie",
        direction="downloadupload"),
        name="transfer_count_pie"),

    url(r'^pingtimeline/?$', views.DefaultChartView.as_view(
        dataSource="ping",
        view="timeline"),
        name="ping_timeline"),
    url(r'^transfertimelinedownload/?$',
        views.DefaultChartView.as_view(
        dataSource="transfer",
        view="timeline",
        direction="download"),
        name="transfer_timeline_download"),
    url(r'^transfertimelineupload/?$',
        views.DefaultChartView.as_view(
        dataSource="transfer",
        view="timeline",
        direction="upload"),
        name="transfer_timeline_upload"),
    url(r'^transfertimeline/?$',
        views.DefaultChartView.as_view(
        dataSource="transfer",
        view="timeline",
        direction="downloadupload"),
        name="transfer_timeline"),
    ]
