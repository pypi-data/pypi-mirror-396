from abc import ABC, abstractmethod
from typing import Any

from ..domain import DomainEvent


class AbstractDomainEventsService(ABC):

    @abstractmethod
    def publish(self, message: Any, event_type: DomainEvent, exchange: str = None):
        pass

    @abstractmethod
    def subscribe(self):
        pass