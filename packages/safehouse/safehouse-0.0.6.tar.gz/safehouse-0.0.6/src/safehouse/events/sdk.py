import logging

from safehouse import config
from .event_manager import EventManager


logger = logging.Logger(__name__)


def init(
    *,
    origin: str,
) -> EventManager:
    return EventManager(origin, config.PROJECT)
