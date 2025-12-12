#
# Copyright (C) 2024 CESNET z.s.p.o.
#
# oarepo-glitchtip is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.
#
"""Glitchtip integration for CESNET invenio flavour."""

from .ext import OARepoGlitchtipExt
from .initialize import initialize_glitchtip

__all__ = ("initialize_glitchtip", "OARepoGlitchtipExt")
