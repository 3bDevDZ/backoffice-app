"""Settings query DTOs."""
from dataclasses import dataclass

from app.application.common.cqrs import Query


@dataclass
class GetCompanySettingsQuery(Query):
    """Query to get company settings."""
    pass


@dataclass
class GetAppSettingsQuery(Query):
    """Query to get application settings."""
    pass

