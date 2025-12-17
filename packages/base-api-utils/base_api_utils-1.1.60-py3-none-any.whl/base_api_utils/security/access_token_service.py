import logging
import sys

import requests
from django.contrib.auth.models import AnonymousUser
from django.core.cache import cache
from django.core.exceptions import PermissionDenied
from django.utils.translation import gettext_lazy as _

from .abstract_access_token_service import AbstractAccessTokenService
from ..utils import config


class AccessTokenService(AbstractAccessTokenService):

    def validate(self, access_token:str):
        """
              Authenticate the request, given the access token.
        """
        logging.getLogger('oauth2').debug('AccessTokenService::validate trying to get {access_token} from cache ...'.format(access_token=access_token))
        # try get access_token from DB and check if not expired
        cached_token_info = cache.get(access_token)

        if cached_token_info is None:
            try:
                logging.getLogger('oauth2').debug(
                    'AccessTokenService::validate {access_token} is not present on cache, trying to validate from instrospection endpoint'.format(access_token=access_token))
                response = requests.post(
                    '{base_url}/{endpoint}'.format
                        (
                        base_url=config('OAUTH2.IDP.BASE_URL', None),
                        endpoint=config('OAUTH2.IDP.INTROSPECTION_ENDPOINT', None)
                    ),
                    auth=(config('OAUTH2.CLIENT.ID', None), config('OAUTH2.CLIENT.SECRET', None),),
                    params={'token': access_token},
                    verify=False if config('DEBUG', False) else True,
                    allow_redirects=False
                )

                if response.status_code == requests.codes.ok:
                    cached_token_info = response.json()
                    lifetime = config('OAUTH2.CLIENT.ACCESS_TOKEN_CACHE_LIFETIME', cached_token_info['expires_in'])
                    logging.getLogger('oauth2').debug(
                        'AccessTokenService::validate {access_token} storing on cache with lifetime {lifetime}'.format(
                            access_token=access_token, lifetime=lifetime))
                    cache.set(access_token, cached_token_info, timeout=int(lifetime))
                    logging.getLogger('oauth2').warning(
                        'http code {code} http content {content}'.format(code=response.status_code,
                                                                         content=response.content))
                    return AnonymousUser, cached_token_info

                logging.getLogger('oauth2').warning(
                    'AccessTokenService::validate http code {code} http content {content}'.format(code=response.status_code,
                                                                     content=response.content))

                result = {
                    'error_code': response.status_code,
                    'error': response.content.get('error', ''),
                    'description': response.content.get('error_description', '')
                }
                return None, result
            except requests.exceptions.RequestException as e:
                logging.getLogger('oauth2').error(e)
                return None
            except:
                logging.getLogger('oauth2').error(sys.exc_info())
                return None

        logging.getLogger('oauth2').debug(
            'AccessTokenService::validate {access_token} cache hit'.format(
                access_token=access_token))
        return AnonymousUser, cached_token_info

    @staticmethod
    def validate_token_info(token_info):
        if token_info is None:
            logging.getLogger('oauth2').warning('AccessTokenService::validate_token_info token info not present.')
            raise PermissionDenied(_("token info not present."))

        if 'error_code' in token_info:
            error_description = token_info.get('error_description', 'token info is invalid.')
            logging.getLogger('oauth2').warning(
                f'AccessTokenService::validate_token_info token info is invalid: {token_info}')
            raise PermissionDenied(error_description)