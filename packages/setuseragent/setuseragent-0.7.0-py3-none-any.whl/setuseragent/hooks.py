import logging

from setuseragent import agent

HOOKS = [
    agent.set_default_user_agent,
]

logger = logging.getLogger(__name__)


def set_user_agent(value) -> str:
    logger.debug("set_user_agent %r", value)
    for func in HOOKS:
        func(value)
    return value


def set_distribution(name) -> str:
    return set_user_agent(agent.user_agent(name))


try:
    import requests.utils
except ImportError:
    logger.debug("requests.utils not found")
else:

    def requests_user_agent(*args):
        return agent.DEFAULT_USER_AGENT

    # The requests library uses a default_user_agent method that we patch to
    # call our version
    requests.utils.default_user_agent = requests_user_agent

try:
    import aiohttp.http
except ImportError:
    logger.debug("aiohttp not found")
else:

    def aiohttp_user_agent(agent):
        aiohttp.http.SERVER_SOFTWARE = agent

    # aiohttp defines a SERVER_SOFTWARE string that we set
    # and also configure a hook to reset the value as needed
    aiohttp_user_agent(agent.DEFAULT_USER_AGENT)
    HOOKS.append(aiohttp_user_agent)

try:
    import feedparser
except ImportError:
    logger.debug("feedparser not found")
else:

    def feedparser_user_agent(agent):
        feedparser.USER_AGENT = agent

    # feedparser defines a USER_AGENT string that we set
    # and also configure a hook to reset the value as needed
    feedparser_user_agent(agent.DEFAULT_USER_AGENT)
    HOOKS.append(feedparser_user_agent)
