from abc import ABC, abstractmethod


class Parser(ABC):  # pragma: no cover

    @classmethod
    @abstractmethod
    def parse(stream, encoding=None):
        pass
