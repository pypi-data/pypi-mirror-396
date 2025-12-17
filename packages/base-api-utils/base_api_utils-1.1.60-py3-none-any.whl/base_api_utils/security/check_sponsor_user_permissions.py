import logging
import os

from django.core.exceptions import PermissionDenied
from django.utils.functional import wraps
from django.utils.translation import gettext_lazy as _
from rest_framework.exceptions import ValidationError, AuthenticationFailed

from . import AccessTokenService
from .shared import get_path, is_admin
from .user_permissions_service import UserPermissionsService


def check_sponsor_user_permissions():
    """
    Decorator to restrict sponsor users to specific sponsors and summits.

    Usage:
        @check_sponsor_user_permissions()
        def my_view(self, request, sponsor_id, summit_id):
    """
    def decorator(func):
        @wraps(func)
        def inner(view, *args, **kwargs):

            request = view.request
            token_info = request.auth

            kwargs['token_info'] = token_info

            # shortcircuit
            if os.getenv("ENV") == 'test':
                return func(view, *args, **kwargs)

            AccessTokenService.validate_token_info(token_info)

            logger = logging.getLogger('api')

            sponsor_id = kwargs.get('sponsor_id')
            if not sponsor_id:
                logger.warning('check_sponsor_user_permissions::decorator sponsor_id is required')
                raise ValidationError(_("sponsor_id is required"))

            summit_id = kwargs.get('summit_id')
            if not summit_id:
                logger.warning('check_sponsor_user_permissions::decorator summit_id is required')
                raise ValidationError(_("summit_id is required"))

            # Bypass admin and super-admin users
            if is_admin(token_info):
                return func(view, *args, **kwargs)

            path = get_path(request)
            method = str(request.method).lower()
            logger.debug(f'check_sponsor_user_permissions::decorator - checking permissions for {method} {path}')

            has_access = UserPermissionsService.has_permissions(
                sponsor_id=sponsor_id,
                summit_id=summit_id,
                token_info=token_info
            )

            if not has_access:
                logger.warning(f'check_sponsor_user_permissions::decorator - '
                               f'access denied for user to sponsor {sponsor_id} in summit {summit_id}')
                raise AuthenticationFailed(
                    f'Sponsor User has no permission to access this resource using sponsor {sponsor_id} and summit {summit_id}')

            logger.debug(f'check_sponsor_user_permissions::decorator - '
                         f'access granted to sponsor {sponsor_id} in summit {summit_id}')

            return func(view, *args, **kwargs)
        return inner
    return decorator