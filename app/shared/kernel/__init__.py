"""Compatibility facade for relocated domain state contracts.

Domain state contracts now live under ``app.domain.shared.contracts``.
This module remains only so non-domain layers can migrate incrementally.
"""

from app.domain.shared.contracts import *  # noqa: F401,F403
