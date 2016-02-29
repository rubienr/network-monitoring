# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone
from solo.models import SingletonModel


# def uniqueConfigNameValidator(value):
#    table = ""
#    if len(PingConfig.objects.filter(probeName=value)):
#        table = PingConfig._meta.verbose_name
#
#    if len(SpeedtestCliConfig.objects.filter(probeName=value)):
#        table = SpeedtestCliConfig._meta.verbose_name
#
#    if len(PycurlConfig.objects.filter(probeName=value)):
#        table = PycurlConfig._meta.verbose_name
#
#    if table is not "":
#        raise ValidationError(('Configuration with this name already exists in %s.' % table),)


class PingConfig(models.Model):
    probeName = models.CharField("probe name", default="", blank=False, max_length=128,  # primary_key=True,
                                 help_text="The profile name will be used as label in charts.",
                                 )  #validators=[uniqueConfigNameValidator])
    isProbeEnabled = models.BooleanField("is enabled", default=True,
                                         help_text="If enabled this probe is active.")
    host = models.CharField("host/address to ping", default="8.8.8.8", max_length=512, blank=False,
                            help_text="Host name or ip-address to ping.")
    packageCount = models.PositiveSmallIntegerField("number of ping packages", default=5,
                                                    help_text="Number of packages ping sould send.")
    packageSize = models.SmallIntegerField("ping package size in [Bytes]", default=55,
                                           validators=[MaxValueValidator(1472), MinValueValidator(25)],
                                           help_text="Size of each ping packet. Must be within 25 to 1472 Bytes.")
    timeout = models.PositiveIntegerField("probe timeout in [s]", default=10,
                                          validators=[MaxValueValidator(20), MinValueValidator(1)],
                                          help_text="A timeout when ping aborts regardless of the received " \
                                                    "packets so far. Aborted probes are not stored.")
    handler = models.CharField("probe class",
                               choices=[("service.probing.OsSystemPingProbe", "default"),
                                        ("service.probing.PypingProbe", "PyPing (needs root permission)"), ],
                               max_length=128, default="service.probing.OsSystemPingProbe",
                               help_text="Which Ping invokation to use. Per default the " \
                                         "os-system's ping is used (values may not be parsed correctly). If this application has root access PyPing is the better choice.")
    order = models.PositiveIntegerField("list order", default=0)

    class Meta:
        verbose_name = "Ping Configuration"

    def __repr__(self):
        asString = ""
        for k, v in dict((key, value) for key, value in self.__dict__.iteritems()
                         if not callable(value) and not key.startswith('_')).iteritems():
            asString += "%s=%s " % (k, v)

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
    probeName = models.CharField("applied probe name", default="", blank=False, max_length=128)

    class Meta:
        verbose_name = "Ping Result"


class SpeedtestCliConfig(models.Model):
    probeName = models.CharField("probe name", default="", blank=False, max_length=128,  # primary_key=True,
                                 help_text="The profile name will be used as label in charts.",
                                 )  #validators=[uniqueConfigNameValidator])
    isProbeEnabled = models.BooleanField("is enabled", default=True, help_text="If enabled this probe is active.")
    serverId = models.PositiveIntegerField("server id",
                                           default="", null=True, blank=True, help_text="Leave empty for automatic " \
                                                                                        "nearest server. A server list can be <a href='/vis/servers'>updated</a> or obtained <a href='/admin/common/speedtestserver/'>here</a>. ")
    direction = models.CharField("up- or download", choices=[("upload", "upload"), ("download", "download")],
                                 max_length=10, default="download",
                                 help_text="Upload: service pushes data to server, download: service fetches data from server.")
    handler = models.CharField("probe class", choices=[("service.probing.SpeedtestCliProbe", "default probe")],
                               max_length=128, default="service.probing.SpeedtestCliProbe",
                               help_text="Which probe implementation to use.", editable=False)
    order = models.PositiveIntegerField("list order", default=0)

    class Meta:
        verbose_name = "Speedtest.net Configuration"

    def __repr__(self):
        asString = ""
        for k, v in dict((key, value) for key, value in self.__dict__.iteritems()
                         if not callable(value) and not key.startswith('_')).iteritems():
            asString += "%s=%s " % (k, v)

        return asString


class PycurlConfig(models.Model):
    probeName = models.CharField("probe name", default="", blank=False, max_length=128,  # primary_key=True,
                                 help_text="The profile name will be used as label in charts.",
                                 )  #validators=[uniqueConfigNameValidator])
    isProbeEnabled = models.BooleanField("is enabled", default=True,
                                         help_text="If enabled this probe is active.")
    url = models.CharField("download file url", default="ftp://ftp.inode.at/speedtest-5mb", max_length=128, blank=False,
                           help_text="Resource URL to be downloaded with curl (http, ftp, ...).")
    direction = models.CharField("up- or download", choices=[("download", "download")],
                                 max_length=128, default="download", editable=False)
    timeout = models.PositiveIntegerField("timeout in [s]", default=20,
                                          validators=[MaxValueValidator(3600), MinValueValidator(1)],
                                          help_text="A timeout when curl aborts regardless of the received " \
                                                    "data so far. Aborted probes are not stored.")
    handler = models.CharField("probe class", choices=[("service.probing.PycurlProbe", "default probe")],
                               max_length=128, default="service.probing.PycurlProbe", editable=False)
    order = models.PositiveIntegerField("list order", default=0)

    class Meta:
        verbose_name = "Curl Configuration"

    def __repr__(self):
        asString = ""
        for k, v in dict((key, value) for key, value in self.__dict__.iteritems()
                         if not callable(value) and not key.startswith('_')).iteritems():
            asString += "%s=%s " % (k, v)
        return asString


class TransferTestResult(models.Model):
    direction = models.CharField("up- or download", choices=[("upload", "upload"), ("download", "download")],
                                 max_length=10, default="download")
    transferStart = models.DateTimeField("probe start time stamp")
    transferEnd = models.DateTimeField("probe end time stamp")
    transferredUnits = models.PositiveIntegerField("transferred units", default=0)
    units = models.CharField("units", max_length=10, choices=[("bit", "bit"), ("Byte", "byte")], default="Byte")
    transferredUnitsPerSecond = models.PositiveIntegerField("transferred units per second", default=0)
    host = models.CharField("host", default="", max_length=256)
    url = models.CharField("url", default="", max_length=512)
    order = models.PositiveIntegerField("list order", default=0)
    probeName = models.CharField("applied probe name", default="", blank=False, max_length=128)

    class Meta:
        verbose_name = "Up-/Download Result"


class SpeedtestResult(models.Model):
    transferResult = models.ForeignKey(TransferTestResult, on_delete=models.CASCADE)
    countryCode = models.CharField("coutry code", default="", max_length=10)
    country = models.CharField("country", default="", max_length=128)
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
    isErroneous = models.BooleanField("is error message", default=False, help_text="If true this is an error message.")
    schedulerUsed = models.CharField("utilized scheduler", default="", max_length=128)
    message = models.CharField("message", default="", max_length=512)
    processId = models.PositiveIntegerField("process id", default=0, help_text="Scheduler process' id.")

    class Meta:
        verbose_name = "Scheduler Event"


class ProbeEvents(models.Model):
    timestampStart = models.DateTimeField("task started")
    onProbeStarted = models.BooleanField("on probe started", default=False,
                                         help_text="If true this message was issued on probe start.")
    onProbeFinished = models.BooleanField("on probe finished", default=False,
                                          help_text="If true this message was issued on probe end.")
    schedulerUsed = models.CharField("utilized scheduler", default="", max_length=128)
    probeExecuted = models.CharField("used probe", default="", max_length=128)
    statusString = models.CharField("message", default="", max_length=128)
    order = models.PositiveIntegerField("list order")

    class Meta:
        verbose_name = "Probe Event"


class SiteConfiguration(SingletonModel):
    isProbingEnabled = models.BooleanField("enable / disable probing service", default=False,
                                           help_text="If disabled the service cannot be activated manually. The "\
                                           "service must be always started manually.")
    probePause = models.PositiveIntegerField("long pause in [s]", default=60,
                                             validators=[MaxValueValidator(60 * 60 * 24), MinValueValidator(0)],
                                             help_text="Specifies the long pause for scheduling. Later referred as '___'.")
    probeShortPause = models.PositiveIntegerField("short pause in [s]", default=3,
                                                  validators=[MaxValueValidator(60 * 60 * 24), MinValueValidator(0)],
                                                  help_text="Specifies the short pause for scheduling. Later referred as '.'.")
    schedulerName = models.CharField("scheduling strategy", choices=[("service.scheduling.AllAtOnceScheduler",
                                                                      "all at once: P.P.P___P.P.P___P.P.P___"),
                                                                     ("service.scheduling.SingleProbeScheduler",
                                                                      "porobe by probe: P___P___P___P___P___")],
                                     max_length=128, default="service.scheduling.AllAtOnceScheduler",
                                     help_text="Depending on the chosen scheduler, the short and long pause interval is "\
                                     "applied according to the illustration (P=probe). The real probe order is undefined.")

    def __unicode__(self):
        return "Site Configuration"

    class Meta:
        verbose_name = "Site Configuration"
