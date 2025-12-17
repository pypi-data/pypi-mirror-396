import re

from django.contrib.admindocs.views import simplify_regex

from ..utils import config

_PATH_PARAMETER_COMPONENT_RE = re.compile(
    r'<(?:(?P<converter>[^>:]+):)?(?P<parameter>\w+)>'
)

def get_path(request) -> str:
    path = simplify_regex(request.resolver_match.route)
    # Strip Django 2.0 convertors as they are incompatible with uritemplate format
    path = re.sub(_PATH_PARAMETER_COMPONENT_RE, r'{\g<parameter>}', path)
    return path.replace('{pk}', '{id}')

client_secret_basic_auth_method = 'client_secret_basic'

application_type_service = 'SERVICE'

def is_admin(token_info):
    """
    Checks if the user has administrator privileges.

    Args:
    token_info (dict): Dictionary with authz information

    Returns:
    bool: True if any of the user groups belongs to the admin groups list, False otherwise
    """
    user_groups = token_info.get('user_groups', [])
    group_slugs = {group['slug'] for group in user_groups}

    admin_group_slugs = config('admin_group_slugs', ['administrators', 'super-admins'])

    return bool(group_slugs.intersection(admin_group_slugs))