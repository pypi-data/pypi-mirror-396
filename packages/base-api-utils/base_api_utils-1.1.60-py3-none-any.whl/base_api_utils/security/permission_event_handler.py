import logging

from ..domain import EventMessage, DomainEvent
from ..handlers import BaseEventHandler

from .user_permissions_service import UserPermissionsService


class PermissionEventHandler(BaseEventHandler):
    HANDLED_EVENTS = [
        DomainEvent.AUTH_ACCESS_RIGHT_ADDED.value,
        DomainEvent.AUTH_ACCESS_RIGHT_REMOVED.value,
        DomainEvent.AUTH_USER_REMOVED_FROM_GROUP.value,
        DomainEvent.AUTH_USER_REMOVED_FROM_SPONSOR_AND_SUMMIT.value,
        DomainEvent.AUTH_USER_REMOVED_FROM_SUMMIT.value
    ]

    def can_handle(self, event_type: str) -> bool:
        return event_type in self.HANDLED_EVENTS

    def handle(self, event: EventMessage) -> bool:
        try:
            logging.getLogger('api').debug(
                f"PermissionEventHandler::handle - Processing permission event: {event.event_type} - {event.payload}")
            if event.event_type == DomainEvent.AUTH_ACCESS_RIGHT_ADDED.value:
                return self._handle_permission_created_or_updated(event)
            elif event.event_type in [DomainEvent.AUTH_ACCESS_RIGHT_REMOVED.value,
                                      DomainEvent.AUTH_USER_REMOVED_FROM_GROUP.value,
                                      DomainEvent.AUTH_USER_REMOVED_FROM_SPONSOR_AND_SUMMIT.value,
                                      DomainEvent.AUTH_USER_REMOVED_FROM_SUMMIT.value]:
                return self._handle_permission_removed(event)

            return False
        except Exception as e:
            logging.getLogger('api').error(f"Error processing permission event: {e}")
            return False

    def _handle_permission_created_or_updated(self, event: EventMessage) -> bool:
        permission_data = event.payload
        sponsor_id = permission_data.get('sponsor_id')
        user_id = permission_data.get('user_external_id')
        summit_id = permission_data.get('summit_id')

        UserPermissionsService.upsert_cached_permission(user_id, summit_id, sponsor_id)
        return True

    def _handle_permission_removed(self, event: EventMessage) -> bool:
        permission_data = event.payload
        sponsor_id = permission_data.get('sponsor_id')
        user_id = permission_data.get('user_external_id')
        summit_id = permission_data.get('summit_id')
        if not summit_id:
            summit_id = permission_data.get('show_id')

        UserPermissionsService.remove_cached_permission(user_id, summit_id, sponsor_id)
        return True