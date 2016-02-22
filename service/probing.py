import speedtest_cli as speedtest
import threading
import os
import models
from django.utils import timezone
import sys
from Queue import Queue
import timeit
import logging
import subprocess
import re


class SpeedTestProbe(object):

    probeConfig = None

    def __init__(self, probeConfig=None):
        self.probeConfig = probeConfig
        pass

    def probe(self):
        raise NotImplementedError()


class OsSystemPingProbe(SpeedTestProbe):
    ''' '''
    #http://pythex.org/
    '''rtt min/avg/max/mdev = 13.347/13.347/13.347/0.000 ms'''
    '''group 1: min rtt, group 2: avg rtt, group 3: max rtt, group 4: standard deviance'''
    rttRegexp = re.compile("^rtt min/avg/max/mdev\s*=\s*([.\d]*)/([.\d]*)/([.\d]*)/([.\d]*)\w*\s*")

    '''5 packets transmitted, 5 received, 0% packet loss, time 4004ms'''
    '''group 1: package transmitted, group 2: p. received, group 3: p. loss, group 4: time in ms'''
    packetCountRegexp = re.compile("^([.\d]*)\s*packets\s*transmitted,\s* ([.\d]*)\s*received,\s* ([.\d]*)%\s*packet\s*loss,\s*time\s*([.\d]*)\s*ms")

    '''PING 8.8.8.8 (8.8.8.8) 10(38) bytes of data.'''
    '''group 1: host, group 2: ip, group 3: sent bytes, group 4: senty bytes inclusive overhead'''
    bytesTransmittedRegexp = re.compile("^PING\s*([.\w]*)\s*\(([.\d]*)\)\s*([.\d]*)\(([.\d]*)\)\s*bytes\s*of\s*data")

    logger = logging.getLogger(__name__)

    def __init__(self, probeConfig):
        super(OsSystemPingProbe, self).__init__(probeConfig)

    def probe(self):

        if not self.probeConfig.enableProbe:
            self.logger.info("skipping %s probe due to config setting" % (type(self).__name__))
            return
        self.logger.info("starting %s probe " % (type(self).__name__))

        output = subprocess.check_output(self.getCommand(), shell=True, stderr=subprocess.STDOUT)
        pingResult = models.PingTestResult()
        pingResult.pingStart = timezone.now()
        pingResult.packageToTransmit = self.probeConfig.packageCount
        for line in output.splitlines():
            result = self.rttRegexp.match(line)
            if result:
                pingResult.rttMin = float(result.group(1))
                pingResult.rttAvg = float(result.group(2))
                pingResult.rttMax = float(result.group(3))
                pingResult.rttStdDev = float(result.group(4))

            result = self.packetCountRegexp.match(line)
            if result:
                pingResult.packageTransmitted = int(result.group(1))
                pingResult.packageReceived = int(result.group(2))
                pingResult.packageLost = int(result.group(3))
                pingResult.totalTime = float(result.group(4))

            result = self.bytesTransmittedRegexp.match(line)
            if result:
                pingResult.destinationHost = result.group(1)
                pingResult.destinationIp = result.group(2)
                pingResult.sendBytesNetto = int(result.group(3))
                pingResult.sendBytesBrutto = int(result.group(4))

        pingResult.pingEnd = timezone.now()
        pingResult.save()
        self.logger.info("%s probe done" % (type(self).__name__))

    def getCommand(self):
        return "ping -nqc %s -s %s %s" % (self.probeConfig.packageCount, self.probeConfig.packageSize, self.probeConfig.host)

class SpeedtestCliProbe(SpeedTestProbe):

    logger = logging.getLogger(__name__)

    def __init__(self, probeConfig=None):
        super(SpeedtestCliProbe, self).__init__(probeConfig)


    def probe(self):

        if not self.probeConfig.enableProbe:
            self.logger.info("skipping %s probe due to config setting" % (type(self).__name__))
            return

        self.logger.info("starting %s probe " % (type(self).__name__))

        speedtest.shutdown_event = threading.Event()
        config = speedtest.getConfig()
        closestServer = speedtest.closestServers(config['client'])

        best = None
        serverId = self.probeConfig.serverId.strip()
        if not serverId == "":
            self.logger.debug("use server id [%s]" %(serverId))
            best = speedtest.getBestServer(filter(lambda x: x['id'] == serverId, closestServer))
            self.logger.debug("found host for [%s] -> host [%s]" %(serverId, best["host"]))
        else:
            best = speedtest.getBestServer(closestServer)

        sizes = [350, 500, 750, 1000, 1500, 2000, 2500, 3000, 3500, 4000]

        if not "download" in self.probeConfig.direction:
            result = models.TransferTestResult(unitsPerSecond="B", transferStart=timezone.now(), direction="upload")
            transferred, speed = self.uploadSpeed(best['url'], sizes, quiet=True)
            result.transferEnd = timezone.now()
            result.transferredUnits = transferred
            result.save()
            self.appendServerInfos(result, best)
            self.logger.debug('upload: %0.2f M%s/s' % ((speed / 1000 / 1000) * 1, "byte"))
        else:
            urls = []
            for size in sizes:
                for i in range(0, 4):
                    urls.append('%s/random%sx%s.jpg' % (os.path.dirname(best['url']), size, size))

            result = models.TransferTestResult(unitsPerSecond="B", transferStart=timezone.now(), direction="download")
            transferred, speed = self.downloadSpeed(urls, quiet=True)
            result.transferEnd = timezone.now()
            result.transferredUnits = transferred
            result.save()
            self.appendServerInfos(result, best)
            self.logger.debug('download: %0.2f M%s/s' % ((speed / 1000 / 1000) * 1, "byte"))

        self.logger.info("%s probe done" % (type(self).__name__))

    def appendServerInfos(self, result, serverInfos):
        result.speedtestresult_set.create(
            countryCode=serverInfos["cc"], country=serverInfos["country"], distance=serverInfos["d"],
            host=serverInfos["host"], hostId=serverInfos["id"], latency=serverInfos["latency"],
            latitude=serverInfos["lat"], longitide=serverInfos["lon"],
            cityName=serverInfos["name"], sponsor=serverInfos["sponsor"], url=serverInfos["url"],
            url2=serverInfos["url2"])

    def downloadSpeed(self, files, quiet=False):
        """slightly modified impl. of speedtest_cli.downloadSpeed()"""
        start = timeit.default_timer()

        def producer(q, files):
            for file in files:
                thread = speedtest.FileGetter(file, start)
                thread.start()
                q.put(thread, True)
                if not quiet and not speedtest.shutdown_event.isSet():
                    sys.stdout.write('.')
                    sys.stdout.flush()

        finished = []

        def consumer(q, total_files):
            while len(finished) < total_files:
                thread = q.get(True)
                while thread.isAlive():
                    thread.join(timeout=0.1)
                finished.append(sum(thread.result))
                del thread

        q = Queue(6)
        prod_thread = threading.Thread(target=producer, args=(q, files))
        cons_thread = threading.Thread(target=consumer, args=(q, len(files)))
        start = timeit.default_timer()
        prod_thread.start()
        cons_thread.start()
        while prod_thread.isAlive():
            prod_thread.join(timeout=0.1)
        while cons_thread.isAlive():
            cons_thread.join(timeout=0.1)
        s = sum(finished)
        return (s, s / (timeit.default_timer() - start))

    def uploadSpeed(self, url, sizes, quiet=False):
        """slightly modified impl. of speedtest_cli.uploadSpeed()"""

        start = timeit.default_timer()

        def producer(q, sizes):
            for size in sizes:
                thread = speedtest.FilePutter(url, start, size)
                thread.start()
                q.put(thread, True)
                if not quiet and not speedtest.shutdown_event.isSet():
                    sys.stdout.write('.')
                    sys.stdout.flush()

        finished = []

        def consumer(q, total_sizes):
            while len(finished) < total_sizes:
                thread = q.get(True)
                while thread.isAlive():
                    thread.join(timeout=0.1)
                finished.append(thread.result)
                del thread

        q = Queue(6)
        prod_thread = threading.Thread(target=producer, args=(q, sizes))
        cons_thread = threading.Thread(target=consumer, args=(q, len(sizes)))
        start = timeit.default_timer()
        prod_thread.start()
        cons_thread.start()
        while prod_thread.isAlive():
            prod_thread.join(timeout=0.1)
        while cons_thread.isAlive():
            cons_thread.join(timeout=0.1)
        s = sum(finished)
        return (s, s / (timeit.default_timer() - start))
