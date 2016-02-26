from django import template
try:
    from git import Repo
except:
    from git import Repository
from monitoring.settings import BASE_DIR

register = template.Library()


@register.tag
def git_load(parser, token):
    r = GitStatusNode()
    return r

class GitStatusNode(template.Node):

    def __init__(self):
        pass

    def render(self, context):
        try:
            r = Repo(BASE_DIR)
            version = r.rev_parse("HEAD").hexsha
            context['git'] = {
                "shortHexSha": version[0:7],
                "hexSha": version,
                "shortRemote": "https://github.com",
                "remote": "https://github.com/rubienr/network-monitoring"
            }
        except Exception:
            context['git'] = {
                "shortHexSha": None,
                "hexSha": None,
                "shortRemote": None,
                "remote": None,
            }
        return ""
