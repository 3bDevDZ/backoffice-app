"""Dashboard queries module."""
from .queries import (
    GetKPIsQuery,
    GetRevenueQuery,
    GetStockAlertsQuery,
    GetActiveOrdersQuery
)
from .handlers import (
    GetKPIsHandler,
    GetRevenueHandler,
    GetStockAlertsHandler,
    GetActiveOrdersHandler
)

__all__ = [
    'GetKPIsQuery',
    'GetRevenueQuery',
    'GetStockAlertsQuery',
    'GetActiveOrdersQuery',
    'GetKPIsHandler',
    'GetRevenueHandler',
    'GetStockAlertsHandler',
    'GetActiveOrdersHandler'
]

