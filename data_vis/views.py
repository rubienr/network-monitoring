# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import speedtest_cli as speedtest
from django.shortcuts import render_to_response
from common.models import PingTestResult
from common.models import TransferTestResult
import time
from django.template.context import RequestContext
from django.views.generic import TemplateView


def defaultView(request):
    return render_to_response('bootstrap/base.html', context_instance=RequestContext(request))


def transformPingProbes2TimelinechartData():
    # pull all timestamps and map from timestamps to results
    timestamps = []
    timestampToResults = {}
    hosts = {}
    for result in PingTestResult.objects.all():
        timestamp = time.mktime(result.pingStart.timetuple()) * 1000
        timestamps.append(timestamp)
        hosts[result.destinationHost] = 0
        if timestamp in timestampToResults.keys():
            timestampToResults[timestamp].append(result)
        else:
            timestampToResults[timestamp] = [result]
    hosts = hosts.keys()

    # create mapping from host to result for each timestamp
    hostToResult = dict((h,[]) for h in hosts)
    for timestamp in timestampToResults.keys():
        for result in timestampToResults[timestamp]:
            for host in hosts:
                if result.destinationHost == host:
                    hostToResult[host].append(result)
                else:
                    hostToResult[host].append(None)

    # refine result to chart value
    hostToChartValue = dict((h,[]) for h in hosts)
    for host in hostToResult.keys():
        for r in hostToResult[host]:
            if r == None:
                hostToChartValue[host].append(0)
            else:
                hostToChartValue[host].append(r.rttAvg)

    tooltip_date = "%d %b %H:%M %p"
    extra_serie = {"tooltip": {"y_start": "", "y_end": " [ms] avg. delay"}, "extra": tooltip_date }
    chartdata = {
        'x': timestamps,
    }

    idx = 1
    for host in hostToResult.keys():
        chartdata["name%s" % idx] = host
        chartdata["y%s" % idx] = hostToChartValue[host]
        chartdata["extra%s" % idx] = extra_serie
        idx += 1

    axis_date= "%H:%M %p"
    data = {
        'charttype': "lineWithFocusChart",
        'chartdata': chartdata,
        "chartcontainer": "linewithfocuschart_container",
        "title": "Average ping duration",
        "extra": {
            'x_is_date': True,
            'x_axis_format': axis_date,
            'tag_script_js': True,
            'jquery_on_ready': False
        }
    }
    return data



def transformTransferProbes2TimelinechartData(direction="download"):
    # pull all timestamps and map from timestamps to results
    timestamps = []
    timestampToResults = {}
    hosts = {}
    for result in TransferTestResult.objects.all():
        timestamp = time.mktime(result.transferStart.timetuple()) * 1000
        timestamps.append(timestamp)
        hosts[result.host] = 0
        if timestamp in timestampToResults.keys():
            timestampToResults[timestamp].append(result)
        else:
            timestampToResults[timestamp] = [result]
    hosts = hosts.keys()

    # create mapping from host to result for each timestamp
    hostToResult = dict((h,[]) for h in hosts)
    for timestamp in timestampToResults.keys():
        for result in timestampToResults[timestamp]:
            for host in hosts:
                if result.host == host:
                    hostToResult[host].append(result)
                else:
                    hostToResult[host].append(None)

    # refine result to chart value
    hostToChartValue = dict((h,[]) for h in hosts)
    for host in hostToResult.keys():
        for r in hostToResult[host]:
            if r == None:
                hostToChartValue[host].append(0)
            else:
                duration = time.mktime(r.transferEnd.timetuple()) - time.mktime(r.transferStart.timetuple())
                throughput = round(((r.transferredUnits * 8) / (1000 * 1000 * duration)),2)
                hostToChartValue[host].append(throughput)

    tooltip_date = "%d %b %H:%M %p"
    extra_serie = {"tooltip": {"y_start": "", "y_end": "mBit/s"}, "extra" : tooltip_date}
    chartdata = {
        'x': timestamps,
    }

    idx = 1
    for key in hostToResult.keys():
        chartdata["name%s" % idx] = key
        chartdata["y%s" % idx] = hostToChartValue[key]
        chartdata["extra%s" % idx] = extra_serie
        idx += 1

    title = ""
    if "download" in direction and "upload" in direction:
        title = "Up-/download Speed Tests"
    elif "download" in direction:
        title = "Download Speed Tests"
    elif "upload" in direction:
        title = "Upload Speed Tests"

    axis_date= "%H:%M %p"
    data = {
        'charttype': "lineWithFocusChart",
        'chartdata': chartdata,
        "chartcontainer": "linewithfocuschart_container",
        "title": title,
        "extra": {
            'x_is_date': True,
            'x_axis_format': axis_date,
            'tag_script_js': True,
            'jquery_on_ready': False
        }
    }
    return data

from collections import  OrderedDict
from common.models import SpeedtestServer

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


def transformPingProbes2PiechartData():
    results = {}
    for result in PingTestResult.objects.all():
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


def transformTransferProbes2PiechartData(direction="download"):
    """
    Arguments
    direction: download, upload, downloadupload"""
    results = {}
    for result in TransferTestResult.objects.all():
        if result.direction in direction:
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
        self.dataSource = dataSource
        self.view = view
        self.direction = direction
        self.template_name = self.templates[self.view]

    def get_context_data(self, **kwargs):
        context = super(DefaultChartView, self).get_context_data(**kwargs)

        if self.direction is not None:
            chartData = self.renderStrategy[self.view][self.dataSource](self.direction)
        else:
            chartData = self.renderStrategy[self.view][self.dataSource]()

        for key, value in chartData.items():
                context[key] = value

        return context
