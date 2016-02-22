from django.db import models
import threading
import logging
from constance import config
from importlib import import_module
from common.models import OsSystemPingConfig as OsSystemPingConfig
from common.models import SpeedtestCliConfig as SpeedtestCliConfig

SCHEDULER = None

class Scheduler(threading.Thread):

    isRunning = True
    probeTypes = [SpeedtestCliConfig, OsSystemPingConfig]
    logger = None

    def __init__(self):
        super(Scheduler, self).__init__()
        self.logger = logging.getLogger(__name__)

    def run(self):
        import time
        self.logger.debug("process started")
        while self.isRunning:

            for instance in self.getInstances():
                try:
                    instance.probe()
                except Exception as e:
                    self.logger.error("failed to probe")
                    self.logger.exception(e)

                time.sleep(config.PROBE_SHORT_PAUSE)
                self.logger.debug("short paused for %s seconds" % (config.PROBE_SHORT_PAUSE))

            self.logger.debug("sleeping for %s seconds" % (config.PROBE_PAUSE))
            time.sleep(config.PROBE_PAUSE)
            self.logger.debug("wakeup")

    def getConfiguredTypes(self):
        all = []
        for type in self.probeTypes:
            for configured in type.objects.all():
                all.append(configured)
        return all

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
    if SCHEDULER == None:
        logger.debug("starting scheduler")
        SCHEDULER = Scheduler()
        SCHEDULER.start()
    elif not SCHEDULER.isAlive():
        SCHEDULER = Scheduler()
        SCHEDULER.start()
        logger.debug("restarting scheduler")
    else:
        logger.debug("scheduler already started")

