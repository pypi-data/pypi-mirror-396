from functools import wraps
from django.apps import apps
from injector import inject as inject_
import inspect

def inject_job(fn):
    # recreates all methods
    signature = inspect.signature(fn)
    is_method = 'self' in signature.parameters  # There must be a better way to do this

    fn = inject_(fn)

    @wraps(fn)
    def wrapper(*args, **kwargs):
        injector_app = apps.get_app_config("django_injector")
        injector = injector_app.injector
        if is_method:
            self_, *args = args
        else:
            self_ = None
        return injector.call_with_injection(fn, self_=self_, args=tuple(args), kwargs=kwargs)

    return wrapper
