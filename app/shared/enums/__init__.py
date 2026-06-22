"""Compatibility facade for relocated domain enums.

Domain-owned enums now live under ``app.domain.shared.enums``.
This module remains only so non-domain layers can migrate incrementally.
"""

from app.domain.shared.enums import *  # noqa: F401,F403
