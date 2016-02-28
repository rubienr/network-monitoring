# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import logging
import os
import pycurl
import re
import subprocess
import sys
import threading
import timeit
import urlparse
from Queue import Queue
from StringIO import StringIO

import pyping
import speedtest_cli as speedtest
from django.utils import timezone

from common.models import PingTestResult, TransferTestResult

class SpeedTestProbe(object):

    probeConfig = None

    def __init__(self, probeConfig=None):
        self.probeConfig = probeConfig
        pass

    def probe(self):
        raise NotImplementedError()

    def __str__(self):
        return type(self).__name__

    def getName(self):
        return type(self).__name__

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
        self.logger.info("starting %s probe " % (type(self).__name__))

        pingResult = PingTestResult(pingStart=timezone.now(), probeName=self.probeConfig.probeName)
        startTimestamp = datetime.datetime.now()

        output = subprocess.check_output(self.getCommand(), shell=True, stderr=subprocess.STDOUT)

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
                #pingResult.totalTime = float(result.group(4))

            result = self.bytesTransmittedRegexp.match(line)
            if result:
                pingResult.destinationHost = result.group(1)
                pingResult.destinationIp = result.group(2)
                pingResult.sendBytesNetto = int(result.group(3))
                pingResult.sendBytesBrutto = int(result.group(4))

        pingResult.pingEnd = timezone.now()
        timeDelta = datetime.datetime.now() - startTimestamp
        pingResult.totalTime = int(timeDelta.microseconds / 1000)
        pingResult.save()
        self.logger.info("%s probe done" % (type(self).__name__))

    def getCommand(self):
        return "ping -w %s -nqc %s -s %s %s" % (self.probeConfig.timeout, self.probeConfig.packageCount,
                                                self.probeConfig.packageSize, self.probeConfig.host)

    def isEnabled(self):
        return self.probeConfig.enableProbe

    def __str__(self):
        return "ping probe (%s, %s)" % (self.probeConfig.host, type(self).__name__)

    def getName(self):
        return type(self).__name__


import datetime

class PypingProbe(SpeedTestProbe):
    logger = logging.getLogger(__name__)

    def __init__(self, probeConfig):
        super(PypingProbe, self).__init__(probeConfig)

    def probe(self):
        self.logger.info("starting %s probe " % (type(self).__name__))

        pingResult = PingTestResult(probeName=self.probeConfig.probeName, pingStart=timezone.now(), rttStdDev=-1,
                                    packageTransmitted=-1, packageReceived=-1, sendBytesBrutto=-1)
        startTimestamp = datetime.datetime.now()

        result = pyping.ping(timeout=(self.probeConfig.timeout * 1000), hostname=self.probeConfig.host,
                             count=self.probeConfig.packageCount, packet_size=self.probeConfig.packageSize)

        pingResult.packageToTransmit = self.probeConfig.packageCount
        pingResult.rttMin = result.min_rtt
        pingResult.rttAvg = result.avg_rtt
        pingResult.rttMax = result.max_rtt
        pingResult.packageLost = result.packet_lost
        pingResult.destinationHost = result.destination
        pingResult.destinationIp = result.destination_ip
        pingResult.sendBytesNetto = result.packet_size
        pingResult.pingEnd = timezone.now()
        timeDelta = datetime.datetime.now() - startTimestamp
        pingResult.totalTime = int(timeDelta.microseconds / 1000)

        pingResult.save()
        self.logger.info("%s probe done" % (type(self).__name__))

    def __str__(self):
        return "ping probe (%s, %s)" % (self.probeConfig.host, type(self).__name__)

    def getName(self):
        return type(self).__name__


class SpeedtestCliProbe(SpeedTestProbe):

    logger = logging.getLogger(__name__)

    def __init__(self, probeConfig=None):
        super(SpeedtestCliProbe, self).__init__(probeConfig)


    def probe(self):
        self.logger.info("starting %s probe " % (type(self).__name__))

        speedtest.shutdown_event = threading.Event()
        config = speedtest.getConfig()
        closestServer = speedtest.closestServers(config['client'])

        best = None
        serverId = self.probeConfig.serverId
        if serverId == None:
            best = speedtest.getBestServer(closestServer)
        else:
            serverId = "%s" % serverId
            self.logger.debug("use server id [%s]" %(serverId))
            best = speedtest.getBestServer(filter(lambda x: x['id'] == serverId, closestServer))
            self.logger.debug("found host for [%s] -> host [%s]" %(serverId, best["host"]))

        transferred, speed, result = None, None, None
        if not "download" in self.probeConfig.direction:
            sizesizes = [int(.25 * 1000 * 1000), int(.5 * 1000 * 1000)]
            sizes = []
            for size in sizesizes:
                for i in range(0, 25):
                    sizes.append(size)
            result = TransferTestResult(units="bit", transferStart=timezone.now(), direction="upload",
                                        probeName=self.probeConfig.probeName)
            transferred, speed = self.uploadSpeed(best['url'], sizes, quiet=True)
            result.transferEnd = timezone.now()
            self.logger.debug('upload: %0.2f M%s/s' % ((speed / 1000 / 1000) * 8, "bit"))

        else:
            sizes = [350, 500, 750, 1000, 1500, 2000, 2500, 3000, 3500, 4000]
            urls = []
            for size in sizes:
                for i in range(0, 4):
                    urls.append('%s/random%sx%s.jpg' % (os.path.dirname(best['url']), size, size))

            result = TransferTestResult(units="bit", transferStart=timezone.now(), direction="download",
                                        probeName=self.probeConfig.probeName)
            transferred, speed = self.downloadSpeed(urls, quiet=True)
            result.transferEnd = timezone.now()
            self.logger.debug('download: %0.2f M%s/s' % ((speed / 1000 / 1000) * 8, "bit"))

        result.transferredUnits = transferred
        result.transferredUnitsPerSecond = speed * 8
        result.host = best["host"]
        result.save()
        self.appendServerInfos(result, best)
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

    def __str__(self):
        return "speedtest.net probe"

    def getName(self):
        return type(self).__name__


class PycurlProbe(SpeedTestProbe):
    logger = logging.getLogger(__name__)

    def __init__(self, probeConfig):
        super(PycurlProbe, self).__init__(probeConfig)

    def probe(self):
        self.logger.info("starting %s probe " % (type(self).__name__))

        result = TransferTestResult(probeName=self.probeConfig.probeName, units="bit", transferStart=timezone.now())

        c = pycurl.Curl()
        url = self.probeConfig.url
        c.setopt(c.URL, url)
        c.setopt(c.TIMEOUT, self.probeConfig.timeout)
        c.setopt(c.WRITEDATA, StringIO())
        c.perform()
        bitsTransferred = c.getinfo(c.SIZE_DOWNLOAD) * 8
        transferDurationSeconds = c.getinfo(c.TOTAL_TIME) - c.getinfo(c.STARTTRANSFER_TIME)
        bitsPerSecond = bitsTransferred / transferDurationSeconds

        result.direction = "download"
        result.transferredUnits = int(bitsTransferred)
        result.transferredUnitsPerSecond = int(bitsPerSecond)

        parsedUrl = urlparse.urlparse(url)
        result.host = "%s://%s" % (parsedUrl.scheme, parsedUrl.netloc)
        result.url = c.getinfo(c.EFFECTIVE_URL)

        result.transferEnd = timezone.now()
        result.save()
        self.logger.info("%s probe done (%sMbit/s for downloading %s)" %
                         (type(self).__name__, (result.transferredUnitsPerSecond / 1000 / 1000), url))

    def __str__(self):
        return "ping probe (%s, %s)" % (self.probeConfig.url, type(self).__name__)

    def getName(self):
        return type(self).__name__
