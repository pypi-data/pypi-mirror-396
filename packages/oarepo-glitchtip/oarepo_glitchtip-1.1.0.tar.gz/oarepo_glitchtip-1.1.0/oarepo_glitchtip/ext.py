#
# Copyright (C) 2024 CESNET z.s.p.o.
#
# oarepo-glitchtip is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.
#
"""Glitchtip extension for OARepo."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

import sentry_sdk
from flask_login import current_user

if TYPE_CHECKING:
    from invenio_accounts.models import User
    from invenio_files_rest.app import Flask

log = logging.getLogger(__name__)


class OARepoGlitchtipExt:
    """Glitchtip extension for OARepo."""

    def __init__(self, app: Flask = None, **kwargs: Any) -> None:
        """Initialize extension."""
        self.app = app
        if app is not None:
            self.init_app(app)

    def init_app(self, app: Flask) -> None:
        """Initialize the extension."""
        app.extensions["oarepo-glitchtip"] = self


def finalize_app(app: Flask) -> None:
    """Add a hook to before_request that adds user to glitchtip breadcrumbs.

    This function is registered in entrypoints -
        invenio_base.finalize_app, invenio_base.api_finalize_app
    """
    app.before_request(add_user_to_glitchtip)


def add_user_to_glitchtip() -> None:
    """Add user to glitchtip hook."""
    try:
        if not current_user.is_authenticated:
            sentry_sdk.set_user(
                {
                    "ip_address": "{{auto}}",
                }
            )
        else:
            u: User = current_user
            sentry_sdk.set_user(
                {
                    "id": u.id,
                    "email": u.email,
                    "username": u.email,
                    "ip_address": "{{auto}}",
                    **u.user_profile,
                }
            )
    except:  # noqa
        log.exception("Failed to add user to glitchtip")
