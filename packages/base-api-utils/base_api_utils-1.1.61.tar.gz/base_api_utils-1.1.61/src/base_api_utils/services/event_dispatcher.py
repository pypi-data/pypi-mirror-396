import logging
from typing import List

from ..domain import EventMessage
from ..handlers import BaseEventHandler
from ..services import AbstractEventDispatcher


class EventDispatcher(AbstractEventDispatcher):
    """Central dispatcher that routes events to appropriate handlers."""

    def __init__(self, handlers: List[BaseEventHandler]):
        self.handlers = handlers

    def dispatch(self, event: EventMessage) -> bool:
        """Find and execute the appropriate handler for the event."""

        for handler in self.handlers:
            if handler.can_handle(event.event_type):
                logging.getLogger('api').info(f"Dispatching {event.event_type} to {handler.__class__.__name__}")
                try:
                    result = handler.handle(event)
                    if result:
                        logging.getLogger('api').info(f"Event {event.event_type} processed successfully")
                        return True
                    else:
                        logging.getLogger('api').warning(f"Handler returned False for {event.event_type}")
                except Exception as e:
                    logging.getLogger('api').error(f"Handler failed for {event.event_type}: {e}", exc_info=True)
                    return False

        logging.getLogger('api').warning(f"No handler found for event type: {event.event_type}")
        return False