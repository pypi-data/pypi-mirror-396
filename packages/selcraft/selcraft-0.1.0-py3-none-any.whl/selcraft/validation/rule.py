from abc import ABC, abstractmethod


class Rule(ABC):
    @abstractmethod
    def validate(self, config: dict) -> None:
        pass

    @property
    def name(self) -> str:
        return type(self).__name__.lower()
