import logging
import sys

import requests

from django.core.cache import cache

from requests import HTTPError

from ..utils import NamedCircuitBreaker, config, call_with_breaker


class UserPermissionsService:
    """
    Client for interacting with the Sponsor Users API.

    Configuration Required:
    -----------------------
    The following parameters must be configured in the client project's settings.py:

    SPONSOR_USERS_API = {
        'BASE_URL': os.getenv('SPONSOR_USERS_API_BASE_URL'),
        'CIRCUIT_BREAKER_INVOKE_RETRIES': os.getenv('SPONSOR_USERS_API_CB_INVOKE_RETRIES', 3),
        'CIRCUIT_BREAKER_RESET_TIMEOUT': os.getenv('SPONSOR_USERS_API_CB_RESET_TIMEOUT', 60),
        'TIMEOUT': os.getenv('SPONSOR_USERS_API_TIMEOUT'),
        'ACCESS_RIGHT_CACHE_LIFETIME': os.getenv('SPONSOR_USERS_API_ACCESS_RIGHT_CACHE_LIFETIME', 300)
    }

    Environment Variables:
    ----------------------
    - SPONSOR_USERS_API_BASE_URL: Base URL for the API (required)
    - SPONSOR_USERS_API_CB_INVOKE_RETRIES: Number of retries for circuit breaker (default: 3)
    - SPONSOR_USERS_API_CB_RESET_TIMEOUT: Circuit breaker reset timeout in seconds (default: 60)
    - SPONSOR_USERS_API_TIMEOUT: Request timeout in seconds (required)
    - SPONSOR_USERS_API_ACCESS_RIGHT_CACHE_LIFETIME: Cache lifetime in seconds (default: 300)
    """

    breaker = NamedCircuitBreaker(
        fail_max=int(config("SPONSOR_USERS_API.CIRCUIT_BREAKER_INVOKE_RETRIES", "3")),
        reset_timeout=float(config("SPONSOR_USERS_API.CIRCUIT_BREAKER_RESET_TIMEOUT", "60")),
        name=config("SPONSOR_USERS_API.CIRCUIT_BREAKER_NAME", 'sponsor_users_api')
    )

    @classmethod
    def _build_cache_key(cls, sponsor_id, summit_id, user_id) -> str:
        return f"summit:{summit_id}:sponsor:{sponsor_id}:user:{user_id}"

    @classmethod
    def _build_cache_index_key(cls, summit_id, user_id) -> str:
        return f"index:summit:{summit_id}:user:{user_id}"

    @classmethod
    def _set_cache(cls, summit_id, sponsor_id, user_id, value, timeout=300):
        key = cls._build_cache_key(sponsor_id, summit_id, user_id)
        cache.set(key, value, timeout)

        # Secondary index storing all sponsor IDs linked to the user's permissions for this summit
        # maps (summit_id, user_id) → set of sponsor_ids
        index_key = cls._build_cache_index_key(summit_id, user_id)

        sponsor_ids = cache.get(index_key, set())
        sponsor_ids.add(sponsor_id)
        cache.set(index_key, sponsor_ids, timeout)

    @classmethod
    def _remove_by_summit_sponsor_user(cls, summit_id, sponsor_id, user_id):
        key = cls._build_cache_key(summit_id, sponsor_id, user_id)
        cache.delete(key)

        # update secondary index
        index_key = cls._build_cache_index_key(summit_id, user_id)
        sponsor_ids = cache.get(index_key, set())

        if sponsor_id in sponsor_ids:
            sponsor_ids.remove(sponsor_id)

            if sponsor_ids:
                cache.set(index_key, sponsor_ids)
            else:
                cache.delete(index_key)

    @classmethod
    def _remove_by_summit_user(cls, summit_id, user_id):
        index_key = cls._build_cache_index_key(summit_id, user_id)
        sponsor_ids = cache.get(index_key, set())

        if not sponsor_ids:
            return

        for sponsor_id in sponsor_ids:
            key = cls._build_cache_key(summit_id, sponsor_id, user_id)
            cache.delete(key)

        # delete secondary index entry
        cache.delete(index_key)

    @classmethod
    def _get_permission(cls, sponsor_id, summit_id, access_token) -> dict:
        url = f"{config("SPONSOR_USERS_API.BASE_URL")}/api/v1/permissions/me/summits/{summit_id}/sponsors/{sponsor_id}"
        query_params = {"access_token": access_token}

        def call():
            response = requests.get(url,
                                    params=query_params,
                                    timeout=int(config("SPONSOR_USERS_API.TIMEOUT", 60)))

            response.raise_for_status()
            return response.json()

        return call_with_breaker(cls.breaker, call)

    @classmethod
    def has_permissions(cls, sponsor_id, summit_id, token_info) -> bool:
        user_id = token_info['user_id']
        access_token = token_info['access_token']

        cache_key = cls._build_cache_key(sponsor_id, summit_id, user_id)

        logging.getLogger('api').debug(
            f'SponsorUsersService::has_access_rights trying to get {access_token} from cache...')

        cached_access_right = cache.get(cache_key)

        if not cached_access_right:
            try:
                lifetime = int(config('SPONSOR_USERS_API.ACCESS_RIGHT_CACHE_LIFETIME', 300))
                access_right_info = cls._get_permission(sponsor_id, summit_id, access_token)
                if access_right_info.get('user_id') is None:
                    return False

                cls._set_cache(summit_id, sponsor_id, user_id, True, timeout=lifetime)
            except HTTPError as e:
                logging.getLogger('api').error(e)
                return False
            except:
                logging.getLogger('api').error(sys.exc_info())
                return False

        return True

    @classmethod
    def upsert_cached_permission(cls, user_id, summit_id, sponsor_id):
        lifetime = int(config('SPONSOR_USERS_API.ACCESS_RIGHT_CACHE_LIFETIME', 300))
        cls._set_cache(summit_id, sponsor_id, user_id, True, timeout=lifetime)

    @classmethod
    def remove_cached_permission(cls, user_id, summit_id, sponsor_id = None):
        if sponsor_id:
            cls._remove_by_summit_sponsor_user(summit_id, sponsor_id, user_id)
        else:
            cls._remove_by_summit_user(summit_id, user_id)
