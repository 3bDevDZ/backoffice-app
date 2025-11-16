from typing import Type, Dict, TypeVar
from .cqrs import Command, Query, CommandHandler, QueryHandler

T = TypeVar('T')

class Mediator:
    def __init__(self):
        self._command_handlers: Dict[Type[Command], CommandHandler] = {}
        self._query_handlers: Dict[Type[Query], QueryHandler] = {}

    def register_command(self, command: Type[Command], handler: CommandHandler):
        self._command_handlers[command] = handler

    def register_query(self, query: Type[Query], handler: QueryHandler):
        self._query_handlers[query] = handler

    def dispatch(self, request: T) -> any:
        if isinstance(request, Command):
            handler = self._command_handlers.get(type(request))
            if handler:
                return handler.handle(request)
            raise ValueError(f"No handler registered for command {type(request).__name__}")
        elif isinstance(request, Query):
            handler = self._query_handlers.get(type(request))
            if handler:
                return handler.handle(request)
            raise ValueError(f"No handler registered for query {type(request).__name__}")
        else:
            raise TypeError(f"Request of type {type(request).__name__} is not a Command or Query")

mediator = Mediator()