# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from service import Scheduler
from django.http import HttpResponse


def toggle(request):
    message = "Service has been %s."
    if Scheduler.isAvailable():
        Scheduler.stopScheduler()
        message %= "stopped"
    else:
        Scheduler.startScheduler()
        message %= "started"
    return HttpResponse(message)


def status(request):
    message = "Service is %s."
    if Scheduler.isAvailable():
        message %= "running"
    else:
        message %= "stopped"
    return HttpResponse(message)


def start(request):
    Scheduler.startScheduler()
    return HttpResponse("")

def stop(request):
    Scheduler.stopScheduler()
    return HttpResponse("")