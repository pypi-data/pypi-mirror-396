from abc import ABC, abstractmethod

from ..domain import EventMessage


class AbstractEventDispatcher(ABC):

    @abstractmethod
    def dispatch(self, event: EventMessage) -> bool:
        pass