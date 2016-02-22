from django.db import models
import threading
import logging
import time
from importlib import import_module
from common.models import OsSystemPingConfig as OsSystemPingConfig
from common.models import SpeedtestCliConfig as SpeedtestCliConfig
from common.models import SiteConfiguration as SiteConfiguration

SCHEDULER = None
SCHEDULER_PROBE_TYPES_REGISTER = [SpeedtestCliConfig, OsSystemPingConfig]

class Scheduler(threading.Thread):

    isRunning = False
    isToBeRestarted = False
    logger = None
    __schedulerConfigured = None

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        super(Scheduler, self).__init__()
        self.__schedulerConfigured = self.config().schedulerName

    def run(self):
        pass

    def config(self):
        return SiteConfiguration.objects.get()

    def getConfiguredTypes(self):
        all = []
        global  SCHEDULER_PROBE_TYPES_REGISTER
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
                self.logger.debug("restart scheduler")
                global SCHEDULER
                SCHEDULER = None
                self.isRunning = False
                startScheduler()
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


class SingleProbeScheduler(Scheduler):
    """executes one probe by probe with a long break between """
    """P1___P2___P3___P1___"""

    def __init__(self):
        super(SingleProbeScheduler, self).__init__()

    def run(self):
        self.isRunning = True
        self.logger.debug("scheduling started")
        while self.getRunningCondition():
            for instance in self.getInstances():
                try:
                    self.logger.info("probing %s" % instance)
                    instance.probe()
                    if not self.getRunningCondition():
                        break
                except Exception as e:
                    self.logger.error("failed to probe")
                    self.logger.exception(e)
                self.logger.debug("sleeping %s seconds" % (self.config().probePause))
                time.sleep(self.config().probePause)
            self.logger.debug("wake up")
        self.logger.info("scheduler is terminating")
        self.isRunning = False


class AllAtOnceScheduler(Scheduler):
    """executes all probes sequentially then sleeps for a long time"""
    """P1.P2.P3___P1.P2.P3___P1.P2.P3___"""

    def __init__(self):
        super(AllAtOnceScheduler, self).__init__()

    def run(self):
        self.isRunning = True
        self.logger.debug("scheduling started")
        while self.getRunningCondition():

            for instance in self.getInstances():
                try:
                    self.logger.info("probing %s" % instance)
                    instance.probe()
                    if not self.getRunningCondition():
                        break
                except Exception as e:
                    self.logger.error("failed to probe")
                    self.logger.exception(e)

                self.logger.debug("short pause of %s seconds" % (self.config().probeShortPause))
                time.sleep(self.config().probePause)

            self.logger.debug("sleeping %s seconds" % (self.config().probePause))
            time.sleep(self.config().probePause)
            self.logger.debug("wake up")
        self.logger.info("scheduler is terminating")
        self.isRunning = False

    def getInstances(self):
        all = []
        for config in self.getConfiguredTypes():
            parts = config.handler.rsplit('.', 1)
            self.logger.info("loading probe %s.%s" %(parts[0], parts[1]))
            SpeedTestProbe = getattr(import_module(parts[0]), parts[1])
            instance = SpeedTestProbe(probeConfig=config)
            all.append(instance)
        return all


def startScheduler():
    logger = logging.getLogger(__name__)
    global SCHEDULER
    if SCHEDULER == None or not SCHEDULER.isAlive():
        config = SiteConfiguration.objects.get()
        parts = config.schedulerName.rsplit('.', 1)
        logger.info("invoke scheduler %s.%s" %(parts[0], parts[1]))
        Scheduler = getattr(import_module(parts[0]), parts[1])
        SCHEDULER = Scheduler()
        SCHEDULER.start()
    else:
        logger.debug("scheduler already active")

