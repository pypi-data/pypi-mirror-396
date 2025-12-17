from injector import Module, Injector
from typing import List, Optional

def create_container(modules: List[Module]) -> Injector:
    return Injector(modules)

_container: Optional[Injector] = None

def get_container() -> Optional[Injector]:
    return _container

def set_container(container: Injector):
    global _container
    _container = container
