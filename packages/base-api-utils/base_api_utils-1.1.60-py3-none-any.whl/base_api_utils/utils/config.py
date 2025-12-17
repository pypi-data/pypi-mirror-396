from django.conf import settings


def config(name: str, default=None):
    """
    Helper function to get a Django setting by name with support for nested attributes.
    If setting doesn't exist, it will return the default value.

    Examples:
        config("DEBUG", False)
        config("SPONSOR_USERS_API.CIRCUIT_BREAKER_INVOKE_RETRIES", 3)
        config("MY_DICT.nested.key", "fallback")

    :param name: Name of setting (supports dot notation for nested access)
    :type name: str
    :param default: Value if setting is unfound
    :returns: Setting's value or default
    """
    parts = name.split('.')
    entry = None

    for i, part in enumerate(parts):
        if entry is None:
            # First level: get from settings
            if not hasattr(settings, part):
                return default
            entry = getattr(settings, part)
        else:
            # Nested levels: navigate through dict/object
            if isinstance(entry, dict):
                if part not in entry:
                    return default
                entry = entry[part]
            else:
                # Try attribute access for objects
                if not hasattr(entry, part):
                    return default
                entry = getattr(entry, part)

    return entry if entry is not None else default