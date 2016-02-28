# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import datetime
import time
from collections import OrderedDict

import speedtest_cli as speedtest
from django.db.models import Max, Min
from django.shortcuts import render
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from django.views.generic import TemplateView

from common.models import PingTestResult
from common.models import SpeedtestServer
from common.models import TransferTestResult


def defaultView(request):
    return render_to_response('bootstrap/base.html', context_instance=RequestContext(request))


def transformPingProbes2TimelinechartData(timeFrame):

    # filter data
    objects = PingTestResult.objects.filter(pingStart__range=[timeFrame["fromDateTime"], timeFrame["toDateTime"]])

    # map data
    hostToTimestampToValue = {}
    for result in objects:
        timestamp = time.mktime(result.pingStart.timetuple()) * 1000
        host = result.destinationHost
        value = result.rttAvg
        if host not in hostToTimestampToValue .keys():
            hostToTimestampToValue[host] = {}
        hostToTimestampToValue[host][timestamp] = value

    # let empty periodes fallback to zero
    relaxedData = []
    for host in hostToTimestampToValue.keys():
        relaxedData.append(seriesToReturnToZeroSeries(hostToTimestampToValue[host]))

    # merge sets to chart data
    xValues, chartData = mergeDictionariesToChartData(relaxedData)


    # prepare template tag arguments

    extra_serie = {"tooltip": {"y_start": "", "y_end": " [ms] avg. delay"}}
    chartdata = {
        'x': xValues,
    }

    idx = 1
    hostnameLookup = dict(zip(chartData.keys(), hostToTimestampToValue.keys()))
    for key, hostData in chartData.items():
        chartdata["name%s" % idx] = hostnameLookup["y%s" % idx]
        chartdata["y%s" % idx] = hostData.values()
        chartdata["extra%s" % idx] = extra_serie
        idx += 1

    axis_date= "%H:%M %p"
    tooltip_date = "%d %b %H:%M"
    data = {
        'charttype': "lineWithFocusChart",
        'chartdata': chartdata,
        "chartcontainer": "linewithfocuschart_container",
        "title": "Average ping duration",
        "extra": {
            'x_is_date': True,
            'x_axis_format': axis_date,
            "charttooltip_dateformat": tooltip_date,
            'tag_script_js': True,
            'jquery_on_ready': False
        }
    }
    return data


def transformTransferProbes2TimelinechartData(direction, timeFrame):

    # filter data
    objects = None

    if "download" in direction and "upload" in direction:
        objects = TransferTestResult.objects\
            .filter(transferStart__range=[timeFrame["fromDateTime"], timeFrame["toDateTime"]])
    else:
        objects = TransferTestResult.objects\
            .filter(transferStart__range=[timeFrame["fromDateTime"], timeFrame["toDateTime"]])\
            .filter(direction=direction)

    # map data
    hostToTimestampToValue = {}
    for result in objects:
        timestamp = time.mktime(result.transferStart.timetuple()) * 1000.0
        host = result.host
        throughput = round(((result.transferredUnitsPerSecond * 1) / (1000.0 * 1000)), 2)

        if host not in hostToTimestampToValue.keys():
            hostToTimestampToValue[host] = {}
        hostToTimestampToValue[host][timestamp] = throughput

    # let empty periodes fallback to zero
    relaxedData = []
    for host in hostToTimestampToValue.keys():
        relaxedData.append(seriesToReturnToZeroSeries(hostToTimestampToValue[host]))

    # merge sets to chart data
    xValues, chartData = mergeDictionariesToChartData(relaxedData)


    # prepare template tag arguments

    extra_serie = {"tooltip": {"y_start": "", "y_end": "MBit/s"}}
    chartdata = {
        'x': xValues,
    }

    idx = 1
    hostnameLookup = dict(zip(chartData.keys(), hostToTimestampToValue.keys()))
    for key, hostData in chartData.items():
        chartdata["name%s" % idx] = hostnameLookup["y%s" % idx]
        chartdata["y%s" % idx] = hostData.values()
        chartdata["extra%s" % idx] = extra_serie
        idx += 1

    title = ""
    if "download" in direction and "upload" in direction:
        title = "Up-/download Speed Tests"
    elif "download" in direction:
        title = "Download Speed Tests"
    elif "upload" in direction:
        title = "Upload Speed Tests"

    axis_date= "%H:%M"
    tooltip_date = "%d %b %H:%M"
    data = {
        'charttype': "lineWithFocusChart",
        'chartdata': chartdata,
        "chartcontainer": "linewithfocuschart_container",
        "title": title,
        "extra": {
            'x_is_date': True,
            'x_axis_format': axis_date,
            "charttooltip_dateformat": tooltip_date,
            'tag_script_js': True,
            'jquery_on_ready': False
        }
    }
    return data


def transformProbes2PreviewTimelinechartData():
    timestampToPingProbes = {}
    roundSeconds = -2 # factor to bin values

    for result in PingTestResult.objects.order_by('pingStart').all():
        timestamp = int(round(time.mktime(result.pingStart.timetuple()), roundSeconds))
        if timestamp in timestampToPingProbes.keys():
            timestampToPingProbes[timestamp] = timestampToPingProbes[timestamp] + 1
        else:
            timestampToPingProbes[timestamp] = 1

    timestampToTransferProbes = {}
    for result in TransferTestResult.objects.order_by('transferStart').all():
        timestamp = int(round(time.mktime(result.transferStart.timetuple()), roundSeconds))
        if timestamp in timestampToTransferProbes.keys():
            timestampToTransferProbes[timestamp] = timestampToTransferProbes[timestamp] + 1
        else:
            timestampToTransferProbes[timestamp] = 1


    pingChartData = seriesToReturnToZeroSeries(timestampToPingProbes)
    transferChartData = seriesToReturnToZeroSeries(timestampToTransferProbes)
    xValues, theData = mergeDictionariesToChartData([pingChartData, transferChartData])


    extra_serie = {"tooltip": {"y_start": "", "y_end": " probes"}}
    chartdata = {'x': [ 1000 * s for s in xValues]}

    chartdata["name1"] = "ping probes"
    chartdata["y1"] = theData["y1"].values()
    chartdata["extra1"] = extra_serie

    chartdata["name2"] = "transfer probes"
    chartdata["y2"] = theData["y2"].values()
    chartdata["extra2"] = extra_serie

    if len(chartdata["x"]) > 30:
        title = "Specify time window to generate charts from (optional):"
    elif len(chartdata["x"]) > 0:
        title = "Data overview (still less probes):"
    else:
        title = "Unfortunately no data available. Please configure and start the service."

    axis_date= "%d %b"
    tooltip_date = "%d %b %H:%M"
    data = {
        'preview_charttype': "lineWithFocusChart",
        'preview_chartdata': chartdata,
        "preview_chartcontainer": "linewithfocuschart_container",
        "preview_title": title,
        "preview_extra": {
            'x_is_date': True,
            'x_axis_format': axis_date,
            "charttooltip_dateformat": tooltip_date,
            'tag_script_js': True,
            'jquery_on_ready': False
        }
    }
    return data


def getClosestServersView(request):
    config = speedtest.getConfig()
    closestServers = speedtest.closestServers(config['client'])

    # store to db
    models = []
    for server in closestServers:
        server["serverId"] = server.pop("id")
        model = SpeedtestServer().fromDict(**server)
        models.append(model)
    SpeedtestServer.objects.bulk_create(models)

    # filter/reorder/translate values for view
    title = "Speedtest.net - Closest Server"
    columnToName = OrderedDict ([
        ("serverId", "ID"),
        ("name", "City"),
        ("url", "URL"),
        ("country", "Country"),
        ("d", "Distance [km]"),
        #("cc", "country code"),
        #("host", "host name"),
        ("sponsor", ""),
        #("url2", "url"),
        ("lat", "Latitude"),
        ("lon", "Longitude"),
    ])
    columns = columnToName.keys()

    servers = []
    for c in closestServers:
        server = OrderedDict([(columnToName[filteredColumn], c[filteredColumn]) for filteredColumn in columns])
        distanceColumn = columnToName["d"]
        server[distanceColumn] = round(server[distanceColumn],1)
        servers.append(server)

    data = {
        "title": title,
        "tableHeader" : servers[0].keys(),
        "servers": servers,
    }

    return render_to_response('bootstrap/serverlist.html', data, context_instance=RequestContext(request))


def transformPingProbes2PiechartData(timeFrame):

    # filter data
    objects = PingTestResult.objects.filter(pingStart__range=[timeFrame["fromDateTime"], timeFrame["toDateTime"]])

    results = {}
    for result in objects:
        if result.destinationHost in results:
            results[result.destinationHost].append(result)
        else:
            results[result.destinationHost] = [result]

    xdata = results.keys()
    ydata = [len(results[x]) for x in results]

    extra_serie = {"tooltip": {"y_start": "", "y_end": " probes"}}

    chartdata = {'x': xdata, 'y': ydata, "extra": extra_serie}
    charttype = "pieChart"
    chartcontainer = 'piechart_container'
    data = {
        "title": "Probes per Host",
        'charttype': charttype,
        'chartdata': chartdata,
        'chartcontainer': chartcontainer,
        'extra': {
            'x_is_date': False,
            'tag_script_js': True,
            'jquery_on_ready': False,
            "donut": True,
            "showLabels": True,
        }
    }
    return data


def transformTransferProbes2PiechartData(direction, timeFrame):
    """
    Arguments
    direction: download, upload, downloadupload"""

    # filter data
    objects = None

    if "download" in direction and "upload" in direction:
        objects = TransferTestResult.objects\
            .filter(transferStart__range=[timeFrame["fromDateTime"], timeFrame["toDateTime"]])
    else:
        objects = TransferTestResult.objects\
            .filter(transferStart__range=[timeFrame["fromDateTime"], timeFrame["toDateTime"]])\
            .filter(direction=direction)

    results = {}
    for result in objects:
        if result.host in results:
            results[result.host].append(result)
        else:
            results[result.host] = [result]

    xdata = results.keys()
    ydata = [len(results[x]) for x in results]

    extra_serie = {"tooltip": {"y_start": "", "y_end": " probes"}}

    chartdata = {'x': xdata, 'y': ydata, "extra": extra_serie}
    charttype = "pieChart"
    chartcontainer = 'piechart_container'

    title = "%s per Hosts"
    if "download" in direction and "upload" in direction:
        title = title % "Up-/downloads"
    elif "download" in direction:
        title = title % "Downloads"
    elif "upload" in direction:
        title = title % "Uploads"

    data = {
        "title": title,
        'charttype': charttype,
        'chartdata': chartdata,
        'chartcontainer': chartcontainer,
        'extra': {
            'x_is_date': False,
            'x_axis_format': '',
            'tag_script_js': True,
            'jquery_on_ready': False,
            "donut": True,
            "showLabels": True,
        }
    }
    return data


class DefaultChartView(TemplateView):
    """Piechart and Timlinechart view

    Arguments
    view -- pie, timeline
    dataSource -- ping, transfer
    direction: None (defaults to download), upload, download, uploaddownload
    """

    template_name = "bootstrap/piechart.html"
    dataSource = "ping"
    view = "pie"
    direction = None

    templates = {
        "pie": "bootstrap/piechart.html",
        "timeline": "bootstrap/timeline.html",
    }

    renderStrategy = {
        "pie":
        {
            "ping": transformPingProbes2PiechartData,
            "transfer": transformTransferProbes2PiechartData,
        },
        "timeline": {
            "ping": transformPingProbes2TimelinechartData,
            "transfer": transformTransferProbes2TimelinechartData,
        },
    }

    def __init__(self, dataSource="ping", view="pie", direction=None):
        object.__init__(self)
        self.dataSource = dataSource
        self.view = view
        self.direction = direction
        self.template_name = self.templates[self.view]
        self.relativeDataFrom = 0
        self.relativeDataTo = 0

    def get(self, request, *args, **kwargs):
        self.relativeDataFrom = float(request.GET.get('relFrom', '0'))
        self.relativeDataTo = float(request.GET.get('relTo', '0'))
        return render(request, self.template_name, self.get_context_data())

    def get_context_data(self, **kwargs):
        context = super(DefaultChartView, self).get_context_data(**kwargs)

        timeFrameArguments = {}
        if 0 <= self.relativeDataFrom \
            and self.relativeDataFrom < self.relativeDataTo \
            and self.relativeDataTo <= 1.0:
                timeFrameArguments["fromDateTime"] = self.relativeToDbTimestamp(self.relativeDataFrom)
                timeFrameArguments["toDateTime"] = self.relativeToDbTimestamp(self.relativeDataTo)
        else:
            timeFrameArguments["fromDateTime"] = self.relativeToDbTimestamp(0)
            timeFrameArguments["toDateTime"] = self.relativeToDbTimestamp(1)

        if self.direction is not None:
            chartData = self.renderStrategy[self.view][self.dataSource](self.direction, timeFrame=timeFrameArguments)
        else:
            chartData = self.renderStrategy[self.view][self.dataSource](timeFrame=timeFrameArguments)

        for key, value in chartData.items():
                context[key] = value

        context["timeframe_filter_extras"] = "relFrom=%s&relTo=%s" % (self.relativeDataFrom, self.relativeDataTo)

        return context

    def relativeToDbTimestamp(self, relativeValue):
        try:
            pingProbes = PingTestResult.objects
            key, latestPingProbe = pingProbes.aggregate(Max('pingStart')).popitem()
            key, firstPingProbe = pingProbes.aggregate(Min('pingStart')).popitem()

            transferProbes = TransferTestResult.objects
            key, latestTransferProbe = transferProbes.aggregate(Max('transferStart')).popitem()
            key, firstTransferProbe = transferProbes.aggregate(Min('transferStart')).popitem()

            # in case of missing probes
            minTime = firstPingProbe
            maxTime = latestPingProbe

            if minTime is None or maxTime is None:
                minTime = firstTransferProbe
                maxTime = latestTransferProbe

            if minTime is None or maxTime is None:
                return datetime.datetime.utcfromtimestamp(0)

            try:
                if firstPingProbe > firstTransferProbe:
                    minTime = firstTransferProbe

                maxTime = latestPingProbe
                if latestPingProbe < latestTransferProbe:
                    maxTime = latestTransferProbe
            except:
                pass

            moment = time.mktime(minTime.timetuple()) + relativeValue * (time.mktime(maxTime.timetuple()) - \
                                                                     time.mktime(minTime.timetuple()))
            return datetime.datetime.utcfromtimestamp(moment)
        except:
            return datetime.datetime.utcfromtimestamp(0)


class ProbePreviewChartView(TemplateView):
    """Timlinechart view showing number of probes per time line
    """

    template_name = "bootstrap/base.html"

    def __init__(self):
        object.__init__(self)
        pass

    def get_context_data(self, **kwargs):
        context = super(ProbePreviewChartView, self).get_context_data(**kwargs)
        chartData = transformProbes2PreviewTimelinechartData()

        for key, value in chartData.items():
                context[key] = value

        return context


def mergeDictionariesToChartData(dictList = []):
    def uniq(lst):
        last = object()
        for item in lst:
            if item == last:
                continue
            yield item
            last = item

    def sort_and_deduplicate(l):
        return list(uniq(sorted(l, reverse=True)))

    # sort the key set of all dicts
    xValues = []
    for d in dictList:
        xValues.extend(d.keys())
    xValues = sort_and_deduplicate(xValues)

    # create result dicts
    idx = 1
    chartDicts = {}
    for d in dictList:
        chartDicts["y%s" % idx] = OrderedDict()
        idx += 1

    # for all keys and all dicts in dictList store value or default (0) to result
    idx = 1
    for d in dictList:
        for x in xValues:
            if x in d.keys():
                chartDicts["y%s" % idx][x] = d[x]
            else:
                chartDicts["y%s" % idx][x] = 0
        idx += 1

    return xValues, chartDicts


def seriesToReturnToZeroSeries(series, cutoffSeconds=300):
    """ let series fallback to zero if no probes available withing cutom timespan"""
    lastTimestamp = None
    withFallback = OrderedDict()
    for timestamp in sorted(series):
        if lastTimestamp is not None:
            if lastTimestamp + cutoffSeconds < timestamp:
                withFallback[lastTimestamp + 1] = 0
                withFallback[timestamp - 1] = 0

        withFallback[timestamp] = series[timestamp]
        lastTimestamp = timestamp

    return withFallback