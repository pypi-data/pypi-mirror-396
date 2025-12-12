from functools import lru_cache

try:
    from importlib_metadata import Distribution, PackageNotFoundError
except ImportError:
    from importlib.metadata import Distribution, PackageNotFoundError


@lru_cache
def user_agent(name=__package__):
    if "." in name:
        name = name.split(".")[0]

    try:
        dist = Distribution.from_name(name)
    except PackageNotFoundError:
        return f"{name}/unknown"

    return f"{dist.name}/{dist.version}"


DEFAULT_USER_AGENT = user_agent(__package__)


def set_default_user_agent(value):
    global DEFAULT_USER_AGENT
    DEFAULT_USER_AGENT = value
