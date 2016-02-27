# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from django.contrib.admin import StackedInline
from solo.admin import SingletonModelAdmin
from suit.admin import SortableModelAdmin

from models import *
from models import SiteConfiguration


class SpeedtestResultInline(StackedInline):
    model = SpeedtestResult
    sortable = "order"
    max_num=1


class PingTestResultAdmin(SortableModelAdmin):
    actions_on_top = True
    actions_on_bottom = False
    save_on_top = True
    list_per_page = 100
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


class TransferRestResultAdmin(SortableModelAdmin):
    save_on_top = True
    actions_on_top = True
    actions_on_bottom = False
    list_per_page = 100
    inlines = [
        SpeedtestResultInline,
    ]
    list_display = ["host", "direction", "transferStart", "transferEnd", "transferredUnitsPerSecond",
                    "transferredUnits", "units"]


class SpeedtestCliConfigAdmin(SortableModelAdmin):
    actions_on_top = True
    actions_on_bottom = False
    save_on_top = True
    list_per_page = 100
    sortable = "order"
    list_display = ["direction", "enableProbe", "serverId", "handler"]


class PingConfigAdmin(SortableModelAdmin):
    actions_on_top = True
    actions_on_bottom = False
    save_on_top = True
    list_per_page = 100
    sortable = "order"
    list_display = ["host", "enableProbe", "packageCount","packageSize","handler"]


class SpeedtestServerAdmin(SortableModelAdmin):
    actions_on_top = True
    actions_on_bottom = False
    save_on_top = True
    list_per_page = 100
    sortable = "order"
    list_display = ["serverId", "name", "country", "d", "timestamp", "sponsor"]


class SchedulerEventsAdmin(SortableModelAdmin):
    actions_on_top = True
    actions_on_bottom = False
    save_on_top = True
    list_per_page = 100
    sortable = "order"
    list_display = ["message", "schedulerUsed", "processId",  "isErroneous", "timestamp"]


class ProbeEventsAdmin(SortableModelAdmin):
    actions_on_top = True
    actions_on_bottom = False
    save_on_top = True
    list_per_page = 100
    sortable = "order"
    list_display = ["probeExecuted", "statusString", "schedulerUsed", "timestampStart", "onProbeStarted",
                    "onProbeFinished"]

admin.site.register(SiteConfiguration, SingletonModelAdmin)
admin.site.register(ServiceStatus, SingletonModelAdmin)
admin.site.register(PingTestResult, PingTestResultAdmin)
admin.site.register(TransferTestResult, TransferRestResultAdmin)
admin.site.register(SpeedtestCliConfig, SpeedtestCliConfigAdmin)
admin.site.register(PingConfig, PingConfigAdmin)
admin.site.register(SpeedtestServer, SpeedtestServerAdmin)
admin.site.register(ProbeEvents, ProbeEventsAdmin)
admin.site.register(SchedulerEvents, SchedulerEventsAdmin)
