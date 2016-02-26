# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from service.scheduling import SCHEDULER
from django.http import HttpResponse
from django.shortcuts import redirect

def toggle(request):
    message = "Service has been %s."
    if SCHEDULER.isAvailable():
        SCHEDULER.stopScheduler()
        message %= "stopped"
    else:
        SCHEDULER.startScheduler()
        message %= "started"
    return HttpResponse(message)


def status(request):
    message = "Service is %s."
    if SCHEDULER.isAvailable():
        message %= "running"
    else:
        message %= "stopped"
    return HttpResponse(message)


def start(request):
    SCHEDULER.startScheduler()
    return redirect('/admin', service_status='service_sopped')


def stop(request):
    SCHEDULER.stopScheduler()
    return redirect('/admin', service_status='service_sopped')
