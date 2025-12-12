# Monkey patches for setting user-agent header.

```python
# Importing hooks automatically handles monkey patching
from setuseragent import hooks
# We can set to a specific value
hooks.set_user_agent("my-new-user-agent")
# Or we can set it with a package version
hooks.set_distribution('my-package')
# or using meta package name
hooks.set_distribution(__package__)
```

If using Django, can optionally set the site name as part of the package

```python
# in settings.py

INSTALLED_APPS = [
    ...,
    "setuseragent.django",
    "django.contrib.sites",
]

# Optionally can configure a specific package to lookup.
# otherwise defaults to the value of DJANGO_SETTINGS_MODULE
USER_AGENT_DISTRIBUTION = __package__
```
