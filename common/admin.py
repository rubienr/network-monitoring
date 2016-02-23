# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.contrib import admin
from models import *

from solo.admin import SingletonModelAdmin
from models import SiteConfiguration
from suit.admin import SortableModelAdmin
from django.contrib.admin import StackedInline


class SpeedtestResultInline(StackedInline):
    model = SpeedtestResult
    sortable = "order"
    max_num=1


class PingTestResultAdmin(SortableModelAdmin):
    sortable = "order"
    list_display = [
        "destinationHost",
        "destinationIp",
        "rttMin",
        "rttMax",
        "rttAvg",
        "rttStdDev",
        "packageTransmitted",
        "packageReceived",
        "packageLost",
        "totalTime",
        "sendBytesNetto",
        "sendBytesBrutto",
        "pingStart",
        "pingEnd",
        "packageToTransmit",
        "order",]

    fieldsets = [
    (None, {
        'classes': ('suit-tab', 'suit-tab-general',),
        'fields': ['pingStart', 'pingEnd',]
    }),
    ('Statistics', {
        'classes': ('suit-tab', 'suit-tab-general',),
        'fields': ['rttMin', 'rttAvg']}),
    ('Architecture', {
        'classes': ('suit-tab', 'suit-tab-cities',),
        'fields': ['destinationHost']}),
    ]

    suit_form_tabs = (('general', 'General'),
                      ('cities', 'Cities'),
                      ('info', 'Info on tabs'))


    suit_form_includes = (
            ('xxpiechart.html', 'middle', 'cities'),
        )



class TransferRestResultAdmin(SortableModelAdmin):
    inlines = [
        SpeedtestResultInline,
    ]
    list_display = ["host", "direction", "transferStart", "transferEnd", "transferredUnits", "unitsPerSecond"]


class SpeedtestCliConfigAdmin(SortableModelAdmin):
    sortable = "order"
    list_display = ["direction", "enableProbe", "serverId", "handler"]


class OsSystemPingConfigAdmin(SortableModelAdmin):
    sortable = "order"
    list_display = ["host", "enableProbe", "packageCount","packageSize","handler"]


class SpeedtestServerAdmin(SortableModelAdmin):
    sortable = "order"
    list_display = ["serverId", "name", "country", "d", "timestamp", "sponsor"]


class SchedulerEventsAdmin(SortableModelAdmin):
    sortable = "order"
    list_display = ["message", "schedulerUsed", "processId",  "isErroneous", "timestamp"]


class ProbeEventsAdmin(SortableModelAdmin):
    sortable = "order"
    list_display = ["schedulerUsed", "statusString", "probeExecuted", "timestampStart", "onProbeStarted", "onProbeFinished"]


admin.site.register(SiteConfiguration, SingletonModelAdmin)
admin.site.register(ServiceStatus, SingletonModelAdmin)
admin.site.register(PingTestResult, PingTestResultAdmin)
admin.site.register(TransferTestResult, TransferRestResultAdmin)
admin.site.register(SpeedtestCliConfig, SpeedtestCliConfigAdmin)
admin.site.register(OsSystemPingConfig, OsSystemPingConfigAdmin)
admin.site.register(SpeedtestServer, SpeedtestServerAdmin)
admin.site.register(ProbeEvents, ProbeEventsAdmin)
admin.site.register(SchedulerEvents, SchedulerEventsAdmin)

