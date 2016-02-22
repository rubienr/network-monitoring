from django.shortcuts import render_to_response
from service.Scheduler import startScheduler


def index(request):
    startScheduler()
    data = {"data": [{
                    "title": "Ping charts",
                    "views": {
                        "number of probes": "/vis/pi",
                        "by time": "/vis/line",
                    },
                },
                {

                    "title": "Up-/download charts",
                    "views": {
                        "number of download probes": "/vis/transferdl",
                        "number of upload probes": "/vis/transferul",
                        "number of total probes": "/vis/transfer",
                        "by time": "/vis/transferline",
                        "list of server IDs": "/vis/servers",
                    }
                }]}

    return render_to_response('index.html', data)
