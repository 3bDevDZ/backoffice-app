"""Report builder service for building custom reports with column selection, filters, and calculated fields."""
from typing import List, Dict, Any, Optional
from decimal import Decimal
from datetime import date
from dataclasses import dataclass

from app.services.report_service import ReportService, ReportData
from app.domain.models.report import ReportTemplate


@dataclass
class ColumnDefinition:
    """Definition of a report column."""
    field: str  # Field name from data
    label: str  # Display label
    type: str  # 'string', 'number', 'date', 'currency'
    visible: bool = True
    width: Optional[int] = None


@dataclass
class FilterCondition:
    """Filter condition for report data."""
    field: str
    operator: str  # 'equals', 'not_equals', 'contains', 'greater_than', 'less_than', 'between'
    value: Any
    value2: Optional[Any] = None  # For 'between' operator


@dataclass
class SortDefinition:
    """Sort definition for report data."""
    field: str
    direction: str  # 'asc', 'desc'


@dataclass
class GroupDefinition:
    """Group definition for report data."""
    field: str
    label: str
    aggregate: Optional[str] = None  # 'sum', 'avg', 'count', 'min', 'max'


@dataclass
class CalculatedField:
    """Calculated field definition."""
    name: str
    label: str
    formula: str  # Simple formula like "revenue - cost" or "margin / revenue * 100"
    type: str = 'number'  # 'number', 'currency', 'percent'


class ReportBuilderService:
    """Service for building custom reports with column selection, filters, and calculated fields."""
    
    def __init__(self):
        self.report_service = ReportService()
    
    def build_report(
        self,
        report_data: ReportData,
        columns: Optional[List[ColumnDefinition]] = None,
        filters: Optional[List[FilterCondition]] = None,
        sorting: Optional[List[SortDefinition]] = None,
        grouping: Optional[List[GroupDefinition]] = None,
        calculated_fields: Optional[List[CalculatedField]] = None
    ) -> ReportData:
        """
        Build a custom report from base report data.
        
        Args:
            report_data: Base ReportData object
            columns: Optional list of column definitions
            filters: Optional list of filter conditions
            sorting: Optional list of sort definitions
            grouping: Optional list of group definitions
            calculated_fields: Optional list of calculated field definitions
            
        Returns:
            Modified ReportData object
        """
        # Start with a copy of the data
        filtered_data = list(report_data.data)
        
        # Apply filters
        if filters:
            filtered_data = self._apply_filters(filtered_data, filters)
        
        # Add calculated fields
        if calculated_fields:
            filtered_data = self._add_calculated_fields(filtered_data, calculated_fields)
        
        # Apply grouping
        if grouping:
            filtered_data = self._apply_grouping(filtered_data, grouping)
        
        # Apply sorting
        if sorting:
            filtered_data = self._apply_sorting(filtered_data, sorting)
        
        # Filter columns
        if columns:
            filtered_data = self._filter_columns(filtered_data, columns)
        
        # Update report data
        report_data.data = filtered_data
        
        # Update metadata
        report_data.metadata.update({
            'columns': [{'field': c.field, 'label': c.label, 'type': c.type} for c in columns] if columns else None,
            'filters': [{'field': f.field, 'operator': f.operator, 'value': f.value} for f in filters] if filters else None,
            'sorting': [{'field': s.field, 'direction': s.direction} for s in sorting] if sorting else None,
            'grouping': [{'field': g.field, 'label': g.label, 'aggregate': g.aggregate} for g in grouping] if grouping else None,
            'calculated_fields': [{'name': cf.name, 'label': cf.label, 'formula': cf.formula} for cf in calculated_fields] if calculated_fields else None
        })
        
        return report_data
    
    def _apply_filters(
        self,
        data: List[Dict[str, Any]],
        filters: List[FilterCondition]
    ) -> List[Dict[str, Any]]:
        """Apply filter conditions to data."""
        filtered = data
        
        for filter_cond in filters:
            field = filter_cond.field
            operator = filter_cond.operator
            value = filter_cond.value
            value2 = filter_cond.value2
            
            if operator == 'equals':
                filtered = [row for row in filtered if row.get(field) == value]
            elif operator == 'not_equals':
                filtered = [row for row in filtered if row.get(field) != value]
            elif operator == 'contains':
                filtered = [row for row in filtered if str(value).lower() in str(row.get(field, '')).lower()]
            elif operator == 'greater_than':
                filtered = [row for row in filtered if self._compare_values(row.get(field), value) > 0]
            elif operator == 'less_than':
                filtered = [row for row in filtered if self._compare_values(row.get(field), value) < 0]
            elif operator == 'between':
                if value2 is not None:
                    filtered = [row for row in filtered if 
                                self._compare_values(row.get(field), value) >= 0 and
                                self._compare_values(row.get(field), value2) <= 0]
            elif operator == 'in':
                if isinstance(value, list):
                    filtered = [row for row in filtered if row.get(field) in value]
        
        return filtered
    
    def _compare_values(self, val1: Any, val2: Any) -> int:
        """Compare two values, handling different types."""
        try:
            # Try numeric comparison
            if isinstance(val1, (int, float, Decimal)) and isinstance(val2, (int, float, Decimal)):
                if Decimal(str(val1)) > Decimal(str(val2)):
                    return 1
                elif Decimal(str(val1)) < Decimal(str(val2)):
                    return -1
                else:
                    return 0
            # String comparison
            elif isinstance(val1, str) and isinstance(val2, str):
                if val1 > val2:
                    return 1
                elif val1 < val2:
                    return -1
                else:
                    return 0
            # Date comparison
            elif isinstance(val1, date) and isinstance(val2, (date, str)):
                if isinstance(val2, str):
                    val2 = date.fromisoformat(val2)
                if val1 > val2:
                    return 1
                elif val1 < val2:
                    return -1
                else:
                    return 0
            else:
                # Fallback to string comparison
                return 1 if str(val1) > str(val2) else (-1 if str(val1) < str(val2) else 0)
        except:
            return 0
    
    def _add_calculated_fields(
        self,
        data: List[Dict[str, Any]],
        calculated_fields: List[CalculatedField]
    ) -> List[Dict[str, Any]]:
        """Add calculated fields to data."""
        result = []
        
        for row in data:
            new_row = dict(row)
            
            for calc_field in calculated_fields:
                try:
                    # Simple formula evaluation (replace field names with values)
                    formula = calc_field.formula
                    for key, val in row.items():
                        # Replace field names in formula
                        formula = formula.replace(key, str(val))
                    
                    # Evaluate formula (simple arithmetic only)
                    # Note: In production, use a proper formula parser for security
                    value = eval(formula)  # WARNING: eval is unsafe, use a proper parser in production
                    
                    new_row[calc_field.name] = value
                except Exception as e:
                    # If calculation fails, set to None
                    new_row[calc_field.name] = None
            
            result.append(new_row)
        
        return result
    
    def _apply_grouping(
        self,
        data: List[Dict[str, Any]],
        grouping: List[GroupDefinition]
    ) -> List[Dict[str, Any]]:
        """Apply grouping to data."""
        if not grouping:
            return data
        
        # Group by first grouping field
        group_field = grouping[0].field
        aggregate = grouping[0].aggregate
        
        # Group data
        groups = {}
        for row in data:
            group_key = row.get(group_field)
            if group_key not in groups:
                groups[group_key] = []
            groups[group_key].append(row)
        
        # Aggregate if specified
        if aggregate:
            result = []
            for group_key, group_rows in groups.items():
                # Create aggregated row
                aggregated_row = {group_field: group_key}
                
                # Aggregate numeric fields
                for field in group_rows[0].keys():
                    if field != group_field:
                        try:
                            values = [row.get(field) for row in group_rows if row.get(field) is not None]
                            if values:
                                if aggregate == 'sum':
                                    aggregated_row[field] = sum(Decimal(str(v)) if not isinstance(v, Decimal) else v for v in values)
                                elif aggregate == 'avg':
                                    aggregated_row[field] = sum(Decimal(str(v)) if not isinstance(v, Decimal) else v for v in values) / len(values)
                                elif aggregate == 'count':
                                    aggregated_row[field] = len(values)
                                elif aggregate == 'min':
                                    aggregated_row[field] = min(values)
                                elif aggregate == 'max':
                                    aggregated_row[field] = max(values)
                                else:
                                    aggregated_row[field] = values[0] if values else None
                            else:
                                aggregated_row[field] = None
                        except:
                            aggregated_row[field] = group_rows[0].get(field)
                
                result.append(aggregated_row)
            
            return result
        else:
            # Return grouped data as-is (nested structure)
            return data
    
    def _apply_sorting(
        self,
        data: List[Dict[str, Any]],
        sorting: List[SortDefinition]
    ) -> List[Dict[str, Any]]:
        """Apply sorting to data."""
        if not sorting:
            return data
        
        # Sort by first sort definition
        sort_def = sorting[0]
        field = sort_def.field
        direction = sort_def.direction
        
        def sort_key(row):
            value = row.get(field)
            # Handle None values
            if value is None:
                return (0, '') if direction == 'asc' else (1, '')
            # Handle different types
            if isinstance(value, (int, float, Decimal)):
                return (1, float(value))
            elif isinstance(value, date):
                return (1, value.isoformat())
            else:
                return (1, str(value))
        
        sorted_data = sorted(data, key=sort_key, reverse=(direction == 'desc'))
        
        # Apply additional sorts if specified
        for sort_def in sorting[1:]:
            field = sort_def.field
            direction = sort_def.direction
            
            def secondary_sort_key(row):
                value = row.get(field)
                if value is None:
                    return (0, '') if direction == 'asc' else (1, '')
                if isinstance(value, (int, float, Decimal)):
                    return (1, float(value))
                elif isinstance(value, date):
                    return (1, value.isoformat())
                else:
                    return (1, str(value))
            
            sorted_data = sorted(sorted_data, key=secondary_sort_key, reverse=(direction == 'desc'))
        
        return sorted_data
    
    def _filter_columns(
        self,
        data: List[Dict[str, Any]],
        columns: List[ColumnDefinition]
    ) -> List[Dict[str, Any]]:
        """Filter data to only include specified columns."""
        visible_columns = [c.field for c in columns if c.visible]
        
        if not visible_columns:
            return data
        
        result = []
        for row in data:
            filtered_row = {field: row.get(field) for field in visible_columns if field in row}
            result.append(filtered_row)
        
        return result
    
    def build_from_template(
        self,
        template: ReportTemplate,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> ReportData:
        """
        Build a report from a template.
        
        Args:
            template: ReportTemplate object
            start_date: Optional start date override
            end_date: Optional end date override
            
        Returns:
            ReportData object
        """
        # Generate base report
        base_report = self.report_service.generate_custom_report(
            template.id,
            start_date,
            end_date
        )
        
        # Convert template configuration to builder definitions
        columns = None
        if template.columns:
            columns = [
                ColumnDefinition(
                    field=col.get('field', ''),
                    label=col.get('label', col.get('field', '')),
                    type=col.get('type', 'string'),
                    visible=col.get('visible', True)
                )
                for col in template.columns
            ]
        
        filters = None
        if template.filters:
            filters = [
                FilterCondition(
                    field=f.get('field', ''),
                    operator=f.get('operator', 'equals'),
                    value=f.get('value'),
                    value2=f.get('value2')
                )
                for f in template.filters
            ]
        
        sorting = None
        if template.sorting:
            sorting = [
                SortDefinition(
                    field=s.get('field', ''),
                    direction=s.get('direction', 'asc')
                )
                for s in template.sorting
            ]
        
        grouping = None
        if template.grouping:
            grouping = [
                GroupDefinition(
                    field=g.get('field', ''),
                    label=g.get('label', g.get('field', '')),
                    aggregate=g.get('aggregate')
                )
                for g in template.grouping
            ]
        
        calculated_fields = None
        if template.calculated_fields:
            calculated_fields = [
                CalculatedField(
                    name=cf.get('name', ''),
                    label=cf.get('label', cf.get('name', '')),
                    formula=cf.get('formula', ''),
                    type=cf.get('type', 'number')
                )
                for cf in template.calculated_fields
            ]
        
        # Build report with template configuration
        return self.build_report(
            base_report,
            columns=columns,
            filters=filters,
            sorting=sorting,
            grouping=grouping,
            calculated_fields=calculated_fields
        )

