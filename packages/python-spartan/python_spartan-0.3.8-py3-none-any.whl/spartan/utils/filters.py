"""Reusable filter utilities for CLI list commands."""

import re
from typing import Any, Dict, List, Optional


class FilterUtility:
    """Utility class for filtering data in CLI list commands."""

    @staticmethod
    def validate_regex_pattern(pattern: str) -> tuple[bool, Optional[str]]:
        """Validate a regex pattern.

        Args:
            pattern: The regex pattern to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            re.compile(pattern)
            return True, None
        except re.error as e:
            return False, str(e)

    @staticmethod
    def apply_prefix_filter(
        items: List[Dict[str, Any]], field: str, prefix: str
    ) -> List[Dict[str, Any]]:
        """Apply prefix filtering to a list of items.

        Args:
            items: List of dictionaries to filter
            field: Field name to apply prefix filter on
            prefix: Prefix string to match

        Returns:
            Filtered list of items
        """
        return [item for item in items if item.get(field, "").startswith(prefix)]

    @staticmethod
    def apply_regex_filter(
        items: List[Dict[str, Any]], field: str, pattern: str
    ) -> List[Dict[str, Any]]:
        """Apply regex filtering to a list of items.

        Args:
            items: List of dictionaries to filter
            field: Field name to apply regex filter on
            pattern: Regex pattern to match

        Returns:
            Filtered list of items
        """
        try:
            compiled_pattern = re.compile(pattern)
            return [
                item for item in items if compiled_pattern.search(item.get(field, ""))
            ]
        except re.error:
            # Return original list if regex is invalid (should be validated beforehand)
            return items

    @staticmethod
    def apply_status_filter(
        items: List[Dict[str, Any]], field: str, status: str
    ) -> List[Dict[str, Any]]:
        """Apply status filtering to a list of items.

        Args:
            items: List of dictionaries to filter
            field: Field name to apply status filter on
            status: Status value to match

        Returns:
            Filtered list of items
        """
        return [item for item in items if item.get(field, "").upper() == status.upper()]

    @staticmethod
    def apply_contains_filter(
        items: List[Dict[str, Any]],
        field: str,
        value: str,
        case_sensitive: bool = False,
    ) -> List[Dict[str, Any]]:
        """Apply contains filtering to a list of items.

        Args:
            items: List of dictionaries to filter
            field: Field name to apply contains filter on
            value: Value to search for
            case_sensitive: Whether the search should be case sensitive

        Returns:
            Filtered list of items
        """
        if case_sensitive:
            return [item for item in items if value in item.get(field, "")]
        else:
            value_lower = value.lower()
            return [
                item for item in items if value_lower in item.get(field, "").lower()
            ]

    @staticmethod
    def apply_multiple_filters(
        items: List[Dict[str, Any]], filters: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Apply multiple filters to a list of items.

        Args:
            items: List of dictionaries to filter
            filters: Dictionary of filter configurations
                    Expected format:
                    {
                        'prefix': {'field': 'name', 'value': 'prefix_string'},
                        'regex': {'field': 'name', 'value': 'regex_pattern'},
                        'status': {'field': 'status', 'value': 'status_value'},
                        'contains': {'field': 'description', 'value': 'search_term', 'case_sensitive': False}
                    }

        Returns:
            Filtered list of items
        """
        filtered_items = items.copy()

        # Apply prefix filter
        if "prefix" in filters and filters["prefix"]:
            field = filters["prefix"].get("field")
            value = filters["prefix"].get("value")
            if field and value:
                filtered_items = FilterUtility.apply_prefix_filter(
                    filtered_items, field, value
                )

        # Apply regex filter
        if "regex" in filters and filters["regex"]:
            field = filters["regex"].get("field")
            value = filters["regex"].get("value")
            if field and value:
                filtered_items = FilterUtility.apply_regex_filter(
                    filtered_items, field, value
                )

        # Apply status filter
        if "status" in filters and filters["status"]:
            field = filters["status"].get("field")
            value = filters["status"].get("value")
            if field and value:
                filtered_items = FilterUtility.apply_status_filter(
                    filtered_items, field, value
                )

        # Apply contains filter
        if "contains" in filters and filters["contains"]:
            field = filters["contains"].get("field")
            value = filters["contains"].get("value")
            case_sensitive = filters["contains"].get("case_sensitive", False)
            if field and value:
                filtered_items = FilterUtility.apply_contains_filter(
                    filtered_items, field, value, case_sensitive
                )

        return filtered_items

    @staticmethod
    def get_filter_summary(filters: Dict[str, Any]) -> List[str]:
        """Generate a summary of applied filters for display.

        Args:
            filters: Dictionary of filter configurations

        Returns:
            List of filter description strings
        """
        summary = []

        if "prefix" in filters and filters["prefix"] and filters["prefix"].get("value"):
            summary.append(f"prefix: {filters['prefix']['value']}")

        if "regex" in filters and filters["regex"] and filters["regex"].get("value"):
            summary.append(f"regex: {filters['regex']['value']}")

        if "status" in filters and filters["status"] and filters["status"].get("value"):
            summary.append(f"status: {filters['status']['value']}")

        if (
            "contains" in filters
            and filters["contains"]
            and filters["contains"].get("value")
        ):
            summary.append(f"contains: {filters['contains']['value']}")

        return summary

    @staticmethod
    def validate_all_filters(
        prefix_filter: Optional[str] = None,
        regex_filter: Optional[str] = None,
        status_filter: Optional[str] = None,
        valid_statuses: Optional[List[str]] = None,
    ) -> tuple[bool, Optional[str]]:
        """Validate all provided filters.

        Args:
            prefix_filter: Prefix filter string
            regex_filter: Regex filter pattern
            status_filter: Status filter value
            valid_statuses: List of valid status values

        Returns:
            Tuple of (is_valid, error_message)
        """
        # Validate regex pattern
        if regex_filter:
            is_valid, error = FilterUtility.validate_regex_pattern(regex_filter)
            if not is_valid:
                return False, f"Invalid regex pattern '{regex_filter}': {error}"

        # Validate status filter
        if status_filter and valid_statuses:
            if status_filter.upper() not in [s.upper() for s in valid_statuses]:
                return (
                    False,
                    f"Invalid status '{status_filter}'. Valid statuses: {', '.join(valid_statuses)}",
                )

        return True, None


class SortUtility:
    """Utility class for sorting data in CLI list commands."""

    @staticmethod
    def validate_sort_field(
        sort_field: str, valid_fields: List[str]
    ) -> tuple[bool, Optional[str]]:
        """Validate a sort field.

        Args:
            sort_field: The field to sort by
            valid_fields: List of valid sort fields

        Returns:
            Tuple of (is_valid, error_message)
        """
        if sort_field not in valid_fields:
            return (
                False,
                f"Invalid sort field '{sort_field}'. Valid fields: {', '.join(valid_fields)}",
            )
        return True, None

    @staticmethod
    def sort_items(
        items: List[Dict[str, Any]],
        sort_field: str,
        reverse: bool = False,
        case_sensitive: bool = False,
    ) -> List[Dict[str, Any]]:
        """Sort a list of items by a specified field.

        Args:
            items: List of dictionaries to sort
            sort_field: Field name to sort by
            reverse: Whether to sort in descending order
            case_sensitive: Whether to use case-sensitive sorting for strings

        Returns:
            Sorted list of items
        """

        def sort_key(item):
            value = item.get(sort_field)
            if value is None:
                return ""
            if isinstance(value, str) and not case_sensitive:
                return value.lower()
            return value

        return sorted(items, key=sort_key, reverse=reverse)

    @staticmethod
    def sort_by_date(
        items: List[Dict[str, Any]],
        date_field: str,
        reverse: bool = True,
        default_date=None,
    ) -> List[Dict[str, Any]]:
        """Sort items by date field.

        Args:
            items: List of dictionaries to sort
            date_field: Field name containing date values
            reverse: Whether to sort newest first (default: True)
            default_date: Default date for items with missing date

        Returns:
            Sorted list of items
        """
        from datetime import datetime

        if default_date is None:
            default_date = datetime.min

        def date_sort_key(item):
            date_value = item.get(date_field)
            if date_value is None:
                return default_date
            if isinstance(date_value, str):
                try:
                    return datetime.fromisoformat(date_value.replace("Z", "+00:00"))
                except ValueError:
                    return default_date
            return date_value

        return sorted(items, key=date_sort_key, reverse=reverse)
