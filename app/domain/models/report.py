"""Report domain models for advanced reporting and analytics."""
from dataclasses import dataclass
from decimal import Decimal
from datetime import datetime, date
from typing import Optional, Dict, List, Any
from sqlalchemy import Column, Integer, String, Text, JSON, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from ...infrastructure.db import Base
from ...domain.primitives.aggregate_root import AggregateRoot


class ReportTemplate(Base, AggregateRoot):
    """ReportTemplate model for saving custom report configurations."""
    __tablename__ = "report_templates"

    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    report_type = Column(String(50), nullable=False)  # 'sales', 'margins', 'stock', 'customers', 'purchases', 'custom'
    
    # Configuration stored as JSON
    columns = Column(JSON, nullable=True)  # List of column definitions
    filters = Column(JSON, nullable=True)  # Filter conditions
    sorting = Column(JSON, nullable=True)  # Sort configuration
    grouping = Column(JSON, nullable=True)  # Grouping configuration
    calculated_fields = Column(JSON, nullable=True)  # Calculated field definitions
    
    # Metadata
    created_by = Column(Integer, ForeignKey('users.id'), nullable=False)
    is_public = Column(Boolean, default=False, nullable=False)  # Whether template is shared
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())

    # Relationships
    creator = relationship("User", foreign_keys=[created_by], backref="report_templates")

    @staticmethod
    def create(
        name: str,
        report_type: str,
        created_by: int,
        description: Optional[str] = None,
        columns: Optional[List[Dict[str, Any]]] = None,
        filters: Optional[Dict[str, Any]] = None,
        sorting: Optional[List[Dict[str, Any]]] = None,
        grouping: Optional[List[Dict[str, Any]]] = None,
        calculated_fields: Optional[List[Dict[str, Any]]] = None,
        is_public: bool = False
    ) -> "ReportTemplate":
        """
        Factory method to create a new ReportTemplate.
        
        Args:
            name: Template name
            report_type: Type of report ('sales', 'margins', 'stock', 'customers', 'purchases', 'custom')
            created_by: User ID who created the template
            description: Optional description
            columns: List of column definitions
            filters: Filter conditions
            sorting: Sort configuration
            grouping: Grouping configuration
            calculated_fields: Calculated field definitions
            is_public: Whether template is shared
            
        Returns:
            ReportTemplate instance
        """
        if not name or not name.strip():
            raise ValueError("Template name is required.")
        
        valid_types = ['sales', 'margins', 'stock', 'customers', 'purchases', 'custom']
        if report_type not in valid_types:
            raise ValueError(f"Report type must be one of: {', '.join(valid_types)}")
        
        template = ReportTemplate()
        template.name = name.strip()
        template.report_type = report_type
        template.created_by = created_by
        template.description = description.strip() if description else None
        template.columns = columns or []
        template.filters = filters or {}
        template.sorting = sorting or []
        template.grouping = grouping or []
        template.calculated_fields = calculated_fields or []
        template.is_public = is_public
        
        return template

    def update(
        self,
        name: Optional[str] = None,
        description: Optional[str] = None,
        columns: Optional[List[Dict[str, Any]]] = None,
        filters: Optional[Dict[str, Any]] = None,
        sorting: Optional[List[Dict[str, Any]]] = None,
        grouping: Optional[List[Dict[str, Any]]] = None,
        calculated_fields: Optional[List[Dict[str, Any]]] = None,
        is_public: Optional[bool] = None
    ) -> None:
        """Update template configuration."""
        if name is not None:
            if not name.strip():
                raise ValueError("Template name cannot be empty.")
            self.name = name.strip()
        if description is not None:
            self.description = description.strip() if description else None
        if columns is not None:
            self.columns = columns
        if filters is not None:
            self.filters = filters
        if sorting is not None:
            self.sorting = sorting
        if grouping is not None:
            self.grouping = grouping
        if calculated_fields is not None:
            self.calculated_fields = calculated_fields
        if is_public is not None:
            self.is_public = is_public
        self.updated_at = datetime.utcnow()

