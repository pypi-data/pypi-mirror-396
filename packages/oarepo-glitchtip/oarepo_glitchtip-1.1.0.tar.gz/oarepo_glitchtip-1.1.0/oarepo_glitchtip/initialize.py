#
# Copyright (C) 2024 CESNET z.s.p.o.
#
# oarepo-glitchtip is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.
#
"""Glitchtip initialization.

The initialize_glitchtip function must be called as the first statement in the `invenio.cfg`.
Example of invenio.cfg:

from oarepo_glitchtip import initialize_glitchtip
initialize_glitchtip()

<rest of file>
"""

import logging
import os

import sentry_sdk
from sentry_sdk.integrations.celery import CeleryIntegration
from sentry_sdk.integrations.flask import FlaskIntegration
from sentry_sdk.integrations.logging import LoggingIntegration
from sentry_sdk.integrations.redis import RedisIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration


def initialize_glitchtip(
    dsn: str | None = None, deployment_version: str | None = None
) -> None:
    """Initialize glitchtip.

    :param dsn: Sentry DSN. If not passed, it is taken from INVENIO_GLITCHTIP_DSN environment variable.
    :param deployment_version: [optional] Deployment version. If not passed,
                               it is taken from DEPLOYMENT_VERSION environment variable.
    """
    if dsn is None:
        dsn = os.environ.get("INVENIO_GLITCHTIP_DSN", "")
    if not dsn:
        return

    sentry_sdk.init(
        dsn=dsn,
        integrations=[
            FlaskIntegration(),
            CeleryIntegration(),
            SqlalchemyIntegration(),
            RedisIntegration(),
            LoggingIntegration(level=logging.INFO, event_level=logging.ERROR),
        ],
        # send details about current user. Note: glitchtip should be run on-premises
        # and we need to remove these records after 12-18 months to comply with CESNET
        # data retention policy
        enable_logs=True,
        send_default_pii=True,
        traces_sample_rate=float(
            os.environ.get("INVENIO_GLITCHTIP_SAMPLE_RATE", "0.5")
        ),
    )

    if deployment_version is None:
        deployment_version = os.environ.get("DEPLOYMENT_VERSION", "")
    if deployment_version:
        sentry_sdk.set_tag("release", deployment_version)
