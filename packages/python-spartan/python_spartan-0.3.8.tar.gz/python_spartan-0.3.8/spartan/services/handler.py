"""Handler service for AWS Lambda function management.

This module provides comprehensive Lambda function management capabilities
including file creation, deletion, listing, and downloading.
"""

import base64
import csv
import difflib
import hashlib
import io
import json
import os
import re
import tempfile
import zipfile
from datetime import datetime
from typing import List, Optional, Union

import boto3
import requests
import yaml
from botocore.exceptions import ClientError, NoCredentialsError
from rich import box, print
from rich.console import Console
from rich.table import Table

from spartan.utils.filters import FilterUtility, SortUtility


class HandlerService:
    """Service for managing AWS Lambda functions and handler files."""

    def __init__(
        self,
        name: str = None,
        subscribe: str = None,
        publish: str = None,
        region: Optional[str] = None,
        profile: Optional[str] = None,
    ):
        """Initialize the HandlerService.

        Args:
            name: Name of the handler
            subscribe: SQS queue to subscribe to
            publish: SQS queue to publish to
            region: AWS region
            profile: AWS profile
        """
        self.name = name
        self.subscribe = subscribe
        self.publish = publish
        self.home_directory = os.path.dirname(
            os.path.dirname(os.path.abspath(__file__))
        )
        self.current_directory = os.getcwd()
        self.destination_folder = "handlers"

        # Only set file attributes if name is provided (for creation/deletion operations)
        if name:
            self.file_name = re.sub(r"\d", "", f"{self.name}.py").lower()
            self.file_path = os.path.join(
                self.current_directory, self.destination_folder, self.file_name
            )
            self.stub_folder = os.path.join(self.home_directory, "stubs", "handler")
            self.source_stub = self.determine_source_stub()

        # AWS client setup for listing operations
        try:
            session = (
                boto3.Session(profile_name=profile) if profile else boto3.Session()
            )
            self.lambda_client = session.client("lambda", region_name=region)
            self.console = Console()
        except NoCredentialsError:
            print(
                "[red]Error: AWS credentials not found. Please configure your AWS credentials.[/red]"
            )
            # Don't raise here as this might be used for file operations only
            self.lambda_client = None
            self.console = Console()
        except Exception as e:
            print(f"[red]Error initializing Lambda client: {e}[/red]")
            self.lambda_client = None
            self.console = Console()

    def determine_source_stub(self):
        """Determine the appropriate source stub for the handler."""
        if self.subscribe and self.publish:
            return os.path.join(self.stub_folder, "sqs_both.stub")
        elif self.subscribe:
            return (
                os.path.join(self.stub_folder, "sqs_subscribe.stub")
                if self.subscribe == "sqs"
                else os.path.join(self.stub_folder, "sns.stub")
            )
        elif self.publish:
            return os.path.join(self.stub_folder, "sqs_publish.stub")
        else:
            print("No specific option chosen.")
            return os.path.join(self.stub_folder, "default.stub")

    def create_handler_file(self):
        """Create a new handler file with appropriate configuration."""
        try:
            if not os.path.exists(
                os.path.join(self.current_directory, self.destination_folder)
            ):
                os.makedirs(
                    os.path.join(self.current_directory, self.destination_folder)
                )
                print(f"Created '{self.destination_folder}' folder.")

            if os.path.exists(self.file_path):
                with open(self.file_path, "r") as dest_file:
                    dest_content = dest_file.read()

                    if "{{ sqs_listen }}" in dest_content and self.subscribe:
                        print(
                            "Destination already has SQS subscription placeholder. Consider updating manually."
                        )
                        return

                    if "{{ sqs_publish }}" in dest_content and self.publish:
                        print(
                            "Destination already has SQS publishing placeholder. Consider updating manually."
                        )
                        return

            with open(self.source_stub, "r") as source_file:
                handler_stub_content = source_file.read()

            # Insert subscribe and publish code if necessary
            handler_stub_content = self.insert_subscribe_publish_code(
                handler_stub_content
            )

            with open(self.file_path, "w") as destination_file:
                destination_file.write(handler_stub_content)

            print(f"File '{self.file_path}' updated successfully.")

        except FileNotFoundError:
            print(f"File '{self.source_stub}' not found.")
        except Exception as e:
            print(f"An error occurred: {e}")

    def insert_subscribe_publish_code(self, handler_stub_content):
        """Insert SQS subscribe and publish code into handler stub content."""
        if self.subscribe or (self.subscribe and self.publish):
            handler_stub_content = self.insert_code_block(
                handler_stub_content, "sqs_listen.stub", "{{ sqs_listen }}"
            )

        if self.publish or (self.subscribe and self.publish):
            handler_stub_content = self.insert_code_block(
                handler_stub_content, "sqs_trigger.stub", "{{ sqs_trigger }}"
            )

        return handler_stub_content

    def insert_code_block(self, content, stub_name, placeholder):
        """Insert a code block into content at the specified placeholder."""
        # Construct the pattern string separately to avoid backslash in f-string curly braces
        pattern = r"^( *)" + re.escape(placeholder)
        match = re.search(pattern, content, re.MULTILINE)
        if match:
            indentation = match.group(1)
            with open(os.path.join(self.stub_folder, stub_name), "r") as insert_file:
                code_to_insert = insert_file.read()
            indented_code_to_insert = code_to_insert.replace("\n", "\n" + indentation)
            content = content.replace(placeholder, indented_code_to_insert, 1)
        return content

    def delete_handler_file(self):
        """Delete an existing handler file."""
        if os.path.exists(self.file_path):
            try:
                os.remove(self.file_path)
                print(f'File "{self.file_path}" deleted successfully.')
            except Exception as e:
                print(f"An error occurred while trying to delete the file: {e}")
        else:
            print(f'File "{self.file_path}" does not exist. No deletion needed.')

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

    def _format_date(self, date_obj: Optional[Union[datetime, str]]) -> str:
        """Format date object or string to readable format."""
        if not date_obj:
            return "N/A"
        try:
            if isinstance(date_obj, datetime):
                return date_obj.strftime("%Y-%m-%d %H:%M:%S UTC")
            else:
                # If it's a string, try to parse it first
                dt = datetime.fromisoformat(date_obj.replace("Z", "+00:00"))
                return dt.strftime("%Y-%m-%d %H:%M:%S UTC")
        except Exception:
            return str(date_obj)

    def list_handlers(  # noqa: C901
        self,
        output_format: str = "table",
        prefix_filter: Optional[str] = None,
        regex_match: Optional[str] = None,
        contains_filter: Optional[str] = None,
        runtime_filter: Optional[str] = None,
        sort_by: str = "name",
        sort_order: str = "asc",
        limit: Optional[int] = None,
        show_filters: bool = False,
        save_to: Optional[str] = None,
    ) -> None:
        """List all Lambda functions with advanced filtering.

        Args:
            output_format: Output format (table, json, yaml, markdown, csv)
            prefix_filter: Filter functions by name prefix
            regex_match: Filter functions by regex pattern
            contains_filter: Filter functions whose names contain a substring
            runtime_filter: Filter functions by runtime (e.g., python3.11)
            sort_by: Sort by field (name, runtime, memory, timeout, modified)
            sort_order: Sort order (asc, desc)
            limit: Limit the number of results shown
            show_filters: Show which filters were applied in the output
            save_to: Save the results to a file (.json, .yaml, .csv, etc.)
        """
        if not self.lambda_client:
            print(
                "[red]Error: Lambda client not initialized. Please check your AWS credentials.[/red]"
            )
            return

        try:
            output_format = self._validate_output_format(output_format)

            # Validate sort field
            valid_sort_fields = ["name", "runtime", "memory", "timeout", "modified"]
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

            # Validate all filters
            is_valid, error = FilterUtility.validate_all_filters(
                prefix_filter=prefix_filter, regex_filter=regex_match
            )
            if not is_valid:
                print(f"[red]{error}[/red]")
                return

            if output_format == "table":
                print("[blue]Fetching Lambda functions...[/blue]")

            # Get all functions using pagination
            functions = []
            paginator = self.lambda_client.get_paginator("list_functions")

            for page in paginator.paginate():
                functions.extend(page.get("Functions", []))

            if not functions:
                self._handle_no_functions_found(output_format)
                return

            # Process function data
            function_data = []
            for function in functions:
                function_info = {
                    "name": function.get("FunctionName", "N/A"),
                    "runtime": function.get("Runtime", "N/A"),
                    "memory": function.get("MemorySize", 0),
                    "timeout": function.get("Timeout", 0),
                    "modified": self._format_date(function.get("LastModified")),
                    "LastModified": function.get(
                        "LastModified"
                    ),  # Keep original for sorting
                    "description": function.get("Description", ""),
                    "handler": function.get("Handler", "N/A"),
                    "arn": function.get("FunctionArn", "N/A"),
                    "role": function.get("Role", "N/A"),
                    "package_type": function.get("PackageType", "N/A"),
                }
                function_data.append(function_info)

            # Apply filters using the filter utility
            filters = {}
            if prefix_filter:
                filters["prefix"] = {"field": "name", "value": prefix_filter}
            if regex_match:
                filters["regex"] = {"field": "name", "value": regex_match}
            if contains_filter:
                filters["contains"] = {
                    "field": "name",
                    "value": contains_filter,
                    "case_sensitive": "false",
                }
            if runtime_filter:
                filters["exact"] = {"field": "runtime", "value": runtime_filter}

            if filters:
                function_data = FilterUtility.apply_multiple_filters(
                    function_data, filters
                )

            # Apply sorting
            reverse = sort_order.lower() == "desc"
            if sort_by == "modified":
                function_data = SortUtility.sort_by_date(
                    function_data, "LastModified", reverse=reverse
                )
            elif sort_by == "name":
                function_data = SortUtility.sort_items(
                    function_data, "name", reverse=reverse, case_sensitive=False
                )
            elif sort_by == "runtime":
                function_data = SortUtility.sort_items(
                    function_data, "runtime", reverse=reverse, case_sensitive=False
                )
            elif sort_by == "memory":
                function_data = SortUtility.sort_items(
                    function_data, "memory", reverse=reverse
                )
            elif sort_by == "timeout":
                function_data = SortUtility.sort_items(
                    function_data, "timeout", reverse=reverse
                )

            # Apply limit
            if limit:
                function_data = function_data[:limit]

            # Check if any functions remain after filtering
            if not function_data:
                self._handle_no_functions_after_filter(
                    output_format,
                    prefix_filter,
                    regex_match,
                    contains_filter,
                    runtime_filter,
                )
                return

            # Prepare filter info for display/saving
            applied_filters = {}
            if prefix_filter:
                applied_filters["prefix"] = prefix_filter
            if regex_match:
                applied_filters["regex"] = regex_match
            if contains_filter:
                applied_filters["contains"] = contains_filter
            if runtime_filter:
                applied_filters["runtime"] = runtime_filter
            if limit:
                applied_filters["limit"] = str(limit)

            # Output in requested format
            if output_format == "csv":
                self._print_functions_csv(
                    function_data, show_filters, applied_filters, save_to
                )
            elif output_format == "table":
                self._print_functions_table(
                    function_data, show_filters, applied_filters, sort_by, sort_order
                )
            elif output_format == "json":
                output_data = {
                    "functions": function_data,
                    "count": len(function_data),
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
                    "functions": function_data,
                    "count": len(function_data),
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
                self._print_functions_markdown(
                    function_data,
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
            print(f"[red]Error listing handlers: {e}[/red]")

    def _print_functions_table(
        self,
        function_data: list,
        show_filters: bool = False,
        applied_filters: dict = None,
        sort_by: str = "name",
        sort_order: str = "asc",
    ) -> None:
        """Print functions in a formatted table."""
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
        table.add_column("Function Name", style="bright_blue", no_wrap=False)
        table.add_column("Runtime", style="green")
        table.add_column("Memory", style="yellow", justify="right")
        table.add_column("Timeout", style="yellow", justify="right")
        table.add_column("Modified", style="dim")

        for function in function_data:
            table.add_row(
                function["name"],
                function["runtime"],
                f"{function['memory']}MB",
                f"{function['timeout']}s",
                function["modified"],
            )

        self.console.print(
            f"🔧 [bold]Lambda Functions[/bold] ([bright_yellow]{len(function_data)}[/bright_yellow] found)"
        )
        if sort_by:
            self.console.print(f"[dim]Sorted by: {sort_by} ({sort_order})[/dim]")
        self.console.print()
        self.console.print(table)

    def _handle_no_functions_found(self, output_format: str) -> None:
        """Handle the case when no functions are found."""
        if output_format == "table":
            print("[yellow]No Lambda functions found in the current region.[/yellow]")
        elif output_format == "json":
            print(json.dumps({"functions": [], "count": 0}, indent=2))
        elif output_format == "yaml":
            print(yaml.dump({"functions": [], "count": 0}))
        elif output_format == "markdown":
            print("# Lambda Functions\n\nNo functions found in the current region.")
        elif output_format == "csv":
            print(
                "FunctionName,Runtime,Memory,Timeout,Modified,Description,Handler,ARN,Role,PackageType"
            )

    def _handle_no_functions_after_filter(
        self,
        output_format: str,
        prefix_filter: Optional[str],
        regex_match: Optional[str],
        contains_filter: Optional[str],
        runtime_filter: Optional[str],
    ) -> None:
        """Handle the case when no functions remain after filtering."""
        filter_desc = []
        if prefix_filter:
            filter_desc.append(f"prefix '{prefix_filter}'")
        if regex_match:
            filter_desc.append(f"regex '{regex_match}'")
        if contains_filter:
            filter_desc.append(f"contains '{contains_filter}'")
        if runtime_filter:
            filter_desc.append(f"runtime '{runtime_filter}'")

        filter_text = ", ".join(filter_desc)
        message = (
            f"No Lambda functions found matching the specified filters: {filter_text}"
        )

        if output_format == "table":
            print(f"[yellow]{message}[/yellow]")
        elif output_format == "json":
            print(
                json.dumps({"functions": [], "count": 0, "message": message}, indent=2)
            )
        elif output_format == "yaml":
            print(yaml.dump({"functions": [], "count": 0, "message": message}))
        elif output_format == "markdown":
            print(f"# Lambda Functions\n\n{message}")
        elif output_format == "csv":
            print("# " + message)
            print(
                "FunctionName,Runtime,Memory,Timeout,Modified,Description,Handler,ARN,Role,PackageType"
            )

    def _print_functions_csv(
        self,
        function_data: list,
        show_filters: bool = False,
        applied_filters: dict = None,
        save_to: Optional[str] = None,
    ) -> None:
        """Print functions in CSV format."""
        output = io.StringIO()
        writer = csv.writer(output)

        # Write header
        writer.writerow(
            [
                "FunctionName",
                "Runtime",
                "Memory",
                "Timeout",
                "Modified",
                "Description",
                "Handler",
                "ARN",
                "Role",
                "PackageType",
            ]
        )

        # Write data
        for function in function_data:
            writer.writerow(
                [
                    function["name"],
                    function["runtime"],
                    function["memory"],
                    function["timeout"],
                    function["modified"],
                    function["description"],
                    function["handler"],
                    function["arn"],
                    function["role"],
                    function["package_type"],
                ]
            )

        csv_content = output.getvalue()

        if save_to:
            self._save_to_file(csv_content, save_to)
        else:
            if show_filters and applied_filters:
                print(f"# Applied filters: {applied_filters}")
            print(csv_content.strip())

    def _print_functions_markdown(
        self,
        function_data: list,
        show_filters: bool = False,
        applied_filters: dict = None,
        sort_by: str = "name",
        sort_order: str = "asc",
        save_to: Optional[str] = None,
    ) -> None:
        """Print functions in markdown format."""
        output_lines = ["# Lambda Functions\n"]

        # Print filter information if any
        if show_filters and applied_filters:
            output_lines.append("## Applied Filters\n")
            for key, value in applied_filters.items():
                output_lines.append(f"- **{key.title()}:** `{value}`")
            output_lines.append("")

        output_lines.append("## Functions\n")
        output_lines.append(
            "| Function Name | Runtime | Memory | Timeout | Modified | Description |"
        )
        output_lines.append(
            "|---------------|---------|--------|---------|----------|-------------|"
        )

        for function in function_data:
            description = (
                function["description"].replace("|", "\\|")
                if function["description"]
                else "N/A"
            )
            output_lines.append(
                f"| {function['name']} | {function['runtime']} | {function['memory']}MB | {function['timeout']}s | {function['modified']} | {description} |"
            )

        output_lines.append(f"\n**Total:** {len(function_data)} function(s)")
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

    def download_function(
        self,
        function_name: str,
        version: str = "$LATEST",
        output_path: Optional[str] = None,
        extract: bool = False,
        check_integrity: bool = False,
        include_config: bool = False,
    ) -> bool:
        """Download Lambda function code and optionally configuration.

        Args:
            function_name: Name of the Lambda function
            version: Version or alias to download (default: $LATEST)
            output_path: Path to save the downloaded code
            extract: Whether to extract the ZIP file
            check_integrity: Whether to verify download integrity
            include_config: Whether to save function configuration

        Returns:
            bool: True if download successful, False otherwise
        """
        console = Console()

        try:
            # Get function details first
            function_response = self.lambda_client.get_function(
                FunctionName=function_name, Qualifier=version
            )

            function_config = function_response["Configuration"]
            code_location = function_response["Code"]["Location"]

            console.print(f"[blue]Downloading Lambda function: {function_name}[/blue]")
            console.print(f"[dim]Version: {version}[/dim]")
            console.print(
                f"[dim]Runtime: {function_config.get('Runtime', 'Unknown')}[/dim]"
            )
            console.print(
                f"[dim]Code Size: {function_config.get('CodeSize', 0)} bytes[/dim]"
            )

            # Determine output path
            if output_path is None:
                output_path = f"{function_name}_{version}.zip".replace("$", "latest")

            # Download the code
            response = requests.get(code_location, stream=True, timeout=30)
            response.raise_for_status()

            # Calculate hash if integrity check requested
            file_hash = None
            if check_integrity:
                hash_obj = hashlib.sha256()

            # Save the ZIP file
            with open(output_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        if check_integrity:
                            hash_obj.update(chunk)

            if check_integrity:
                file_hash = hash_obj.hexdigest()
                console.print(f"[dim]SHA256: {file_hash}[/dim]")

            console.print(f"[green]✓ Code downloaded to: {output_path}[/green]")

            # Extract if requested
            if extract:
                extract_dir = output_path.replace(".zip", "_extracted")
                with zipfile.ZipFile(output_path, "r") as zip_ref:
                    zip_ref.extractall(extract_dir)
                console.print(f"[green]✓ Code extracted to: {extract_dir}[/green]")

            # Save configuration if requested
            if include_config:
                config_path = output_path.replace(".zip", "_config.json")

                # Clean up configuration for saving
                config_to_save = {
                    "FunctionName": function_config["FunctionName"],
                    "FunctionArn": function_config["FunctionArn"],
                    "Runtime": function_config.get("Runtime"),
                    "Handler": function_config.get("Handler"),
                    "Description": function_config.get("Description", ""),
                    "Timeout": function_config.get("Timeout"),
                    "MemorySize": function_config.get("MemorySize"),
                    "Version": function_config.get("Version"),
                    "Environment": function_config.get("Environment", {}),
                    "VpcConfig": function_config.get("VpcConfig", {}),
                    "DeadLetterConfig": function_config.get("DeadLetterConfig", {}),
                    "TracingConfig": function_config.get("TracingConfig", {}),
                    "Layers": function_config.get("Layers", []),
                    "Role": function_config.get("Role"),
                    "CodeSha256": function_config.get("CodeSha256"),
                    "CodeSize": function_config.get("CodeSize"),
                    "LastModified": function_config.get("LastModified"),
                    "ReservedConcurrencyExecutions": function_config.get(
                        "ReservedConcurrencyExecutions"
                    ),
                    "Tags": function_config.get("Tags", {}),
                }

                if check_integrity:
                    config_to_save["DownloadInfo"] = {
                        "SHA256": file_hash,
                        "DownloadedAt": datetime.now().isoformat(),
                        "DownloadedVersion": version,
                    }

                with open(config_path, "w") as f:
                    json.dump(config_to_save, f, indent=2, default=str)

                console.print(f"[green]✓ Configuration saved to: {config_path}[/green]")

            # Display summary table
            summary_table = Table(title="Download Summary", box=box.SIMPLE)
            summary_table.add_column("Property", style="cyan")
            summary_table.add_column("Value", style="white")

            summary_table.add_row("Function Name", function_name)
            summary_table.add_row("Version", version)
            summary_table.add_row("Output Path", output_path)
            summary_table.add_row("Extracted", "Yes" if extract else "No")
            summary_table.add_row("Config Saved", "Yes" if include_config else "No")
            summary_table.add_row("Integrity Check", "Yes" if check_integrity else "No")
            if check_integrity and file_hash:
                summary_table.add_row("SHA256", file_hash[:16] + "...")

            console.print(summary_table)

            return True

        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            error_message = e.response["Error"]["Message"]

            if error_code == "ResourceNotFoundException":
                console.print(f"[red]✗ Function '{function_name}' not found[/red]")
            elif error_code == "InvalidParameterValueException":
                console.print(
                    f"[red]✗ Invalid version '{version}' for function '{function_name}'[/red]"
                )
            else:
                console.print(f"[red]✗ AWS Error ({error_code}): {error_message}[/red]")

            return False

        except Exception as e:
            console.print(f"[red]✗ Error downloading function: {e}[/red]")
            return False

    def invoke_function(
        self,
        function_name: str,
        payload: Optional[str] = None,
        invocation_type: str = "RequestResponse",
        log_type: str = "Tail",
        qualifier: str = "$LATEST",
    ) -> bool:
        """Invoke a Lambda function and capture the response.

        Args:
            function_name: Name of the Lambda function to invoke
            payload: JSON payload to send to the function
            invocation_type: RequestResponse (sync) or Event (async)
            log_type: None or Tail (include logs in response)
            qualifier: Version or alias to invoke

        Returns:
            bool: True if invocation successful, False otherwise
        """
        console = Console()

        try:
            console.print(f"[blue]Invoking Lambda function: {function_name}[/blue]")
            console.print(f"[dim]Qualifier: {qualifier}[/dim]")
            console.print(f"[dim]Invocation Type: {invocation_type}[/dim]")

            # Prepare payload
            payload_bytes = None
            if payload:
                try:
                    # Validate JSON
                    json.loads(payload)
                    payload_bytes = payload.encode("utf-8")
                    console.print(
                        f"[dim]Payload Size: {len(payload_bytes)} bytes[/dim]"
                    )
                except json.JSONDecodeError as e:
                    console.print(f"[red]✗ Invalid JSON payload: {e}[/red]")
                    return False

            # Invoke the function
            response = self.lambda_client.invoke(
                FunctionName=function_name,
                InvocationType=invocation_type,
                LogType=log_type,
                Payload=payload_bytes or b"{}",
                Qualifier=qualifier,
            )

            # Process response
            status_code = response["StatusCode"]

            # Create response table
            response_table = Table(title="Invocation Response", box=box.SIMPLE)
            response_table.add_column("Property", style="cyan")
            response_table.add_column("Value", style="white")

            response_table.add_row("Status Code", str(status_code))
            response_table.add_row(
                "Executed Version", response.get("ExecutedVersion", "N/A")
            )

            # Handle payload response
            payload_response = response.get("Payload")
            if payload_response:
                payload_data = payload_response.read().decode("utf-8")
                if payload_data:
                    response_table.add_row(
                        "Response Size", f"{len(payload_data)} bytes"
                    )
                    console.print(response_table)

                    # Display response payload
                    console.print("\n[cyan]Response Payload:[/cyan]")
                    try:
                        # Try to format as JSON
                        formatted_payload = json.dumps(
                            json.loads(payload_data), indent=2
                        )
                        console.print(formatted_payload)
                    except json.JSONDecodeError:
                        # If not JSON, display as-is
                        console.print(payload_data)
                else:
                    console.print(response_table)
                    console.print("\n[dim]No response payload[/dim]")

            # Handle logs
            log_result = response.get("LogResult")
            if log_result:
                log_data = base64.b64decode(log_result).decode("utf-8")
                console.print("\n[cyan]Function Logs:[/cyan]")
                console.print(log_data)

            # Handle function errors
            function_error = response.get("FunctionError")
            if function_error:
                console.print(f"\n[red]Function Error: {function_error}[/red]")
                return False

            # Success indicator
            if status_code == 200:
                console.print("\n[green]✓ Function invoked successfully[/green]")
            else:
                console.print(
                    f"\n[yellow]⚠ Function invoked with status: {status_code}[/yellow]"
                )

            return True

        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            error_message = e.response["Error"]["Message"]

            if error_code == "ResourceNotFoundException":
                console.print(f"[red]✗ Function '{function_name}' not found[/red]")
            elif error_code == "InvalidParameterValueException":
                console.print(
                    f"[red]✗ Invalid parameter for function '{function_name}': {error_message}[/red]"
                )
            elif error_code == "TooManyRequestsException":
                console.print(
                    f"[red]✗ Rate limit exceeded for function '{function_name}'[/red]"
                )
            else:
                console.print(f"[red]✗ AWS Error ({error_code}): {error_message}[/red]")

            return False

        except Exception as e:
            console.print(f"[red]✗ Error invoking function: {e}[/red]")
            return False

    def diff_function(
        self,
        function_name: str,
        local_path: str,
        qualifier: str = "$LATEST",
        ignore_metadata: bool = False,
        show_context: bool = True,
    ) -> bool:
        """Compare deployed Lambda function with local version.

        Args:
            function_name: Name of the Lambda function
            local_path: Path to local ZIP file or directory
            qualifier: Version or alias to compare against
            ignore_metadata: Skip metadata comparison
            show_context: Show context lines in diff

        Returns:
            bool: True if comparison completed, False on error
        """
        console = Console()

        try:
            console.print("[blue]Comparing deployed vs local version[/blue]")
            console.print(f"[dim]Function: {function_name}[/dim]")
            console.print(f"[dim]Qualifier: {qualifier}[/dim]")
            console.print(
                f"[dim]Local Path: {local_path}[/dim]"
            )  # Download deployed version to temp directory
            with tempfile.TemporaryDirectory() as temp_dir:
                deployed_zip = os.path.join(temp_dir, "deployed.zip")

                # Download deployed function
                success = self.download_function(
                    function_name=function_name,
                    version=qualifier,
                    output_path=deployed_zip,
                    extract=True,
                    check_integrity=False,
                    include_config=not ignore_metadata,
                )

                if not success:
                    return False

                deployed_extracted = deployed_zip.replace(".zip", "_extracted")

                # Prepare local path for comparison
                if os.path.isfile(local_path) and local_path.endswith(".zip"):
                    # Extract local ZIP
                    local_extracted = os.path.join(temp_dir, "local_extracted")
                    with zipfile.ZipFile(local_path, "r") as zip_ref:
                        zip_ref.extractall(local_extracted)
                elif os.path.isdir(local_path):
                    local_extracted = local_path
                else:
                    console.print(
                        "[red]✗ Local path must be a ZIP file or directory[/red]"
                    )
                    return False

                # Compare files
                differences_found = False
                console.print("\n[cyan]File Comparison Results:[/cyan]")

                # Get all files from both directories
                deployed_files = self._get_all_files(deployed_extracted)
                local_files = self._get_all_files(local_extracted)

                all_files = set(deployed_files.keys()) | set(local_files.keys())

                for file_path in sorted(all_files):
                    deployed_content = deployed_files.get(file_path, "")
                    local_content = local_files.get(file_path, "")

                    if deployed_content != local_content:
                        differences_found = True
                        console.print(f"\n[yellow]📄 {file_path}[/yellow]")

                        if not deployed_content:
                            console.print("  [green]+ File only exists locally[/green]")
                        elif not local_content:
                            console.print(
                                "  [red]- File only exists in deployed version[/red]"
                            )
                        else:
                            # Show diff
                            if show_context:
                                diff_lines = list(
                                    difflib.unified_diff(
                                        deployed_content.splitlines(keepends=True),
                                        local_content.splitlines(keepends=True),
                                        fromfile=f"deployed/{file_path}",
                                        tofile=f"local/{file_path}",
                                        n=3,
                                    )
                                )

                                if diff_lines:
                                    console.print("  [dim]Differences:[/dim]")
                                    for line in diff_lines[2:]:  # Skip the file headers
                                        line = line.rstrip()
                                        if line.startswith("+"):
                                            console.print(f"  [green]{line}[/green]")
                                        elif line.startswith("-"):
                                            console.print(f"  [red]{line}[/red]")
                                        elif line.startswith("@@"):
                                            console.print(f"  [blue]{line}[/blue]")
                                        else:
                                            console.print(f"  {line}")
                            else:
                                console.print("  [yellow]Files differ[/yellow]")

                # Compare metadata if not ignored
                if not ignore_metadata:
                    config_file = deployed_zip.replace(".zip", "_config.json")
                    if os.path.exists(config_file):
                        console.print("\n[cyan]Metadata Available:[/cyan]")
                        console.print(
                            f"[dim]Configuration saved to: {config_file}[/dim]"
                        )

                # Summary
                if differences_found:
                    console.print(
                        "\n[yellow]⚠ Differences found between deployed and local versions[/yellow]"
                    )
                else:
                    console.print(
                        "\n[green]✓ No differences found - versions match[/green]"
                    )

                return True

        except Exception as e:
            console.print(f"[red]✗ Error comparing versions: {e}[/red]")
            return False

    def _get_all_files(self, directory: str) -> dict:
        """Get all files from a directory recursively.

        Args:
            directory: Path to directory

        Returns:
            dict: Mapping of relative file paths to their content
        """
        files = {}
        for root, _, filenames in os.walk(directory):
            for filename in filenames:
                file_path = os.path.join(root, filename)
                relative_path = os.path.relpath(file_path, directory)

                try:
                    # Try to read as text first
                    with open(file_path, "r", encoding="utf-8") as f:
                        files[relative_path] = f.read()
                except UnicodeDecodeError:
                    # If binary, just note that it exists
                    files[relative_path] = f"<binary file: {filename}>"
                except Exception:
                    files[relative_path] = f"<unable to read: {filename}>"

        return files

    def upload_function(
        self,
        function_name: str,
        local_path: str,
        runtime: Optional[str] = None,
        handler: Optional[str] = None,
        role: Optional[str] = None,
        description: Optional[str] = None,
        timeout: Optional[int] = None,
        memory_size: Optional[int] = None,
        environment_vars: Optional[dict] = None,
        update_if_exists: bool = True,
        publish: bool = False,
        dry_run: bool = False,
    ) -> bool:
        """Upload/update a Lambda function from a local handler file or directory.

        Args:
            function_name: Name of the Lambda function
            local_path: Path to local file, directory, or ZIP file
            runtime: Lambda runtime (e.g., python3.11, nodejs18.x)
            handler: Function handler (e.g., index.handler, main.lambda_handler)
            role: IAM role ARN for the function
            description: Function description
            timeout: Function timeout in seconds (1-900)
            memory_size: Memory allocation in MB (128-10240)
            environment_vars: Environment variables as key-value pairs
            update_if_exists: Update function if it already exists
            publish: Publish a new version after upload
            dry_run: Show what would be uploaded without actually doing it

        Returns:
            bool: True if upload successful, False otherwise
        """
        console = Console()

        try:
            # Validate local path
            if not os.path.exists(local_path):
                console.print(f"[red]✗ Local path does not exist: {local_path}[/red]")
                return False

            console.print("[blue]Preparing Lambda function upload[/blue]")
            console.print(f"[dim]Function: {function_name}[/dim]")
            console.print(f"[dim]Local Path: {local_path}[/dim]")

            # Prepare ZIP file
            zip_bytes = None
            if os.path.isfile(local_path):
                if local_path.endswith(".zip"):
                    # Use existing ZIP file
                    with open(local_path, "rb") as f:
                        zip_bytes = f.read()
                    console.print("[dim]Using existing ZIP file[/dim]")
                else:
                    # Single file - create ZIP
                    zip_buffer = io.BytesIO()
                    with zipfile.ZipFile(
                        zip_buffer, "w", zipfile.ZIP_DEFLATED
                    ) as zip_file:
                        zip_file.write(local_path, os.path.basename(local_path))
                    zip_bytes = zip_buffer.getvalue()
                    console.print("[dim]Created ZIP from single file[/dim]")
            elif os.path.isdir(local_path):
                # Directory - create ZIP
                zip_buffer = io.BytesIO()
                with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
                    for root, _, files in os.walk(local_path):
                        for file in files:
                            file_path = os.path.join(root, file)
                            arc_name = os.path.relpath(file_path, local_path)
                            zip_file.write(file_path, arc_name)
                zip_bytes = zip_buffer.getvalue()
                console.print("[dim]Created ZIP from directory[/dim]")

            if not zip_bytes:
                console.print("[red]✗ Failed to create deployment package[/red]")
                return False

            zip_size = len(zip_bytes)
            console.print(
                f"[dim]Package Size: {zip_size:,} bytes ({zip_size/1024/1024:.2f} MB)[/dim]"
            )

            # Check if function exists
            function_exists = False
            existing_config = None
            try:
                existing_response = self.lambda_client.get_function(
                    FunctionName=function_name
                )
                function_exists = True
                existing_config = existing_response["Configuration"]
                console.print(
                    f"[yellow]Function '{function_name}' already exists[/yellow]"
                )
            except ClientError as e:
                if e.response["Error"]["Code"] == "ResourceNotFoundException":
                    console.print(
                        f"[dim]Function '{function_name}' does not exist - will create new[/dim]"
                    )
                else:
                    raise

            # Dry run - show what would happen
            if dry_run:
                console.print("\n[cyan]Dry Run - Changes that would be made:[/cyan]")

                if function_exists:
                    console.print(
                        f"[yellow]• Update existing function: {function_name}[/yellow]"
                    )
                    if existing_config:
                        if runtime and runtime != existing_config.get("Runtime"):
                            console.print(
                                f"  Runtime: {existing_config.get('Runtime')} → {runtime}"
                            )
                        if handler and handler != existing_config.get("Handler"):
                            console.print(
                                f"  Handler: {existing_config.get('Handler')} → {handler}"
                            )
                        if timeout and timeout != existing_config.get("Timeout"):
                            console.print(
                                f"  Timeout: {existing_config.get('Timeout')}s → {timeout}s"
                            )
                        if memory_size and memory_size != existing_config.get(
                            "MemorySize"
                        ):
                            console.print(
                                f"  Memory: {existing_config.get('MemorySize')}MB → {memory_size}MB"
                            )
                else:
                    console.print(
                        f"[green]• Create new function: {function_name}[/green]"
                    )
                    if runtime:
                        console.print(f"  Runtime: {runtime}")
                    if handler:
                        console.print(f"  Handler: {handler}")
                    if role:
                        console.print(f"  Role: {role}")

                console.print(f"[dim]• Upload {zip_size:,} bytes of code[/dim]")
                if publish:
                    console.print("[dim]• Publish new version[/dim]")

                console.print("\n[green]✓ Dry run completed - no changes made[/green]")
                return True

            # Function creation or update
            if function_exists:
                if not update_if_exists:
                    console.print(
                        "[red]✗ Function exists and update_if_exists=False[/red]"
                    )
                    return False

                # Update function code
                console.print("[blue]Updating function code...[/blue]")
                self.lambda_client.update_function_code(
                    FunctionName=function_name, ZipFile=zip_bytes, Publish=publish
                )

                # Update configuration if needed
                config_updates = {}
                if (
                    runtime
                    and existing_config
                    and runtime != existing_config.get("Runtime")
                ):
                    config_updates["Runtime"] = runtime
                if (
                    handler
                    and existing_config
                    and handler != existing_config.get("Handler")
                ):
                    config_updates["Handler"] = handler
                if description is not None:
                    config_updates["Description"] = description
                if timeout is not None:
                    config_updates["Timeout"] = timeout
                if memory_size is not None:
                    config_updates["MemorySize"] = memory_size
                if environment_vars is not None:
                    config_updates["Environment"] = {"Variables": environment_vars}

                if config_updates:
                    console.print("[blue]Updating function configuration...[/blue]")
                    config_updates["FunctionName"] = function_name
                    self.lambda_client.update_function_configuration(**config_updates)

                console.print(
                    f"[green]✓ Function '{function_name}' updated successfully[/green]"
                )

            else:
                # Create new function
                if not runtime:
                    console.print("[red]✗ Runtime is required for new functions[/red]")
                    return False
                if not handler:
                    console.print("[red]✗ Handler is required for new functions[/red]")
                    return False
                if not role:
                    console.print("[red]✗ Role ARN is required for new functions[/red]")
                    return False

                console.print("[blue]Creating new function...[/blue]")

                create_params = {
                    "FunctionName": function_name,
                    "Runtime": runtime,
                    "Role": role,
                    "Handler": handler,
                    "Code": {"ZipFile": zip_bytes},
                    "Publish": publish,
                }

                if description:
                    create_params["Description"] = description
                if timeout:
                    create_params["Timeout"] = timeout
                if memory_size:
                    create_params["MemorySize"] = memory_size
                if environment_vars:
                    create_params["Environment"] = {"Variables": environment_vars}

                self.lambda_client.create_function(**create_params)
                console.print(
                    f"[green]✓ Function '{function_name}' created successfully[/green]"
                )

            # Get final function info
            final_response = self.lambda_client.get_function(FunctionName=function_name)
            final_config = final_response["Configuration"]

            # Display summary table
            summary_table = Table(title="Upload Summary", box=box.SIMPLE)
            summary_table.add_column("Property", style="cyan")
            summary_table.add_column("Value", style="white")

            summary_table.add_row("Function Name", final_config["FunctionName"])
            summary_table.add_row("Runtime", final_config.get("Runtime", "N/A"))
            summary_table.add_row("Handler", final_config.get("Handler", "N/A"))
            summary_table.add_row(
                "Memory Size", f"{final_config.get('MemorySize', 0)} MB"
            )
            summary_table.add_row(
                "Timeout", f"{final_config.get('Timeout', 0)} seconds"
            )
            summary_table.add_row(
                "Code Size", f"{final_config.get('CodeSize', 0):,} bytes"
            )
            summary_table.add_row("Version", final_config.get("Version", "N/A"))
            summary_table.add_row(
                "Last Modified", self._format_date(final_config.get("LastModified"))
            )
            summary_table.add_row(
                "Status", "Created" if not function_exists else "Updated"
            )

            console.print(summary_table)

            return True

        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            error_message = e.response["Error"]["Message"]

            if error_code == "InvalidParameterValueException":
                console.print(f"[red]✗ Invalid parameter: {error_message}[/red]")
            elif error_code == "ResourceConflictException":
                console.print(f"[red]✗ Resource conflict: {error_message}[/red]")
            elif error_code == "CodeStorageExceededException":
                console.print(
                    f"[red]✗ Code storage limit exceeded: {error_message}[/red]"
                )
            elif error_code == "TooManyRequestsException":
                console.print(f"[red]✗ Rate limit exceeded: {error_message}[/red]")
            else:
                console.print(f"[red]✗ AWS Error ({error_code}): {error_message}[/red]")

            return False

        except Exception as e:
            console.print(f"[red]✗ Error uploading function: {e}[/red]")
            return False

    def get_environment_variables(  # noqa: C901
        self,
        function_name: str,
        format_type: str = "json",
        mask_secrets: bool = True,
        output_file: Optional[str] = None,
        single_key: Optional[str] = None,
    ) -> bool:
        """Get environment variables from a Lambda function in various formats.

        Args:
            function_name: Name of the Lambda function
            format_type: Output format (json, yaml, text, markdown, env)
            mask_secrets: Whether to mask values that look like secrets
            output_file: Optional file path to save output
            single_key: Optional specific key to retrieve

        Returns:
            bool: True if successful, False otherwise
        """
        if not self.lambda_client:
            print("[red]AWS Lambda client not available[/red]")
            return False

        try:
            # Validate format type
            valid_formats = ["json", "yaml", "text", "markdown", "env"]
            if format_type not in valid_formats:
                print(
                    f"[red]Invalid format type. Valid formats: {', '.join(valid_formats)}[/red]"
                )
                return False

            # Get function configuration
            response = self.lambda_client.get_function_configuration(
                FunctionName=function_name
            )

            # Extract environment variables
            env_vars = response.get("Environment", {}).get("Variables", {})

            if not env_vars:
                print(
                    "[yellow]No environment variables found for this function[/yellow]"
                )
                return True

            # Handle single key request
            if single_key:
                if single_key not in env_vars:
                    print(f"[red]Environment variable '{single_key}' not found[/red]")
                    print(
                        f"[dim]Available keys: {', '.join(sorted(env_vars.keys()))}[/dim]"
                    )
                    return False

                # Create single key dict
                env_vars = {single_key: env_vars[single_key]}
                print(f"[blue]Getting environment variable: {single_key}[/blue]")
            else:
                print(
                    f"[blue]Getting all environment variables ({len(env_vars)} found)[/blue]"
                )

            # Mask secrets if requested
            if mask_secrets:
                env_vars = self._mask_secret_values(env_vars)

            # Format output based on type
            if format_type == "json":
                output_content = self._format_env_as_json(env_vars)
            elif format_type == "yaml":
                output_content = self._format_env_as_yaml(env_vars)
            elif format_type == "text":
                output_content = self._format_env_as_text(env_vars)
            elif format_type == "markdown":
                output_content = self._format_env_as_markdown(env_vars, function_name)
            elif format_type == "env":
                output_content = self._format_env_as_dotenv(env_vars)
            else:
                output_content = self._format_env_as_json(env_vars)

            # Output to file or console
            if output_file:
                self._save_env_to_file(output_content, output_file)
                print(
                    f"[green]✅ Environment variables saved to: {output_file}[/green]"
                )
            else:
                print(output_content)

            # Show summary
            masked_count = sum(1 for v in env_vars.values() if "***" in str(v))
            print("\n[cyan]📊 Summary:[/cyan]")
            if single_key:
                print(f"  Retrieved variable: {single_key}")
                print(f"  Value masked: {'Yes' if masked_count > 0 else 'No'}")
            else:
                print(f"  Total variables: {len(env_vars)}")
                if mask_secrets and masked_count > 0:
                    print(f"  Masked secrets: {masked_count}")
            print(f"  Format: {format_type}")

            return True

        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            error_message = e.response["Error"]["Message"]

            if error_code == "ResourceNotFoundException":
                print(f"[red]Function '{function_name}' not found[/red]")
            elif error_code == "AccessDeniedException":
                print("[red]Access denied. Check your IAM permissions for Lambda[/red]")
            else:
                print(f"[red]AWS Error ({error_code}): {error_message}[/red]")
            return False

        except Exception as e:
            print(f"[red]Error getting environment variables: {e}[/red]")
            return False

    def _mask_secret_values(self, env_vars: dict) -> dict:
        """Mask values that look like secrets or sensitive data."""
        secret_patterns = [
            r"(?i).*key.*",
            r"(?i).*secret.*",
            r"(?i).*password.*",
            r"(?i).*token.*",
            r"(?i).*api.*key.*",
            r"(?i).*auth.*",
            r"(?i).*credential.*",
            r"(?i).*private.*",
        ]

        masked_vars = {}
        for key, value in env_vars.items():
            # Check if key matches secret patterns
            is_secret = any(re.match(pattern, key) for pattern in secret_patterns)

            # Also check for long base64-like strings or UUIDs
            if not is_secret and value:
                value_str = str(value)
                # Base64-like pattern (long string with alphanumeric + special chars)
                if len(value_str) > 20 and re.match(r"^[A-Za-z0-9+/=_-]+$", value_str):
                    is_secret = True
                # UUID pattern
                elif re.match(
                    r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$",
                    value_str,
                    re.IGNORECASE,
                ):
                    is_secret = True

            if is_secret and value:
                # Mask the value but show first/last few characters for identification
                value_str = str(value)
                if len(value_str) <= 8:
                    masked_vars[key] = "***"
                else:
                    masked_vars[key] = f"{value_str[:3]}***{value_str[-3:]}"
            else:
                masked_vars[key] = value

        return masked_vars

    def _format_env_as_json(self, env_vars: dict) -> str:
        """Format environment variables as JSON."""
        return json.dumps(env_vars, indent=2, sort_keys=True)

    def _format_env_as_yaml(self, env_vars: dict) -> str:
        """Format environment variables as YAML."""
        try:
            return yaml.dump(env_vars, default_flow_style=False, sort_keys=True)
        except ImportError:
            print("[yellow]PyYAML not installed, falling back to JSON format[/yellow]")
            return self._format_env_as_json(env_vars)

    def _format_env_as_text(self, env_vars: dict) -> str:
        """Format environment variables as plain text."""
        lines = []
        for key, value in sorted(env_vars.items()):
            lines.append(f"{key}={value}")
        return "\n".join(lines)

    def _format_env_as_markdown(self, env_vars: dict, function_name: str) -> str:
        """Format environment variables as Markdown table."""
        lines = [
            f"# Environment Variables: {function_name}",
            "",
            "| Variable | Value |",
            "|----------|-------|",
        ]

        for key, value in sorted(env_vars.items()):
            # Escape pipe characters in values for markdown
            escaped_value = str(value).replace("|", "\\|")
            lines.append(f"| {key} | {escaped_value} |")

        lines.extend(["", f"**Total Variables:** {len(env_vars)}"])

        return "\n".join(lines)

    def _format_env_as_dotenv(self, env_vars: dict) -> str:
        """Format environment variables as .env file format."""
        lines = []
        lines.append("# Environment variables exported from AWS Lambda")
        lines.append(f"# Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append("")

        for key, value in sorted(env_vars.items()):
            # Quote values that contain spaces or special characters
            value_str = str(value)
            if (
                re.search(r'[\s#"\'\\$`]', value_str)
                or value_str.startswith("=")
                or not value_str
            ):
                # Use double quotes and escape internal quotes
                escaped_value = value_str.replace('"', '\\"')
                lines.append(f'{key}="{escaped_value}"')
            else:
                lines.append(f"{key}={value_str}")

        return "\n".join(lines)

    def _save_env_to_file(self, content: str, file_path: str) -> None:
        """Save environment variables content to a file."""
        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(file_path), exist_ok=True)

            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)

        except Exception as e:
            print(f"[red]Error saving to file {file_path}: {e}[/red]")
            raise

    def set_environment_variables(  # noqa: C901
        self,
        function_name: str,
        key_value_pairs: List[str] = None,
        env_file_path: Optional[str] = None,
        overwrite: bool = False,
        dry_run: bool = False,
    ) -> bool:
        """Set or update environment variables for a Lambda function.

        Args:
            function_name: Name of the Lambda function
            key_value_pairs: List of KEY=value strings
            env_file_path: Path to .env or JSON file
            overwrite: Whether to replace all existing variables
            dry_run: Preview changes without applying

        Returns:
            bool: True if successful, False otherwise
        """
        if not self.lambda_client:
            print("[red]AWS Lambda client not available[/red]")
            return False

        try:
            print(
                f"[blue]Setting environment variables for Lambda function: {function_name}[/blue]"
            )

            # Get current environment variables
            current_response = self.lambda_client.get_function_configuration(
                FunctionName=function_name
            )
            current_env_vars = current_response.get("Environment", {}).get(
                "Variables", {}
            )

            # Parse new variables
            new_env_vars = {}

            # Parse key-value pairs from command line
            if key_value_pairs:
                for kv_pair in key_value_pairs:
                    if "=" not in kv_pair:
                        print(
                            f"[red]Invalid key-value pair format: '{kv_pair}'. Expected format: KEY=value[/red]"
                        )
                        return False

                    key, value = kv_pair.split("=", 1)  # Split only on first '='
                    key = key.strip()
                    value = value.strip()

                    if not key:
                        print(f"[red]Empty key in pair: '{kv_pair}'[/red]")
                        return False

                    new_env_vars[key] = value
                    print(f"[dim]Parsed inline: {key}={value}[/dim]")

            # Parse variables from file
            if env_file_path:
                file_vars = self._parse_env_file(env_file_path)
                if file_vars is None:
                    return False

                # Merge file variables with inline variables (inline takes precedence)
                for key, value in file_vars.items():
                    if key not in new_env_vars:  # Don't override inline variables
                        new_env_vars[key] = value

                print(
                    f"[dim]Loaded {len(file_vars)} variables from file: {env_file_path}[/dim]"
                )

            if not new_env_vars:
                print("[yellow]No environment variables to set[/yellow]")
                return True

            # Validate environment variable keys
            for key in new_env_vars.keys():
                if not self._validate_env_key(key):
                    print(f"[red]Invalid environment variable key: '{key}'[/red]")
                    print(
                        "[dim]Keys must start with a letter, contain only alphanumeric characters and underscores[/dim]"
                    )
                    return False

            # Calculate final environment variables
            if overwrite:
                final_env_vars = new_env_vars.copy()
                print(
                    f"[yellow]⚠️  Overwrite mode: Will replace all {len(current_env_vars)} existing variables[/yellow]"
                )
            else:
                final_env_vars = current_env_vars.copy()
                final_env_vars.update(new_env_vars)
                print(
                    f"[blue]Merge mode: Will merge with {len(current_env_vars)} existing variables[/blue]"
                )

            # Show what will change
            if dry_run:
                print("\n[cyan]🔍 Dry Run - Preview of Changes:[/cyan]")
                self._preview_env_changes(current_env_vars, final_env_vars, overwrite)
                print("\n[green]✓ Dry run completed - no changes made[/green]")
                return True

            # Show changes and ask for confirmation if not dry run
            changes_summary = self._get_env_changes_summary(
                current_env_vars, final_env_vars, overwrite
            )
            if changes_summary["total_changes"] > 0:
                print("\n[cyan]📋 Summary of Changes:[/cyan]")
                if changes_summary["new"] > 0:
                    print(f"  New variables: {changes_summary['new']}")
                if changes_summary["updated"] > 0:
                    print(f"  Updated variables: {changes_summary['updated']}")
                if changes_summary["deleted"] > 0:
                    print(f"  Deleted variables: {changes_summary['deleted']}")
                print(f"  Total variables after update: {len(final_env_vars)}")

            # Apply the changes
            print("\n[blue]Updating environment variables...[/blue]")
            self.lambda_client.update_function_configuration(
                FunctionName=function_name, Environment={"Variables": final_env_vars}
            )

            print(
                f"[green]✅ Successfully updated environment variables for '{function_name}'[/green]"
            )
            print(
                f"[cyan]📊 Final state: {len(final_env_vars)} environment variables[/cyan]"
            )

            return True

        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            error_message = e.response["Error"]["Message"]

            if error_code == "ResourceNotFoundException":
                print(f"[red]Function '{function_name}' not found[/red]")
            elif error_code == "InvalidParameterValueException":
                print(f"[red]Invalid parameter: {error_message}[/red]")
            elif error_code == "AccessDeniedException":
                print("[red]Access denied. Check your IAM permissions for Lambda[/red]")
            else:
                print(f"[red]AWS Error ({error_code}): {error_message}[/red]")
            return False

        except Exception as e:
            print(f"[red]Error setting environment variables: {e}[/red]")
            return False

    def _parse_env_file(self, file_path: str) -> Optional[dict]:
        """Parse environment variables from a .env or JSON file."""
        if not os.path.exists(file_path):
            print(f"[red]File not found: {file_path}[/red]")
            return None

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read().strip()

            # Try to parse as JSON first
            if file_path.endswith(".json") or content.startswith("{"):
                try:
                    data = json.loads(content)
                    if isinstance(data, dict):
                        # Convert all values to strings
                        return {str(k): str(v) for k, v in data.items()}
                    else:
                        print(
                            f"[red]JSON file must contain an object, not {type(data).__name__}[/red]"
                        )
                        return None
                except json.JSONDecodeError as e:
                    print(f"[red]Invalid JSON in file {file_path}: {e}[/red]")
                    return None

            # Parse as .env format
            env_vars = {}
            for line_num, line in enumerate(content.splitlines(), 1):
                line = line.strip()

                # Skip empty lines and comments
                if not line or line.startswith("#"):
                    continue

                # Parse KEY=value format
                if "=" not in line:
                    print(
                        f"[yellow]Warning: Skipping invalid line {line_num} in {file_path}: '{line}'[/yellow]"
                    )
                    continue

                key, value = line.split("=", 1)
                key = key.strip()
                value = value.strip()

                # Remove quotes from value if present
                if len(value) >= 2:
                    if (value.startswith('"') and value.endswith('"')) or (
                        value.startswith("'") and value.endswith("'")
                    ):
                        value = value[1:-1]
                        # Unescape quotes
                        value = value.replace('\\"', '"').replace("\\'", "'")

                if not key:
                    print(
                        f"[yellow]Warning: Skipping empty key on line {line_num} in {file_path}[/yellow]"
                    )
                    continue

                env_vars[key] = value

            return env_vars

        except Exception as e:
            print(f"[red]Error reading file {file_path}: {e}[/red]")
            return None

    def _validate_env_key(self, key: str) -> bool:
        """Validate environment variable key format."""
        import re

        # AWS Lambda environment variable names must start with a letter and contain only letters, numbers, and underscores
        return re.match(r"^[a-zA-Z][a-zA-Z0-9_]*$", key) is not None

    def _preview_env_changes(
        self, current_vars: dict, final_vars: dict, overwrite: bool
    ) -> None:
        """Preview environment variable changes."""
        if overwrite:
            print("  [red]➖ All existing variables will be removed[/red]")
            for key in sorted(current_vars.keys()):
                print(f"    [dim]{key}[/dim]")
            print()

        # Show new variables
        new_vars = {k: v for k, v in final_vars.items() if k not in current_vars}
        if new_vars:
            print("  [green]➕ New variables:[/green]")
            for key, value in sorted(new_vars.items()):
                # Mask potential secrets in preview
                display_value = self._mask_secret_values({key: value})[key]
                print(f"    {key}={display_value}")
            print()

        # Show updated variables
        updated_vars = {
            k: v
            for k, v in final_vars.items()
            if k in current_vars and current_vars[k] != v
        }
        if updated_vars:
            print("  [yellow]🔄 Updated variables:[/yellow]")
            for key, new_value in sorted(updated_vars.items()):
                old_value = current_vars[key]
                # Mask potential secrets in preview
                masked_vars = self._mask_secret_values(
                    {key: old_value, f"{key}_new": new_value}
                )
                display_old = masked_vars[key]
                display_new = masked_vars[f"{key}_new"]
                print(f"    {key}: {display_old} → {display_new}")
            print()

        # Show removed variables (only in overwrite mode)
        if overwrite:
            removed_vars = {
                k: v for k, v in current_vars.items() if k not in final_vars
            }
            if removed_vars:
                print("  [red]➖ Removed variables:[/red]")
                for key in sorted(removed_vars.keys()):
                    print(f"    {key}")
                print()

    def _get_env_changes_summary(
        self, current_vars: dict, final_vars: dict, overwrite: bool
    ) -> dict:
        """Get summary of environment variable changes."""
        new_vars = len([k for k in final_vars if k not in current_vars])
        updated_vars = len(
            [
                k
                for k in final_vars
                if k in current_vars and current_vars[k] != final_vars[k]
            ]
        )

        if overwrite:
            deleted_vars = len([k for k in current_vars if k not in final_vars])
        else:
            deleted_vars = 0

        return {
            "new": new_vars,
            "updated": updated_vars,
            "deleted": deleted_vars,
            "total_changes": new_vars + updated_vars + deleted_vars,
        }
