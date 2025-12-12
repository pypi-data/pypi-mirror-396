from django.apps import AppConfig
from django.conf import settings

from setuseragent import agent, hooks

DEFAULT_DISTRIBUTION = getattr(settings, "USER_AGENT_DISTRIBUTION", settings.SETTINGS_MODULE)


class CustomConfig(AppConfig):
    name = "setuseragent.django"

    def ready(self):
        user_agent = agent.user_agent(DEFAULT_DISTRIBUTION)
        return hooks.set_user_agent(user_agent)
