"""Layer service for managing AWS Lambda layers."""

import json
import os
import urllib.request
import zipfile
from pathlib import Path
from typing import Any, Dict, Optional

import boto3
import yaml
from botocore.exceptions import ClientError, NoCredentialsError
from rich import box, print
from rich.console import Console
from rich.table import Table


class LayerService:
    """Service class for managing AWS Lambda layers."""

    def __init__(self):
        """Initialize the LayerService with AWS Lambda client."""
        try:
            self.lambda_client = boto3.client("lambda")
            self.console = Console()
        except NoCredentialsError:
            print(
                "[red]Error: AWS credentials not found. Please configure your AWS credentials.[/red]"
            )
            raise
        except Exception as e:
            print(f"[red]Error initializing Lambda client: {e}[/red]")
            raise

    def _validate_output_format(self, output_format: str) -> str:
        """Validate and normalize output format."""
        valid_formats = ["table", "json", "yaml", "text", "markdown"]
        output_format = output_format.lower()
        if output_format not in valid_formats:
            print(
                f"[red]Invalid output format '{output_format}'. Valid formats: {', '.join(valid_formats)}[/red]"
            )
            raise ValueError(f"Invalid output format: {output_format}")
        return output_format

    def _format_date(self, date_str: str) -> str:
        """Format ISO date string to readable format."""
        if not date_str:
            return "N/A"
        try:
            from datetime import datetime

            dt = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
            return dt.strftime("%Y-%m-%d %H:%M")
        except Exception:
            return date_str

    def list_layers(self, output_format: str = "table") -> None:  # noqa: C901
        """List all Lambda layers in the current AWS account and region.

        Args:
            output_format: Output format (table, json, yaml, text, markdown)
        """
        try:
            output_format = self._validate_output_format(output_format)

            if output_format == "table":
                print("[blue]Fetching Lambda layers...[/blue]")

            # Get all layers using pagination
            layers = []
            paginator = self.lambda_client.get_paginator("list_layers")

            for page in paginator.paginate():
                layers.extend(page.get("Layers", []))

            if not layers:
                if output_format == "table":
                    print(
                        "[yellow]No Lambda layers found in the current region.[/yellow]"
                    )
                elif output_format == "json":
                    print(json.dumps({"layers": [], "count": 0}, indent=2))
                elif output_format == "yaml":
                    print(yaml.dump({"layers": [], "count": 0}))
                elif output_format == "text":
                    print("No Lambda layers found in the current region.")
                elif output_format == "markdown":
                    print(
                        "# Lambda Layers\n\nNo Lambda layers found in the current region."
                    )
                return

            # Process layer data
            layer_data = []
            for layer in layers:
                latest_version_info = layer.get("LatestMatchingVersion", {})
                layer_info = {
                    "name": layer.get("LayerName", "N/A"),
                    "latest_version": latest_version_info.get("Version", "N/A"),
                    "description": latest_version_info.get(
                        "Description", "No description"
                    ),
                    "compatible_runtimes": latest_version_info.get(
                        "CompatibleRuntimes", []
                    ),
                    "created_date": latest_version_info.get("CreatedDate", ""),
                    "formatted_created": self._format_date(
                        latest_version_info.get("CreatedDate", "")
                    ),
                }
                layer_data.append(layer_info)

            # Output in requested format
            if output_format == "json":
                output = {"layers": layer_data, "count": len(layer_data)}
                print(json.dumps(output, indent=2, default=str))
            elif output_format == "yaml":
                output = {"layers": layer_data, "count": len(layer_data)}
                print(yaml.dump(output, default_flow_style=False))
            elif output_format == "text":
                for layer in layer_data:
                    print(f"Name: {layer['name']}")
                    print(f"Latest Version: {layer['latest_version']}")
                    print(f"Description: {layer['description']}")
                    print(
                        f"Compatible Runtimes: {', '.join(layer['compatible_runtimes']) if layer['compatible_runtimes'] else 'N/A'}"
                    )
                    print(f"Created: {layer['formatted_created']}")
                    print("-" * 50)
                print(f"\nTotal: {len(layer_data)} layer(s)")
            elif output_format == "markdown":
                print("# Lambda Layers\n")
                print(
                    "| Layer Name | Latest Version | Description | Compatible Runtimes | Created |"
                )
                print(
                    "|------------|----------------|-------------|---------------------|---------|"
                )
                for layer in layer_data:
                    runtimes = (
                        ", ".join(layer["compatible_runtimes"])
                        if layer["compatible_runtimes"]
                        else "N/A"
                    )
                    desc = (
                        layer["description"][:50] + "..."
                        if len(layer["description"]) > 50
                        else layer["description"]
                    )
                    print(
                        f"| {layer['name']} | {layer['latest_version']} | {desc} | {runtimes} | {layer['formatted_created']} |"
                    )
                print(f"\n**Total: {len(layer_data)} layer(s)**")
            else:  # table format (default)
                # Create a table to display the layers
                table = Table(
                    show_header=True,
                    header_style="bold",
                    box=box.SIMPLE,
                    border_style="dim",
                )
                table.add_column("Layer Name", no_wrap=True)
                table.add_column("Latest Version")
                table.add_column("Description")
                table.add_column("Compatible Runtimes")
                table.add_column("Created")

                for layer in layer_data:
                    runtimes_str = (
                        ", ".join(layer["compatible_runtimes"])
                        if layer["compatible_runtimes"]
                        else "N/A"
                    )

                    table.add_row(
                        layer["name"],
                        str(layer["latest_version"]),
                        (
                            layer["description"][:50] + "..."
                            if len(layer["description"]) > 50
                            else layer["description"]
                        ),
                        (
                            runtimes_str[:30] + "..."
                            if len(runtimes_str) > 30
                            else runtimes_str
                        ),
                        layer["formatted_created"],
                    )

                self.console.print(table)
                print(f"\n[green]Found {len(layer_data)} layer(s) in total.[/green]")

        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            if error_code == "AccessDenied":
                print(
                    "[red]Error: Access denied. Please check your AWS permissions for Lambda.[/red]"
                )
            else:
                print(f"[red]AWS Error: {e.response['Error']['Message']}[/red]")
        except Exception as e:
            print(f"[red]Error listing layers: {e}[/red]")

    def get_layer_info(  # noqa: C901
        self, name: str, version: Optional[int] = None, output_format: str = "table"
    ) -> None:
        """Get detailed information about a specific Lambda layer.

        Args:
            name: The name of the Lambda layer
            version: The version number of the layer (defaults to latest)
            output_format: Output format (table, json, yaml, text, markdown)
        """
        try:
            output_format = self._validate_output_format(output_format)

            if output_format == "table":
                print(f"[blue]Fetching information for layer '{name}'...[/blue]")

            # If no version specified, get the latest version
            if version is None:
                try:
                    # List layer versions to get the latest
                    response = self.lambda_client.list_layer_versions(LayerName=name)
                    if not response.get("LayerVersions"):
                        if output_format == "table":
                            print(f"[red]No versions found for layer '{name}'[/red]")
                        elif output_format == "json":
                            print(
                                json.dumps(
                                    {"error": f"No versions found for layer '{name}'"},
                                    indent=2,
                                )
                            )
                        elif output_format == "yaml":
                            print(
                                yaml.dump(
                                    {"error": f"No versions found for layer '{name}'"}
                                )
                            )
                        elif output_format == "text":
                            print(f"No versions found for layer '{name}'")
                        elif output_format == "markdown":
                            print(
                                f"# Layer Information\n\n**Error:** No versions found for layer '{name}'"
                            )
                        return

                    # Get the highest version number
                    latest_version = max(
                        lv["Version"] for lv in response["LayerVersions"]
                    )
                    version = latest_version
                    if output_format == "table":
                        print(f"[dim]Using latest version: {version}[/dim]")

                except ClientError as e:
                    if e.response["Error"]["Code"] == "ResourceNotFoundException":
                        error_msg = f"Layer '{name}' not found."
                        if output_format == "table":
                            print(f"[red]{error_msg}[/red]")
                        elif output_format == "json":
                            print(json.dumps({"error": error_msg}, indent=2))
                        elif output_format == "yaml":
                            print(yaml.dump({"error": error_msg}))
                        elif output_format == "text":
                            print(error_msg)
                        elif output_format == "markdown":
                            print(f"# Layer Information\n\n**Error:** {error_msg}")
                        return
                    raise

            # Get layer version details
            try:
                response = self.lambda_client.get_layer_version(
                    LayerName=name, VersionNumber=version
                )
            except ClientError as e:
                if e.response["Error"]["Code"] == "ResourceNotFoundException":
                    error_msg = f"Layer '{name}' version {version} not found."
                    if output_format == "table":
                        print(f"[red]{error_msg}[/red]")
                    elif output_format == "json":
                        print(json.dumps({"error": error_msg}, indent=2))
                    elif output_format == "yaml":
                        print(yaml.dump({"error": error_msg}))
                    elif output_format == "text":
                        print(error_msg)
                    elif output_format == "markdown":
                        print(f"# Layer Information\n\n**Error:** {error_msg}")
                    return
                raise

            # Get all versions for this layer
            try:
                versions_response = self.lambda_client.list_layer_versions(
                    LayerName=name
                )
                all_versions = versions_response.get("LayerVersions", [])
                all_versions.sort(key=lambda x: x["Version"], reverse=True)
            except Exception:
                all_versions = []

            # Prepare layer data
            layer_data = {
                "name": name,
                "version": response.get("Version"),
                "layer_arn": response.get("LayerArn", "N/A"),
                "description": response.get("Description", "No description"),
                "compatible_runtimes": response.get("CompatibleRuntimes", []),
                "compatible_architectures": response.get("CompatibleArchitectures", []),
                "license_info": response.get("LicenseInfo"),
                "created_date": response.get("CreatedDate", ""),
                "formatted_created": self._format_date(response.get("CreatedDate", "")),
                "content": response.get("Content", {}),
                "all_versions": [],
            }

            # Process all versions
            for v in all_versions:
                version_info = {
                    "version": v["Version"],
                    "description": v.get("Description", "No description"),
                    "created_date": v.get("CreatedDate", ""),
                    "formatted_created": self._format_date(v.get("CreatedDate", "")),
                    "compatible_runtimes": v.get("CompatibleRuntimes", []),
                    "is_current": v["Version"] == version,
                }
                layer_data["all_versions"].append(version_info)

            # Output in requested format
            if output_format == "json":
                print(json.dumps(layer_data, indent=2, default=str))
            elif output_format == "yaml":
                print(yaml.dump(layer_data, default_flow_style=False))
            elif output_format == "text":
                print(
                    f"Layer Information: {layer_data['name']} (Version {layer_data['version']})"
                )
                print("=" * 60)
                print(f"Layer ARN: {layer_data['layer_arn']}")
                print(f"Version: {layer_data['version']}")
                print(f"Description: {layer_data['description']}")
                print(
                    f"Compatible Runtimes: {', '.join(layer_data['compatible_runtimes']) if layer_data['compatible_runtimes'] else 'None specified'}"
                )
                if layer_data["compatible_architectures"]:
                    print(
                        f"Compatible Architectures: {', '.join(layer_data['compatible_architectures'])}"
                    )
                if layer_data["license_info"]:
                    print(f"License: {layer_data['license_info']}")
                print(f"Created: {layer_data['formatted_created']}")

                if layer_data["content"]:
                    print("\nContent Information:")
                    print(f"Location: {layer_data['content'].get('Location', 'N/A')}")
                    print(
                        f"Code SHA256: {layer_data['content'].get('CodeSha256', 'N/A')}"
                    )
                    print(
                        f"Code Size: {layer_data['content'].get('CodeSize', 'N/A')} bytes"
                    )

                print("\nAvailable Versions:")
                for v in layer_data["all_versions"]:
                    current_indicator = "*" if v["is_current"] else " "
                    print(
                        f"{current_indicator}{v['version']} - {v['description']} ({v['formatted_created']})"
                    )

            elif output_format == "markdown":
                print(
                    f"# Layer Information: {layer_data['name']} (Version {layer_data['version']})\n"
                )
                print("## Basic Information\n")
                print(f"- **Layer ARN:** {layer_data['layer_arn']}")
                print(f"- **Version:** {layer_data['version']}")
                print(f"- **Description:** {layer_data['description']}")
                print(
                    f"- **Compatible Runtimes:** {', '.join(layer_data['compatible_runtimes']) if layer_data['compatible_runtimes'] else 'None specified'}"
                )
                if layer_data["compatible_architectures"]:
                    print(
                        f"- **Compatible Architectures:** {', '.join(layer_data['compatible_architectures'])}"
                    )
                if layer_data["license_info"]:
                    print(f"- **License:** {layer_data['license_info']}")
                print(f"- **Created:** {layer_data['formatted_created']}")

                if layer_data["content"]:
                    print("\n## Content Information\n")
                    print(
                        f"- **Location:** {layer_data['content'].get('Location', 'N/A')}"
                    )
                    print(
                        f"- **Code SHA256:** {layer_data['content'].get('CodeSha256', 'N/A')}"
                    )
                    print(
                        f"- **Code Size:** {layer_data['content'].get('CodeSize', 'N/A')} bytes"
                    )

                print("\n## Available Versions\n")
                print("| Version | Description | Created | Runtimes |")
                print("|---------|-------------|---------|----------|")
                for v in layer_data["all_versions"]:
                    current_indicator = "*" if v["is_current"] else ""
                    runtimes = (
                        ", ".join(v["compatible_runtimes"])
                        if v["compatible_runtimes"]
                        else "N/A"
                    )
                    desc = (
                        v["description"][:40] + "..."
                        if len(v["description"]) > 40
                        else v["description"]
                    )
                    print(
                        f"| {current_indicator}{v['version']} | {desc} | {v['formatted_created']} | {runtimes} |"
                    )

            else:  # table format (default)
                # Display layer information
                print(
                    f"\n[bold cyan]Layer Information: {layer_data['name']} (Version {layer_data['version']})[/bold cyan]"
                )
                print("=" * 60)

                # Basic info
                print(f"[bold]Layer ARN:[/bold] {layer_data['layer_arn']}")
                print(f"[bold]Version:[/bold] {layer_data['version']}")
                print(f"[bold]Description:[/bold] {layer_data['description']}")

                # Compatible runtimes
                if layer_data["compatible_runtimes"]:
                    print(
                        f"[bold]Compatible Runtimes:[/bold] {', '.join(layer_data['compatible_runtimes'])}"
                    )
                else:
                    print("[bold]Compatible Runtimes:[/bold] None specified")

                # Compatible architectures
                if layer_data["compatible_architectures"]:
                    print(
                        f"[bold]Compatible Architectures:[/bold] {', '.join(layer_data['compatible_architectures'])}"
                    )

                # License info
                if layer_data["license_info"]:
                    print(f"[bold]License:[/bold] {layer_data['license_info']}")

                # Creation date
                print(f"[bold]Created:[/bold] {layer_data['formatted_created']}")

                # Content info
                content = layer_data["content"]
                if content:
                    print("\n[bold cyan]Content Information:[/bold cyan]")
                    print(f"[bold]Location:[/bold] {content.get('Location', 'N/A')}")
                    print(
                        f"[bold]Code SHA256:[/bold] {content.get('CodeSha256', 'N/A')}"
                    )
                    print(
                        f"[bold]Code Size:[/bold] {content.get('CodeSize', 'N/A')} bytes"
                    )

                # List all versions for this layer
                print("\n[bold cyan]Available Versions:[/bold cyan]")
                if layer_data["all_versions"]:
                    table = Table(
                        show_header=True,
                        header_style="bold",
                        box=box.SIMPLE,
                        border_style="dim",
                    )
                    table.add_column("Version")
                    table.add_column("Description")
                    table.add_column("Created")
                    table.add_column("Runtimes")

                    for v in layer_data["all_versions"]:
                        # Highlight current version
                        version_text = (
                            f"*{v['version']}" if v["is_current"] else str(v["version"])
                        )

                        runtimes_str = (
                            ", ".join(v["compatible_runtimes"])
                            if v["compatible_runtimes"]
                            else "N/A"
                        )

                        table.add_row(
                            version_text,
                            (
                                v["description"][:40] + "..."
                                if len(v["description"]) > 40
                                else v["description"]
                            ),
                            v["formatted_created"],
                            (
                                runtimes_str[:25] + "..."
                                if len(runtimes_str) > 25
                                else runtimes_str
                            ),
                        )

                    self.console.print(table)
                else:
                    print("[yellow]No versions found[/yellow]")

        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            if error_code == "AccessDenied":
                print(
                    "[red]Error: Access denied. Please check your AWS permissions for Lambda.[/red]"
                )
            else:
                print(f"[red]AWS Error: {e.response['Error']['Message']}[/red]")
        except Exception as e:
            print(f"[red]Error getting layer info: {e}[/red]")

    def attach_layer_to_function(  # noqa: C901
        self,
        function_name: str,
        layer_name: str,
        version: str = "latest",
        output_format: str = "table",
        dry_run: bool = False,
    ) -> None:
        """Attach a Lambda layer to a function.

        Args:
            function_name: The name of the Lambda function
            layer_name: The name or ARN of the Lambda layer
            version: The version of the layer (defaults to 'latest')
            output_format: Output format (table, json, yaml, text, markdown)
            dry_run: Show what would be done without making any changes
        """
        try:
            output_format = self._validate_output_format(output_format)

            if output_format == "table":
                print(
                    f"[blue]Attaching layer '{layer_name}' to function '{function_name}'...[/blue]"
                )

            # Get current function configuration
            try:
                current_config = self.lambda_client.get_function_configuration(
                    FunctionName=function_name
                )
            except ClientError as e:
                if e.response["Error"]["Code"] == "ResourceNotFoundException":
                    error_msg = f"Function '{function_name}' not found."
                    if output_format == "table":
                        print(f"[red]{error_msg}[/red]")
                    elif output_format == "json":
                        print(json.dumps({"error": error_msg}, indent=2))
                    elif output_format == "yaml":
                        print(yaml.dump({"error": error_msg}))
                    elif output_format == "text":
                        print(error_msg)
                    elif output_format == "markdown":
                        print(f"# Layer Attachment\n\n**Error:** {error_msg}")
                    return
                raise

            # Resolve layer ARN if needed
            layer_arn = self._resolve_layer_arn(layer_name, version)
            if not layer_arn:
                error_msg = (
                    f"Could not resolve layer '{layer_name}' with version '{version}'"
                )
                if output_format == "table":
                    print(f"[red]{error_msg}[/red]")
                elif output_format == "json":
                    print(json.dumps({"error": error_msg}, indent=2))
                elif output_format == "yaml":
                    print(yaml.dump({"error": error_msg}))
                elif output_format == "text":
                    print(error_msg)
                elif output_format == "markdown":
                    print(f"# Layer Attachment\n\n**Error:** {error_msg}")
                return

            # Get existing layers and add the new one
            existing_layers = current_config.get("Layers", [])
            existing_layer_arns = [layer["Arn"] for layer in existing_layers]

            # Check if layer is already attached
            if layer_arn in existing_layer_arns:
                message = f"Layer '{layer_name}' is already attached to function '{function_name}'"
                if output_format == "table":
                    print(f"[yellow]{message}[/yellow]")
                elif output_format == "json":
                    print(
                        json.dumps(
                            {"message": message, "already_attached": True}, indent=2
                        )
                    )
                elif output_format == "yaml":
                    print(yaml.dump({"message": message, "already_attached": True}))
                elif output_format == "text":
                    print(message)
                elif output_format == "markdown":
                    print(f"# Layer Attachment\n\n**Info:** {message}")
                return

            # Add new layer
            new_layers = existing_layer_arns + [layer_arn]

            # Prepare result data
            if dry_run:
                status = "dry-run"
                message = f"[DRY RUN] Would attach layer '{layer_name}' to function '{function_name}'"
            else:
                status = "success"
                message = f"Successfully attached layer '{layer_name}' to function '{function_name}'"

            result_data = {
                "function_name": function_name,
                "layer_arn": layer_arn,
                "layer_name": layer_name,
                "version": version,
                "status": status,
                "message": message,
                "total_layers": len(new_layers),
                "attached_layers": new_layers,
                "dry_run": dry_run,
            }

            # Update function configuration (skip if dry run)
            if not dry_run:
                try:
                    self.lambda_client.update_function_configuration(
                        FunctionName=function_name, Layers=new_layers
                    )
                except ClientError as e:
                    error_msg = (
                        f"Failed to attach layer: {e.response['Error']['Message']}"
                    )
                    if output_format == "table":
                        print(f"[red]{error_msg}[/red]")
                    elif output_format == "json":
                        print(json.dumps({"error": error_msg}, indent=2))
                    elif output_format == "yaml":
                        print(yaml.dump({"error": error_msg}))
                    elif output_format == "text":
                        print(error_msg)
                    elif output_format == "markdown":
                        print(f"# Layer Attachment\n\n**Error:** {error_msg}")
                    return

            # Output result
            if output_format == "json":
                print(json.dumps(result_data, indent=2))
            elif output_format == "yaml":
                print(yaml.dump(result_data, default_flow_style=False))
            elif output_format == "text":
                print(f"Status: {result_data['status']}")
                print(f"Function: {result_data['function_name']}")
                print(f"Layer: {result_data['layer_name']} ({result_data['version']})")
                print(f"Layer ARN: {result_data['layer_arn']}")
                print(f"Total Layers: {result_data['total_layers']}")
                print(f"Message: {result_data['message']}")
            elif output_format == "markdown":
                print("# Layer Attachment Result\n")
                print(f"- **Status:** {result_data['status']}")
                print(f"- **Function:** {result_data['function_name']}")
                print(
                    f"- **Layer:** {result_data['layer_name']} ({result_data['version']})"
                )
                print(f"- **Layer ARN:** {result_data['layer_arn']}")
                print(f"- **Total Layers:** {result_data['total_layers']}")
                print(f"\n**Message:** {result_data['message']}")
            else:  # table format
                if dry_run:
                    print(f"[yellow]🔍 {result_data['message']}[/yellow]")
                else:
                    print(f"[green]✓ {result_data['message']}[/green]")
                print(f"[bold]Function:[/bold] {result_data['function_name']}")
                print(f"[bold]Layer ARN:[/bold] {result_data['layer_arn']}")
                print(f"[bold]Total Layers:[/bold] {result_data['total_layers']}")
                if dry_run:
                    print("[dim]No changes were made (dry run mode)[/dim]")

        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            if error_code == "AccessDenied":
                print(
                    "[red]Error: Access denied. Please check your AWS permissions for Lambda.[/red]"
                )
            else:
                print(f"[red]AWS Error: {e.response['Error']['Message']}[/red]")
        except Exception as e:
            print(f"[red]Error attaching layer: {e}[/red]")

    def detach_layer_from_function(  # noqa: C901
        self,
        function_name: str,
        layer_name: str,
        output_format: str = "table",
        dry_run: bool = False,
    ) -> None:
        """Detach a Lambda layer from a function.

        Args:
            function_name: The name of the Lambda function
            layer_name: The name or ARN of the Lambda layer
            output_format: Output format (table, json, yaml, text, markdown)
            dry_run: Show what would be done without making any changes
        """
        try:
            output_format = self._validate_output_format(output_format)

            if output_format == "table":
                print(
                    f"[blue]Detaching layer '{layer_name}' from function '{function_name}'...[/blue]"
                )

            # Get current function configuration
            try:
                current_config = self.lambda_client.get_function_configuration(
                    FunctionName=function_name
                )
            except ClientError as e:
                if e.response["Error"]["Code"] == "ResourceNotFoundException":
                    error_msg = f"Function '{function_name}' not found."
                    if output_format == "table":
                        print(f"[red]{error_msg}[/red]")
                    elif output_format == "json":
                        print(json.dumps({"error": error_msg}, indent=2))
                    elif output_format == "yaml":
                        print(yaml.dump({"error": error_msg}))
                    elif output_format == "text":
                        print(error_msg)
                    elif output_format == "markdown":
                        print(f"# Layer Detachment\n\n**Error:** {error_msg}")
                    return
                raise

            # Get existing layers
            existing_layers = current_config.get("Layers", [])
            existing_layer_arns = [layer["Arn"] for layer in existing_layers]

            if not existing_layer_arns:
                message = f"Function '{function_name}' has no layers attached."
                if output_format == "table":
                    print(f"[yellow]{message}[/yellow]")
                elif output_format == "json":
                    print(json.dumps({"message": message, "no_layers": True}, indent=2))
                elif output_format == "yaml":
                    print(yaml.dump({"message": message, "no_layers": True}))
                elif output_format == "text":
                    print(message)
                elif output_format == "markdown":
                    print(f"# Layer Detachment\n\n**Info:** {message}")
                return

            # Find matching layers to remove
            layers_to_remove = []
            new_layers = []

            for layer_arn in existing_layer_arns:
                # Check if this layer matches our search criteria
                should_remove = False

                # If layer_name is already an ARN, do exact match
                if layer_name.startswith("arn:aws:lambda:"):
                    should_remove = layer_arn == layer_name
                else:
                    # For layer names, check if the ARN contains the layer name
                    should_remove = (
                        f":{layer_name}:" in layer_arn or f"/{layer_name}" in layer_arn
                    )

                if should_remove:
                    layers_to_remove.append(layer_arn)
                else:
                    new_layers.append(layer_arn)

            # Check if any layers were found to remove
            if not layers_to_remove:
                message = f"Layer '{layer_name}' is not attached to function '{function_name}'"
                if output_format == "table":
                    print(f"[yellow]{message}[/yellow]")
                elif output_format == "json":
                    print(
                        json.dumps({"message": message, "not_attached": True}, indent=2)
                    )
                elif output_format == "yaml":
                    print(yaml.dump({"message": message, "not_attached": True}))
                elif output_format == "text":
                    print(message)
                elif output_format == "markdown":
                    print(f"# Layer Detachment\n\n**Info:** {message}")
                return

            # Prepare result data
            if dry_run:
                status = "dry-run"
                message = f"[DRY RUN] Would detach {len(layers_to_remove)} layer(s) from function '{function_name}'"
            else:
                status = "success"
                message = f"Successfully detached {len(layers_to_remove)} layer(s) from function '{function_name}'"

            result_data: Dict[str, Any] = {
                "function_name": function_name,
                "layer_name": layer_name,
                "status": status,
                "message": message,
                "layers_removed": layers_to_remove,
                "remaining_layers": new_layers,
                "total_layers_before": len(existing_layer_arns),
                "total_layers_after": len(new_layers),
                "dry_run": dry_run,
            }

            # Update function configuration (skip if dry run)
            if not dry_run:
                try:
                    self.lambda_client.update_function_configuration(
                        FunctionName=function_name, Layers=new_layers
                    )
                except ClientError as e:
                    error_msg = (
                        f"Failed to detach layer: {e.response['Error']['Message']}"
                    )
                    if output_format == "table":
                        print(f"[red]{error_msg}[/red]")
                    elif output_format == "json":
                        print(json.dumps({"error": error_msg}, indent=2))
                    elif output_format == "yaml":
                        print(yaml.dump({"error": error_msg}))
                    elif output_format == "text":
                        print(error_msg)
                    elif output_format == "markdown":
                        print(f"# Layer Detachment\n\n**Error:** {error_msg}")
                    return

            # Output result
            if output_format == "json":
                print(json.dumps(result_data, indent=2))
            elif output_format == "yaml":
                print(yaml.dump(result_data, default_flow_style=False))
            elif output_format == "text":
                print(f"Status: {result_data['status']}")
                print(f"Function: {result_data['function_name']}")
                print(f"Layer Pattern: {result_data['layer_name']}")
                print(f"Layers Removed: {len(result_data['layers_removed'])}")
                print(f"Total Layers Before: {result_data['total_layers_before']}")
                print(f"Total Layers After: {result_data['total_layers_after']}")
                print(f"Message: {result_data['message']}")
                if result_data["layers_removed"]:
                    print("\nRemoved Layers:")
                    for layer_arn in result_data["layers_removed"]:
                        print(f"  - {layer_arn}")
            elif output_format == "markdown":
                print("# Layer Detachment Result\n")
                print(f"- **Status:** {result_data['status']}")
                print(f"- **Function:** {result_data['function_name']}")
                print(f"- **Layer Pattern:** {result_data['layer_name']}")
                print(f"- **Layers Removed:** {len(result_data['layers_removed'])}")
                print(
                    f"- **Total Layers Before:** {result_data['total_layers_before']}"
                )
                print(f"- **Total Layers After:** {result_data['total_layers_after']}")
                print(f"\n**Message:** {result_data['message']}")
                if result_data["layers_removed"]:
                    print("\n## Removed Layers")
                    for layer_arn in result_data["layers_removed"]:
                        print(f"- `{layer_arn}`")
            else:  # table format
                if dry_run:
                    print(f"[yellow]🔍 {result_data['message']}[/yellow]")
                else:
                    print(f"[green]✓ {result_data['message']}[/green]")
                print(f"[bold]Function:[/bold] {result_data['function_name']}")
                print(
                    f"[bold]Layers Removed:[/bold] {len(result_data['layers_removed'])}"
                )
                print(
                    f"[bold]Total Layers:[/bold] {result_data['total_layers_before']} → {result_data['total_layers_after']}"
                )

                if result_data["layers_removed"]:
                    print("[bold]Removed Layers:[/bold]")
                    for layer_arn in result_data["layers_removed"]:
                        print(f"  • {layer_arn}")

                if dry_run:
                    print("[dim]No changes were made (dry run mode)[/dim]")

        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            if error_code == "AccessDenied":
                print(
                    "[red]Error: Access denied. Please check your AWS permissions for Lambda.[/red]"
                )
            else:
                print(f"[red]AWS Error: {e.response['Error']['Message']}[/red]")
        except Exception as e:
            print(f"[red]Error detaching layer: {e}[/red]")

    def scan_layer_usage(  # noqa: C901
        self, layer_name: str, output_format: str = "table"
    ) -> None:
        """Scan and display which Lambda functions are using a specific layer.

        Args:
            layer_name: The name or ARN of the Lambda layer
            output_format: Output format (table, json, yaml, text, markdown)
        """
        try:
            output_format = self._validate_output_format(output_format)

            if output_format == "table":
                print(f"[blue]Scanning usage for layer '{layer_name}'...[/blue]")

            # Get all functions
            functions = []
            paginator = self.lambda_client.get_paginator("list_functions")

            for page in paginator.paginate():
                functions.extend(page.get("Functions", []))

            if not functions:
                message = "No Lambda functions found in the current region."
                if output_format == "table":
                    print(f"[yellow]{message}[/yellow]")
                elif output_format == "json":
                    print(
                        json.dumps(
                            {"functions": [], "count": 0, "message": message}, indent=2
                        )
                    )
                elif output_format == "yaml":
                    print(yaml.dump({"functions": [], "count": 0, "message": message}))
                elif output_format == "text":
                    print(message)
                elif output_format == "markdown":
                    print(f"# Layer Usage Scan\n\n{message}")
                return

            # Find functions using the layer
            functions_using_layer = []
            layer_arn_patterns = []

            # Create possible ARN patterns for the layer
            if layer_name.startswith("arn:aws:lambda:"):
                layer_arn_patterns.append(layer_name)
            else:
                # Add patterns for different versions
                layer_arn_patterns.append(f":{layer_name}:")
                layer_arn_patterns.append(f"/{layer_name}")

            for function in functions:
                function_name = function.get("FunctionName", "")
                layers = function.get("Layers", [])

                matching_layers = []
                for layer in layers:
                    layer_arn = layer.get("Arn", "")
                    # Check if this layer matches our search
                    if any(pattern in layer_arn for pattern in layer_arn_patterns):
                        matching_layers.append(
                            {
                                "arn": layer_arn,
                                "version": (
                                    layer_arn.split(":")[-1]
                                    if ":" in layer_arn
                                    else "unknown"
                                ),
                                "code_size": layer.get("CodeSize", 0),
                            }
                        )

                if matching_layers:
                    function_info = {
                        "function_name": function_name,
                        "runtime": function.get("Runtime", "N/A"),
                        "last_modified": function.get("LastModified", ""),
                        "formatted_modified": self._format_date(
                            function.get("LastModified", "")
                        ),
                        "matching_layers": matching_layers,
                        "total_layers": len(layers),
                        "code_size": function.get("CodeSize", 0),
                        "memory_size": function.get("MemorySize", 0),
                        "timeout": function.get("Timeout", 0),
                    }
                    functions_using_layer.append(function_info)

            # Prepare summary data
            summary_data = {
                "layer_name": layer_name,
                "functions_using_layer": functions_using_layer,
                "total_functions_found": len(functions),
                "functions_using_count": len(functions_using_layer),
                "scan_summary": f"Found {len(functions_using_layer)} function(s) using layer '{layer_name}' out of {len(functions)} total functions",
            }

            # Output results
            if output_format == "json":
                print(json.dumps(summary_data, indent=2, default=str))
            elif output_format == "yaml":
                print(yaml.dump(summary_data, default_flow_style=False))
            elif output_format == "text":
                print(f"Layer Usage Scan Results for: {layer_name}")
                print("=" * 60)
                print(
                    f"Total Functions Scanned: {summary_data['total_functions_found']}"
                )
                print(f"Functions Using Layer: {summary_data['functions_using_count']}")
                print()

                if functions_using_layer:
                    for func in functions_using_layer:
                        print(f"Function: {func['function_name']}")
                        print(f"  Runtime: {func['runtime']}")
                        print(f"  Last Modified: {func['formatted_modified']}")
                        print(f"  Total Layers: {func['total_layers']}")
                        print(f"  Memory: {func['memory_size']} MB")
                        print(f"  Timeout: {func['timeout']} seconds")
                        print("  Matching Layers:")
                        for layer in func["matching_layers"]:
                            print(f"    - {layer['arn']} (Version: {layer['version']})")
                        print("-" * 40)
                else:
                    print(f"No functions found using layer '{layer_name}'")

            elif output_format == "markdown":
                print(f"# Layer Usage Scan: {layer_name}\n")
                print(
                    f"**Total Functions Scanned:** {summary_data['total_functions_found']}"
                )
                print(
                    f"**Functions Using Layer:** {summary_data['functions_using_count']}\n"
                )

                if functions_using_layer:
                    print("## Functions Using This Layer\n")
                    print(
                        "| Function Name | Runtime | Last Modified | Total Layers | Memory | Timeout |"
                    )
                    print(
                        "|---------------|---------|---------------|--------------|--------|---------|"
                    )

                    for func in functions_using_layer:
                        print(
                            f"| {func['function_name']} | {func['runtime']} | {func['formatted_modified']} | {func['total_layers']} | {func['memory_size']} MB | {func['timeout']}s |"
                        )

                    print("\n### Layer Details\n")
                    for func in functions_using_layer:
                        print(f"**{func['function_name']}:**")
                        for layer in func["matching_layers"]:
                            print(f"- `{layer['arn']}` (Version: {layer['version']})")
                        print()
                else:
                    print(f"No functions found using layer '{layer_name}'")

            else:  # table format
                if functions_using_layer:
                    # Combined table with all function and layer information
                    table = Table(
                        show_header=True,
                        header_style="bold cyan",
                        box=box.SIMPLE,
                        border_style="dim",
                    )
                    table.add_column("Function Name", style="green", no_wrap=False)
                    table.add_column("Runtime", style="blue", no_wrap=True)
                    table.add_column("Modified", style="dim", no_wrap=True)
                    table.add_column(
                        "Memory", style="yellow", justify="right", no_wrap=True
                    )
                    table.add_column(
                        "Timeout", style="yellow", justify="right", no_wrap=True
                    )
                    table.add_column(
                        "Layers", style="cyan", justify="center", no_wrap=True
                    )
                    table.add_column("Layer ARN", style="white", overflow="fold")
                    table.add_column(
                        "Ver", style="magenta", justify="center", no_wrap=True
                    )

                    for func in functions_using_layer:
                        for layer in func["matching_layers"]:
                            table.add_row(
                                func["function_name"],
                                func["runtime"],
                                func["formatted_modified"],
                                f"{func['memory_size']} MB",
                                f"{func['timeout']}s",
                                str(func["total_layers"]),
                                layer.get("arn", "No ARN found"),
                                str(layer.get("version", "N/A")),
                            )

                    self.console.print(table)
                    print(
                        f"\n[green]Found {len(functions_using_layer)} function(s) using layer '{layer_name}' out of {len(functions)} total functions.[/green]"
                    )
                else:
                    print(
                        f"[yellow]No functions found using layer '{layer_name}'[/yellow]"
                    )
                    print(f"[dim]Scanned {len(functions)} function(s) in total[/dim]")

        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            if error_code == "AccessDenied":
                print(
                    "[red]Error: Access denied. Please check your AWS permissions for Lambda.[/red]"
                )
            else:
                print(f"[red]AWS Error: {e.response['Error']['Message']}[/red]")
        except Exception as e:
            print(f"[red]Error scanning layer usage: {e}[/red]")

    def download_layer(  # noqa: C901
        self,
        layer_name: str,
        version: int,
        output_path: Optional[str] = None,
        extract: bool = False,
    ) -> None:
        """Download a Lambda layer.

        Args:
            layer_name: The name of the Lambda layer
            version: The version number of the layer
            output_path: Output path for downloaded .zip or extracted folder
            extract: Whether to extract the downloaded layer
        """
        try:
            print(f"[blue]Downloading layer '{layer_name}' version {version}...[/blue]")

            # Get layer version details
            try:
                response = self.lambda_client.get_layer_version(
                    LayerName=layer_name, VersionNumber=version
                )
            except ClientError as e:
                if e.response["Error"]["Code"] == "ResourceNotFoundException":
                    print(
                        f"[red]Layer '{layer_name}' version {version} not found.[/red]"
                    )
                    return
                raise

            # Get download URL from the content
            content = response.get("Content", {})
            download_url = content.get("Location")

            if not download_url:
                print(
                    f"[red]No download URL available for layer '{layer_name}' version {version}.[/red]"
                )
                return

            # Determine output path
            if output_path is None:
                if extract:
                    output_path = f"./{layer_name}-v{version}"
                else:
                    output_path = f"./{layer_name}-v{version}.zip"

            # Create output directory if needed
            if extract:
                output_dir = Path(output_path)
                output_dir.mkdir(parents=True, exist_ok=True)
                zip_path = output_dir / f"{layer_name}-v{version}.zip"
            else:
                output_file = Path(output_path)
                output_file.parent.mkdir(parents=True, exist_ok=True)
                zip_path = output_file

            print(f"[dim]Download URL: {download_url[:100]}...[/dim]")
            print(f"[dim]Downloading to: {zip_path}[/dim]")

            # Download the layer zip file
            try:
                urllib.request.urlretrieve(
                    download_url, zip_path
                )  # nosec B310 - AWS S3 presigned URL
                print(f"[green]✓ Downloaded layer to: {zip_path}[/green]")
            except Exception as e:
                print(f"[red]Failed to download layer: {e}[/red]")
                return

            # Extract if requested
            if extract:
                try:
                    print(f"[blue]Extracting layer to: {output_path}[/blue]")
                    with zipfile.ZipFile(zip_path, "r") as zip_ref:
                        zip_ref.extractall(output_path)

                    # Remove the zip file after extraction
                    os.remove(zip_path)

                    print(f"[green]✓ Extracted layer to: {output_path}[/green]")

                    # Show extracted contents
                    extracted_items = list(Path(output_path).iterdir())
                    if extracted_items:
                        print(
                            f"[cyan]Extracted contents ({len(extracted_items)} items):[/cyan]"
                        )
                        for item in sorted(extracted_items)[:10]:  # Show first 10 items
                            item_type = "📁" if item.is_dir() else "📄"
                            print(f"  {item_type} {item.name}")
                        if len(extracted_items) > 10:
                            print(f"  ... and {len(extracted_items) - 10} more items")

                except zipfile.BadZipFile:
                    print("[red]Error: Downloaded file is not a valid zip file.[/red]")
                except Exception as e:
                    print(f"[red]Failed to extract layer: {e}[/red]")

            # Show layer information
            print("\n[bold cyan]Layer Information:[/bold cyan]")
            print(f"[bold]Name:[/bold] {layer_name}")
            print(f"[bold]Version:[/bold] {version}")
            print(
                f"[bold]Description:[/bold] {response.get('Description', 'No description')}"
            )
            print(f"[bold]Size:[/bold] {content.get('CodeSize', 0):,} bytes")
            print(
                f"[bold]Created:[/bold] {self._format_date(response.get('CreatedDate', ''))}"
            )

            if response.get("CompatibleRuntimes"):
                print(
                    f"[bold]Compatible Runtimes:[/bold] {', '.join(response['CompatibleRuntimes'])}"
                )

            if response.get("CompatibleArchitectures"):
                print(
                    f"[bold]Compatible Architectures:[/bold] {', '.join(response['CompatibleArchitectures'])}"
                )

        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            if error_code == "AccessDenied":
                print(
                    "[red]Error: Access denied. Please check your AWS permissions for Lambda.[/red]"
                )
            else:
                print(f"[red]AWS Error: {e.response['Error']['Message']}[/red]")
        except Exception as e:
            print(f"[red]Error downloading layer: {e}[/red]")

    def _resolve_layer_arn(
        self, layer_name: str, version: str = "latest"
    ) -> Optional[str]:
        """Resolve layer name to full ARN.

        Args:
            layer_name: The name or ARN of the layer
            version: The version of the layer

        Returns:
            The full layer ARN or None if not found
        """
        try:
            # If already an ARN, return as-is
            if layer_name.startswith("arn:aws:lambda:"):
                return layer_name

            # Try to resolve the layer name to ARN
            if version.lower() == "latest":
                # Get latest version
                response = self.lambda_client.list_layer_versions(LayerName=layer_name)
                if not response.get("LayerVersions"):
                    return None

                latest_version = max(lv["Version"] for lv in response["LayerVersions"])
                version = str(latest_version)

            # Get specific version
            response = self.lambda_client.get_layer_version(
                LayerName=layer_name, VersionNumber=int(version)
            )
            return response.get("LayerVersionArn")

        except (ClientError, ValueError):
            return None
