from django.shortcuts import render_to_response
from service.Scheduler import startScheduler

def index(request):
    startScheduler()
    data = {
        "title" : "Views",
        "views" : {
            "pie chart" : "/vis/pi",
            "line chart" : "/vis/line",
        }
    }
    return render_to_response('index.html', data)
