"""Compatibility facade for relocated domain value objects.

Scientific value objects now live under ``app.domain.shared.value_objects``.
This module remains only so non-domain layers can migrate incrementally.
"""

from app.domain.shared.value_objects import *  # noqa: F401,F403
