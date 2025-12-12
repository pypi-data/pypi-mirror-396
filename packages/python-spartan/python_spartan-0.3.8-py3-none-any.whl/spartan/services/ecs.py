"""ECS service for AWS ECS cluster and task management.

This module provides comprehensive AWS ECS management capabilities
including listing clusters, tasks, services, and detailed information.
"""

import csv
import io
import json
import re
from datetime import datetime
from typing import Any, Dict, List, Optional

import boto3
import yaml
from botocore.exceptions import ClientError, NoCredentialsError
from rich import box, print
from rich.console import Console
from rich.table import Table

from spartan.utils.filters import FilterUtility, SortUtility


class ECSService:
    """Service for managing AWS ECS resources."""

    def __init__(
        self,
        region: Optional[str] = None,
        profile: Optional[str] = None,
    ):
        """Initialize the ECSService.

        Args:
            region: AWS region
            profile: AWS profile
        """
        # AWS client setup
        try:
            session = (
                boto3.Session(profile_name=profile) if profile else boto3.Session()
            )
            self.ecs_client = session.client("ecs", region_name=region)
            self.console = Console()
        except NoCredentialsError:
            print(
                "[red]Error: AWS credentials not found. Please configure your AWS credentials.[/red]"
            )
            self.ecs_client = None
            self.console = Console()
        except Exception as e:
            print(f"[red]Error initializing ECS client: {e}[/red]")
            self.ecs_client = None
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

    def list_clusters(  # noqa: C901
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
        """List all ECS clusters with filtering options.

        Args:
            output_format: Output format (table, json, yaml, markdown, csv)
            prefix_filter: Filter clusters by name prefix
            regex_match: Filter clusters by regex pattern
            contains_filter: Filter clusters by substring
            sort_by: Sort by field (name, status, running_tasks, pending_tasks, active_services)
            sort_order: Sort order (asc, desc)
            limit: Limit the number of results shown
            show_filters: Show which filters were applied in the output
            save_to: Save the results to a file (.json, .yaml, .csv, etc.)
        """
        if not self.ecs_client:
            print(
                "[red]Error: ECS client not initialized. Please check your AWS credentials.[/red]"
            )
            return

        try:
            # Validate inputs
            if not self._validate_inputs(output_format, sort_by, sort_order, limit):
                return

            if output_format == "table":
                print("[blue]Fetching ECS clusters...[/blue]")

            # Get and process cluster data
            cluster_data = self._get_cluster_data()
            if not cluster_data:
                self._handle_no_clusters_found(output_format)
                return

            # Apply filters and sorting
            filtered_data, applied_filters = self._process_cluster_data(
                cluster_data,
                prefix_filter,
                regex_match,
                contains_filter,
                sort_by,
                sort_order,
                limit,
            )

            if not filtered_data and applied_filters:
                self._handle_no_clusters_found(output_format, filtered=True)
                return

            # Output results
            self._output_cluster_results(
                filtered_data,
                output_format,
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
            print(f"[red]Error listing clusters: {e}[/red]")

    def _validate_inputs(
        self, output_format: str, sort_by: str, sort_order: str, limit: Optional[int]
    ) -> bool:
        """Validate input parameters."""
        try:
            self._validate_output_format(output_format)
        except ValueError:
            return False

        # Validate sort field
        valid_sort_fields = [
            "name",
            "status",
            "running_tasks",
            "pending_tasks",
            "active_services",
            "registered_container_instances",
        ]
        is_valid, error = SortUtility.validate_sort_field(sort_by, valid_sort_fields)
        if not is_valid:
            print(f"[red]{error}[/red]")
            return False

        # Validate sort order
        if sort_order.lower() not in ["asc", "desc"]:
            print(
                f"[red]Invalid sort order '{sort_order}'. Valid options: asc, desc[/red]"
            )
            return False

        # Validate limit
        if limit is not None and limit <= 0:
            print(f"[red]Limit must be a positive integer, got: {limit}[/red]")
            return False

        return True

    def _get_cluster_data(self) -> List[Dict]:
        """Get and process raw cluster data from AWS ECS."""
        try:
            # Get list of cluster ARNs
            response = self.ecs_client.list_clusters()
            cluster_arns = response.get("clusterArns", [])

            if not cluster_arns:
                return []

            # Describe clusters to get detailed information
            detailed_response = self.ecs_client.describe_clusters(clusters=cluster_arns)
            clusters = detailed_response.get("clusters", [])

            cluster_data = []
            for cluster in clusters:
                cluster_info = {
                    "name": cluster.get("clusterName", "N/A"),
                    "arn": cluster.get("clusterArn", "N/A"),
                    "status": cluster.get("status", "N/A"),
                    "running_tasks": cluster.get("runningTasksCount", 0),
                    "pending_tasks": cluster.get("pendingTasksCount", 0),
                    "active_services": cluster.get("activeServicesCount", 0),
                    "registered_container_instances": cluster.get(
                        "registeredContainerInstancesCount", 0
                    ),
                    "statistics": cluster.get("statistics", []),
                    "tags": cluster.get("tags", []),
                    "configuration": cluster.get("configuration", {}),
                    "capacity_providers": cluster.get("capacityProviders", []),
                    "default_capacity_provider_strategy": cluster.get(
                        "defaultCapacityProviderStrategy", []
                    ),
                }
                cluster_data.append(cluster_info)

            return cluster_data

        except Exception as e:
            print(f"[red]Error fetching clusters: {e}[/red]")
            return []

    def _process_cluster_data(
        self,
        cluster_data: List[Dict],
        prefix_filter: Optional[str],
        regex_match: Optional[str],
        contains_filter: Optional[str],
        sort_by: str,
        sort_order: str,
        limit: Optional[int],
    ) -> tuple[List[Dict], Dict]:
        """Apply filters, sorting, and limiting to cluster data."""
        original_count = len(cluster_data)

        # Apply filters
        if prefix_filter:
            cluster_data = FilterUtility.apply_prefix_filter(
                cluster_data, "name", prefix_filter
            )
        if regex_match:
            cluster_data = FilterUtility.apply_regex_filter(
                cluster_data, "name", regex_match
            )
        if contains_filter:
            cluster_data = FilterUtility.apply_contains_filter(
                cluster_data, "name", contains_filter, case_sensitive=False
            )

        # Apply sorting
        reverse = sort_order.lower() == "desc"
        if sort_by == "name":
            cluster_data = SortUtility.sort_items(
                cluster_data, "name", reverse=reverse, case_sensitive=False
            )
        elif sort_by in [
            "status",
            "running_tasks",
            "pending_tasks",
            "active_services",
            "registered_container_instances",
        ]:
            cluster_data = SortUtility.sort_items(
                cluster_data, sort_by, reverse=reverse, case_sensitive=False
            )

        # Apply limit
        if limit:
            cluster_data = cluster_data[:limit]

        # Prepare filter info
        applied_filters = self._build_applied_filters(
            prefix_filter, regex_match, contains_filter, limit, original_count
        )

        return cluster_data, applied_filters

    def _build_applied_filters(
        self,
        prefix_filter: Optional[str],
        regex_match: Optional[str],
        contains_filter: Optional[str],
        limit: Optional[int],
        original_count: int,
    ) -> Dict:
        """Build the applied filters dictionary."""
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

        return applied_filters

    def _output_cluster_results(
        self,
        cluster_data: List[Dict],
        output_format: str,
        show_filters: bool,
        applied_filters: Dict,
        sort_by: str,
        sort_order: str,
        save_to: Optional[str],
    ) -> None:
        """Output results in the requested format."""
        if output_format == "csv":
            self._print_clusters_csv(
                cluster_data, show_filters, applied_filters, save_to
            )
        elif output_format == "table":
            self._print_clusters_table(
                cluster_data, show_filters, applied_filters, sort_by, sort_order
            )
        elif output_format == "json":
            self._output_clusters_json(
                cluster_data,
                show_filters,
                applied_filters,
                sort_by,
                sort_order,
                save_to,
            )
        elif output_format == "yaml":
            self._output_clusters_yaml(
                cluster_data,
                show_filters,
                applied_filters,
                sort_by,
                sort_order,
                save_to,
            )
        elif output_format == "markdown":
            self._print_clusters_markdown(
                cluster_data,
                show_filters,
                applied_filters,
                sort_by,
                sort_order,
                save_to,
            )

    def _print_clusters_table(
        self,
        cluster_data: List[Dict],
        show_filters: bool = False,
        applied_filters: Dict = None,
        sort_by: str = "name",
        sort_order: str = "asc",
    ) -> None:
        """Print clusters in a formatted table."""
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
        table.add_column("Cluster Name", style="bright_blue", no_wrap=False)
        table.add_column("Status", style="yellow")
        table.add_column("Running Tasks", justify="right", style="green")
        table.add_column("Pending Tasks", justify="right", style="orange3")
        table.add_column("Services", justify="right", style="magenta")
        table.add_column("Instances", justify="right", style="cyan")

        for cluster in cluster_data:
            # Color code status
            status = cluster["status"]
            if status == "ACTIVE":
                status_styled = f"[green]{status}[/green]"
            elif status == "INACTIVE":
                status_styled = f"[red]{status}[/red]"
            else:
                status_styled = f"[yellow]{status}[/yellow]"

            table.add_row(
                cluster["name"],
                status_styled,
                str(cluster["running_tasks"]),
                str(cluster["pending_tasks"]),
                str(cluster["active_services"]),
                str(cluster["registered_container_instances"]),
            )

        self.console.print(
            f"🐳 [bold]ECS Clusters[/bold] ([bright_yellow]{len(cluster_data)}[/bright_yellow] found)"
        )
        if sort_by:
            self.console.print(f"[dim]Sorted by: {sort_by} ({sort_order})[/dim]")
        self.console.print()
        self.console.print(table)

    def _handle_no_clusters_found(
        self, output_format: str, filtered: bool = False
    ) -> None:
        """Handle the case when no clusters are found."""
        if filtered:
            message = "No ECS clusters match the specified filters."
            json_message = {
                "clusters": [],
                "count": 0,
                "message": "No clusters match the filters",
            }
            yaml_message = {
                "clusters": [],
                "count": 0,
                "message": "No clusters match the filters",
            }
            markdown_message = (
                "# ECS Clusters\n\nNo clusters match the specified filters."
            )
        else:
            message = "No ECS clusters found in the current account."
            json_message = {"clusters": [], "count": 0, "message": "No clusters found"}
            yaml_message = {"clusters": [], "count": 0, "message": "No clusters found"}
            markdown_message = (
                "# ECS Clusters\n\nNo clusters found in the current account."
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
            print(
                "cluster_name,status,running_tasks,pending_tasks,active_services,registered_container_instances"
            )

    def _print_clusters_csv(
        self,
        cluster_data: List[Dict],
        show_filters: bool = False,
        applied_filters: Dict = None,
        save_to: Optional[str] = None,
    ) -> None:
        """Print clusters in CSV format."""
        output = io.StringIO()
        writer = csv.writer(output)

        # Write header
        writer.writerow(
            [
                "cluster_name",
                "status",
                "running_tasks",
                "pending_tasks",
                "active_services",
                "registered_container_instances",
                "arn",
            ]
        )

        # Write data
        for cluster in cluster_data:
            writer.writerow(
                [
                    cluster["name"],
                    cluster["status"],
                    cluster["running_tasks"],
                    cluster["pending_tasks"],
                    cluster["active_services"],
                    cluster["registered_container_instances"],
                    cluster["arn"],
                ]
            )

        csv_content = output.getvalue()

        if save_to:
            self._save_to_file(csv_content, save_to)
        else:
            if show_filters and applied_filters:
                print(f"# Applied filters: {applied_filters}")
            print(csv_content.strip())

    def _output_clusters_json(
        self,
        cluster_data: List[Dict],
        show_filters: bool,
        applied_filters: Dict,
        sort_by: str,
        sort_order: str,
        save_to: Optional[str],
    ) -> None:
        """Output results in JSON format."""
        output_data = {
            "clusters": cluster_data,
            "count": len(cluster_data),
            "sort": {"by": sort_by, "order": sort_order},
        }
        if show_filters and applied_filters:
            output_data["applied_filters"] = applied_filters

        output_str = json.dumps(output_data, indent=2, default=str)
        if save_to:
            self._save_to_file(output_str, save_to)
        else:
            print(output_str)

    def _output_clusters_yaml(
        self,
        cluster_data: List[Dict],
        show_filters: bool,
        applied_filters: Dict,
        sort_by: str,
        sort_order: str,
        save_to: Optional[str],
    ) -> None:
        """Output results in YAML format."""
        output_data = {
            "clusters": cluster_data,
            "count": len(cluster_data),
            "sort": {"by": sort_by, "order": sort_order},
        }
        if show_filters and applied_filters:
            output_data["applied_filters"] = applied_filters

        output_str = yaml.dump(output_data, default_flow_style=False)
        if save_to:
            self._save_to_file(output_str, save_to)
        else:
            print(output_str)

    def _print_clusters_markdown(
        self,
        cluster_data: List[Dict],
        show_filters: bool = False,
        applied_filters: Dict = None,
        sort_by: str = "name",
        sort_order: str = "asc",
        save_to: Optional[str] = None,
    ) -> None:
        """Print clusters in markdown format."""
        output_lines = ["# ECS Clusters\n"]

        # Print filter information if any
        if show_filters and applied_filters:
            output_lines.append("## Applied Filters\n")
            for key, value in applied_filters.items():
                output_lines.append(f"- **{key.title()}:** `{value}`")
            output_lines.append("")

        output_lines.append("## Clusters\n")
        output_lines.append(
            "| Cluster Name | Status | Running Tasks | Pending Tasks | Services | Instances |"
        )
        output_lines.append(
            "|--------------|--------|---------------|---------------|----------|-----------|"
        )

        for cluster in cluster_data:
            output_lines.append(
                f"| {cluster['name']} | {cluster['status']} | {cluster['running_tasks']} | "
                f"{cluster['pending_tasks']} | {cluster['active_services']} | {cluster['registered_container_instances']} |"
            )

        output_lines.append(f"\n**Total:** {len(cluster_data)} cluster(s)")
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

    # Task management methods
    def list_tasks(
        self,
        cluster: str,
        service: Optional[str] = None,
        limit: Optional[int] = None,
        output_format: str = "table",
        save_to: Optional[str] = None,
    ) -> None:
        """List ECS tasks in a cluster."""
        if not self.ecs_client:
            print("[red]Error: ECS client not initialized[/red]")
            return

        try:
            # List tasks
            kwargs = {"cluster": cluster}
            if service:
                kwargs["serviceName"] = service

            response = self.ecs_client.list_tasks(**kwargs)
            task_arns = response.get("taskArns", [])

            if not task_arns:
                print(f"[yellow]No tasks found in cluster '{cluster}'[/yellow]")
                return

            # Apply limit if specified
            if limit:
                task_arns = task_arns[:limit]

            # Get detailed task information
            task_details = self.ecs_client.describe_tasks(
                cluster=cluster, tasks=task_arns
            )
            tasks = task_details.get("tasks", [])

            # Format and output results
            self._output_tasks(tasks, output_format, save_to)

        except ClientError as e:
            print(f"[red]AWS Error: {e}[/red]")
        except Exception as e:
            print(f"[red]Error listing tasks: {e}[/red]")

    def describe_task(
        self, cluster: str, task_id: str, output_format: str = "json"
    ) -> None:
        """Describe a specific ECS task."""
        if not self.ecs_client:
            print("[red]Error: ECS client not initialized[/red]")
            return

        try:
            response = self.ecs_client.describe_tasks(cluster=cluster, tasks=[task_id])
            tasks = response.get("tasks", [])

            if not tasks:
                print(f"[red]Task '{task_id}' not found in cluster '{cluster}'[/red]")
                return

            task = tasks[0]
            if output_format == "json":
                print(json.dumps(task, indent=2, default=str))
            elif output_format == "table":
                self._print_task_details_table(task)
            else:
                print(json.dumps(task, indent=2, default=str))

        except ClientError as e:
            print(f"[red]AWS Error: {e}[/red]")
        except Exception as e:
            print(f"[red]Error describing task: {e}[/red]")

    def stop_task(self, cluster: str, task_id: str, reason: str = None) -> None:
        """Stop a specific ECS task."""
        if not self.ecs_client:
            print("[red]Error: ECS client not initialized[/red]")
            return

        try:
            kwargs = {"cluster": cluster, "task": task_id}
            if reason:
                kwargs["reason"] = reason

            response = self.ecs_client.stop_task(**kwargs)
            task = response.get("task", {})

            print(f"[green]Task '{task_id}' stopped successfully[/green]")
            print(f"Task ARN: {task.get('taskArn', 'N/A')}")
            print(f"Desired Status: {task.get('desiredStatus', 'N/A')}")

        except ClientError as e:
            print(f"[red]AWS Error: {e}[/red]")
        except Exception as e:
            print(f"[red]Error stopping task: {e}[/red]")

    def run_task(
        self,
        cluster: str,
        task_definition: str,
        count: int = 1,
        launch_type: str = "EC2",
        network_configuration: Optional[Dict] = None,
    ) -> None:
        """Run a one-off ECS task."""
        if not self.ecs_client:
            print("[red]Error: ECS client not initialized[/red]")
            return

        try:
            kwargs = {
                "cluster": cluster,
                "taskDefinition": task_definition,
                "count": count,
                "launchType": launch_type,
            }

            if network_configuration:
                kwargs["networkConfiguration"] = network_configuration

            response = self.ecs_client.run_task(**kwargs)
            tasks = response.get("tasks", [])
            failures = response.get("failures", [])

            if tasks:
                print(f"[green]Successfully started {len(tasks)} task(s)[/green]")
                for task in tasks:
                    print(f"Task ARN: {task.get('taskArn')}")
                    print(f"Task Definition: {task.get('taskDefinitionArn')}")
                    print(f"Desired Status: {task.get('desiredStatus')}")
                    print("---")

            if failures:
                print(f"[red]Failed to start {len(failures)} task(s)[/red]")
                for failure in failures:
                    print(f"Reason: {failure.get('reason')}")
                    print(f"Detail: {failure.get('detail')}")

        except ClientError as e:
            print(f"[red]AWS Error: {e}[/red]")
        except Exception as e:
            print(f"[red]Error running task: {e}[/red]")

    def get_task_logs(
        self,
        cluster: str,
        task_id: str,
        container: Optional[str] = None,
        follow: bool = False,
        lines: int = 100,
    ) -> None:
        """Fetch CloudWatch logs for a task."""
        if not self.ecs_client:
            print("[red]Error: ECS client not initialized[/red]")
            return

        try:
            # Get task details to find log groups
            response = self.ecs_client.describe_tasks(cluster=cluster, tasks=[task_id])
            tasks = response.get("tasks", [])

            if not tasks:
                print(f"[red]Task '{task_id}' not found in cluster '{cluster}'[/red]")
                return

            task = tasks[0]

            # Get task definition to find log configuration
            task_def_arn = task.get("taskDefinitionArn")
            if not task_def_arn:
                print("[red]Task definition ARN not found[/red]")
                return

            # For now, show a message about log fetching
            # In a full implementation, you'd use CloudWatch Logs client
            print(
                f"[blue]Log fetching for task '{task_id}' would be implemented here[/blue]"
            )
            print(f"Task Definition: {task_def_arn}")
            print(f"Container Filter: {container or 'All containers'}")
            print(f"Follow Mode: {follow}")
            print(f"Lines: {lines}")

        except ClientError as e:
            print(f"[red]AWS Error: {e}[/red]")
        except Exception as e:
            print(f"[red]Error fetching logs: {e}[/red]")

    def exec_task(
        self, cluster: str, task_id: str, container: str, command: str = "/bin/bash"
    ) -> None:
        """Execute command in a running task container."""
        if not self.ecs_client:
            print("[red]Error: ECS client not initialized[/red]")
            return

        try:
            # Check if ECS Exec is enabled
            print(
                f"[blue]ECS Exec into task '{task_id}' container '{container}'[/blue]"
            )
            print(f"Command: {command}")
            print(
                "[yellow]Note: This requires ECS Exec to be enabled on the task[/yellow]"
            )
            print(
                "[yellow]Implementation would use 'aws ecs execute-command' CLI[/yellow]"
            )

        except Exception as e:
            print(f"[red]Error executing command: {e}[/red]")

    def get_task_status(self, cluster: str, task_id: str) -> None:
        """Get current status and health of a task."""
        if not self.ecs_client:
            print("[red]Error: ECS client not initialized[/red]")
            return

        try:
            response = self.ecs_client.describe_tasks(cluster=cluster, tasks=[task_id])
            tasks = response.get("tasks", [])

            if not tasks:
                print(f"[red]Task '{task_id}' not found in cluster '{cluster}'[/red]")
                return

            task = tasks[0]
            self._print_task_status_table(task)

        except ClientError as e:
            print(f"[red]AWS Error: {e}[/red]")
        except Exception as e:
            print(f"[red]Error getting task status: {e}[/red]")

    def _output_tasks(
        self, tasks: List[Dict], output_format: str, save_to: Optional[str]
    ) -> None:
        """Output tasks in the specified format."""
        if output_format == "json":
            content = json.dumps(tasks, indent=2, default=str)
            if save_to:
                self._save_to_file(content, save_to)
            else:
                print(content)
        elif output_format == "table":
            self._print_tasks_table(tasks)
        elif output_format == "text":
            for task in tasks:
                print(f"Task: {task.get('taskArn', 'Unknown')}")
                print(f"  Status: {task.get('lastStatus', 'Unknown')}")
                print(f"  Health: {task.get('healthStatus', 'Unknown')}")
                print(
                    f"  CPU/Memory: {task.get('cpu', 'N/A')}/{task.get('memory', 'N/A')}"
                )
                print("---")
        else:
            # Default to table
            self._print_tasks_table(tasks)

    def _print_tasks_table(self, tasks: List[Dict]) -> None:
        """Print tasks in a table format."""
        table = Table(
            show_header=True,
            header_style="bold cyan",
            box=box.SIMPLE,
            border_style="dim",
        )

        table.add_column("Task ID", style="cyan")
        table.add_column("Status", style="green")
        table.add_column("Health", style="yellow")
        table.add_column("CPU", style="blue")
        table.add_column("Memory", style="blue")
        table.add_column("Created", style="dim")

        for task in tasks:
            # Extract task ID from ARN
            task_arn = task.get("taskArn", "")
            task_id = task_arn.split("/")[-1] if task_arn else "Unknown"

            created_at = task.get("createdAt")
            created_str = (
                created_at.strftime("%Y-%m-%d %H:%M:%S") if created_at else "Unknown"
            )

            table.add_row(
                task_id,
                task.get("lastStatus", "Unknown"),
                task.get("healthStatus", "Unknown"),
                task.get("cpu", "N/A"),
                task.get("memory", "N/A"),
                created_str,
            )

        self.console.print(
            f"📋 [bold]ECS Tasks[/bold] ([bright_yellow]{len(tasks)}[/bright_yellow] found)"
        )
        self.console.print()
        self.console.print(table)

    def _print_task_details_table(self, task: Dict) -> None:
        """Print detailed task information in table format."""
        table = Table(
            show_header=True,
            header_style="bold cyan",
            box=box.SIMPLE,
            border_style="dim",
        )

        table.add_column("Property", style="cyan", width=25)
        table.add_column("Value", style="white")

        # Basic task information
        task_arn = task.get("taskArn", "N/A")
        task_id = task_arn.split("/")[-1] if task_arn else "Unknown"

        table.add_row("Task ID", task_id)
        table.add_row("Task ARN", task_arn)
        table.add_row("Cluster ARN", task.get("clusterArn", "N/A"))
        table.add_row("Task Definition", task.get("taskDefinitionArn", "N/A"))
        table.add_row("Desired Status", task.get("desiredStatus", "N/A"))
        table.add_row("Last Status", task.get("lastStatus", "N/A"))
        table.add_row("Health Status", task.get("healthStatus", "N/A"))
        table.add_row("Launch Type", task.get("launchType", "N/A"))
        table.add_row("Platform Version", task.get("platformVersion", "N/A"))
        table.add_row("CPU", task.get("cpu", "N/A"))
        table.add_row("Memory", task.get("memory", "N/A"))

        # Timestamps
        created_at = task.get("createdAt")
        if created_at:
            table.add_row("Created At", created_at.strftime("%Y-%m-%d %H:%M:%S UTC"))

        started_at = task.get("startedAt")
        if started_at:
            table.add_row("Started At", started_at.strftime("%Y-%m-%d %H:%M:%S UTC"))

        print("📋 [bold]Task Details[/bold]")
        print()
        self.console.print(table)

        # Container information
        containers = task.get("containers", [])
        if containers:
            container_table = Table(
                show_header=True,
                header_style="bold cyan",
                box=box.SIMPLE,
                border_style="dim",
            )
            container_table.add_column("Name", style="cyan")
            container_table.add_column("Status", style="green")
            container_table.add_column("Health", style="yellow")
            container_table.add_column("Exit Code", style="red")

            for container in containers:
                container_table.add_row(
                    container.get("name", "Unknown"),
                    container.get("lastStatus", "Unknown"),
                    container.get("healthStatus", "Unknown"),
                    str(container.get("exitCode", "N/A")),
                )

            print()
            print(
                f"🐳 [bold]Containers[/bold] ([bright_yellow]{len(containers)}[/bright_yellow] found)"
            )
            print()
            self.console.print(container_table)

    def _print_task_status_table(self, task: Dict) -> None:
        """Print task status in a focused table format."""
        table = Table(
            show_header=True,
            header_style="bold cyan",
            box=box.SIMPLE,
            border_style="dim",
        )

        table.add_column("Property", style="cyan", width=20)
        table.add_column("Value", style="white")

        # Extract task ID from ARN
        task_arn = task.get("taskArn", "")
        task_id = task_arn.split("/")[-1] if task_arn else "Unknown"

        table.add_row("Task ID", task_id)
        table.add_row("Desired Status", task.get("desiredStatus", "N/A"))
        table.add_row("Last Status", task.get("lastStatus", "N/A"))
        table.add_row("Health Status", task.get("healthStatus", "N/A"))
        table.add_row("Connectivity", task.get("connectivity", "N/A"))
        table.add_row("Stop Code", task.get("stopCode", "N/A"))
        table.add_row("Stop Reason", task.get("stopReason", "N/A"))

        print("📊 [bold]Task Status[/bold]")
        print()
        self.console.print(table)

        # Container status
        containers = task.get("containers", [])
        if containers:
            container_table = Table(
                show_header=True,
                header_style="bold cyan",
                box=box.SIMPLE,
                border_style="dim",
            )
            container_table.add_column("Container", style="cyan")
            container_table.add_column("Status", style="green")
            container_table.add_column("Health", style="yellow")
            container_table.add_column("Reason", style="white")

            for container in containers:
                container_table.add_row(
                    container.get("name", "Unknown"),
                    container.get("lastStatus", "Unknown"),
                    container.get("healthStatus", "Unknown"),
                    container.get("reason", "N/A"),
                )

            print()
            print(
                f"🐳 [bold]Container Status[/bold] ([bright_yellow]{len(containers)}[/bright_yellow] found)"
            )
            print()
            self.console.print(container_table)

    def describe_cluster(self, cluster_name: str, output_format: str = "table") -> None:
        """Describe a specific ECS cluster."""
        if not self.ecs_client:
            print("[red]Error: ECS client not initialized[/red]")
            return

        try:
            response = self.ecs_client.describe_clusters(
                clusters=[cluster_name],
                include=["ATTACHMENTS", "CONFIGURATIONS", "STATISTICS", "TAGS"],
            )

            clusters = response.get("clusters", [])
            if not clusters:
                print(f"[red]Cluster '{cluster_name}' not found[/red]")
                return

            cluster = clusters[0]

            if output_format == "json":
                print(json.dumps(cluster, indent=2, default=str))
            else:
                self._print_cluster_details(cluster)

        except ClientError as e:
            print(f"[red]AWS Error: {e}[/red]")
        except Exception as e:
            print(f"[red]Error describing cluster: {e}[/red]")

    def list_cluster_services(
        self, cluster_name: str, output_format: str = "table"
    ) -> None:
        """List all services in a specific cluster."""
        if not self.ecs_client:
            print("[red]Error: ECS client not initialized[/red]")
            return

        try:
            # First get the list of service ARNs
            response = self.ecs_client.list_services(cluster=cluster_name)
            service_arns = response.get("serviceArns", [])

            if not service_arns:
                print(f"[yellow]No services found in cluster '{cluster_name}'[/yellow]")
                return

            # Get detailed information about the services
            services_response = self.ecs_client.describe_services(
                cluster=cluster_name, services=service_arns
            )
            services = services_response.get("services", [])

            if output_format == "json":
                print(json.dumps(services, indent=2, default=str))
            else:
                self._print_cluster_services_table(services, cluster_name)

        except ClientError as e:
            print(f"[red]AWS Error: {e}[/red]")
        except Exception as e:
            print(f"[red]Error listing cluster services: {e}[/red]")

    def get_cluster_capacity(
        self, cluster_name: str, output_format: str = "table"
    ) -> None:
        """Get cluster capacity information."""
        if not self.ecs_client:
            print("[red]Error: ECS client not initialized[/red]")
            return

        try:
            # Get cluster description with statistics
            cluster_response = self.ecs_client.describe_clusters(
                clusters=[cluster_name], include=["STATISTICS"]
            )

            clusters = cluster_response.get("clusters", [])
            if not clusters:
                print(f"[red]Cluster '{cluster_name}' not found[/red]")
                return

            cluster = clusters[0]

            # Get container instances for capacity info
            instances_response = self.ecs_client.list_container_instances(
                cluster=cluster_name
            )
            instance_arns = instances_response.get("containerInstanceArns", [])

            capacity_data = {"cluster": cluster, "instances": []}

            if instance_arns:
                instances_details = self.ecs_client.describe_container_instances(
                    cluster=cluster_name, containerInstances=instance_arns
                )
                capacity_data["instances"] = instances_details.get(
                    "containerInstances", []
                )

            if output_format == "json":
                print(json.dumps(capacity_data, indent=2, default=str))
            else:
                self._print_cluster_capacity_table(capacity_data)

        except ClientError as e:
            print(f"[red]AWS Error: {e}[/red]")
        except Exception as e:
            print(f"[red]Error getting cluster capacity: {e}[/red]")

    def _print_cluster_details(self, cluster: Dict) -> None:
        """Print cluster details in a readable format."""
        table = Table(
            show_header=True,
            header_style="bold cyan",
            box=box.SIMPLE,
            border_style="dim",
        )

        table.add_column("Property", style="cyan", width=25)
        table.add_column("Value", style="white")

        # Basic cluster information
        table.add_row("Cluster Name", cluster.get("clusterName", "N/A"))
        table.add_row("Cluster ARN", cluster.get("clusterArn", "N/A"))
        table.add_row("Status", cluster.get("status", "N/A"))
        table.add_row("Running Tasks", str(cluster.get("runningTasksCount", 0)))
        table.add_row("Pending Tasks", str(cluster.get("pendingTasksCount", 0)))
        table.add_row("Active Services", str(cluster.get("activeServicesCount", 0)))
        table.add_row(
            "Registered Instances",
            str(cluster.get("registeredContainerInstancesCount", 0)),
        )

        # Statistics
        statistics = cluster.get("statistics", [])
        for stat in statistics:
            name = stat.get("name", "")
            value = stat.get("value", "")
            if name and value:
                # Format the statistic name nicely by adding spaces
                display_name = re.sub(r"([a-z])([A-Z])", r"\1 \2", name)
                display_name = display_name.replace("Count", "").strip()
                table.add_row(f"📊 {display_name}", value)

        print("🏗️ [bold]Cluster Details[/bold]")
        print()
        self.console.print(table)

        # Tags if available
        tags = cluster.get("tags", [])
        if tags:
            tags_table = Table(
                show_header=True,
                header_style="bold cyan",
                box=box.SIMPLE,
                border_style="dim",
            )
            tags_table.add_column("Key", style="cyan")
            tags_table.add_column("Value", style="white")

            for tag in tags:
                tags_table.add_row(tag.get("key", ""), tag.get("value", ""))

            print()
            print(
                f"🏷️ [bold]Tags[/bold] ([bright_yellow]{len(tags)}[/bright_yellow] found)"
            )
            print()
            self.console.print(tags_table)

    def _print_cluster_services_table(
        self, services: List[Dict], cluster_name: str
    ) -> None:
        """Print cluster services in a table format."""
        table = Table(
            show_header=True,
            header_style="bold cyan",
            box=box.SIMPLE,
            border_style="dim",
        )

        table.add_column("Service Name", style="cyan")
        table.add_column("Status", style="white")
        table.add_column("Task Definition", style="white")
        table.add_column("Running", style="green")
        table.add_column("Pending", style="yellow")
        table.add_column("Desired", style="white")
        table.add_column("Launch Type", style="white")

        for service in services:
            table.add_row(
                service.get("serviceName", "N/A"),
                service.get("status", "N/A"),
                (
                    service.get("taskDefinition", "N/A").split("/")[-1]
                    if service.get("taskDefinition")
                    else "N/A"
                ),
                str(service.get("runningCount", 0)),
                str(service.get("pendingCount", 0)),
                str(service.get("desiredCount", 0)),
                service.get("launchType", "N/A"),
            )

        print(
            f"🚀 [bold]Services in Cluster '{cluster_name}'[/bold] ([bright_yellow]{len(services)}[/bright_yellow] found)"
        )
        print()
        self.console.print(table)

    def _print_cluster_capacity_table(self, capacity_data: Dict) -> None:
        """Print cluster capacity information in a table format."""
        cluster = capacity_data["cluster"]
        instances = capacity_data["instances"]

        # Cluster overview
        overview_table = Table(
            show_header=True,
            header_style="bold cyan",
            box=box.SIMPLE,
            border_style="dim",
        )

        overview_table.add_column("Metric", style="cyan", width=25)
        overview_table.add_column("Count", style="white")

        overview_table.add_row(
            "Total Instances", str(cluster.get("registeredContainerInstancesCount", 0))
        )
        overview_table.add_row(
            "Running Tasks", str(cluster.get("runningTasksCount", 0))
        )
        overview_table.add_row(
            "Pending Tasks", str(cluster.get("pendingTasksCount", 0))
        )
        overview_table.add_row(
            "Active Services", str(cluster.get("activeServicesCount", 0))
        )

        print("⚙️ [bold]Cluster Capacity Overview[/bold]")
        print()
        self.console.print(overview_table)

        # Container instances details
        if instances:
            instances_table = Table(
                show_header=True,
                header_style="bold cyan",
                box=box.SIMPLE,
                border_style="dim",
            )

            instances_table.add_column("Instance ID", style="cyan")
            instances_table.add_column("Status", style="white")
            instances_table.add_column("Running Tasks", style="green")
            instances_table.add_column("Pending Tasks", style="yellow")
            instances_table.add_column("CPU (Available)", style="white")
            instances_table.add_column("Memory (Available)", style="white")

            for instance in instances:
                ec2_instance_id = instance.get("ec2InstanceId", "N/A")
                status = instance.get("status", "N/A")
                running_tasks = instance.get("runningTasksCount", 0)
                pending_tasks = instance.get("pendingTasksCount", 0)

                # Extract resource information
                cpu_available = "N/A"
                memory_available = "N/A"

                remaining_resources = instance.get("remainingResources", [])
                for resource in remaining_resources:
                    if resource.get("name") == "CPU":
                        cpu_available = f"{resource.get('integerValue', 0)}"
                    elif resource.get("name") == "MEMORY":
                        memory_available = f"{resource.get('integerValue', 0)} MB"

                instances_table.add_row(
                    ec2_instance_id,
                    status,
                    str(running_tasks),
                    str(pending_tasks),
                    cpu_available,
                    memory_available,
                )

            print()
            print(
                f"🖥️ [bold]Container Instances[/bold] ([bright_yellow]{len(instances)}[/bright_yellow] found)"
            )
            print()
            self.console.print(instances_table)
        else:
            print()
            print(
                "[yellow]No container instances found (this might be a Fargate-only cluster)[/yellow]"
            )

    def list_services(
        self,
        cluster: str,
        output_format: str = "table",
    ) -> None:
        """List all ECS services in a specific cluster.

        Args:
            cluster: ECS cluster name
            output_format: Output format (table, json, yaml)
        """
        if not self.ecs_client:
            print("[red]Error: ECS client not initialized[/red]")
            return

        try:
            # List services
            response = self.ecs_client.list_services(cluster=cluster)
            service_arns = response.get("serviceArns", [])

            if not service_arns:
                print(f"[yellow]No services found in cluster '{cluster}'[/yellow]")
                return

            # Get detailed service information
            services_response = self.ecs_client.describe_services(
                cluster=cluster, services=service_arns
            )
            services = services_response.get("services", [])

            if output_format == "json":
                print(json.dumps(services, indent=2, default=str))
                return
            elif output_format == "yaml":
                print(yaml.dump(services, default_flow_style=False))
                return

            # Create table
            table = Table(title=f"ECS Services in Cluster: {cluster}", box=box.SIMPLE)
            table.add_column("Service Name", style="cyan")
            table.add_column("Status", style="green")
            table.add_column("Task Definition", style="blue")
            table.add_column("Running/Desired", style="magenta")
            table.add_column("Pending", style="yellow")
            table.add_column("Platform Version", style="dim")

            for service in services:
                service_name = service.get("serviceName", "N/A")
                status = service.get("status", "N/A")
                task_definition = service.get("taskDefinition", "N/A")
                running_count = service.get("runningCount", 0)
                desired_count = service.get("desiredCount", 0)
                pending_count = service.get("pendingCount", 0)
                platform_version = service.get("platformVersion", "N/A")

                # Extract just the task definition name:revision
                if "/" in task_definition:
                    task_definition = task_definition.split("/")[-1]

                table.add_row(
                    service_name,
                    status,
                    task_definition,
                    f"{running_count}/{desired_count}",
                    str(pending_count),
                    platform_version,
                )

            print()
            self.console.print(table)
            print()
            print(
                f"📊 Found [bright_yellow]{len(services)}[/bright_yellow] services in cluster '[cyan]{cluster}[/cyan]'"
            )

        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            if error_code == "ClusterNotFoundException":
                print(f"[red]Error: Cluster '{cluster}' not found[/red]")
            else:
                print(f"[red]Error listing services: {e}[/red]")
        except Exception as e:
            print(f"[red]Error listing services: {e}[/red]")

    def describe_service(
        self,
        cluster: str,
        service_name: str,
        output_format: str = "table",
    ) -> None:
        """Show detailed information about a specific ECS service.

        Args:
            cluster: ECS cluster name
            service_name: Service name
            output_format: Output format (table, json)
        """
        if not self.ecs_client:
            print("[red]Error: ECS client not initialized[/red]")
            return

        try:
            # Get service details
            response = self.ecs_client.describe_services(
                cluster=cluster, services=[service_name]
            )
            services = response.get("services", [])

            if not services:
                print(
                    f"[red]Service '{service_name}' not found in cluster '{cluster}'[/red]"
                )
                return

            service = services[0]

            if output_format == "json":
                print(json.dumps(service, indent=2, default=str))
                return

            # Create detailed table
            table = Table(title=f"Service Details: {service_name}", box=box.SIMPLE)
            table.add_column("Property", style="cyan", width=25)
            table.add_column("Value", style="white")

            # Basic service information
            table.add_row("Service Name", service.get("serviceName", "N/A"))
            table.add_row("Service ARN", service.get("serviceArn", "N/A"))
            table.add_row("Status", service.get("status", "N/A"))
            table.add_row("Task Definition", service.get("taskDefinition", "N/A"))
            table.add_row("Platform Version", service.get("platformVersion", "N/A"))
            table.add_row("Launch Type", service.get("launchType", "N/A"))

            # Task counts
            table.add_row("Running Count", str(service.get("runningCount", 0)))
            table.add_row("Desired Count", str(service.get("desiredCount", 0)))
            table.add_row("Pending Count", str(service.get("pendingCount", 0)))

            # Deployment information
            deployments = service.get("deployments", [])
            if deployments:
                primary_deployment = deployments[0]
                table.add_row(
                    "Deployment Status", primary_deployment.get("status", "N/A")
                )
                table.add_row(
                    "Deployment Created",
                    self._format_date(primary_deployment.get("createdAt")),
                )
                table.add_row(
                    "Deployment Updated",
                    self._format_date(primary_deployment.get("updatedAt")),
                )

            # Network configuration
            network_config = service.get("networkConfiguration", {})
            if network_config:
                awsvpc_config = network_config.get("awsvpcConfiguration", {})
                if awsvpc_config:
                    subnets = awsvpc_config.get("subnets", [])
                    security_groups = awsvpc_config.get("securityGroups", [])
                    table.add_row("Subnets", ", ".join(subnets) if subnets else "N/A")
                    table.add_row(
                        "Security Groups",
                        ", ".join(security_groups) if security_groups else "N/A",
                    )
                    table.add_row(
                        "Assign Public IP", awsvpc_config.get("assignPublicIp", "N/A")
                    )

            # Service creation/update times
            table.add_row("Created At", self._format_date(service.get("createdAt")))

            print()
            self.console.print(table)

            # Show deployment history if multiple deployments
            if len(deployments) > 1:
                print()
                deployment_table = Table(title="Deployment History", box=box.SIMPLE)
                deployment_table.add_column("Status", style="green")
                deployment_table.add_column("Task Definition", style="blue")
                deployment_table.add_column("Running/Desired", style="magenta")
                deployment_table.add_column("Created At", style="dim")

                for deployment in deployments:
                    task_def = deployment.get("taskDefinition", "N/A")
                    if "/" in task_def:
                        task_def = task_def.split("/")[-1]

                    deployment_table.add_row(
                        deployment.get("status", "N/A"),
                        task_def,
                        f"{deployment.get('runningCount', 0)}/{deployment.get('desiredCount', 0)}",
                        self._format_date(deployment.get("createdAt")),
                    )

                self.console.print(deployment_table)

        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            if error_code == "ClusterNotFoundException":
                print(f"[red]Error: Cluster '{cluster}' not found[/red]")
            elif error_code == "ServiceNotFoundException":
                print(
                    f"[red]Error: Service '{service_name}' not found in cluster '{cluster}'[/red]"
                )
            else:
                print(f"[red]Error describing service: {e}[/red]")
        except Exception as e:
            print(f"[red]Error describing service: {e}[/red]")

    def update_service(
        self,
        cluster: str,
        service_name: str,
        desired_count: Optional[int] = None,
        task_definition: Optional[str] = None,
    ) -> None:
        """Update an ECS service configuration.

        Args:
            cluster: ECS cluster name
            service_name: Service name
            desired_count: Desired number of tasks
            task_definition: Task definition ARN or family:revision
        """
        if not self.ecs_client:
            print("[red]Error: ECS client not initialized[/red]")
            return

        if not desired_count and not task_definition:
            print(
                "[red]Error: Either desired_count or task_definition must be specified[/red]"
            )
            return

        try:
            # Prepare update parameters
            update_params: Dict[str, Any] = {
                "cluster": cluster,
                "service": service_name,
            }

            if desired_count is not None:
                update_params["desiredCount"] = desired_count

            if task_definition:
                update_params["taskDefinition"] = task_definition

            # Update the service
            response = self.ecs_client.update_service(**update_params)
            service = response.get("service", {})

            print(
                f"[green]✅ Service '{service_name}' update initiated successfully[/green]"
            )
            print()

            # Show update details
            table = Table(title="Service Update Details", box=box.SIMPLE)
            table.add_column("Property", style="cyan")
            table.add_column("Value", style="white")

            table.add_row("Service Name", service.get("serviceName", "N/A"))
            table.add_row("Status", service.get("status", "N/A"))

            if desired_count is not None:
                table.add_row("New Desired Count", str(desired_count))

            if task_definition:
                task_def_display = task_definition
                if "/" in task_def_display:
                    task_def_display = task_def_display.split("/")[-1]
                table.add_row("New Task Definition", task_def_display)

            table.add_row("Running Count", str(service.get("runningCount", 0)))
            table.add_row("Pending Count", str(service.get("pendingCount", 0)))

            self.console.print(table)
            print()
            print(
                "[dim]💡 Note: Service update may take a few minutes to complete.[/dim]"
            )

        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            if error_code == "ClusterNotFoundException":
                print(f"[red]Error: Cluster '{cluster}' not found[/red]")
            elif error_code == "ServiceNotFoundException":
                print(
                    f"[red]Error: Service '{service_name}' not found in cluster '{cluster}'[/red]"
                )
            elif error_code == "InvalidParameterException":
                print(
                    f"[red]Error: Invalid parameter - {e.response['Error']['Message']}[/red]"
                )
            else:
                print(f"[red]Error updating service: {e}[/red]")
        except Exception as e:
            print(f"[red]Error updating service: {e}[/red]")

    def restart_service(
        self,
        cluster: str,
        service_name: str,
    ) -> None:
        """Restart an ECS service by forcing a new deployment.

        Args:
            cluster: ECS cluster name
            service_name: Service name
        """
        if not self.ecs_client:
            print("[red]Error: ECS client not initialized[/red]")
            return

        try:
            # Force new deployment
            response = self.ecs_client.update_service(
                cluster=cluster,
                service=service_name,
                forceNewDeployment=True,
            )

            service = response.get("service", {})

            print(
                f"[green]✅ Service '{service_name}' restart initiated successfully[/green]"
            )
            print()

            # Show restart details
            table = Table(title="Service Restart Details", box=box.SIMPLE)
            table.add_column("Property", style="cyan")
            table.add_column("Value", style="white")

            table.add_row("Service Name", service.get("serviceName", "N/A"))
            table.add_row("Status", service.get("status", "N/A"))
            table.add_row("Task Definition", service.get("taskDefinition", "N/A"))
            table.add_row("Desired Count", str(service.get("desiredCount", 0)))
            table.add_row("Running Count", str(service.get("runningCount", 0)))
            table.add_row("Pending Count", str(service.get("pendingCount", 0)))

            self.console.print(table)
            print()
            print(
                "[dim]💡 Note: Service restart may take a few minutes to complete.[/dim]"
            )

        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            if error_code == "ClusterNotFoundException":
                print(f"[red]Error: Cluster '{cluster}' not found[/red]")
            elif error_code == "ServiceNotFoundException":
                print(
                    f"[red]Error: Service '{service_name}' not found in cluster '{cluster}'[/red]"
                )
            else:
                print(f"[red]Error restarting service: {e}[/red]")
        except Exception as e:
            print(f"[red]Error restarting service: {e}[/red]")
