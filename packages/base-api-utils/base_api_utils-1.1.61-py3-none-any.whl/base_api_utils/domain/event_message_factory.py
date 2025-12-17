from typing import Dict, Type

from . import EventMessage


class EventMessageFactory:
    """Factory to create instances based on message type"""

    _message_types: Dict[str, Type[EventMessage]] = {
        "standard": EventMessage,
    }

    @classmethod
    def register_type(cls, name: str, message_class: Type[EventMessage]):
        cls._message_types[name] = message_class

    @classmethod
    def create(cls, message_type: str, ch, method, properties, body) -> EventMessage:
        """
        Creates an instance of the specified message type

        Args:
            message_type: Message type name
            ch, method, properties, body: RabbitMQ params

        Returns:
            EventMessage instance or its subclass
        """
        if message_type is None:
            message_class = EventMessage
        else:
            message_class = cls._message_types.get(message_type, EventMessage)

        return message_class.from_rabbit(ch, method, properties, body)