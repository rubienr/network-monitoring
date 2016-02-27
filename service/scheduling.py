# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import logging
import threading
from django.utils import timezone
from importlib import import_module
from common.models import PingConfig, SpeedtestCliConfig, SiteConfiguration, ServiceStatus, ProbeEvents, SchedulerEvents

SCHEDULER_PROBE_TYPES_REGISTER = [SpeedtestCliConfig, PingConfig]

class SchedulerBase(threading.Thread):

    isRunning = False
    isToBeRestarted = False
    logger = None
    condition = threading.Condition()
    __schedulerConfigured = None
    __isRestatLoggedOnce = False


    def __init__(self):
        self.logger = logging.getLogger(__name__)
        super(SchedulerBase, self).__init__()
        self.__schedulerConfigured = self.config().schedulerName

    def wait(self, timeout):
        if self.getRunningCondition() is False:
            return False

        self.condition.acquire()
        self.condition.wait(timeout=timeout)
        self.condition.release()

        return self.getRunningCondition()

    def notify_all(self):
        self.condition.acquire()
        self.condition.notify_all()
        self.condition.release()

    def run(self):
        pass

    def config(self):
        return SiteConfiguration.objects.get()

    def getConfiguredTypes(self):
        all = []
        for type in SCHEDULER_PROBE_TYPES_REGISTER:
            for configured in type.objects.all():
                all.append(configured)
        return all

    def getRunningCondition(self):
        scheduler = self.config().schedulerName
        if not self.__schedulerConfigured == scheduler:
            self.isToBeRestarted = True
            self.__schedulerConfigured = scheduler

        if self.isToBeRestarted:
            if self.config().isProbingEnabled:
                if not self.__isRestatLoggedOnce:
                    self.logger.debug("respawn scheduler due to config change")

                    self.onEvent("scheduler exchange (%s -> %s)" %
                                 (type(self).__name__, scheduler.rsplit('.', 1)[1]))
                    self.__isRestatLoggedOnce = True
                self.isRunning = False
                SCHEDULER.resetSchedulerReference(self)
                SCHEDULER.startScheduler()
            return False
        else:
            if self.isRunning and self.config().isProbingEnabled:
                return True
        return False

    def getInstances(self):
        all = []
        for config in self.getConfiguredTypes():
            parts = config.handler.rsplit('.', 1)
            self.logger.info("loading probe %s.%s" %(parts[0], parts[1]))
            SpeedTestProbe = getattr(import_module(parts[0]), parts[1])
            instance = SpeedTestProbe(probeConfig=config)
            all.append(instance)
        return all

    def onStart(self):
        SchedulerEvents(order = 0, timestamp=timezone.now(), isErroneous=False, message="start",
                        schedulerUsed=type(self).__name__, processId=self.ident).save()
        self.updateServiceStatusDb()

    def onStop(self):
        SchedulerEvents(order = 0, timestamp=timezone.now(), isErroneous=False, message="stop",
                        schedulerUsed=type(self).__name__, processId=self.ident).save()
        self.updateServiceStatusDb("stopped")
        SCHEDULER.resetSchedulerReference(self)

    def onProbe(self, probe):
        # ProbeEvents(timestampStart=timezone.now(), schedulerUsed=type(self).__name__, probeExecuted=probe.getName(),
        #            order = 0, onProbeStarted=True, onProbeFinished=False, statusString="start").save()
        # self.updateServiceStatusDb()
        pass

    def onProbeDone(self, probe):
        # ProbeEvents(timestampStart=timezone.now(), schedulerUsed=type(self).__name__, probeExecuted=probe.getName(),
        #            order = 0, onProbeFinished=True, onProbeStarted=False, statusString="finish").save()
        # self.updateServiceStatusDb()
        pass

    def onProbeException(self, probe, exception):
        ProbeEvents(timestampStart=timezone.now(), schedulerUsed=type(self).__name__, probeExecuted=probe.getName(),
                    order=0, onProbeFinished=True, onProbeStarted=False,
                    statusString=("exception: %s configuration: %s" %(exception, repr(probe.probeConfig)))).save()

    def onEvent(self, statusString):
        SchedulerEvents(order=0, timestamp=timezone.now(), isErroneous=False, message=statusString,
                        schedulerUsed=type(self).__name__, processId=self.ident).save()

    def updateServiceStatusDb(self, statusString="started"):
        ServiceStatus(isRunning=self.getRunningCondition(), statusString=statusString).save()


class SingleProbeScheduler(SchedulerBase):
    """executes one probe by probe with a long break between """
    """P1___P2___P3___P1___"""

    def __init__(self):
        super(SingleProbeScheduler, self).__init__()

    def run(self):
        self.isRunning = True
        self.logger.debug("scheduling started")
        self.onStart()
        while self.getRunningCondition():
            for instance in self.getInstances():
                try:
                    self.logger.info("probing %s" % instance)
                    self.onProbe(instance)
                    instance.probe()
                    self.onProbeDone(instance)
                    if not self.getRunningCondition():
                        break
                except Exception as e:
                    self.logger.exception(e)
                    self.onProbeException(instance, e)

                self.logger.debug("sleeping %s seconds" % (self.config().probePause))
                if self.wait(self.config().probePause) is False:
                    break

            self.logger.debug("wake up")
        self.logger.info("scheduler terminated")
        self.isRunning = False
        self.onStop()


class AllAtOnceScheduler(SchedulerBase):
    """executes all probes sequentially then sleeps for a long time"""
    """P1.P2.P3___P1.P2.P3___P1.P2.P3___"""

    def __init__(self):
        super(AllAtOnceScheduler, self).__init__()

    def run(self):
        self.isRunning = True
        self.logger.debug("scheduling started")
        self.onStart()
        while self.getRunningCondition():

            for instance in self.getInstances():
                try:
                    self.logger.info("probing %s" % instance)
                    self.onProbe(instance)
                    instance.probe()
                    self.onProbeDone(instance)
                    if not self.getRunningCondition():
                        break
                except BaseException as e:
                    self.logger.exception(e)
                    self.onProbeException(instance, e)

                self.logger.debug("short pause of %s seconds" % (self.config().probeShortPause))
                if self.wait(self.config().probePause) is False:
                    break

            self.logger.debug("sleeping %s seconds" % (self.config().probePause))
            if self.wait(self.config().probePause) is False:
                break

            self.logger.debug("wake up")
        self.logger.info("scheduler is terminating")
        self.isRunning = False
        self.onStop()

    def getInstances(self):
        all = []
        for config in self.getConfiguredTypes():
            parts = config.handler.rsplit('.', 1)
            self.logger.info("loading probe %s.%s" %(parts[0], parts[1]))
            SpeedTestProbe = getattr(import_module(parts[0]), parts[1])
            instance = SpeedTestProbe(probeConfig=config)
            all.append(instance)
        return all


class SchedulerSingleton():

    logger = logging.getLogger(__name__)
    __scheduler = None

    def startScheduler(self):

        if self.__scheduler == None:
            config = SiteConfiguration.objects.get()
            parts = config.schedulerName.rsplit('.', 1)
            self.logger.info("request scheduler start, invoke %s.%s" %(parts[0], parts[1]))
            SchedulerBase = getattr(import_module(parts[0]), parts[1])
            self.__scheduler = SchedulerBase()
            self.__scheduler.start()
        else:
            self.logger.debug("request scheduler start but scheduler already active")


    def stopScheduler(self):
        if self.__scheduler == None:
            self.logger.debug("request scheduler stop but no scheduler running")
        else:
            self.__scheduler.isRunning = False
            self.__scheduler.isToBeRestarted = False
            self.__scheduler.notify_all()
            self.logger.debug("request scheduler stop")


    def isAvailable(self):
        return self.__scheduler is not None

    def resetSchedulerReference(self, instance):
        if self.__scheduler == None:
            self.logger.debug("nothing to reset")

        if self.__scheduler == instance:
            self.logger.debug("detached scheduler from reference")
            self.__scheduler = None
        else:
            self.logger.debug("wrong instance is calling for detaching from reference")


SCHEDULER = SchedulerSingleton()
