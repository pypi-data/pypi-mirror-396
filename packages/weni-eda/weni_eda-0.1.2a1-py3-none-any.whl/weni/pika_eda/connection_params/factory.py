from abc import ABC, abstractmethod

from .connection_params import PikaConnectionParams


class PikaParamsFactory(ABC):

    @classmethod
    @abstractmethod
    def get_params(cls) -> PikaConnectionParams:
        pass
