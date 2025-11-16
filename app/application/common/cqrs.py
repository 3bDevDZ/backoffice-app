from abc import ABC, abstractmethod
from typing import Type, Dict, TypeVar, Generic

T = TypeVar('T')

class Query(ABC):
    pass

class Command(ABC):
    pass

class QueryHandler(Generic[T], ABC):
    @abstractmethod
    def handle(self, query: Query) -> T:
        raise NotImplementedError

class CommandHandler(Generic[T], ABC):
    @abstractmethod
    def handle(self, command: Command) -> T:
        raise NotImplementedError