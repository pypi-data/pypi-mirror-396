from ..utils import config


class AuthzUserDTO:
    def __init__(self, token_info=None):
        if token_info is None:
            token_info = {}
        self.id = token_info.get('user_id', None)
        self.first_name = token_info.get('user_first_name', None)
        self.last_name = token_info.get('user_last_name', None)
        self.email = token_info.get('user_email', None)
        self.groups = token_info.get('user_groups', [])

    def is_admin(self) -> bool:
        admin_groups = config('OAUTH2.ADMIN_GROUPS', '').split()

        for group in self.groups:
            if group.get("slug") in admin_groups:
                return True

        return False





