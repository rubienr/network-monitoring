from django.db import models


class OsSystemPingConfig(models.Model):
    enableProbe = models.BooleanField("enable or deactivate probe", default=True)
    host = models.CharField("host/address to ping", default="8.8.8.8", max_length=512)
    packageCount = models.PositiveSmallIntegerField("number of ping packages", default=5)
    packageSize = models.SmallIntegerField("ping package size (min 25)", default=55)
    handler = models.CharField("the probe class", choices=[("service.probing.OsSystemPingProbe", "default probe")],
                                 max_length=128, default="service.probing.OsSystemPingProbe")


class PingTestResult(models.Model):
    pingStart = models.DateTimeField("probe start time stamp")
    pingEnd = models.DateTimeField("probe end time stamp")
    packageToTransmit = models.SmallIntegerField("packages to transmit", default=-1)
    rttMin = models.FloatField("shortest trip time [ms]", default=-1.0)
    rttMax = models.FloatField("longest trip time [ms]", default=-1.0)
    rttAvg = models.FloatField("average trip time [ms]", default=-1.0)
    rttStdDev = models.FloatField("trip time standard deviance [ms]", default=-1.0)
    packageTransmitted = models.IntegerField("number transmitted packages", default=-1)
    packageReceived = models.IntegerField("number received packages", default=-1)
    packageLost = models.IntegerField("number lost packages", default=-1)
    totalTime = models.FloatField("total duration in [ms]", default=-1)
    destinationHost = models.CharField("destination hostname", default="", max_length=256)
    destinationIp = models.CharField("destination ip address", default="", max_length=256)
    sendBytesNetto = models.IntegerField("bytes sent", default=-1)
    sendBytesBrutto = models.IntegerField("bytes sent including overhead", default=-1)

class SpeedtestCliConfig(models.Model):
    enableProbe = models.BooleanField("enable or deactivate probe", default=True)
    serverId = models.PositiveIntegerField("server id, leave empty for automatic detecting nearest server", default="", null=True, blank=True)
    direction = models.CharField("up- or download", choices=(("upload", "upload"), ("download", "download")),
                                 max_length=10, default="download")
    handler = models.CharField("the probe class", choices=[("service.probing.SpeedtestCliProbe", "default probe")],
                                 max_length=128, default="service.probing.SpeedtestCliProbe")


class TransferTestResult(models.Model):
    direction = models.CharField("up- or download", choices=(("upload", "upload"), ("download", "download")),
                                 max_length=10, default="download")
    transferStart = models.DateTimeField("probe start time stamp")
    transferEnd = models.DateTimeField("probe end time stamp")
    transferredUnits = models.PositiveIntegerField("transferred units", default=0)
    unitsPerSecond = models.CharField("units of transferred", max_length=10, choices=(("b", "bit"), ("B",  "byte")), default="B")

class SpeedtestResult(models.Model):
    transferResult = models.ForeignKey(TransferTestResult, on_delete=models.CASCADE)
    countryCode = models.CharField("coutry code", default="", max_length=10)
    country =models.CharField("country", default="", max_length=128)
    distance = models.FloatField("distance ", default=-1.0, )
    host = models.CharField("host", default="", max_length=256)
    hostId = models.CharField("host id", default="", max_length=10)
    latency = models.FloatField("seconds latency", default=-1.0, max_length=10)
    latitude = models.CharField("latitude", default="", max_length=10)
    longitide = models.CharField("longitude", default="", max_length=10)
    cityName = models.CharField("city name", default="", max_length=128)
    sponsor = models.CharField("sponsor", default="", max_length=256)
    url = models.CharField("URL", default="", max_length=256)
    url2 = models.CharField("URL 2", default="", max_length=256)
