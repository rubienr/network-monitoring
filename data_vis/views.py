from django.http import HttpResponse
from django.shortcuts import render_to_response
from common.models import PingTestResult
import time
from service.Scheduler import startScheduler

def piChart(request):
    startScheduler()
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
            'x_axis_format': '',
            'tag_script_js': True,
            'jquery_on_ready': False,
            "donut": True,
            "showLabels": True,
        }
    }
    return render_to_response('piechart.html', data)


def lineWithFocusChart(request):
    startScheduler()
    xdata = []
    hostToResult = {}
    for result in PingTestResult.objects.all():
        xdata.append(time.mktime(result.pingStart.timetuple()) * 1000)
        if result.destinationHost in hostToResult.keys():
            hostToResult[result.destinationHost].append(result)
        else:
            hostToResult[result.destinationHost] = [result]

    tooltip_date = "%d %b %Y %H:%M:%S %p"
    extra_serie = {"tooltip": {"y_start": "duration ", "y_end": " [ms]"},
                   "date_format": tooltip_date}
    chartdata = {
        'x': xdata,
    }

    idx = 1
    for key in hostToResult.keys():
        chartdata["name%s" % idx] = key
        chartdata["y%s" % idx] = [v.rttAvg for v in hostToResult[key]]
        chartdata["extra%s" % idx] = extra_serie
        idx += 1

    data = {
        'charttype': "lineWithFocusChart",
        'chartdata': chartdata,
        "chartcontainer": "linewithfocuschart_container",
        "title": "Average ping duration",
        "extra": {
            'x_is_date': True,
            'x_axis_format': tooltip_date,
            'tag_script_js': True,
            'jquery_on_ready': False
        }
    }
    return render_to_response('linewithfocuschart.html', data)
