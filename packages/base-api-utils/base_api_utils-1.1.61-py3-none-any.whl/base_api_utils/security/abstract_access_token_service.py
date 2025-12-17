from abc import abstractmethod, ABC


class AbstractAccessTokenService(ABC):

    def __init__(self):
        pass

    @abstractmethod
    def validate(self, access_token:str):
        pass
