from django import template
from common.models import SiteConfiguration, SchedulerEvents
from service.Scheduler import isAvailable as isSchedulerAvailable
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
        isRunning = isSchedulerAvailable()

        events = SchedulerEvents.objects.order_by('-timestamp')
        lastEvent = events[0]
        lastStartEvent = events.filter(message="start")[0]

        module, schedulerName = config.schedulerName.rsplit('.', 1)
        context['monitoring'] = {
            "statusString": self.generateStatusString(isEnabled, isRunning),
            "lastActivity": lastEvent.timestamp,
            "isLastActivityErroneous": lastEvent.isErroneous,
            "timeStarted": lastStartEvent.timestamp,
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
