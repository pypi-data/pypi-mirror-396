from abc import ABC, abstractmethod

from ..domain import EventMessage


class BaseEventHandler(ABC):

    @abstractmethod
    def can_handle(self, event_type: str) -> bool:
        pass
    
    @abstractmethod
    def handle(self, event: EventMessage) -> bool:
        pass