"""
Sigmoda Python SDK.

Call `sigmoda.init(...)` to configure, then use `sigmoda.openai.chat.completions.create(...)`
or `sigmoda.log_event(...)` to send events.
"""

from .config import init, get_config  # noqa: F401
from .client import flush, get_stats, log_event  # noqa: F401
from . import openai_wrapper as openai  # noqa: F401

__all__ = ["init", "get_config", "log_event", "flush", "get_stats", "openai"]
