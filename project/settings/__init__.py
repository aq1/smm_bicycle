from .settings_base import *
from .settings_celery import *

from .settings_local import *

import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration


if not DEBUG:
    sentry_sdk.init(
        dsn=SENTRY_URL,
        integrations=[DjangoIntegration()]
    )
