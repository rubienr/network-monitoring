from django.contrib import admin
from models import SpeedtestCliConfig, OsSystemPingConfig, PingTestResult, SpeedtestResult, TransferTestResult


admin.site.register(SpeedtestCliConfig)
admin.site.register(OsSystemPingConfig)

admin.site.register(PingTestResult)
admin.site.register(SpeedtestResult)
admin.site.register(TransferTestResult)



from django.contrib import admin
from solo.admin import SingletonModelAdmin
from models import SiteConfiguration

admin.site.register(SiteConfiguration, SingletonModelAdmin)
