"""S3 service for AWS S3 bucket and object management.

This module provides comprehensive S3 management capabilities
including listing buckets, listing objects, and managing S3 resources.
"""

import csv
import fnmatch
import io
import json
import os
from datetime import datetime
from typing import Optional

import boto3
import yaml
from botocore.exceptions import ClientError, NoCredentialsError
from rich import box, print
from rich.console import Console
from rich.table import Table

from spartan.utils.filters import FilterUtility, SortUtility


class S3Service:
    """Service for managing AWS S3 buckets and objects."""

    def __init__(
        self,
        region: Optional[str] = None,
        profile: Optional[str] = None,
    ):
        """Initialize the S3Service.

        Args:
            region: AWS region
            profile: AWS profile
        """
        # AWS client setup
        try:
            session = (
                boto3.Session(profile_name=profile) if profile else boto3.Session()
            )
            self.s3_client = session.client("s3", region_name=region)
            self.console = Console()
        except NoCredentialsError:
            print(
                "[red]Error: AWS credentials not found. Please configure your AWS credentials.[/red]"
            )
            self.s3_client = None
            self.console = Console()
        except Exception as e:
            print(f"[red]Error initializing S3 client: {e}[/red]")
            self.s3_client = None
            self.console = Console()

    def _validate_output_format(self, output_format: str) -> str:
        """Validate and normalize output format."""
        valid_formats = ["table", "json", "yaml", "markdown", "csv"]
        output_format = output_format.lower()
        if output_format not in valid_formats:
            print(
                f"[red]Invalid output format '{output_format}'. Valid formats: {', '.join(valid_formats)}[/red]"
            )
            raise ValueError(f"Invalid output format: {output_format}")
        return output_format

    def _format_date(self, date_obj: Optional[datetime]) -> str:
        """Format date object to readable format."""
        if not date_obj:
            return "N/A"
        try:
            if isinstance(date_obj, datetime):
                return date_obj.strftime("%Y-%m-%d %H:%M:%S UTC")
            else:
                return str(date_obj)
        except Exception:
            return str(date_obj)

    def _format_size(self, size_bytes: int, human_readable: bool = False) -> str:
        """Format file size."""
        if not human_readable:
            return str(size_bytes)

        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.1f} KB"
        elif size_bytes < 1024 * 1024 * 1024:
            return f"{size_bytes / (1024 * 1024):.1f} MB"
        else:
            return f"{size_bytes / (1024 * 1024 * 1024):.2f} GB"

    def _matches_pattern(self, filename: str, pattern: str) -> bool:
        """Check if filename matches the given pattern."""
        return fnmatch.fnmatch(filename, pattern) or fnmatch.fnmatch(
            filename.lower(), pattern.lower()
        )

    def _should_include_object(
        self, key: str, include_pattern: str = None, exclude_pattern: str = None
    ) -> bool:
        """Determine if an object should be included based on patterns."""
        filename = os.path.basename(key)

        # Check exclude pattern first
        if exclude_pattern and self._matches_pattern(filename, exclude_pattern):
            return False

        # Check include pattern
        if include_pattern and not self._matches_pattern(filename, include_pattern):
            return False

        return True

    def list_buckets(  # noqa: C901
        self,
        output_format: str = "table",
        prefix_filter: Optional[str] = None,
        regex_match: Optional[str] = None,
        contains_filter: Optional[str] = None,
        sort_by: str = "name",
        sort_order: str = "asc",
        limit: Optional[int] = None,
        show_filters: bool = False,
        save_to: Optional[str] = None,
    ) -> None:
        """List all S3 buckets with filtering options.

        Args:
            output_format: Output format (table, json, yaml, markdown, csv)
            prefix_filter: Filter buckets by name prefix
            regex_match: Filter buckets by regex pattern
            contains_filter: Filter buckets by substring
            sort_by: Sort by field (name, creation_date)
            sort_order: Sort order (asc, desc)
            limit: Limit the number of results shown
            show_filters: Show which filters were applied in the output
            save_to: Save the results to a file (.json, .yaml, .csv, etc.)
        """
        if not self.s3_client:
            print(
                "[red]Error: S3 client not initialized. Please check your AWS credentials.[/red]"
            )
            return

        try:
            output_format = self._validate_output_format(output_format)

            # Validate sort field
            valid_sort_fields = ["name", "creation_date"]
            is_valid, error = SortUtility.validate_sort_field(
                sort_by, valid_sort_fields
            )
            if not is_valid:
                print(f"[red]{error}[/red]")
                return

            # Validate sort order
            if sort_order.lower() not in ["asc", "desc"]:
                print(
                    f"[red]Invalid sort order '{sort_order}'. Valid options: asc, desc[/red]"
                )
                return

            # Validate limit
            if limit is not None and limit <= 0:
                print(f"[red]Limit must be a positive integer, got: {limit}[/red]")
                return

            if output_format == "table":
                print("[blue]Fetching S3 buckets...[/blue]")

            # Get all buckets
            response = self.s3_client.list_buckets()
            buckets = response.get("Buckets", [])

            if not buckets:
                self._handle_no_buckets_found(output_format)
                return

            # Process bucket data
            bucket_data = []
            for bucket in buckets:
                bucket_info = {
                    "name": bucket.get("Name", "N/A"),
                    "creation_date": self._format_date(bucket.get("CreationDate")),
                    "CreationDate": bucket.get(
                        "CreationDate"
                    ),  # Keep original for sorting
                }
                bucket_data.append(bucket_info)

            # Apply filters
            original_count = len(bucket_data)
            if prefix_filter:
                bucket_data = FilterUtility.apply_prefix_filter(
                    bucket_data, "name", prefix_filter
                )
            if regex_match:
                bucket_data = FilterUtility.apply_regex_filter(
                    bucket_data, "name", regex_match
                )
            if contains_filter:
                bucket_data = FilterUtility.apply_contains_filter(
                    bucket_data, "name", contains_filter, case_sensitive=False
                )

            # Check if any buckets remain after filtering
            if not bucket_data and (prefix_filter or regex_match or contains_filter):
                self._handle_no_buckets_found(output_format, filtered=True)
                return

            # Apply sorting
            reverse = sort_order.lower() == "desc"
            if sort_by == "creation_date":
                bucket_data = SortUtility.sort_by_date(
                    bucket_data, "CreationDate", reverse=reverse
                )
            elif sort_by == "name":
                bucket_data = SortUtility.sort_items(
                    bucket_data, "name", reverse=reverse, case_sensitive=False
                )

            # Apply limit
            if limit:
                bucket_data = bucket_data[:limit]

            # Prepare filter info for display/saving
            applied_filters = {}
            if prefix_filter:
                applied_filters["prefix"] = prefix_filter
            if regex_match:
                applied_filters["regex_match"] = regex_match
            if contains_filter:
                applied_filters["contains"] = contains_filter
            if limit:
                applied_filters["limit"] = str(limit)

            # Add result summary
            if prefix_filter or regex_match or contains_filter:
                applied_filters["filtered_from"] = str(original_count)

            # Output in requested format
            if output_format == "csv":
                self._print_buckets_csv(
                    bucket_data, show_filters, applied_filters, save_to
                )
            elif output_format == "table":
                self._print_buckets_table(
                    bucket_data, show_filters, applied_filters, sort_by, sort_order
                )
            elif output_format == "json":
                output_data = {
                    "buckets": bucket_data,
                    "count": len(bucket_data),
                    "sort": {"by": sort_by, "order": sort_order},
                }
                if show_filters and applied_filters:
                    output_data["applied_filters"] = applied_filters

                output_str = json.dumps(output_data, indent=2, default=str)
                if save_to:
                    self._save_to_file(output_str, save_to)
                else:
                    print(output_str)
            elif output_format == "yaml":
                output_data = {
                    "buckets": bucket_data,
                    "count": len(bucket_data),
                    "sort": {"by": sort_by, "order": sort_order},
                }
                if show_filters and applied_filters:
                    output_data["applied_filters"] = applied_filters

                output_str = yaml.dump(output_data, default_flow_style=False)
                if save_to:
                    self._save_to_file(output_str, save_to)
                else:
                    print(output_str)
            elif output_format == "markdown":
                self._print_buckets_markdown(
                    bucket_data,
                    show_filters,
                    applied_filters,
                    sort_by,
                    sort_order,
                    save_to,
                )

        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            error_message = e.response["Error"]["Message"]
            print(f"[red]AWS Error ({error_code}): {error_message}[/red]")
        except Exception as e:
            print(f"[red]Error listing buckets: {e}[/red]")

    def _print_buckets_table(
        self,
        bucket_data: list,
        show_filters: bool = False,
        applied_filters: dict = None,
        sort_by: str = "name",
        sort_order: str = "asc",
    ) -> None:
        """Print buckets in a formatted table."""
        # Show filters if requested
        if show_filters and applied_filters:
            self.console.print(f"[dim]Applied filters: {applied_filters}[/dim]")
            self.console.print()

        table = Table(
            show_header=True,
            header_style="bold cyan",
            box=box.SIMPLE,
            border_style="dim",
        )
        table.add_column("Bucket Name", style="bright_blue", no_wrap=False)
        table.add_column("Creation Date", style="dim")

        for bucket in bucket_data:
            table.add_row(
                bucket["name"],
                bucket["creation_date"],
            )

        self.console.print(
            f"📦 [bold]S3 Buckets[/bold] ([bright_yellow]{len(bucket_data)}[/bright_yellow] found)"
        )
        if sort_by:
            self.console.print(f"[dim]Sorted by: {sort_by} ({sort_order})[/dim]")
        self.console.print()
        self.console.print(table)

    def _handle_no_buckets_found(
        self, output_format: str, filtered: bool = False
    ) -> None:
        """Handle the case when no buckets are found."""
        if filtered:
            message = "No S3 buckets match the specified filters."
            json_message = {
                "buckets": [],
                "count": 0,
                "message": "No buckets match the filters",
            }
            yaml_message = {
                "buckets": [],
                "count": 0,
                "message": "No buckets match the filters",
            }
            markdown_message = "# S3 Buckets\n\nNo buckets match the specified filters."
        else:
            message = "No S3 buckets found in the current account."
            json_message = {"buckets": [], "count": 0, "message": "No buckets found"}
            yaml_message = {"buckets": [], "count": 0, "message": "No buckets found"}
            markdown_message = (
                "# S3 Buckets\n\nNo buckets found in the current account."
            )

        if output_format == "table":
            print(f"[yellow]{message}[/yellow]")
        elif output_format == "json":
            print(json.dumps(json_message, indent=2))
        elif output_format == "yaml":
            print(yaml.dump(yaml_message))
        elif output_format == "markdown":
            print(markdown_message)
        elif output_format == "csv":
            print("bucket_name,creation_date")

    def _print_buckets_csv(
        self,
        bucket_data: list,
        show_filters: bool = False,
        applied_filters: dict = None,
        save_to: Optional[str] = None,
    ) -> None:
        """Print buckets in CSV format."""
        output = io.StringIO()
        writer = csv.writer(output)

        # Write header
        writer.writerow(["bucket_name", "creation_date"])

        # Write data
        for bucket in bucket_data:
            writer.writerow([bucket["name"], bucket["creation_date"]])

        csv_content = output.getvalue()

        if save_to:
            self._save_to_file(csv_content, save_to)
        else:
            if show_filters and applied_filters:
                print(f"# Applied filters: {applied_filters}")
            print(csv_content.strip())

    def _print_buckets_markdown(
        self,
        bucket_data: list,
        show_filters: bool = False,
        applied_filters: dict = None,
        sort_by: str = "name",
        sort_order: str = "asc",
        save_to: Optional[str] = None,
    ) -> None:
        """Print buckets in markdown format."""
        output_lines = ["# S3 Buckets\n"]

        # Print filter information if any
        if show_filters and applied_filters:
            output_lines.append("## Applied Filters\n")
            for key, value in applied_filters.items():
                output_lines.append(f"- **{key.title()}:** `{value}`")
            output_lines.append("")

        output_lines.append("## Buckets\n")
        output_lines.append("| Bucket Name | Creation Date |")
        output_lines.append("|-------------|---------------|")

        for bucket in bucket_data:
            output_lines.append(f"| {bucket['name']} | {bucket['creation_date']} |")

        output_lines.append(f"\n**Total:** {len(bucket_data)} bucket(s)")
        if sort_by:
            output_lines.append(f"**Sorted by:** {sort_by} ({sort_order})")

        markdown_content = "\n".join(output_lines)

        if save_to:
            self._save_to_file(markdown_content, save_to)
        else:
            print(markdown_content)

    def _save_to_file(self, content: str, file_path: str) -> None:
        """Save content to a file."""
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"[green]Results saved to: {file_path}[/green]")
        except Exception as e:
            print(f"[red]Error saving to file {file_path}: {e}[/red]")

    def list_objects(
        self,
        bucket_name: str,
        prefix_filter: Optional[str] = None,
        include_pattern: Optional[str] = None,
        exclude_pattern: Optional[str] = None,
        sort_by: str = "key",
        sort_order: str = "asc",
        output_format: str = "table",
        limit: Optional[int] = None,
        human_readable: bool = False,
        show_filters: bool = False,
        save_to: Optional[str] = None,
    ) -> None:
        """List objects in an S3 bucket."""
        if not self.s3_client:
            print("[red]Error: S3 client not initialized.[/red]")
            return

        try:
            output_format = self._validate_output_format(output_format)

            # List objects
            paginator = self.s3_client.get_paginator("list_objects_v2")
            page_iterator = paginator.paginate(
                Bucket=bucket_name, Prefix=prefix_filter or ""
            )

            objects = []
            for page in page_iterator:
                objects.extend(page.get("Contents", []))

            if not objects:
                print(f"[yellow]No objects found in bucket '{bucket_name}'[/yellow]")
                return

            # Filter objects
            filtered_objects = []
            for obj in objects:
                key = obj["Key"]
                if self._should_include_object(key, include_pattern, exclude_pattern):
                    filtered_objects.append(
                        {
                            "key": key,
                            "size": obj["Size"],
                            "modified": self._format_date(obj["LastModified"]),
                            "storage_class": obj.get("StorageClass", "STANDARD"),
                            "size_formatted": self._format_size(
                                obj["Size"], human_readable
                            ),
                        }
                    )

            # Sort objects
            if sort_by == "size":
                filtered_objects.sort(
                    key=lambda x: x["size"], reverse=(sort_order == "desc")
                )
            elif sort_by == "modified":
                filtered_objects.sort(
                    key=lambda x: x["modified"], reverse=(sort_order == "desc")
                )
            else:  # key
                filtered_objects.sort(
                    key=lambda x: x["key"], reverse=(sort_order == "desc")
                )

            # Apply limit
            if limit:
                filtered_objects = filtered_objects[:limit]

            # Output results
            if output_format == "table":
                self._print_objects_table(filtered_objects, bucket_name, human_readable)
            elif output_format == "json":
                output_data = {
                    "objects": filtered_objects,
                    "count": len(filtered_objects),
                }
                print(json.dumps(output_data, indent=2, default=str))

        except ClientError as e:
            print(f"[red]AWS Error: {e}[/red]")
        except Exception as e:
            print(f"[red]Error listing objects: {e}[/red]")

    def _print_objects_table(
        self, objects: list, bucket_name: str, human_readable: bool
    ) -> None:
        """Print objects in table format."""
        table = Table(
            show_header=True,
            header_style="bold cyan",
            box=box.SIMPLE,
            border_style="dim",
        )
        table.add_column("Key", style="bright_blue")
        table.add_column("Size", justify="right")
        table.add_column("Modified", style="dim")
        table.add_column("Storage Class", style="green")

        for obj in objects:
            table.add_row(
                obj["key"],
                obj["size_formatted"] if human_readable else str(obj["size"]),
                obj["modified"],
                obj["storage_class"],
            )

        self.console.print(
            f"📦 [bold]S3 Objects in '{bucket_name}'[/bold] ([bright_yellow]{len(objects)}[/bright_yellow] found)"
        )
        self.console.print(table)

    def create_bucket(
        self,
        bucket_name: str,
        region: Optional[str] = None,
        public_read: bool = False,
        versioning: bool = False,
        dry_run: bool = False,
    ) -> None:
        """Create an S3 bucket."""
        if not self.s3_client:
            print("[red]Error: S3 client not initialized.[/red]")
            return

        try:
            if dry_run:
                print(f"[yellow][DRY RUN] Would create bucket: {bucket_name}[/yellow]")
                return

            # Create bucket
            if region and region != "us-east-1":
                self.s3_client.create_bucket(
                    Bucket=bucket_name,
                    CreateBucketConfiguration={"LocationConstraint": region},
                )
            else:
                self.s3_client.create_bucket(Bucket=bucket_name)

            print(f"[green]✓ Bucket '{bucket_name}' created successfully[/green]")

            # Configure versioning if requested
            if versioning:
                self.s3_client.put_bucket_versioning(
                    Bucket=bucket_name, VersioningConfiguration={"Status": "Enabled"}
                )
                print(f"[green]✓ Versioning enabled for bucket '{bucket_name}'[/green]")

        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            if error_code == "BucketAlreadyExists":
                print(f"[red]Error: Bucket '{bucket_name}' already exists[/red]")
            else:
                print(f"[red]AWS Error: {e}[/red]")
        except Exception as e:
            print(f"[red]Error creating bucket: {e}[/red]")

    def delete_bucket(
        self,
        bucket_name: str,
        force: bool = False,
        dry_run: bool = False,
    ) -> None:
        """Delete an S3 bucket."""
        if not self.s3_client:
            print("[red]Error: S3 client not initialized.[/red]")
            return

        try:
            if dry_run:
                print(f"[yellow][DRY RUN] Would delete bucket: {bucket_name}[/yellow]")
                return

            # Check if bucket has objects
            if force:
                # Delete all objects first
                paginator = self.s3_client.get_paginator("list_objects_v2")
                pages = paginator.paginate(Bucket=bucket_name)

                for page in pages:
                    objects = page.get("Contents", [])
                    if objects:
                        delete_keys = [{"Key": obj["Key"]} for obj in objects]
                        self.s3_client.delete_objects(
                            Bucket=bucket_name, Delete={"Objects": delete_keys}
                        )
                        print(f"[yellow]Deleted {len(delete_keys)} objects[/yellow]")

            # Delete bucket
            self.s3_client.delete_bucket(Bucket=bucket_name)
            print(f"[green]✓ Bucket '{bucket_name}' deleted successfully[/green]")

        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            if error_code == "BucketNotEmpty":
                print(
                    f"[red]Error: Bucket '{bucket_name}' is not empty. Use --force to delete all objects[/red]"
                )
            elif error_code == "NoSuchBucket":
                print(f"[red]Error: Bucket '{bucket_name}' does not exist[/red]")
            else:
                print(f"[red]AWS Error: {e}[/red]")
        except Exception as e:
            print(f"[red]Error deleting bucket: {e}[/red]")

    def upload_objects(
        self,
        local_path: str,
        bucket_name: str,
        object_key: Optional[str] = None,
        recursive: bool = False,
        include_pattern: Optional[str] = None,
        exclude_pattern: Optional[str] = None,
        public_read: bool = False,
        storage_class: str = "STANDARD",
        dry_run: bool = False,
    ) -> None:
        """Upload files to S3."""
        if not self.s3_client:
            print("[red]Error: S3 client not initialized.[/red]")
            return

        try:
            if os.path.isfile(local_path):
                # Single file upload
                key = object_key or os.path.basename(local_path)
                if dry_run:
                    print(
                        f"[yellow][DRY RUN] Would upload: {local_path} -> s3://{bucket_name}/{key}[/yellow]"
                    )
                else:
                    self.s3_client.upload_file(local_path, bucket_name, key)
                    print(
                        f"[green]✓ Uploaded: {local_path} -> s3://{bucket_name}/{key}[/green]"
                    )

            elif os.path.isdir(local_path) and recursive:
                # Directory upload
                for root, _dirs, files in os.walk(local_path):
                    for file in files:
                        file_path = os.path.join(root, file)
                        if self._should_include_object(
                            file, include_pattern, exclude_pattern
                        ):
                            relative_path = os.path.relpath(file_path, local_path)
                            key = (
                                f"{object_key}/{relative_path}"
                                if object_key
                                else relative_path
                            )

                            if dry_run:
                                print(
                                    f"[yellow][DRY RUN] Would upload: {file_path} -> s3://{bucket_name}/{key}[/yellow]"
                                )
                            else:
                                self.s3_client.upload_file(file_path, bucket_name, key)
                                print(
                                    f"[green]✓ Uploaded: {file_path} -> s3://{bucket_name}/{key}[/green]"
                                )
            else:
                print(
                    f"[red]Error: Path '{local_path}' is not a file or use --recursive for directories[/red]"
                )

        except ClientError as e:
            print(f"[red]AWS Error: {e}[/red]")
        except Exception as e:
            print(f"[red]Error uploading: {e}[/red]")

    def download_objects(
        self,
        bucket_name: str,
        object_key: Optional[str] = None,
        local_path: str = ".",
        prefix_filter: Optional[str] = None,
        include_pattern: Optional[str] = None,
        exclude_pattern: Optional[str] = None,
        overwrite: bool = False,
        dry_run: bool = False,
    ) -> None:
        """Download objects from S3."""
        if not self.s3_client:
            print("[red]Error: S3 client not initialized.[/red]")
            return

        try:
            if object_key:
                # Single object download
                local_file = os.path.join(local_path, os.path.basename(object_key))
                if dry_run:
                    print(
                        f"[yellow][DRY RUN] Would download: s3://{bucket_name}/{object_key} -> {local_file}[/yellow]"
                    )
                else:
                    os.makedirs(os.path.dirname(local_file), exist_ok=True)
                    self.s3_client.download_file(bucket_name, object_key, local_file)
                    print(
                        f"[green]✓ Downloaded: s3://{bucket_name}/{object_key} -> {local_file}[/green]"
                    )
            else:
                # Multiple objects download
                paginator = self.s3_client.get_paginator("list_objects_v2")
                pages = paginator.paginate(
                    Bucket=bucket_name, Prefix=prefix_filter or ""
                )

                for page in pages:
                    for obj in page.get("Contents", []):
                        key = obj["Key"]
                        if self._should_include_object(
                            key, include_pattern, exclude_pattern
                        ):
                            local_file = os.path.join(local_path, key)

                            if not overwrite and os.path.exists(local_file):
                                print(
                                    f"[yellow]Skipping existing file: {local_file}[/yellow]"
                                )
                                continue

                            if dry_run:
                                print(
                                    f"[yellow][DRY RUN] Would download: s3://{bucket_name}/{key} -> {local_file}[/yellow]"
                                )
                            else:
                                os.makedirs(os.path.dirname(local_file), exist_ok=True)
                                self.s3_client.download_file(
                                    bucket_name, key, local_file
                                )
                                print(
                                    f"[green]✓ Downloaded: s3://{bucket_name}/{key} -> {local_file}[/green]"
                                )

        except ClientError as e:
            print(f"[red]AWS Error: {e}[/red]")
        except Exception as e:
            print(f"[red]Error downloading: {e}[/red]")

    def delete_objects(
        self,
        bucket_name: str,
        object_key: Optional[str] = None,
        prefix_filter: Optional[str] = None,
        include_pattern: Optional[str] = None,
        exclude_pattern: Optional[str] = None,
        force: bool = False,
        dry_run: bool = False,
    ) -> None:
        """Delete objects from S3."""
        if not self.s3_client:
            print("[red]Error: S3 client not initialized.[/red]")
            return

        try:
            if object_key:
                # Single object deletion
                if dry_run:
                    print(
                        f"[yellow][DRY RUN] Would delete: s3://{bucket_name}/{object_key}[/yellow]"
                    )
                else:
                    self.s3_client.delete_object(Bucket=bucket_name, Key=object_key)
                    print(f"[green]✓ Deleted: s3://{bucket_name}/{object_key}[/green]")
            else:
                # Multiple objects deletion
                paginator = self.s3_client.get_paginator("list_objects_v2")
                pages = paginator.paginate(
                    Bucket=bucket_name, Prefix=prefix_filter or ""
                )

                objects_to_delete = []
                for page in pages:
                    for obj in page.get("Contents", []):
                        key = obj["Key"]
                        if self._should_include_object(
                            key, include_pattern, exclude_pattern
                        ):
                            objects_to_delete.append({"Key": key})

                if not objects_to_delete:
                    print("[yellow]No objects found to delete[/yellow]")
                    return

                if not force and not dry_run:
                    confirm = input(f"Delete {len(objects_to_delete)} objects? (y/N): ")
                    if confirm.lower() != "y":
                        print("[yellow]Deletion cancelled[/yellow]")
                        return

                if dry_run:
                    for obj in objects_to_delete:
                        print(
                            f"[yellow][DRY RUN] Would delete: s3://{bucket_name}/{obj['Key']}[/yellow]"
                        )
                else:
                    # Delete in batches of 1000 (AWS limit)
                    for i in range(0, len(objects_to_delete), 1000):
                        batch = objects_to_delete[i : i + 1000]
                        self.s3_client.delete_objects(
                            Bucket=bucket_name, Delete={"Objects": batch}
                        )
                        print(f"[green]✓ Deleted batch of {len(batch)} objects[/green]")

        except ClientError as e:
            print(f"[red]AWS Error: {e}[/red]")
        except Exception as e:
            print(f"[red]Error deleting objects: {e}[/red]")

    def copy_object(
        self,
        source_bucket: str,
        source_key: str,
        dest_bucket: str,
        dest_key: str,
        storage_class: Optional[str] = None,
        dry_run: bool = False,
    ) -> None:
        """Copy an object within S3."""
        if not self.s3_client:
            print("[red]Error: S3 client not initialized.[/red]")
            return

        try:
            if dry_run:
                print(
                    f"[yellow][DRY RUN] Would copy: s3://{source_bucket}/{source_key} -> s3://{dest_bucket}/{dest_key}[/yellow]"
                )
                return

            copy_source = {"Bucket": source_bucket, "Key": source_key}
            extra_args = {}
            if storage_class:
                extra_args["StorageClass"] = storage_class

            self.s3_client.copy_object(
                CopySource=copy_source, Bucket=dest_bucket, Key=dest_key, **extra_args
            )

            print(
                f"[green]✓ Copied: s3://{source_bucket}/{source_key} -> s3://{dest_bucket}/{dest_key}[/green]"
            )

        except ClientError as e:
            print(f"[red]AWS Error: {e}[/red]")
        except Exception as e:
            print(f"[red]Error copying object: {e}[/red]")
