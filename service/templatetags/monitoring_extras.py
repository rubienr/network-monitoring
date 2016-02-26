from django import template
from common.models import SiteConfiguration, SchedulerEvents
from service.scheduling import SCHEDULER
register = template.Library()


@register.tag
def monitoring_load(parser, token):
    r = ServiceStatusNode()
    return r

class ServiceStatusNode(template.Node):

    def __init__(self):
        pass

    def render(self, context):
        config = SiteConfiguration.objects.get()
        isEnabled = config.isProbingEnabled
        isRunning = SCHEDULER.isAvailable()

        events = SchedulerEvents.objects.order_by('-timestamp')
        lastSchedulerEvent = ""
        islastSchedulerEventErroneous = False
        try:
            lastEvent = events[0]
            lastSchedulerEvent = lastEvent.message
            islastSchedulerEventErroneous = lastEvent.isErroneous
        except:
            pass

        lastStartEventTimestamp = ""
        try:
            lastStartEventTimestamp = events.filter(message="start")[0]
        except:
            pass

        module, schedulerName = config.schedulerName.rsplit('.', 1)
        context['monitoring'] = {
            "statusString": self.generateStatusString(isEnabled, isRunning),
            "lastActivity": lastSchedulerEvent,
            "isLastActivityErroneous": islastSchedulerEventErroneous,
            "timeStarted": lastStartEventTimestamp,
            "schedulerName": schedulerName,
            "isEnabled": isEnabled,
            "isRunning": isRunning,
        }
        return ""

    def generateStatusString(self, isEnabled, isRunning):
        if isEnabled:
            if isRunning:
                return "running"
            else:
                return "enabled but not running"
        else:
            if isRunning:
                return "disabled but running"
            else:
                return "stopped"
