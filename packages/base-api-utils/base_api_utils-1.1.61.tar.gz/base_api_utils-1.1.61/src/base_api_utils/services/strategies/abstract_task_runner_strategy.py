from abc import ABC, abstractmethod


class AbstractTaskRunnerStrategy(ABC):

    @abstractmethod
    def run(self, *args, **kwargs):
        pass