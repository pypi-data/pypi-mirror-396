from abc import ABC, abstractmethod

from .connection_params import ConnectionParams


class ParamsFactory(ABC):

    @classmethod
    @abstractmethod
    def get_params(cls) -> ConnectionParams:
        pass
