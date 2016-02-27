# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import models
from django.utils import timezone
from solo.models import SingletonModel
from django.core.validators import MaxValueValidator, MinValueValidator


class PingConfig(models.Model):
    enableProbe = models.BooleanField("enable configuraton", default=True)
    host = models.CharField("host/address to ping", default="8.8.8.8", max_length=512)
    packageCount = models.PositiveSmallIntegerField("number of ping packages", default=5)
    packageSize = models.SmallIntegerField("ping package size (25 to 1472) in [Bytes]", default=55,
                                           validators=[MaxValueValidator(1472), MinValueValidator(25)])
    timeout = models.PositiveIntegerField("probe timeout in [s]", default=3,  validators=[MaxValueValidator(20), MinValueValidator(1)])
    handler = models.CharField("the probe class",
                               choices=[("service.probing.OsSystemPingProbe", "default probe"),
                                        ("service.probing.PypingProbe", "python ping (needs root perm.)"), ],
                               max_length=128, default="service.probing.OsSystemPingProbe")
    order = models.PositiveIntegerField("list order", default=0)

    class Meta:
        verbose_name = "Ping Configuration"

    def __repr__(self):
        asString = ""
        for k, v in dict((key, value) for key, value in self.__dict__.iteritems()
                         if not callable(value) and not key.startswith('_')).iteritems():
            asString += "%s=%s " % (k,v)

        return asString



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
    order = models.PositiveIntegerField("list order", default=0)

    class Meta:
        verbose_name = "Ping Result"


class SpeedtestCliConfig(models.Model):
    enableProbe = models.BooleanField("enable configuration", default=True)
    serverId = models.PositiveIntegerField("server id, leave empty for automatic detecting nearest server", default="", null=True, blank=True)
    direction = models.CharField("up- or download", choices=[("upload", "upload"), ("download", "download")],
                                 max_length=10, default="download")
    handler = models.CharField("the probe class", choices=[("service.probing.SpeedtestCliProbe", "default probe")],
                                 max_length=128, default="service.probing.SpeedtestCliProbe")
    order = models.PositiveIntegerField("list order", default=0)

    class Meta:
        verbose_name = "Speedtest.net Configuration"

    def __repr__(self):
        asString = ""
        for k, v in dict((key, value) for key, value in self.__dict__.iteritems()
                         if not callable(value) and not key.startswith('_')).iteritems():
            asString += "%s=%s " % (k,v)

        return asString



class TransferTestResult(models.Model):
    direction = models.CharField("up- or download", choices=[("upload", "upload"), ("download", "download")],
                                 max_length=10, default="download")
    transferStart = models.DateTimeField("probe start time stamp")
    transferEnd = models.DateTimeField("probe end time stamp")
    transferredUnits = models.PositiveIntegerField("transferred units", default=0)
    unitsPerSecond = models.CharField("units of transferred", max_length=10, choices=[("b", "bit"), ("B",  "byte")], default="B")
    host = models.CharField("host", default="", max_length=256)
    order = models.PositiveIntegerField("list order", default=0)

    class Meta:
        verbose_name = "Up-/Download Result"



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
    order = models.PositiveIntegerField("list order", default=0)

    class Meta:
        verbose_name = "Speedtest.net Result"



class SpeedtestServer(models.Model):
    timestamp = models.DateTimeField("timestamp")
    serverId = models.CharField("speedtest.net server id", default="", max_length=128)
    name = models.CharField("city name", default="", max_length=128)
    url = models.CharField("url", default="", max_length=128)
    country = models.CharField("location country", default="", max_length=128)
    d = models.CharField("distance [km]", default="", max_length=128)
    cc = models.CharField("country code", default="", max_length=128)
    host = models.CharField("host name", default="", max_length=128)
    sponsor = models.CharField("service sponsor", default="", max_length=128)
    url2 = models.CharField("url2", default="", max_length=128)
    lat = models.CharField("latitude", default="", max_length=128)
    lon = models.CharField("longitude", default="", max_length=128)
    order = models.PositiveIntegerField("list order", default=0)

    def fromDict(self, serverId, name, url, country, d, cc, host, sponsor, url2, lat, lon):
        self.timestamp = timezone.now()
        self.serverId = serverId
        self.name = name
        self.url = url
        self.country = country
        self.d = d
        self.cc = cc
        self.host = host
        self.sponsor = sponsor
        self.url2 = url2
        self.lat = lat
        self.lon = lon
        self.order = 0
        return self

    class Meta:
        verbose_name = "Speedtest.net Server"


class SchedulerEvents(models.Model):
    order = models.PositiveIntegerField("list order")
    timestamp = models.DateTimeField("time stamp")
    isErroneous = models.BooleanField("is error message", default=False)
    schedulerUsed = models.CharField("utilized scheduler", default="", max_length=128)
    message = models.CharField("message", default="", max_length=512)
    processId = models.PositiveIntegerField("process id", default=0)

    class Meta:
        verbose_name = "Scheduler Event"


class ProbeEvents(models.Model):
    timestampStart = models.DateTimeField("task started")
    onProbeStarted = models.BooleanField("on probe started", default=False)
    onProbeFinished = models.BooleanField("on probe finished", default=False)
    schedulerUsed = models.CharField("utilized scheduler", default="", max_length=128)
    probeExecuted = models.CharField("used probe", default="", max_length=128)
    statusString = models.CharField("message", default="", max_length=128)
    order = models.PositiveIntegerField("list order")

    class Meta:
        verbose_name = "Probe Event"


class ServiceStatus(SingletonModel):
    isRunning = models.BooleanField("service started", default=False)
    statusString = models.CharField("status", max_length=128, default="")

    def __unicode__(self):
        return u"Service Status"

    class Meta:
        verbose_name = "Service Status"


class SiteConfiguration(SingletonModel):
    isProbingEnabled = models.BooleanField("enable / disable probing", default=False)
    probePause = models.PositiveIntegerField("long pause in [s] (___)", default=60,
                                             validators=[MaxValueValidator(60*60*24), MinValueValidator(0)])
    probeShortPause = models.PositiveIntegerField("short pause in [s] (.)", default=3,
                                              validators=[MaxValueValidator(60*60*24), MinValueValidator(0)])
    schedulerName = models.CharField("scheduling strategy", choices=[("service.scheduling.AllAtOnceScheduler",
                                                                      "all at once: P1.P2.P3___P1.P2.P3___P1.P2.P3___"),
                                                                     ("service.scheduling.SingleProbeScheduler",
                                                                      "porobe by probe: P1___P2___P3___P1___")],
                                     max_length=128, default="service.scheduling.AllAtOnceScheduler")

    def __unicode__(self):
        return "Site Configuration"

    class Meta:
        verbose_name = "Site Configuration"
