"""Example usage of the reusable filter utility for CLI list commands."""

from spartan.utils.filters import FilterUtility, SortUtility


def example_list_with_filters(  # noqa: C901
    items: list,
    prefix_filter: str = None,
    regex_filter: str = None,
    status_filter: str = None,
    sort_by: str = "name",
    output_format: str = "table",
) -> None:
    """Demonstrate how to implement a list command with filtering.

    This shows how any CLI list command can easily add filtering capabilities.
    """
    # 1. Validate filters
    valid_statuses = ["ACTIVE", "INACTIVE", "PENDING"]
    is_valid, error = FilterUtility.validate_all_filters(
        prefix_filter=prefix_filter,
        regex_filter=regex_filter,
        status_filter=status_filter,
        valid_statuses=valid_statuses,
    )
    if not is_valid:
        print(f"[red]{error}[/red]")
        return

    # 2. Validate sort field
    valid_sort_fields = ["name", "type", "status", "created"]
    is_valid, error = SortUtility.validate_sort_field(sort_by, valid_sort_fields)
    if not is_valid:
        print(f"[red]{error}[/red]")
        return

    # 3. Apply filters
    filters = {}
    if prefix_filter:
        filters["prefix"] = {"field": "name", "value": prefix_filter}
    if regex_filter:
        filters["regex"] = {"field": "name", "value": regex_filter}
    if status_filter:
        filters["status"] = {"field": "status", "value": status_filter}

    if filters:
        items = FilterUtility.apply_multiple_filters(items, filters)

    # 4. Apply sorting
    if sort_by == "created":
        items = SortUtility.sort_by_date(items, "created", reverse=True)
    else:
        case_sensitive = False if sort_by == "name" else True
        items = SortUtility.sort_items(items, sort_by, case_sensitive=case_sensitive)

    # 5. Generate filter summary for output
    filter_summary = FilterUtility.get_filter_summary(filters)
    if sort_by != "name":
        filter_summary.append(f"sorted by: {sort_by}")

    # 6. Output results with filter information
    if output_format == "table":
        print_table_with_filters(items, filter_summary)
    elif output_format == "json":
        output_json_with_metadata(items, filters, sort_by)
    # ... other output formats


def print_table_with_filters(items: list, filter_summary: list) -> None:
    """Print items in table format with filter information."""
    # Print table (implementation depends on your table library)
    print(f"Found {len(items)} items")

    # Show applied filters
    if filter_summary:
        filter_text = f" ({', '.join(filter_summary)})"
        print(f"Filters applied{filter_text}")


def output_json_with_metadata(items: list, filters: dict, sort_by: str) -> None:
    """Output items in JSON format with filter metadata."""
    import json

    # Extract filter values for metadata
    filter_metadata = {}
    for filter_type, config in filters.items():
        filter_metadata[filter_type] = config.get("value")

    output = {
        "items": items,
        "count": len(items),
        "filters": filter_metadata,
        "sort_by": sort_by,
    }

    print(json.dumps(output, indent=2, default=str))


# Example usage in a new CLI command:
# @app.command("list")
# def list_resources(
#     prefix: Optional[str] = typer.Option(None, "--prefix", help="Filter by name prefix"),
#     match: Optional[str] = typer.Option(None, "--match", help="Filter by regex pattern"),
#     status: Optional[str] = typer.Option(None, "--status", help="Filter by status"),
#     sort: str = typer.Option("name", "--sort", help="Sort by field"),
#     output: str = typer.Option("table", "--output", help="Output format"),
# ):
#     # Get your data
#     items = fetch_resources()
#
#     # Apply filters and sorting using the utility
#     example_list_with_filters(
#         items=items,
#         prefix_filter=prefix,
#         regex_filter=match,
#         status_filter=status,
#         sort_by=sort,
#         output_format=output
#     )
