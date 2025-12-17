import logging
from functools import wraps
from django.db import connection, close_old_connections
from django.db.utils import OperationalError

def handle_db_connections(max_retries=3):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    close_old_connections()  # Close stale connections
                    result = func(*args, **kwargs)
                    connection.close()  # Close after use
                    return result
                except OperationalError as e:
                    if '2013' in str(e) or 'Lost connection' in str(e):
                        logging.getLogger('api').warning(f"DB connection lost (attempt {attempt + 1}/{max_retries})")
                        connection.close()
                        if attempt == max_retries - 1:
                            raise
                    else:
                        raise
            return None
        return wrapper
    return decorator