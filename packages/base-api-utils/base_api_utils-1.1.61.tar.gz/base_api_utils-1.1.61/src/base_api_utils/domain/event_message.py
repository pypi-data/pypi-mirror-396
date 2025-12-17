import json
from typing import Dict, Optional, Any


class EventMessage:
    def __init__(self,
                 event_type: str,
                 payload: Dict[str, Any],
                 routing_key: str,
                 properties: Optional[Dict[str, Any]] = None) -> None:
        self.event_type = event_type
        self.payload = payload
        self.routing_key = routing_key
        self.properties = properties

    @staticmethod
    def from_rabbit(ch, method, properties, body):
        try:
            payload = json.loads(body) if isinstance(body, (str, bytes)) else body
        except json.JSONDecodeError:
            payload = {"raw_body": str(body)}

        return EventMessage(
            event_type=method.routing_key,
            payload=payload,
            routing_key=method.routing_key,
            properties=vars(properties) if properties else None
        )
