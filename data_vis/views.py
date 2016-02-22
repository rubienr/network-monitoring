import speedtest_cli as speedtest
from django.shortcuts import render_to_response
from common.models import PingTestResult
from common.models import TransferTestResult

import time
from service.Scheduler import startScheduler


def pingProbesCountChart(request):
    startScheduler()
    return render_to_response('piechart.html', transformPingProbesChartData())


def transformPingProbesChartData():
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
        "title": "Probes vs Hosts",
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

def pingProbesTimeLineChart(request):
    startScheduler()
    return render_to_response('linewithfocuschart.html', transformPingProbesTimeLineChartData())

def transformPingProbesTimeLineChartData():
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


def transferProbesTimeLineChart(request):
    return  render_to_response("linewithfocuschart.html", transformTransferByTimeChartData())


def transformTransferByTimeChartData():
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

    axis_date= "%H:%M %p"
    data = {
        'charttype': "lineWithFocusChart",
        'chartdata': chartdata,
        "chartcontainer": "linewithfocuschart_container",
        "title": "Download speedtest",
        "extra": {
            'x_is_date': True,
            'x_axis_format': axis_date,
            'tag_script_js': True,
            'jquery_on_ready': False
        }
    }
    return data

def getClosestServers(request):
    config = speedtest.getConfig()
    closestServer = speedtest.closestServers(config['client'])

    data = {
        "title": "a title",
        "tableHeader" :closestServer[0].keys(),
        "servers": closestServer,
    }

    return render_to_response('serverlist.html', data)


def transferProbesCountPieChart(request):
    return render_to_response("piechart.html", transformTransfersCountPiechartData(direction="downloadupload"))


def dlTransferProbesCountPieChart(request):
    startScheduler()
    return render_to_response("piechart.html", transformTransfersCountPiechartData(direction="download"))


def ulTransferProbesCountPieChart(request):
    startScheduler()
    return render_to_response("piechart.html", transformTransfersCountPiechartData(direction="upload"))


def transformTransfersCountPiechartData(direction="download"):
    """direction: download, upload, downloadupload"""
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
