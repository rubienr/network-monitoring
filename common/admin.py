from django.contrib import admin
from models import SpeedtestCliConfig, OsSystemPingConfig, PingTestResult, SpeedtestResult, TransferTestResult
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


admin.site.register(SiteConfiguration, SingletonModelAdmin)
admin.site.register(PingTestResult, PingTestResultAdmin)
admin.site.register(TransferTestResult, TransferRestResultAdmin)
admin.site.register(SpeedtestCliConfig, SpeedtestCliConfigAdmin)
admin.site.register(OsSystemPingConfig, OsSystemPingConfigAdmin)