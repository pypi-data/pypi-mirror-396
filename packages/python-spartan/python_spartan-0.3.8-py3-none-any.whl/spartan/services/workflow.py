"""Workflow service for managing AWS Step Functions state machines."""

import json
from datetime import datetime
from typing import Optional, Union

import boto3
import yaml
from botocore.exceptions import ClientError, NoCredentialsError
from rich import box, print
from rich.console import Console
from rich.table import Table

from spartan.utils.filters import FilterUtility, SortUtility


class WorkflowService:
    """Service class for managing AWS Step Functions workflows."""

    def __init__(self, region: Optional[str] = None, profile: Optional[str] = None):
        """Initialize the WorkflowService with AWS Step Functions client.

        Args:
            region: AWS region to use (overrides default/profile)
            profile: AWS CLI profile to use
        """
        try:
            session = (
                boto3.Session(profile_name=profile) if profile else boto3.Session()
            )
            self.stepfunctions_client = session.client(
                "stepfunctions", region_name=region
            )
            self.console = Console()
        except NoCredentialsError:
            print(
                "[red]Error: AWS credentials not found. Please configure your AWS credentials.[/red]"
            )
            raise
        except Exception as e:
            print(f"[red]Error initializing Step Functions client: {e}[/red]")
            raise

    def _validate_output_format(self, output_format: str) -> str:
        """Validate and normalize output format."""
        valid_formats = ["table", "json", "yaml", "markdown", "csv", "text"]
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

    def _get_workflow_health_status(self, state_machine_arn: str) -> dict:
        """Get health status and recent execution info for a workflow."""
        try:
            response = self.stepfunctions_client.list_executions(
                stateMachineArn=state_machine_arn, maxResults=20
            )

            executions = response.get("executions", [])

            if not executions:
                return {
                    "status": "INACTIVE",
                    "icon": "⚪",
                    "last_execution": "Never",
                    "success_rate": "N/A",
                    "total_executions": 0,
                    "trend": "➖",
                    "last_24h": 0,
                }

            # Get trend information
            trend_info = self._calculate_execution_trend(executions)

            succeeded = sum(1 for ex in executions if ex.get("status") == "SUCCEEDED")
            failed = sum(1 for ex in executions if ex.get("status") == "FAILED")
            running = sum(1 for ex in executions if ex.get("status") == "RUNNING")

            total = len(executions)
            success_rate = (succeeded / total * 100) if total > 0 else 0

            if running > 0:
                status, icon = "RUNNING", "🔵"
            elif failed > succeeded:
                status, icon = "UNHEALTHY", "🔴"
            elif success_rate >= 90:
                status, icon = "HEALTHY", "🟢"
            elif success_rate >= 70:
                status, icon = "WARNING", "🟡"
            else:
                status, icon = "CRITICAL", "🔴"

            last_execution = "N/A"
            if executions:
                last_start = executions[0].get("startDate")
                if last_start:
                    now = datetime.now(last_start.tzinfo)
                    diff = now - last_start

                    if diff.days > 0:
                        last_execution = f"{diff.days}d ago"
                    elif diff.seconds > 3600:
                        last_execution = f"{diff.seconds // 3600}h ago"
                    elif diff.seconds > 60:
                        last_execution = f"{diff.seconds // 60}m ago"
                    else:
                        last_execution = "Just now"

            return {
                "status": status,
                "icon": icon,
                "last_execution": last_execution,
                "success_rate": f"{success_rate:.0f}%" if total > 0 else "N/A",
                "total_executions": total,
                "trend": trend_info["trend_icon"],
                "last_24h": trend_info["last_24h_count"],
            }

        except Exception:
            return {
                "status": "UNKNOWN",
                "icon": "❓",
                "last_execution": "Unknown",
                "success_rate": "N/A",
                "total_executions": 0,
                "trend": "❓",
                "last_24h": 0,
            }

    def _calculate_execution_trend(self, executions: list) -> dict:
        """Calculate execution trend from recent executions."""
        try:
            now = datetime.now()
            last_24h = now - datetime.timedelta(days=1)
            last_48h = now - datetime.timedelta(days=2)

            # Count executions in last 24h and previous 24h
            recent_count = 0
            previous_count = 0

            for execution in executions:
                start_date = execution.get("startDate")
                if start_date:
                    # Make start_date timezone-aware if it isn't already
                    if start_date.tzinfo is None:
                        start_date = start_date.replace(tzinfo=now.tzinfo)

                    if start_date >= last_24h:
                        recent_count += 1
                    elif start_date >= last_48h:
                        previous_count += 1

            # Calculate trend
            if previous_count == 0:
                if recent_count > 0:
                    trend_icon = "📈"  # New activity
                else:
                    trend_icon = "➖"  # No activity
            else:
                change_percent = (
                    (recent_count - previous_count) / previous_count
                ) * 100
                if change_percent > 20:
                    trend_icon = "📈"  # Significant increase
                elif change_percent < -20:
                    trend_icon = "📉"  # Significant decrease
                else:
                    trend_icon = "➖"  # Stable

            return {
                "trend_icon": trend_icon,
                "last_24h_count": recent_count,
                "previous_24h_count": previous_count,
            }

        except Exception:
            return {"trend_icon": "❓", "last_24h_count": 0, "previous_24h_count": 0}

    def list_workflows(  # noqa: C901
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
        interactive: bool = False,
    ) -> None:
        """List all Step Functions state machines with advanced filtering.

        Args:
            output_format: Output format (table, json, yaml, markdown, csv)
            prefix_filter: Filter workflows by name prefix
            regex_match: Filter workflows by regex pattern
            contains_filter: Filter workflows whose names contain a substring
            sort_by: Sort by field (name, creationDate)
            sort_order: Sort order (asc, desc)
            limit: Limit the number of results shown
            show_filters: Show which filters were applied in the output
            save_to: Save the results to a file (.json, .yaml, .csv, etc.)
        """
        try:
            output_format = self._validate_output_format(output_format)

            # Validate sort field
            valid_sort_fields = ["name", "creationDate"]
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
                print("[blue]Fetching Step Functions state machines...[/blue]")

            # Get all state machines using pagination
            state_machines = []
            paginator = self.stepfunctions_client.get_paginator("list_state_machines")

            for page in paginator.paginate():
                state_machines.extend(page.get("stateMachines", []))

            if not state_machines:
                self._handle_no_workflows_found(output_format)
                return

            # Process workflow data with health status
            workflow_data = []
            for state_machine in state_machines:
                arn = state_machine.get("stateMachineArn", "N/A")
                health_info = self._get_workflow_health_status(arn)

                workflow_info = {
                    "name": state_machine.get("name", "N/A"),
                    "type": state_machine.get("type", "N/A"),
                    "created": self._format_date(state_machine.get("creationDate")),
                    "creationDate": state_machine.get(
                        "creationDate"
                    ),  # Keep original for sorting
                    "arn": arn,
                    "status": health_info["status"],
                    "status_icon": health_info["icon"],
                    "last_execution": health_info["last_execution"],
                    "success_rate": health_info["success_rate"],
                    "total_executions": health_info["total_executions"],
                    "trend": health_info["trend"],
                    "last_24h": health_info["last_24h"],
                }
                workflow_data.append(workflow_info)

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

            if filters:
                workflow_data = FilterUtility.apply_multiple_filters(
                    workflow_data, filters
                )

            # Apply sorting
            reverse = sort_order.lower() == "desc"
            if sort_by == "creationDate":
                workflow_data = SortUtility.sort_by_date(
                    workflow_data, "creationDate", reverse=reverse
                )
            else:
                case_sensitive = False if sort_by == "name" else True
                workflow_data = SortUtility.sort_items(
                    workflow_data,
                    sort_by,
                    reverse=reverse,
                    case_sensitive=case_sensitive,
                )

            # Apply limit
            if limit:
                workflow_data = workflow_data[:limit]

            # Check if any workflows remain after filtering
            if not workflow_data:
                self._handle_no_workflows_after_filter(
                    output_format, prefix_filter, regex_match, contains_filter
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
            if limit:
                applied_filters["limit"] = str(limit)

            # Output in requested format
            if output_format == "csv":
                self._print_workflows_csv(
                    workflow_data, show_filters, applied_filters, save_to
                )
            elif output_format == "table":
                self._print_workflows_table(
                    workflow_data, show_filters, applied_filters, sort_by, sort_order
                )

                # Interactive mode for table output
                if interactive:
                    self._handle_interactive_mode(workflow_data)

            elif output_format == "json":
                output_data = {
                    "workflows": workflow_data,
                    "count": len(workflow_data),
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
                    "workflows": workflow_data,
                    "count": len(workflow_data),
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
                self._print_workflows_markdown(
                    workflow_data,
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
            print(f"[red]Error listing workflows: {e}[/red]")

    def _handle_interactive_mode(self, workflow_data: list) -> None:
        """Handle interactive mode for workflow selection and actions."""
        if not workflow_data:
            return

        print("\n[bold cyan]🎯 Interactive Mode[/bold cyan]")
        print("Select a workflow for quick actions:")

        # Display numbered workflow list
        for i, workflow in enumerate(workflow_data, 1):
            status_icon = workflow.get("status_icon", "⚪")
            print(f"  {i}. {status_icon} {workflow['name']}")

        print(f"  {len(workflow_data) + 1}. Exit")

        try:
            while True:
                choice = input("\nEnter your choice (number): ").strip()

                if not choice.isdigit():
                    print("Please enter a valid number.")
                    continue

                choice_num = int(choice)

                if choice_num == len(workflow_data) + 1:
                    print("Goodbye! 👋")
                    break
                elif 1 <= choice_num <= len(workflow_data):
                    selected_workflow = workflow_data[choice_num - 1]
                    self._show_workflow_actions(selected_workflow)
                    break
                else:
                    print(
                        f"Please enter a number between 1 and {len(workflow_data) + 1}."
                    )

        except KeyboardInterrupt:
            print("\n\nOperation cancelled. 👋")
        except Exception as e:
            print(f"\n[red]Error in interactive mode: {e}[/red]")

    def _get_recent_executions(self, workflow_name: str, limit: int = 10) -> list:
        """Get recent executions for a workflow."""
        try:
            state_machine_arn = self._find_state_machine_arn(workflow_name)
            if not state_machine_arn:
                return []

            response = self.stepfunctions_client.list_executions(
                stateMachineArn=state_machine_arn, maxResults=limit
            )
            return response.get("executions", [])
        except Exception:
            return []

    def _interactive_execution_details(self, exec_name: str) -> None:
        """Interactive execution details with various view options."""
        while True:
            try:
                print(f"\n[bold green]🔍 Execution Details: {exec_name}[/bold green]")
                print("\n[bold]View Options:[/bold]")
                print("  1. 📋 Basic details")
                print("  2. 📥 Show input")
                print("  3. 📤 Show output")
                print("  4. 🔄 Show states")
                print("  5. 🔧 Show state I/O")
                print("  6. 🔍 Show diff")
                print("  7. 📊 Full details")
                print("  8. ⬅️  Back")

                choice = input("\nSelect option (1-8): ").strip()

                if choice == "1":
                    self.get_execution(exec_name)
                elif choice == "2":
                    self.get_execution(exec_name, show_input=True)
                elif choice == "3":
                    self.get_execution(exec_name, show_output=True)
                elif choice == "4":
                    self.get_execution(exec_name, show_states=True)
                elif choice == "5":
                    self.get_execution(exec_name, show_state_io=True)
                elif choice == "6":
                    self.get_execution(exec_name, show_diff=True)
                elif choice == "7":
                    self.get_execution(
                        exec_name,
                        show_input=True,
                        show_output=True,
                        show_states=True,
                        show_state_io=True,
                    )
                elif choice == "8":
                    break
                else:
                    print("[red]Please enter a number between 1 and 8[/red]")

                if choice in ["1", "2", "3", "4", "5", "6", "7"]:
                    input("\nPress Enter to continue...")

            except KeyboardInterrupt:
                print("\n\nReturning...")
                break
            except Exception as e:
                print(f"\n[red]Error: {e}[/red]")
                input("Press Enter to continue...")

    def _interactive_list_executions(self, workflow_name: str) -> None:
        """Interactive execution listing with configurable limit."""
        limit = 10  # Default limit

        while True:
            try:
                # List executions with current limit
                print(f"\n[cyan]📋 Recent executions (showing last {limit}):[/cyan]")
                self.list_executions(workflow_name, max_results=limit)

                print("\n[bold]Options:[/bold]")
                print("  1. 🎯 Select first execution (get details)")
                print("  2. 🔄 Refresh (same limit)")
                print("  3. 📈 Show more executions")
                print("  4. 📉 Show fewer executions")
                print("  5. 🎯 Set custom limit")
                print("  6. ⬅️  Back to workflow actions")

                choice = input("\nSelect option (1-6): ").strip()

                if choice == "1":
                    # Get first execution details
                    executions = self._get_recent_executions(workflow_name, 1)
                    if executions:
                        exec_name = executions[0].get("name", "")
                        self._interactive_execution_details(exec_name)
                    else:
                        print("[yellow]No executions found[/yellow]")
                        input("Press Enter to continue...")
                elif choice == "2":
                    continue  # Refresh with same limit
                elif choice == "3":
                    limit = min(limit * 2, 100)  # Double limit, max 100
                    print(f"[green]Increased limit to {limit}[/green]")
                elif choice == "4":
                    limit = max(limit // 2, 5)  # Half limit, min 5
                    print(f"[green]Decreased limit to {limit}[/green]")
                elif choice == "5":
                    try:
                        new_limit = int(input("Enter new limit (5-100): ").strip())
                        if 5 <= new_limit <= 100:
                            limit = new_limit
                            print(f"[green]Set limit to {limit}[/green]")
                        else:
                            print("[red]Limit must be between 5 and 100[/red]")
                    except ValueError:
                        print("[red]Please enter a valid number[/red]")
                elif choice == "6":
                    break
                else:
                    print("[red]Please enter a number between 1 and 6[/red]")

            except KeyboardInterrupt:
                print("\n\nReturning to workflow actions...")
                break
            except Exception as e:
                print(f"\n[red]Error: {e}[/red]")
                break

    def _show_workflow_actions(self, workflow: dict) -> None:
        """Show available actions for selected workflow."""
        workflow_name = workflow["name"]
        print(f"\n[bold green]📋 Actions for: {workflow_name}[/bold green]")

        actions = [
            "1. 📄 Describe workflow",
            "2. 🔄 List executions",
            "3. 🎨 Visualize workflow",
            "4. 🔧 Analyze resources",
            "5. ⬅️  Back to workflow list",
            "6. 🚺 Exit",
        ]

        for action in actions:
            print(f"  {action}")

        try:
            while True:
                action_choice = input("\nSelect action (number): ").strip()

                if not action_choice.isdigit():
                    print("Please enter a valid number.")
                    continue

                action_num = int(action_choice)

                if action_num == 1:
                    print(f"\n[blue]Describing workflow: {workflow_name}[/blue]")
                    self.describe_workflow(workflow_name)
                    break
                elif action_num == 2:
                    print(f"\n[blue]Listing executions for: {workflow_name}[/blue]")
                    self._interactive_list_executions(workflow_name)
                    break
                elif action_num == 3:
                    print(f"\n[blue]Visualizing workflow: {workflow_name}[/blue]")
                    self.visualize_workflow(workflow_name)
                    break
                elif action_num == 4:
                    print(f"\n[blue]Analyzing resources for: {workflow_name}[/blue]")
                    self.analyze_workflow_resources(workflow_name)
                    break
                elif action_num == 5:
                    return  # Go back to workflow list
                elif action_num == 6:
                    print("Goodbye! 👋")
                    return
                else:
                    print("Please enter a number between 1 and 6.")

        except KeyboardInterrupt:
            print("\n\nOperation cancelled. 👋")
        except Exception as e:
            print(f"\n[red]Error executing action: {e}[/red]")

    def _print_workflows_table(
        self,
        workflow_data: list,
        show_filters: bool = False,
        applied_filters: dict = None,
        sort_by: str = "name",
        sort_order: str = "asc",
    ) -> None:
        """Print workflows in a formatted table."""
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
        table.add_column("Name", style="bright_blue", no_wrap=False)
        table.add_column("Status", style="white", no_wrap=True)
        table.add_column("Last 24h", style="magenta", no_wrap=True)
        table.add_column("Trend", style="white", no_wrap=True)
        table.add_column("Success Rate", style="cyan", no_wrap=True)
        table.add_column("Type", style="green")
        table.add_column("Created", style="dim")

        for workflow in workflow_data:
            # Color code the status
            status_display = f"{workflow['status_icon']} {workflow['status']}"

            # Color code success rate
            success_rate = workflow["success_rate"]
            if success_rate != "N/A":
                rate_val = float(success_rate.replace("%", ""))
                if rate_val >= 90:
                    success_rate = f"[green]{success_rate}[/green]"
                elif rate_val >= 70:
                    success_rate = f"[yellow]{success_rate}[/yellow]"
                else:
                    success_rate = f"[red]{success_rate}[/red]"

            table.add_row(
                workflow["name"],
                status_display,
                f"{workflow['last_24h']} runs",
                workflow["trend"],
                success_rate,
                workflow["type"],
                workflow["created"],
            )

        self.console.print(
            f"📋 [bold]Step Functions Workflows[/bold] ([bright_yellow]{len(workflow_data)}[/bright_yellow] found)"
        )
        if sort_by:
            self.console.print(f"[dim]Sorted by: {sort_by} ({sort_order})[/dim]")
        self.console.print()
        self.console.print(table)

    def _handle_no_workflows_found(self, output_format: str) -> None:
        """Handle the case when no workflows are found."""
        if output_format == "table":
            print(
                "[yellow]No Step Functions state machines found in the current region.[/yellow]"
            )
        elif output_format == "json":
            print(json.dumps({"workflows": [], "count": 0}, indent=2))
        elif output_format == "yaml":
            print(yaml.dump({"workflows": [], "count": 0}))
        elif output_format == "text":
            print("No Step Functions state machines found in the current region.")
        elif output_format == "markdown":
            print(
                "# Step Functions Workflows\n\nNo workflows found in the current region."
            )

    def _handle_no_workflows_after_filter(
        self,
        output_format: str,
        prefix_filter: Optional[str],
        regex_match: Optional[str],
        contains_filter: Optional[str],
    ) -> None:
        """Handle the case when no workflows remain after filtering."""
        filter_desc = []
        if prefix_filter:
            filter_desc.append(f"prefix '{prefix_filter}'")
        if regex_match:
            filter_desc.append(f"regex '{regex_match}'")
        if contains_filter:
            filter_desc.append(f"contains '{contains_filter}'")

        filter_text = ", ".join(filter_desc)
        message = f"No workflows found matching the specified filters: {filter_text}"

        if output_format == "table":
            print(f"[yellow]{message}[/yellow]")
        elif output_format == "json":
            print(
                json.dumps({"workflows": [], "count": 0, "message": message}, indent=2)
            )
        elif output_format == "yaml":
            print(yaml.dump({"workflows": [], "count": 0, "message": message}))
        elif output_format == "text":
            print(message)
        elif output_format == "markdown":
            print(f"# Step Functions Workflows\n\n{message}")

    def _print_workflows_csv(
        self,
        workflow_data: list,
        show_filters: bool = False,
        applied_filters: dict = None,
        save_to: Optional[str] = None,
    ) -> None:
        """Print workflows in CSV format."""
        import csv
        import io

        output = io.StringIO()
        writer = csv.writer(output)

        # Write header
        writer.writerow(["Name", "Type", "Created", "ARN"])

        # Write data
        for workflow in workflow_data:
            writer.writerow(
                [
                    workflow["name"],
                    workflow["type"],
                    workflow["created"],
                    workflow["arn"],
                ]
            )

        csv_content = output.getvalue()

        if save_to:
            self._save_to_file(csv_content, save_to)
        else:
            if show_filters and applied_filters:
                print(f"# Applied filters: {applied_filters}")
            print(csv_content.strip())

    def _print_workflows_markdown(
        self,
        workflow_data: list,
        show_filters: bool = False,
        applied_filters: dict = None,
        sort_by: str = "name",
        sort_order: str = "asc",
        save_to: Optional[str] = None,
    ) -> None:
        """Print workflows in markdown format."""
        output_lines = ["# Step Functions Workflows\n"]

        # Print filter information if any
        if show_filters and applied_filters:
            output_lines.append("## Applied Filters\n")
            for key, value in applied_filters.items():
                output_lines.append(f"- **{key.title()}:** `{value}`")
            output_lines.append("")

        output_lines.append("## Workflows\n")
        output_lines.append("| Name | Type | Created | ARN |")
        output_lines.append("|------|------|---------|-----|")

        for workflow in workflow_data:
            output_lines.append(
                f"| {workflow['name']} | {workflow['type']} | {workflow['created']} | {workflow['arn']} |"
            )

        output_lines.append(f"\n**Total:** {len(workflow_data)} workflow(s)")
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

    def _print_workflows_text(
        self,
        workflow_data: list,
        prefix_filter: Optional[str],
        regex_match: Optional[str],
        status_filter: Optional[str],
        sort_by: str,
    ) -> None:
        """Print workflows in text format."""
        for workflow in workflow_data:
            print(f"Name: {workflow['name']}")
            print(f"Type: {workflow['type']}")
            print(f"Created: {workflow['created']}")
            print(f"ARN: {workflow['arn']}")
            print("-" * 50)

        # Print filter summary
        filters_dict = {}
        if prefix_filter:
            filters_dict["prefix"] = {"value": prefix_filter}
        if regex_match:
            filters_dict["regex"] = {"value": regex_match}

        filter_summary = FilterUtility.get_filter_summary(filters_dict)
        if sort_by != "name":
            filter_summary.append(f"sorted by: {sort_by}")

        filter_text = (
            f" (filtered by: {', '.join(filter_summary)})" if filter_summary else ""
        )
        print(f"\nTotal: {len(workflow_data)} workflow(s){filter_text}")

    def _print_workflows_markdown_old(  # noqa: C901
        self,
        workflow_data: list,
        prefix_filter: Optional[str],
        regex_match: Optional[str],
        status_filter: Optional[str],
        sort_by: str,
    ) -> None:
        """Print workflows in markdown format."""
        print("# Step Functions Workflows\n")

        # Print filter information if any
        filters_dict = {}
        if prefix_filter:
            filters_dict["prefix"] = {"value": prefix_filter}
        if regex_match:
            filters_dict["regex"] = {"value": regex_match}

        filter_summary = FilterUtility.get_filter_summary(filters_dict)
        if sort_by != "name":
            filter_summary.append(f"sorted by: {sort_by}")

        if filter_summary:
            print("## Applied Filters\n")
            for filter_desc in filter_summary:
                # Convert to markdown-friendly format
                if filter_desc.startswith("prefix:"):
                    print(f"- **Prefix filter:** `{filter_desc.split(': ', 1)[1]}`")
                elif filter_desc.startswith("regex:"):
                    pass  # This is handled by the new markdown method

    def describe_workflow(self, name: str, output_format: str = "table") -> None:
        """Describe a specific Step Functions state machine.

        Args:
            name: Name of the state machine
            output_format: Output format (table, json, yaml, text, markdown)
        """
        try:
            output_format = self._validate_output_format(output_format)

            if output_format == "table":
                print(f"[blue]Fetching details for workflow: {name}...[/blue]")

            # Find the state machine ARN by name
            state_machine_arn = self._find_state_machine_arn(name)
            if not state_machine_arn:
                self._handle_workflow_not_found(name, output_format)
                return

            # Get detailed information about the state machine
            workflow_details = self._get_workflow_details(state_machine_arn)

            # Output in requested format
            self._output_workflow_details(workflow_details, output_format)

        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            error_message = e.response["Error"]["Message"]
            print(f"[red]AWS Error ({error_code}): {error_message}[/red]")
        except Exception as e:
            print(f"[red]Error describing workflow: {e}[/red]")

    def list_executions(  # noqa: C901
        self,
        workflow_name: str,
        status_filter: str = "ALL",
        max_results: int = 50,
        output_format: str = "table",
    ) -> None:
        """List executions for a specific Step Functions state machine.

        Args:
            workflow_name: Name of the state machine
            status_filter: Filter by status (ALL, RUNNING, SUCCEEDED, FAILED, etc.)
            max_results: Maximum number of executions to return
            output_format: Output format (table, json, yaml, text, markdown)
        """
        try:
            output_format = self._validate_output_format(output_format)

            if output_format == "table":
                print(
                    f"[blue]Fetching executions for workflow: {workflow_name}...[/blue]"
                )

            # Find the state machine ARN by name
            state_machine_arn = self._find_state_machine_arn(workflow_name)
            if not state_machine_arn:
                self._handle_workflow_not_found(workflow_name, output_format)
                return

            # Validate status filter
            valid_statuses = [
                "ALL",
                "RUNNING",
                "SUCCEEDED",
                "FAILED",
                "TIMED_OUT",
                "ABORTED",
            ]
            status_filter = status_filter.upper()
            if status_filter not in valid_statuses:
                error_msg = f"Invalid status '{status_filter}'. Valid statuses: {', '.join(valid_statuses)}"
                if output_format == "table":
                    print(f"[red]{error_msg}[/red]")
                elif output_format == "json":
                    print(json.dumps({"error": error_msg}, indent=2))
                elif output_format == "yaml":
                    print(yaml.dump({"error": error_msg}))
                elif output_format == "text":
                    print(error_msg)
                elif output_format == "markdown":
                    print(f"# Workflow Executions\n\n**Error:** {error_msg}")
                return

            # Validate max_results
            if max_results < 1 or max_results > 1000:
                error_msg = "max_results must be between 1 and 1000"
                if output_format == "table":
                    print(f"[red]{error_msg}[/red]")
                elif output_format == "json":
                    print(json.dumps({"error": error_msg}, indent=2))
                elif output_format == "yaml":
                    print(yaml.dump({"error": error_msg}))
                elif output_format == "text":
                    print(error_msg)
                elif output_format == "markdown":
                    print(f"# Workflow Executions\n\n**Error:** {error_msg}")
                return

            # Get executions
            list_params = {
                "stateMachineArn": state_machine_arn,
                "maxResults": max_results,
            }

            # Add status filter if not ALL
            if status_filter != "ALL":
                list_params["statusFilter"] = status_filter

            executions = []
            paginator = self.stepfunctions_client.get_paginator("list_executions")

            for page in paginator.paginate(**list_params):
                executions.extend(page.get("executions", []))

            if not executions:
                message = f"No executions found for workflow '{workflow_name}'"
                if status_filter != "ALL":
                    message += f" with status '{status_filter}'"

                if output_format == "table":
                    print(f"[yellow]{message}.[/yellow]")
                elif output_format == "json":
                    print(
                        json.dumps(
                            {"executions": [], "count": 0, "message": message}, indent=2
                        )
                    )
                elif output_format == "yaml":
                    print(yaml.dump({"executions": [], "count": 0, "message": message}))
                elif output_format == "text":
                    print(f"{message}.")
                elif output_format == "markdown":
                    print(f"# Workflow Executions\n\n{message}.")
                return

            # Process execution data
            execution_data = []
            for execution in executions:
                execution_info = {
                    "name": execution.get("name", "N/A"),
                    "status": execution.get("status", "N/A"),
                    "started": self._format_date(execution.get("startDate")),
                    "stopped": self._format_date(execution.get("stopDate")),
                    "execution_arn": execution.get("executionArn", "N/A"),
                }
                execution_data.append(execution_info)

            # Output in requested format
            if output_format == "table":
                self._print_executions_table(
                    execution_data, workflow_name, status_filter
                )
            elif output_format == "json":
                print(
                    json.dumps(
                        {
                            "workflow_name": workflow_name,
                            "status_filter": status_filter,
                            "executions": execution_data,
                            "count": len(execution_data),
                        },
                        indent=2,
                        default=str,
                    )
                )
            elif output_format == "yaml":
                print(
                    yaml.dump(
                        {
                            "workflow_name": workflow_name,
                            "status_filter": status_filter,
                            "executions": execution_data,
                            "count": len(execution_data),
                        },
                        default_flow_style=False,
                    )
                )
            elif output_format == "text":
                print(f"Executions for workflow: {workflow_name}")
                if status_filter != "ALL":
                    print(f"Status filter: {status_filter}")
                print("=" * 60)
                for execution in execution_data:
                    print(f"Name: {execution['name']}")
                    print(f"Status: {execution['status']}")
                    print(f"Started: {execution['started']}")
                    print(f"Stopped: {execution['stopped']}")
                    print(f"ARN: {execution['execution_arn']}")
                    print("-" * 40)
                print(f"\nTotal: {len(execution_data)} execution(s)")
            elif output_format == "markdown":
                print(f"# Workflow Executions: {workflow_name}\n")
                if status_filter != "ALL":
                    print(f"**Status filter:** {status_filter}\n")
                print("| Name | Status | Started | Stopped |")
                print("|------|--------|---------|---------|")
                for execution in execution_data:
                    print(
                        f"| {execution['name']} | {execution['status']} | {execution['started']} | {execution['stopped']} |"
                    )
                print(f"\n**Total:** {len(execution_data)} execution(s)")

        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            error_message = e.response["Error"]["Message"]
            print(f"[red]AWS Error ({error_code}): {error_message}[/red]")
        except Exception as e:
            print(f"[red]Error listing executions: {e}[/red]")

    def _print_executions_table(
        self, execution_data: list, workflow_name: str, status_filter: str
    ) -> None:
        """Print executions in a formatted table."""
        table = Table(
            show_header=True,
            header_style="bold",
            box=box.SIMPLE,
            border_style="dim",
        )
        table.add_column("Execution Name", no_wrap=True)
        table.add_column("Status")
        table.add_column("Started")
        table.add_column("Stopped")

        for execution in execution_data:
            # Color code status
            status = execution["status"]
            if status == "SUCCEEDED":
                status_color = "[green]SUCCEEDED[/green]"
            elif status == "FAILED":
                status_color = "[red]FAILED[/red]"
            elif status == "RUNNING":
                status_color = "[blue]RUNNING[/blue]"
            elif status == "TIMED_OUT":
                status_color = "[yellow]TIMED_OUT[/yellow]"
            elif status == "ABORTED":
                status_color = "[red]ABORTED[/red]"
            else:
                status_color = f"[dim]{status}[/dim]"

            table.add_row(
                execution["name"],
                status_color,
                execution["started"],
                execution["stopped"] or "N/A",
            )

        self.console.print(table)

        # Show summary
        filter_text = (
            f" (filtered by {status_filter})" if status_filter != "ALL" else ""
        )
        print(
            f"\n[green]Found {len(execution_data)} execution(s) for '{workflow_name}'{filter_text}.[/green]"
        )

    def _find_state_machine_arn(self, name: str) -> Optional[str]:
        """Find the ARN of a state machine by name."""
        paginator = self.stepfunctions_client.get_paginator("list_state_machines")

        for page in paginator.paginate():
            for state_machine in page.get("stateMachines", []):
                if state_machine.get("name") == name:
                    return state_machine.get("stateMachineArn")
        return None

    def _handle_workflow_not_found(self, name: str, output_format: str) -> None:
        """Handle the case when a workflow is not found."""
        error_msg = f"Workflow '{name}' not found"

        if output_format == "table":
            print(f"[red]{error_msg}.[/red]")
        elif output_format == "json":
            print(json.dumps({"error": error_msg}, indent=2))
        elif output_format == "yaml":
            print(yaml.dump({"error": error_msg}))
        elif output_format == "text":
            print(f"{error_msg}.")
        elif output_format == "markdown":
            print(f"# Workflow Details\n\n{error_msg}.")

    def _get_workflow_details(self, state_machine_arn: str) -> dict:
        """Get detailed information about a state machine."""
        response = self.stepfunctions_client.describe_state_machine(
            stateMachineArn=state_machine_arn
        )

        # Parse the definition JSON
        definition = json.loads(response.get("definition", "{}"))

        return {
            "name": response.get("name", "N/A"),
            "arn": response.get("stateMachineArn", "N/A"),
            "type": response.get("type", "N/A"),
            "status": response.get("status", "N/A"),
            "created": self._format_date(response.get("creationDate")),
            "updated": self._format_date(response.get("updateDate")),
            "role_arn": response.get("roleArn", "N/A"),
            "logging_configuration": response.get("loggingConfiguration", {}),
            "tracing_configuration": response.get("tracingConfiguration", {}),
            "definition": definition,
            "definition_raw": response.get("definition", "{}"),
        }

    def _output_workflow_details(
        self, workflow_details: dict, output_format: str
    ) -> None:
        """Output workflow details in the specified format."""
        if output_format == "table":
            self._print_workflow_details_table(workflow_details)
        elif output_format == "json":
            print(json.dumps(workflow_details, indent=2, default=str))
        elif output_format == "yaml":
            print(yaml.dump(workflow_details, default_flow_style=False))
        elif output_format == "text":
            self._print_workflow_details_text(workflow_details)
        elif output_format == "markdown":
            self._print_workflow_details_markdown(workflow_details)

    def _print_workflow_details_text(self, workflow_details: dict) -> None:
        """Print workflow details in text format."""
        print(f"Name: {workflow_details['name']}")
        print(f"ARN: {workflow_details['arn']}")
        print(f"Type: {workflow_details['type']}")
        print(f"Status: {workflow_details['status']}")
        print(f"Created: {workflow_details['created']}")
        print(f"Updated: {workflow_details['updated']}")
        print(f"Role ARN: {workflow_details['role_arn']}")
        print(f"Definition:\n{json.dumps(workflow_details['definition'], indent=2)}")

    def _print_workflow_details_markdown(self, workflow_details: dict) -> None:
        """Print workflow details in markdown format."""
        print(f"# Workflow Details: {workflow_details['name']}\n")
        print(f"**ARN:** {workflow_details['arn']}\n")
        print(f"**Type:** {workflow_details['type']}\n")
        print(f"**Status:** {workflow_details['status']}\n")
        print(f"**Created:** {workflow_details['created']}\n")
        print(f"**Updated:** {workflow_details['updated']}\n")
        print(f"**Role ARN:** {workflow_details['role_arn']}\n")
        print("## Definition")
        print("```json")
        print(json.dumps(workflow_details["definition"], indent=2))
        print("```")

    def _print_workflow_details_table(self, workflow_details: dict) -> None:
        """Print workflow details in a formatted table."""
        # Basic info table
        basic_table = Table(
            title=f"Workflow: {workflow_details['name']}", box=box.SIMPLE
        )
        basic_table.add_column("Property", style="cyan", no_wrap=True)
        basic_table.add_column("Value", style="white")

        # Color code status
        status = workflow_details["status"]
        if status == "ACTIVE":
            status_display = "[green]ACTIVE[/green]"
        elif status == "DELETING":
            status_display = "[red]DELETING[/red]"
        else:
            status_display = f"[yellow]{status}[/yellow]"

        basic_table.add_row("Name", workflow_details["name"])
        basic_table.add_row("Type", workflow_details["type"])
        basic_table.add_row("Status", status_display)
        basic_table.add_row("Created", workflow_details["created"])
        basic_table.add_row("Updated", workflow_details["updated"])
        basic_table.add_row("Role ARN", workflow_details["role_arn"])
        basic_table.add_row("ARN", workflow_details["arn"])

        self.console.print(basic_table)

        # Definition table (states)
        definition = workflow_details.get("definition", {})
        states = definition.get("States", {})

        if states:
            print("\n")
            states_table = Table(title="State Machine States", box=box.SIMPLE)
            states_table.add_column("State Name", style="cyan")
            states_table.add_column("Type", style="green")
            states_table.add_column("Resource", style="blue", overflow="fold")

            for state_name, state_config in states.items():
                state_type = state_config.get("Type", "N/A")
                resource = state_config.get("Resource", state_config.get("Next", "N/A"))
                states_table.add_row(state_name, state_type, str(resource))

            self.console.print(states_table)

        # Show raw definition
        print("\n[bold]Definition JSON:[/bold]")
        print(json.dumps(definition, indent=2))

    def get_execution(  # noqa: C901
        self,
        execution_name: str,
        output_format: str = "table",
        show_input: bool = False,
        show_output: bool = False,
        show_states: bool = False,
        show_state_io: bool = False,
        state_filter: Optional[str] = None,
        show_diff: bool = False,
        limit: Optional[int] = None,
        save_to: Optional[str] = None,
    ) -> None:
        """Get detailed information about a specific Step Functions execution.

        Args:
            execution_name: Execution ARN or execution name
            output_format: Output format (table, json, yaml, markdown, text)
            show_input: Show full input passed into the execution
            show_output: Show final output of the execution
            show_states: Display state transition events (enter, exit, success/fail)
            show_state_io: Show detailed input/output mapping per state
            state_filter: Focus debug output on a specific state by name
            show_diff: Highlight key differences between input and output
            limit: Limit number of state events displayed
            save_to: Save detailed execution report to file
        """
        try:
            output_format = self._validate_output_format(output_format)

            if output_format == "table":
                print(f"[blue]Fetching execution details: {execution_name}...[/blue]")

            # Get execution details
            execution_details = self._get_execution_details(execution_name)
            if not execution_details:
                return

            # Get execution history if show_states or show_state_io is requested
            execution_history = None
            state_io_data = None
            if show_states or show_state_io:
                execution_history = self._get_execution_history(
                    execution_details["execution_arn"], limit, state_filter
                )

            # Get detailed state input/output data if requested
            if show_state_io:
                state_io_data = self._get_state_io_data(
                    execution_details["execution_arn"], state_filter, execution_history
                )

            # Generate diff data if requested
            diff_data = None
            if show_diff:
                diff_data = self._generate_diff_data(
                    execution_details["input"], execution_details["output"]
                )

            # Output in requested format
            if output_format == "json":
                output_data = {
                    "execution": execution_details,
                    "show_input": show_input,
                    "show_output": show_output,
                    "show_states": show_states,
                    "show_state_io": show_state_io,
                    "state_filter": state_filter,
                    "show_diff": show_diff,
                }
                if execution_history:
                    output_data["state_transitions"] = execution_history
                if state_io_data:
                    output_data["state_io_data"] = state_io_data
                if diff_data:
                    output_data["diff_data"] = diff_data

                output_str = json.dumps(output_data, indent=2, default=str)
                if save_to:
                    self._save_to_file(output_str, save_to)
                else:
                    print(output_str)
            elif output_format == "yaml":
                output_data = {
                    "execution": execution_details,
                    "show_input": show_input,
                    "show_output": show_output,
                    "show_states": show_states,
                    "show_state_io": show_state_io,
                    "state_filter": state_filter,
                    "show_diff": show_diff,
                }
                if execution_history:
                    output_data["state_transitions"] = execution_history
                if state_io_data:
                    output_data["state_io_data"] = state_io_data
                if diff_data:
                    output_data["diff_data"] = diff_data

                output_str = yaml.dump(output_data, default_flow_style=False)
                if save_to:
                    self._save_to_file(output_str, save_to)
                else:
                    print(output_str)
            elif output_format == "markdown":
                self._print_execution_markdown(
                    execution_details,
                    show_input,
                    show_output,
                    show_states,
                    execution_history,
                    save_to,
                    show_state_io,
                    state_filter,
                    show_diff,
                    state_io_data,
                    diff_data,
                )
            elif output_format == "text":
                self._print_execution_text(
                    execution_details,
                    show_input,
                    show_output,
                    show_states,
                    execution_history,
                    show_state_io,
                    state_filter,
                    show_diff,
                    state_io_data,
                    diff_data,
                )
            else:  # table format
                self._print_execution_table(
                    execution_details,
                    show_input,
                    show_output,
                    show_states,
                    execution_history,
                    show_state_io,
                    state_filter,
                    show_diff,
                    state_io_data,
                    diff_data,
                )

        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            error_message = e.response["Error"]["Message"]
            print(f"[red]AWS Error ({error_code}): {error_message}[/red]")
        except Exception as e:
            print(f"[red]Error getting execution details: {e}[/red]")

    def _get_execution_details(self, execution_name: str) -> Optional[dict]:
        """Get detailed information about an execution."""
        try:
            # Try to get execution details directly (if full ARN provided)
            execution_arn: Optional[str]
            if execution_name.startswith("arn:aws:states:"):
                execution_arn = execution_name
            else:
                # If just a name is provided, we need to find the execution ARN
                # This is tricky because execution names are not globally unique
                # We'll try to find it by listing recent executions across all state machines
                execution_arn = self._find_execution_arn(execution_name)
                if not execution_arn:
                    print(
                        f"[red]Execution '{execution_name}' not found. Please provide the full execution ARN for unique identification.[/red]"
                    )
                    return None

            response = self.stepfunctions_client.describe_execution(
                executionArn=execution_arn
            )

            # Format the execution details
            execution_info = {
                "name": response.get("name", "N/A"),
                "execution_arn": response.get("executionArn", "N/A"),
                "state_machine_arn": response.get("stateMachineArn", "N/A"),
                "status": response.get("status", "N/A"),
                "start_date": self._format_date(response.get("startDate")),
                "stop_date": self._format_date(response.get("stopDate")),
                "input": response.get("input", ""),
                "output": response.get("output", ""),
                "error": response.get("error", ""),
                "cause": response.get("cause", ""),
                "execution_role_arn": response.get("roleArn", "N/A"),
            }

            return execution_info

        except ClientError as e:
            if e.response["Error"]["Code"] == "ExecutionDoesNotExist":
                print(f"[red]Execution '{execution_name}' does not exist.[/red]")
            else:
                raise
            return None

    def _find_execution_arn(self, execution_name: str) -> Optional[str]:
        """Find execution ARN by name across all state machines."""
        try:
            # Get all state machines
            paginator = self.stepfunctions_client.get_paginator("list_state_machines")

            for page in paginator.paginate():
                for state_machine in page.get("stateMachines", []):
                    state_machine_arn = state_machine.get("stateMachineArn")

                    # List executions for this state machine
                    try:
                        exec_paginator = self.stepfunctions_client.get_paginator(
                            "list_executions"
                        )
                        for exec_page in exec_paginator.paginate(
                            stateMachineArn=state_machine_arn
                        ):
                            for execution in exec_page.get("executions", []):
                                if execution.get("name") == execution_name:
                                    return execution.get("executionArn")
                    except ClientError:
                        # Skip state machines we can't access
                        continue

            return None
        except Exception:
            return None

    def _get_execution_history(
        self,
        execution_arn: str,
        limit: Optional[int] = None,
        state_filter: Optional[str] = None,
    ) -> list:
        """Get execution history events."""
        try:
            events = []
            paginator = self.stepfunctions_client.get_paginator("get_execution_history")

            params = {"executionArn": execution_arn, "reverseOrder": False}
            if limit:
                params["maxResults"] = min(limit, 1000)  # AWS API limit

            for page in paginator.paginate(**params):
                page_events = page.get("events", [])
                events.extend(page_events)

                if limit and len(events) >= limit:
                    events = events[:limit]
                    break

            # Process events into more readable format
            processed_events = []
            for event in events:
                state_name = self._extract_state_name(event)

                # Apply state filter if specified
                if state_filter and state_name != state_filter and state_name != "N/A":
                    continue

                event_info = {
                    "id": event.get("id", "N/A"),
                    "timestamp": self._format_date(event.get("timestamp")),
                    "type": event.get("type", "N/A"),
                    "state_name": state_name,
                    "details": self._extract_event_details(event),
                }
                processed_events.append(event_info)

            return processed_events

        except ClientError as e:
            print(
                f"[yellow]Warning: Could not retrieve execution history: {e}[/yellow]"
            )
            return []

    def _extract_state_name(self, event: dict) -> str:
        """Extract state name from execution event."""
        event_type = event.get("type", "")

        # Different event types store state names in different fields
        if "stateEntered" in event_type.lower():
            return event.get("stateEnteredEventDetails", {}).get("name", "N/A")
        elif "stateExited" in event_type.lower():
            return event.get("stateExitedEventDetails", {}).get("name", "N/A")
        elif "taskStateEntered" in event_type:
            return event.get("taskStateEnteredEventDetails", {}).get("name", "N/A")
        elif "taskStateExited" in event_type:
            return event.get("taskStateExitedEventDetails", {}).get("name", "N/A")
        elif "lambdaFunction" in event_type.lower():
            return event.get("lambdaFunctionScheduledEventDetails", {}).get(
                "resource", "Lambda"
            )

        return "N/A"

    def _extract_event_details(self, event: dict) -> str:
        """Extract relevant details from execution event."""
        event_type = event.get("type", "")

        if "Failed" in event_type:
            return f"Error: {event.get('executionFailedEventDetails', {}).get('error', 'Unknown error')}"
        elif "Succeeded" in event_type:
            return "Execution completed successfully"
        elif "TimedOut" in event_type:
            return "Execution timed out"
        elif "Aborted" in event_type:
            return "Execution was aborted"
        elif "Started" in event_type:
            return "Execution started"
        elif "StateEntered" in event_type:
            return "State entered"
        elif "StateExited" in event_type:
            return "State exited"

        return ""

    def _print_execution_table(  # noqa: C901
        self,
        execution_details: dict,
        show_input: bool,
        show_output: bool,
        show_states: bool,
        execution_history: Optional[list] = None,
        show_state_io: bool = False,
        state: Optional[str] = None,
        diff: bool = False,
        state_io_data: Optional[dict] = None,
        diff_data: Optional[dict] = None,
    ) -> None:
        """Print execution details in a formatted table."""
        # Main execution info table
        table = Table(
            show_header=True,
            header_style="bold cyan",
            box=box.SIMPLE,
            border_style="dim",
        )
        table.add_column("Property", style="cyan", no_wrap=True)
        table.add_column("Value", style="white")

        # Color code status
        status = execution_details["status"]
        if status == "SUCCEEDED":
            status_display = "[green]SUCCEEDED[/green]"
        elif status == "FAILED":
            status_display = "[red]FAILED[/red]"
        elif status == "RUNNING":
            status_display = "[blue]RUNNING[/blue]"
        elif status == "TIMED_OUT":
            status_display = "[yellow]TIMED_OUT[/yellow]"
        elif status == "ABORTED":
            status_display = "[red]ABORTED[/red]"
        else:
            status_display = f"[dim]{status}[/dim]"

        table.add_row("Name", execution_details["name"])
        table.add_row("Status", status_display)
        table.add_row("Started", execution_details["start_date"])
        table.add_row("Stopped", execution_details["stop_date"] or "Still running")
        table.add_row("State Machine ARN", execution_details["state_machine_arn"])
        table.add_row("Execution ARN", execution_details["execution_arn"])

        if execution_details["error"]:
            table.add_row("Error", f"[red]{execution_details['error']}[/red]")
        if execution_details["cause"]:
            table.add_row("Cause", f"[red]{execution_details['cause']}[/red]")

        # Print header and table
        self.console.print(
            f"🔄 [bold]Step Function Execution[/bold] ([bright_yellow]{execution_details['name']}[/bright_yellow])"
        )
        self.console.print()
        self.console.print(table)

        # Show input if requested
        if show_input and execution_details["input"]:
            print("\n[bold]📥 Input Payload:[/bold]")
            try:
                input_json = json.loads(execution_details["input"])
                print(json.dumps(input_json, indent=2))
            except json.JSONDecodeError:
                print(execution_details["input"])

        # Show output if requested
        if show_output and execution_details["output"]:
            print("\n[bold]📤 Output Result:[/bold]")
            try:
                output_json = json.loads(execution_details["output"])
                print(json.dumps(output_json, indent=2))
            except json.JSONDecodeError:
                print(execution_details["output"])

        # Show state transitions if requested
        if show_states and execution_history:
            print("\n[bold]🔄 State Transitions:[/bold]")

            states_table = Table(
                box=box.SIMPLE, show_header=True, header_style="bold cyan"
            )
            states_table.add_column("ID", justify="right", style="dim")
            states_table.add_column("Timestamp", style="yellow")
            states_table.add_column("Event Type", style="cyan")
            states_table.add_column("State Name", style="green")
            states_table.add_column("Details", style="white")

            for event in execution_history:
                states_table.add_row(
                    str(event["id"]),
                    event["timestamp"],
                    event["type"],
                    event["state_name"],
                    event["details"],
                )

            self.console.print(states_table)

        # Show state I/O data if requested
        if show_state_io and state_io_data:
            print("\n[bold]🔄 State Data Flow Analysis:[/bold]")

            for state_name, data in state_io_data.items():
                print(f"\n[bold cyan]State: {state_name}[/bold cyan]")
                print(f"[bold]Type[/bold]           : {data.get('type', 'N/A')}")

                # Show state configuration
                input_path = data.get("input_path", "$")
                print(f"[bold]InputPath[/bold]       : {input_path}")

                parameters = data.get("parameters")
                if parameters:
                    print(
                        f"[bold]Parameters[/bold]      : {json.dumps(parameters, indent=18)}"
                    )
                else:
                    print("[bold]Parameters[/bold]      : None")

                result_selector = data.get("result_selector")
                if result_selector:
                    print(
                        f"[bold]ResultSelector[/bold]  : {json.dumps(result_selector, indent=18)}"
                    )
                else:
                    print("[bold]ResultSelector[/bold]  : None")

                result_path = data.get("result_path", "$")
                print(f"[bold]ResultPath[/bold]      : {result_path}")

                output_path = data.get("output_path", "$")
                print(f"[bold]OutputPath[/bold]      : {output_path}")

                # Show resource if available
                resource_arn = data.get("resource_arn")
                if resource_arn:
                    # Extract just the function name from Lambda ARN
                    if "lambda" in resource_arn.lower():
                        resource_display = resource_arn.split(":")[-1]
                    else:
                        resource_display = resource_arn
                    print(f"[bold]Resource[/bold]        : {resource_display}")

                # Show duration
                duration_str = (
                    f"{data['duration_ms']}ms" if data["duration_ms"] else "N/A"
                )
                print(f"[bold]Duration[/bold]        : {duration_str}")

                # Show state input
                input_data = data.get("input_data")
                if input_data and input_data != "N/A":
                    print("\n[bold green]🡒 State Input:[/bold green]")
                    try:
                        input_json = json.loads(input_data)
                        print(json.dumps(input_json, indent=2))
                    except json.JSONDecodeError:
                        print(input_data)
                else:
                    print("\n[bold green]🡒 State Input:[/bold green] N/A")

                # Show state output
                output_data = data.get("output_data")
                if output_data and output_data != "N/A":
                    print("\n[bold magenta]🡒 State Output:[/bold magenta]")
                    try:
                        output_json = json.loads(output_data)
                        print(json.dumps(output_json, indent=2))
                    except json.JSONDecodeError:
                        print(output_data)
                else:
                    print("\n[bold magenta]🡒 State Output:[/bold magenta] N/A")

                print("-" * 80)

            # Show summary
            print(
                f"\n[dim]💡 State Data Flow Summary: {len(state_io_data)} states processed[/dim]"
            )

        # Show diff data if requested
        if diff and diff_data:
            print("\n[bold]🔍 Input/Output Differences:[/bold]")

            diff_table = Table(
                box=box.SIMPLE, show_header=True, header_style="bold cyan"
            )
            diff_table.add_column("Metric", style="cyan")
            diff_table.add_column("Value", style="white")

            diff_table.add_row("Input Size", f"{diff_data['input_size']} characters")
            diff_table.add_row("Output Size", f"{diff_data['output_size']} characters")
            diff_table.add_row("Input Keys", str(len(diff_data["input_keys"])))
            diff_table.add_row("Output Keys", str(len(diff_data["output_keys"])))
            diff_table.add_row("Added Keys", str(len(diff_data["added_keys"])))
            diff_table.add_row("Removed Keys", str(len(diff_data["removed_keys"])))
            diff_table.add_row("Changed Values", str(len(diff_data["changed_values"])))

            self.console.print(diff_table)

            if diff_data["changed_values"]:
                print("\n[bold]📋 Changed Values Detail:[/bold]")
                changes_table = Table(
                    box=box.SIMPLE, show_header=True, header_style="bold cyan"
                )
                changes_table.add_column("Key", style="green")
                changes_table.add_column("Input Value", style="red")
                changes_table.add_column("Output Value", style="blue")

                for change in diff_data["changed_values"]:
                    changes_table.add_row(
                        change["key"],
                        change["input_value"],
                        change["output_value"],
                    )

                self.console.print(changes_table)

    def _print_execution_text(  # noqa: C901
        self,
        execution_details: dict,
        show_input: bool,
        show_output: bool,
        show_states: bool,
        execution_history: Optional[list] = None,
        show_state_io: bool = False,
        state: Optional[str] = None,
        diff: bool = False,
        state_io_data: Optional[dict] = None,
        diff_data: Optional[dict] = None,
    ) -> None:
        """Print execution details in text format."""
        print(f"Execution: {execution_details['name']}")
        print(f"Status: {execution_details['status']}")
        print(f"Started: {execution_details['start_date']}")
        print(f"Stopped: {execution_details['stop_date'] or 'Still running'}")
        print(f"State Machine ARN: {execution_details['state_machine_arn']}")
        print(f"Execution ARN: {execution_details['execution_arn']}")

        if execution_details["error"]:
            print(f"Error: {execution_details['error']}")
        if execution_details["cause"]:
            print(f"Cause: {execution_details['cause']}")

        if show_input and execution_details["input"]:
            print("\nInput Payload:")
            print(execution_details["input"])

        if show_output and execution_details["output"]:
            print("\nOutput Result:")
            print(execution_details["output"])

        if show_states and execution_history:
            print("\nState Transitions:")
            for event in execution_history:
                print(
                    f"[{event['id']}] {event['timestamp']} - {event['type']} - {event['state_name']} - {event['details']}"
                )

        # Show state I/O data if requested
        if show_state_io and state_io_data:
            print("\nState Data Flow Analysis:")
            for state_name, data in state_io_data.items():
                print(f"\n  State: {state_name}")
                print(f"    Duration: {data.get('duration_ms', 'N/A')}ms")
                print(f"    Resource: {data.get('resource', 'N/A')}")
                print(f"    Events: {data.get('events_count', 0)}")
                print(f"    First Event: {data.get('first_event', 'N/A')}")
                print(f"    Last Event: {data.get('last_event', 'N/A')}")
                print(f"    Event Types: {', '.join(data.get('event_types', []))}")

                # Show input data
                input_data = data.get("input_data")
                if input_data and input_data != "N/A":
                    print("    Input Data:")
                    try:
                        input_json = json.loads(input_data)
                        formatted_input = json.dumps(input_json, indent=6)
                        print(f"      {formatted_input}")
                    except json.JSONDecodeError:
                        print(f"      {input_data}")
                else:
                    print("    Input Data: N/A")

                # Show output data
                output_data = data.get("output_data")
                if output_data and output_data != "N/A":
                    print("    Output Data:")
                    try:
                        output_json = json.loads(output_data)
                        formatted_output = json.dumps(output_json, indent=6)
                        print(f"      {formatted_output}")
                    except json.JSONDecodeError:
                        print(f"      {output_data}")
                else:
                    print("    Output Data: N/A")

        # Show diff data if requested
        if diff and diff_data:
            print("\nInput/Output Differences:")
            print(f"  Input Size: {diff_data['input_size']} characters")
            print(f"  Output Size: {diff_data['output_size']} characters")
            print(f"  Input Keys: {len(diff_data['input_keys'])}")
            print(f"  Output Keys: {len(diff_data['output_keys'])}")
            print(f"  Added Keys: {len(diff_data['added_keys'])}")
            print(f"  Removed Keys: {len(diff_data['removed_keys'])}")
            print(f"  Changed Values: {len(diff_data['changed_values'])}")

            if diff_data["changed_values"]:
                print("\n  Changed Values Detail:")
                for change in diff_data["changed_values"]:
                    print(f"    {change['key']}:")
                    print(f"      Input: {change['input_value']}")
                    print(f"      Output: {change['output_value']}")

    def _print_execution_markdown(  # noqa: C901
        self,
        execution_details: dict,
        show_input: bool,
        show_output: bool,
        show_states: bool,
        execution_history: Optional[list] = None,
        save_to: Optional[str] = None,
        show_state_io: bool = False,
        state: Optional[str] = None,
        diff: bool = False,
        state_io_data: Optional[dict] = None,
        diff_data: Optional[dict] = None,
    ) -> None:
        """Print execution details in markdown format."""
        output_lines = [f"# Execution: {execution_details['name']}\n"]

        output_lines.append("## Execution Details\n")
        output_lines.append("| Property | Value |")
        output_lines.append("|----------|-------|")
        output_lines.append(f"| Name | {execution_details['name']} |")
        output_lines.append(f"| Status | {execution_details['status']} |")
        output_lines.append(f"| Started | {execution_details['start_date']} |")
        output_lines.append(
            f"| Stopped | {execution_details['stop_date'] or 'Still running'} |"
        )
        output_lines.append(
            f"| State Machine ARN | {execution_details['state_machine_arn']} |"
        )
        output_lines.append(f"| Execution ARN | {execution_details['execution_arn']} |")

        if execution_details["error"]:
            output_lines.append(f"| Error | {execution_details['error']} |")
        if execution_details["cause"]:
            output_lines.append(f"| Cause | {execution_details['cause']} |")

        if show_input and execution_details["input"]:
            output_lines.append("\n## Input Payload\n")
            output_lines.append("```json")
            try:
                input_json = json.loads(execution_details["input"])
                output_lines.append(json.dumps(input_json, indent=2))
            except json.JSONDecodeError:
                output_lines.append(execution_details["input"])
            output_lines.append("```")

        if show_output and execution_details["output"]:
            output_lines.append("\n## Output Result\n")
            output_lines.append("```json")
            try:
                output_json = json.loads(execution_details["output"])
                output_lines.append(json.dumps(output_json, indent=2))
            except json.JSONDecodeError:
                output_lines.append(execution_details["output"])
            output_lines.append("```")

        if show_states and execution_history:
            output_lines.append("\n## State Transitions\n")
            output_lines.append(
                "| ID | Timestamp | Event Type | State Name | Details |"
            )
            output_lines.append(
                "|----|-----------|------------|------------|---------|"
            )

            for event in execution_history:
                output_lines.append(
                    f"| {event['id']} | {event['timestamp']} | {event['type']} | {event['state_name']} | {event['details']} |"
                )

        # Show state I/O data if requested
        if show_state_io and state_io_data:
            output_lines.append("\n## State Data Flow Analysis\n")
            output_lines.append(
                "| State | Duration | Resource | Input Size | Output Size | Event Types |"
            )
            output_lines.append(
                "|-------|----------|----------|------------|-------------|-------------|"
            )

            for state_name, data in state_io_data.items():
                duration = f"{data.get('duration_ms', 'N/A')}ms"
                resource = data.get("resource", "N/A")

                # Calculate input/output sizes
                input_size = (
                    len(data.get("input_data", "")) if data.get("input_data") else 0
                )
                output_size = (
                    len(data.get("output_data", "")) if data.get("output_data") else 0
                )

                event_types = ", ".join(data.get("event_types", []))

                output_lines.append(
                    f"| {state_name} | {duration} | {resource} | {input_size} chars | {output_size} chars | {event_types} |"
                )

            # Add detailed input/output sections for each state
            for state_name, data in state_io_data.items():
                output_lines.append(f"\n### State: {state_name}\n")

                if data.get("input_data") and data["input_data"] != "N/A":
                    output_lines.append("#### Input Data\n")
                    output_lines.append("```json")
                    try:
                        input_json = json.loads(data["input_data"])
                        output_lines.append(json.dumps(input_json, indent=2))
                    except json.JSONDecodeError:
                        output_lines.append(data["input_data"])
                    output_lines.append("```")

                if data.get("output_data") and data["output_data"] != "N/A":
                    output_lines.append("\n#### Output Data\n")
                    output_lines.append("```json")
                    try:
                        output_json = json.loads(data["output_data"])
                        output_lines.append(json.dumps(output_json, indent=2))
                    except json.JSONDecodeError:
                        output_lines.append(data["output_data"])
                    output_lines.append("```")

        # Show diff data if requested
        if diff and diff_data:
            output_lines.append("\n## Input/Output Differences\n")
            output_lines.append("| Metric | Value |")
            output_lines.append("|--------|-------|")
            output_lines.append(
                f"| Input Size | {diff_data['input_size']} characters |"
            )
            output_lines.append(
                f"| Output Size | {diff_data['output_size']} characters |"
            )
            output_lines.append(f"| Input Keys | {len(diff_data['input_keys'])} |")
            output_lines.append(f"| Output Keys | {len(diff_data['output_keys'])} |")
            output_lines.append(f"| Added Keys | {len(diff_data['added_keys'])} |")
            output_lines.append(f"| Removed Keys | {len(diff_data['removed_keys'])} |")
            output_lines.append(
                f"| Changed Values | {len(diff_data['changed_values'])} |"
            )

            if diff_data["changed_values"]:
                output_lines.append("\n### Changed Values Detail\n")
                output_lines.append("| Key | Input Value | Output Value |")
                output_lines.append("|-----|-------------|--------------|")

                for change in diff_data["changed_values"]:
                    output_lines.append(
                        f"| {change['key']} | {change['input_value']} | {change['output_value']} |"
                    )

        markdown_content = "\n".join(output_lines)

        if save_to:
            self._save_to_file(markdown_content, save_to)
        else:
            print(markdown_content)

    def _get_state_io_data(  # noqa: C901
        self,
        execution_arn: str,
        state_filter: Optional[str] = None,
        execution_history: Optional[list] = None,
    ) -> dict:
        """Get detailed input/output data for each state in the execution."""
        state_io_data: dict = {}

        if not execution_history:
            return state_io_data

        # Get state machine definition to extract state configuration
        state_machine_definition = self._get_state_machine_definition(execution_arn)

        # Get full execution history with detailed event data
        try:
            events = []
            paginator = self.stepfunctions_client.get_paginator("get_execution_history")

            for page in paginator.paginate(
                executionArn=execution_arn, reverseOrder=False
            ):
                events.extend(page.get("events", []))

            # Group events by state to track input/output flow
            state_events: dict = {}
            for event in events:
                state_name = self._extract_state_name_detailed(event)
                if state_name == "N/A":
                    continue

                if state_filter and state_name != state_filter:
                    continue

                if state_name not in state_events:
                    state_events[state_name] = []
                state_events[state_name].append(event)

            # Extract detailed input/output for each state
            for state_name, events in state_events.items():
                state_config = state_machine_definition.get("States", {}).get(
                    state_name, {}
                )

                state_data = {
                    "state_name": state_name,
                    "events_count": len(events),
                    "first_event": (
                        self._format_date(events[0]["timestamp"]) if events else "N/A"
                    ),
                    "last_event": (
                        self._format_date(events[-1]["timestamp"]) if events else "N/A"
                    ),
                    "event_types": list({event["type"] for event in events}),
                    "input_data": None,
                    "output_data": None,
                    "resource": None,
                    "duration_ms": None,
                    # State configuration details
                    "type": state_config.get("Type", "N/A"),
                    "input_path": state_config.get("InputPath", "$"),
                    "output_path": state_config.get("OutputPath", "$"),
                    "result_path": state_config.get("ResultPath", "$"),
                    "result_selector": state_config.get("ResultSelector", None),
                    "parameters": state_config.get("Parameters", None),
                    "resource_arn": state_config.get("Resource", None),
                }

                # Extract input/output data from state events
                for event in events:
                    event_type = event.get("type", "")

                    # State entered events contain input data
                    if "StateEntered" in event_type or "TaskStateEntered" in event_type:
                        if "stateEnteredEventDetails" in event:
                            details = event["stateEnteredEventDetails"]
                            if "input" in details:
                                state_data["input_data"] = details["input"]
                        elif "taskStateEnteredEventDetails" in event:
                            details = event["taskStateEnteredEventDetails"]
                            if "input" in details:
                                state_data["input_data"] = details["input"]

                    # State exited events contain output data
                    elif "StateExited" in event_type or "TaskStateExited" in event_type:
                        if "stateExitedEventDetails" in event:
                            details = event["stateExitedEventDetails"]
                            if "output" in details:
                                state_data["output_data"] = details["output"]
                        elif "taskStateExitedEventDetails" in event:
                            details = event["taskStateExitedEventDetails"]
                            if "output" in details:
                                state_data["output_data"] = details["output"]

                    # Lambda function events contain resource and input/output
                    elif "LambdaFunctionScheduled" in event_type:
                        if "lambdaFunctionScheduledEventDetails" in event:
                            details = event["lambdaFunctionScheduledEventDetails"]
                            state_data["resource"] = details.get("resource", "N/A")
                            if "input" in details:
                                state_data["input_data"] = details["input"]
                    elif "LambdaFunctionSucceeded" in event_type:
                        if "lambdaFunctionSucceededEventDetails" in event:
                            details = event["lambdaFunctionSucceededEventDetails"]
                            if "output" in details:
                                state_data["output_data"] = details["output"]

                # Calculate duration if we have both start and end events
                if len(events) >= 2:
                    start_time = events[0]["timestamp"]
                    end_time = events[-1]["timestamp"]
                    duration = (end_time - start_time).total_seconds() * 1000
                    state_data["duration_ms"] = round(duration, 2)

                state_io_data[state_name] = state_data

        except Exception as e:
            print(
                f"[yellow]Warning: Could not retrieve detailed state I/O data: {e}[/yellow]"
            )

        return state_io_data

    def _get_state_machine_definition(self, execution_arn: str) -> dict:
        """Get the state machine definition for the execution."""
        try:
            # Get execution details to find the state machine ARN
            response = self.stepfunctions_client.describe_execution(
                executionArn=execution_arn
            )
            state_machine_arn = response.get("stateMachineArn")

            # Get state machine definition
            sm_response = self.stepfunctions_client.describe_state_machine(
                stateMachineArn=state_machine_arn
            )

            # Parse the definition JSON
            definition = json.loads(sm_response.get("definition", "{}"))
            return definition

        except Exception as e:
            print(
                f"[yellow]Warning: Could not retrieve state machine definition: {e}[/yellow]"
            )
            return {}

    def _extract_state_name_detailed(self, event: dict) -> str:  # noqa: C901
        """Extract state name from execution event with more detail."""
        event_type = event.get("type", "")

        # Different event types store state names in different fields
        if "StateEntered" in event_type:
            return event.get("stateEnteredEventDetails", {}).get("name", "N/A")
        elif "StateExited" in event_type:
            return event.get("stateExitedEventDetails", {}).get("name", "N/A")
        elif "TaskStateEntered" in event_type:
            return event.get("taskStateEnteredEventDetails", {}).get("name", "N/A")
        elif "TaskStateExited" in event_type:
            return event.get("taskStateExitedEventDetails", {}).get("name", "N/A")
        elif "LambdaFunction" in event_type:
            # Extract function name from ARN for better display
            resource = event.get("lambdaFunctionScheduledEventDetails", {}).get(
                "resource", ""
            )
            if resource:
                # Extract function name from ARN like arn:aws:lambda:region:account:function:name
                if ":function:" in resource:
                    return resource.split(":function:")[-1].split(":")[0]
                return "Lambda"
            return "Lambda"
        elif "TaskScheduled" in event_type:
            details = event.get("taskScheduledEventDetails", {})
            resource = details.get("resource", "")
            if resource:
                # Extract service name from resource ARN
                if ":states:" in resource:
                    return "StepFunction"
                elif ":lambda:" in resource:
                    if ":function:" in resource:
                        return resource.split(":function:")[-1].split(":")[0]
                    return "Lambda"
                elif ":sns:" in resource:
                    return "SNS"
                elif ":sqs:" in resource:
                    return "SQS"
                return resource.split(":")[-1] if ":" in resource else resource
        elif "TaskSucceeded" in event_type or "TaskFailed" in event_type:
            # Try to get the resource from the scheduled event
            return "Task"

        return "N/A"

    def _generate_diff_data(self, input_data: str, output_data: str) -> dict:
        """Generate differences between input and output data."""
        diff_data: dict = {
            "input_keys": [],
            "output_keys": [],
            "added_keys": [],
            "removed_keys": [],
            "changed_values": [],
            "input_size": len(input_data) if input_data else 0,
            "output_size": len(output_data) if output_data else 0,
        }

        try:
            # Parse JSON if possible
            input_json = json.loads(input_data) if input_data else {}
            output_json = json.loads(output_data) if output_data else {}

            if isinstance(input_json, dict) and isinstance(output_json, dict):
                input_keys = set(input_json.keys())
                output_keys = set(output_json.keys())

                diff_data["input_keys"] = list(input_keys)
                diff_data["output_keys"] = list(output_keys)
                diff_data["added_keys"] = list(output_keys - input_keys)
                diff_data["removed_keys"] = list(input_keys - output_keys)

                # Check for changed values in common keys
                common_keys = input_keys & output_keys
                for key in common_keys:
                    if input_json[key] != output_json[key]:
                        diff_data["changed_values"].append(
                            {
                                "key": key,
                                "input_value": (
                                    str(input_json[key])[:100] + "..."
                                    if len(str(input_json[key])) > 100
                                    else str(input_json[key])
                                ),
                                "output_value": (
                                    str(output_json[key])[:100] + "..."
                                    if len(str(output_json[key])) > 100
                                    else str(output_json[key])
                                ),
                            }
                        )

        except json.JSONDecodeError:
            # If not valid JSON, just provide basic size comparison
            pass

        return diff_data

    def visualize_workflow(
        self,
        name: str,
        output_format: str = "ascii",
        save_to: Optional[str] = None,
    ) -> None:
        """Generate ASCII diagram visualization of a Step Function workflow.

        Args:
            name: State machine name or ARN to visualize
            output_format: Output format (ascii, mermaid, dot)
            save_to: Save diagram to file
        """
        try:
            # Find the state machine ARN
            state_machine_arn = self._find_state_machine_arn(name)
            if not state_machine_arn:
                print(f"[red]State machine '{name}' not found.[/red]")
                return

            # Get the state machine definition
            workflow_details = self._get_workflow_details(state_machine_arn)
            definition = workflow_details.get("definition", {})

            if not definition:
                print(f"[red]Could not retrieve definition for '{name}'.[/red]")
                return

            # Generate the diagram based on output format
            if output_format.lower() == "ascii":
                diagram = self._generate_ascii_diagram(
                    definition, workflow_details["name"]
                )
            elif output_format.lower() == "mermaid":
                diagram = self._generate_mermaid_diagram(
                    definition, workflow_details["name"]
                )
            elif output_format.lower() == "dot":
                diagram = self._generate_dot_diagram(
                    definition, workflow_details["name"]
                )
            else:
                print(f"[red]Unsupported output format: {output_format}[/red]")
                return

            # Output or save the diagram
            if save_to:
                self._save_to_file(diagram, save_to)
                print(f"[green]Diagram saved to {save_to}[/green]")
            else:
                print(diagram)

        except Exception as e:
            print(f"[red]Error visualizing workflow: {e}[/red]")

    def _generate_ascii_diagram(self, definition: dict, workflow_name: str) -> str:
        """Generate ASCII diagram of the state machine."""
        lines = [f"State Machine: {workflow_name}", "=" * (len(workflow_name) + 15), ""]

        states = definition.get("States", {})
        start_at = definition.get("StartAt", "")

        if not states:
            return "\n".join(lines + ["No states defined in this workflow."])

        # Track processed states to avoid infinite loops
        processed_states: set[str] = set()
        diagram_lines = []

        # Start the diagram
        if start_at:
            diagram_lines.append(f"StartAt: {start_at}")
            diagram_lines.append("     |")
            diagram_lines.append("     v")
            self._build_ascii_flow(
                states, start_at, diagram_lines, processed_states, indent=0
            )

        lines.extend(diagram_lines)
        return "\n".join(lines)

    def _build_ascii_flow(  # noqa: C901
        self,
        states: dict,
        current_state: str,
        diagram_lines: list,
        processed_states: set,
        indent: int = 0,
    ) -> None:
        """Recursively build ASCII flow diagram."""
        if current_state in processed_states or current_state not in states:
            return

        processed_states.add(current_state)
        state_config = states[current_state]
        state_type = state_config.get("Type", "Unknown")

        # Format the current state
        indent_str = "    " * indent
        state_display = f"[{current_state}]"

        if state_type == "Task":
            resource = state_config.get("Resource", "")
            if "lambda" in resource.lower():
                # Extract Lambda function name
                if ":function:" in resource:
                    func_name = resource.split(":function:")[-1].split(":")[0]
                    state_display = f"[{current_state}] (λ {func_name})"
                else:
                    state_display = f"[{current_state}] (λ)"
            elif resource:
                # Extract service name
                if ":states:" in resource:
                    state_display = f"[{current_state}] (StepFunctions)"
                elif ":sns:" in resource:
                    state_display = f"[{current_state}] (SNS)"
                elif ":sqs:" in resource:
                    state_display = f"[{current_state}] (SQS)"
                else:
                    state_display = f"[{current_state}] (Task)"

        elif state_type == "Choice":
            state_display = f"[{current_state}] (Choice)"
        elif state_type == "Parallel":
            state_display = f"[{current_state}] (Parallel)"
        elif state_type == "Map":
            state_display = f"[{current_state}] (Map)"
        elif state_type == "Wait":
            state_display = f"[{current_state}] (Wait)"
        elif state_type == "Succeed":
            state_display = f"[{current_state}] (Success)"
        elif state_type == "Fail":
            state_display = f"[{current_state}] (Fail)"

        # Handle different state types
        if state_type == "Choice":
            self._handle_choice_state(
                states,
                state_config,
                diagram_lines,
                processed_states,
                indent,
                state_display,
            )
        elif state_type == "Parallel":
            self._handle_parallel_state(
                states,
                state_config,
                diagram_lines,
                processed_states,
                indent,
                state_display,
            )
        elif state_type == "Map":
            self._handle_map_state(
                states,
                state_config,
                diagram_lines,
                processed_states,
                indent,
                state_display,
            )
        else:
            # Simple linear flow
            diagram_lines.append(f"{indent_str}{state_display}")

            # Check for next state
            next_state = state_config.get("Next")
            end = state_config.get("End", False)

            if next_state and not end:
                diagram_lines.append(f"{indent_str}     |")
                diagram_lines.append(f"{indent_str}     v")
                self._build_ascii_flow(
                    states, next_state, diagram_lines, processed_states, indent
                )
            elif end or state_type in ["Succeed", "Fail"]:
                diagram_lines.append(f"{indent_str}     |")
                diagram_lines.append(f"{indent_str}   [END]")

    def _handle_choice_state(
        self,
        states: dict,
        state_config: dict,
        diagram_lines: list,
        processed_states: set,
        indent: int,
        state_display: str,
    ) -> None:
        """Handle Choice state visualization."""
        indent_str = "    " * indent
        diagram_lines.append(f"{indent_str}{state_display}")

        choices = state_config.get("Choices", [])
        default = state_config.get("Default")

        if choices:
            for i, choice in enumerate(choices):
                next_state = choice.get("Next", "")
                # Simplified condition display
                condition = "condition"
                if "StringEquals" in choice:
                    condition = "StringEquals"
                elif "NumericEquals" in choice:
                    condition = "NumericEquals"
                elif "BooleanEquals" in choice:
                    condition = "BooleanEquals"

                if i == 0:
                    diagram_lines.append(
                        f"{indent_str}     ├── ({condition}) --> [{next_state}]"
                    )
                else:
                    diagram_lines.append(
                        f"{indent_str}     ├── ({condition}) --> [{next_state}]"
                    )

                if next_state not in processed_states:
                    self._build_ascii_flow(
                        states, next_state, diagram_lines, processed_states, indent + 1
                    )

        if default:
            diagram_lines.append(f"{indent_str}     └── (default) --> [{default}]")
            if default not in processed_states:
                self._build_ascii_flow(
                    states, default, diagram_lines, processed_states, indent + 1
                )

    def _handle_parallel_state(
        self,
        states: dict,
        state_config: dict,
        diagram_lines: list,
        processed_states: set,
        indent: int,
        state_display: str,
    ) -> None:
        """Handle Parallel state visualization."""
        indent_str = "    " * indent
        diagram_lines.append(f"{indent_str}{state_display}")

        branches = state_config.get("Branches", [])
        if branches:
            diagram_lines.append(f"{indent_str}     |")
            for i, branch in enumerate(branches):
                branch_start = branch.get("StartAt", "")
                if i == 0:
                    diagram_lines.append(
                        f"{indent_str}     ├── Branch {i+1}: [{branch_start}]"
                    )
                else:
                    diagram_lines.append(
                        f"{indent_str}     ├── Branch {i+1}: [{branch_start}]"
                    )

            # Show convergence
            next_state = state_config.get("Next")
            if next_state:
                diagram_lines.append(f"{indent_str}     |")
                diagram_lines.append(f"{indent_str}     v")
                diagram_lines.append(f"{indent_str}[Join] --> [{next_state}]")
                if next_state not in processed_states:
                    self._build_ascii_flow(
                        states, next_state, diagram_lines, processed_states, indent
                    )

    def _handle_map_state(
        self,
        states: dict,
        state_config: dict,
        diagram_lines: list,
        processed_states: set,
        indent: int,
        state_display: str,
    ) -> None:
        """Handle Map state visualization."""
        indent_str = "    " * indent
        iterator = state_config.get("Iterator", {})
        iterator_start = iterator.get("StartAt", "")

        diagram_lines.append(f"{indent_str}{state_display}")
        if iterator_start:
            diagram_lines.append(f"{indent_str}     |")
            diagram_lines.append(f"{indent_str}     v")
            diagram_lines.append(f"{indent_str}   (for each item)")
            diagram_lines.append(f"{indent_str}     |")
            diagram_lines.append(f"{indent_str}     v")
            diagram_lines.append(f"{indent_str}  [{iterator_start}] (iterator)")

        # Show next state after map
        next_state = state_config.get("Next")
        if next_state:
            diagram_lines.append(f"{indent_str}     |")
            diagram_lines.append(f"{indent_str}     v")
            if next_state not in processed_states:
                self._build_ascii_flow(
                    states, next_state, diagram_lines, processed_states, indent
                )

    def _generate_mermaid_diagram(  # noqa: C901
        self, definition: dict, workflow_name: str
    ) -> str:
        """Generate Mermaid diagram of the state machine."""
        lines = [
            "---",
            f"title: {workflow_name}",
            "---",
            "flowchart TD",
        ]

        states = definition.get("States", {})
        start_at = definition.get("StartAt", "")

        # Generate nodes
        for state_name, state_config in states.items():
            state_type = state_config.get("Type", "Unknown")
            if state_type == "Choice":
                lines.append(f"    {state_name}{{{{Choice: {state_name}}}}}")
            elif state_type == "Parallel":
                lines.append(f"    {state_name}[Parallel: {state_name}]")
            elif state_type == "Succeed":
                lines.append(f"    {state_name}((Success: {state_name}))")
            elif state_type == "Fail":
                lines.append(f"    {state_name}((Fail: {state_name}))")
            else:
                lines.append(f"    {state_name}[{state_name}]")

        # Generate connections
        lines.append("")
        if start_at:
            lines.append(f"    Start --> {start_at}")

        for state_name, state_config in states.items():
            state_type = state_config.get("Type", "Unknown")

            if state_type == "Choice":
                choices = state_config.get("Choices", [])
                for choice in choices:
                    next_state = choice.get("Next", "")
                    if next_state:
                        lines.append(f"    {state_name} --> {next_state}")

                default = state_config.get("Default")
                if default:
                    lines.append(f"    {state_name} --> {default}")

            elif state_type == "Parallel":
                branches = state_config.get("Branches", [])
                for _i, branch in enumerate(branches):
                    branch_start = branch.get("StartAt", "")
                    if branch_start:
                        lines.append(f"    {state_name} --> {branch_start}")

                next_state = state_config.get("Next")
                if next_state:
                    lines.append(f"    {state_name} --> {next_state}")

            else:
                next_state = state_config.get("Next")
                if next_state:
                    lines.append(f"    {state_name} --> {next_state}")

        return "\n".join(lines)

    def _generate_dot_diagram(  # noqa: C901
        self, definition: dict, workflow_name: str
    ) -> str:
        """Generate DOT (Graphviz) diagram of the state machine."""
        lines = [
            f'digraph "{workflow_name}" {{',
            f'    label="{workflow_name}";',
            "    rankdir=TD;",
            "    node [shape=box];",
            "",
        ]

        states = definition.get("States", {})
        start_at = definition.get("StartAt", "")

        # Generate nodes with styling
        for state_name, state_config in states.items():
            state_type = state_config.get("Type", "Unknown")
            if state_type == "Choice":
                lines.append(
                    f'    "{state_name}" [shape=diamond, label="{state_name}\\n(Choice)"];'
                )
            elif state_type == "Parallel":
                lines.append(
                    f'    "{state_name}" [shape=parallelogram, label="{state_name}\\n(Parallel)"];'
                )
            elif state_type == "Succeed":
                lines.append(
                    f'    "{state_name}" [shape=doublecircle, style=filled, fillcolor=lightgreen, label="{state_name}\\n(Success)"];'
                )
            elif state_type == "Fail":
                lines.append(
                    f'    "{state_name}" [shape=doublecircle, style=filled, fillcolor=lightcoral, label="{state_name}\\n(Fail)"];'
                )
            else:
                lines.append(
                    f'    "{state_name}" [label="{state_name}\\n({state_type})"];'
                )

        # Generate connections
        lines.append("")
        lines.append("    Start [shape=circle, style=filled, fillcolor=lightblue];")
        if start_at:
            lines.append(f'    Start -> "{start_at}";')

        for state_name, state_config in states.items():
            state_type = state_config.get("Type", "Unknown")

            if state_type == "Choice":
                choices = state_config.get("Choices", [])
                for i, choice in enumerate(choices):
                    next_state = choice.get("Next", "")
                    if next_state:
                        lines.append(
                            f'    "{state_name}" -> "{next_state}" [label="choice {i+1}"];'
                        )

                default = state_config.get("Default")
                if default:
                    lines.append(
                        f'    "{state_name}" -> "{default}" [label="default"];'
                    )

            elif state_type == "Parallel":
                branches = state_config.get("Branches", [])
                for i, branch in enumerate(branches):
                    branch_start = branch.get("StartAt", "")
                    if branch_start:
                        lines.append(
                            f'    "{state_name}" -> "{branch_start}" [label="branch {i+1}"];'
                        )

                next_state = state_config.get("Next")
                if next_state:
                    lines.append(f'    "{state_name}" -> "{next_state}";')

            else:
                next_state = state_config.get("Next")
                if next_state:
                    lines.append(f'    "{state_name}" -> "{next_state}";')

        lines.append("}")
        return "\n".join(lines)

    def analyze_workflow_resources(
        self,
        name: str,
        output_format: str = "table",
        show_unused: bool = False,
        save_to: Optional[str] = None,
    ) -> None:
        """Analyze and display all AWS resources used by a Step Function workflow.

        Args:
            name: State machine name or ARN to analyze
            output_format: Output format (table, json, yaml, csv)
            show_unused: Include potentially unused resources
            save_to: Save analysis to file
        """
        try:
            # Find the state machine ARN
            state_machine_arn = self._find_state_machine_arn(name)
            if not state_machine_arn:
                print(f"[red]State machine '{name}' not found.[/red]")
                return

            # Get the state machine definition
            workflow_details = self._get_workflow_details(state_machine_arn)
            definition = workflow_details.get("definition", {})

            if not definition:
                print(f"[red]Could not retrieve definition for '{name}'.[/red]")
                return

            # Analyze resources from the definition
            resources = self._extract_workflow_resources(definition, workflow_details)

            # Output the analysis based on format
            if output_format.lower() == "json":
                output_str = json.dumps(resources, indent=2, default=str)
                if save_to:
                    self._save_to_file(output_str, save_to)
                    print(f"[green]Resource analysis saved to {save_to}[/green]")
                else:
                    print(output_str)
            elif output_format.lower() == "yaml":
                import yaml

                output_str = yaml.dump(resources, default_flow_style=False)
                if save_to:
                    self._save_to_file(output_str, save_to)
                    print(f"[green]Resource analysis saved to {save_to}[/green]")
                else:
                    print(output_str)
            elif output_format.lower() == "csv":
                self._print_resources_csv(resources, save_to)
            else:  # table format
                self._print_resources_table(resources, workflow_details["name"])

        except Exception as e:
            print(f"[red]Error analyzing workflow resources: {e}[/red]")

    def _extract_workflow_resources(  # noqa: C901
        self, definition: dict, workflow_details: dict
    ) -> dict:
        """Extract all AWS resources from the workflow definition."""
        resources = {
            "workflow_name": workflow_details.get("name", ""),
            "workflow_arn": workflow_details.get("arn", ""),
            "analysis_timestamp": self._format_date(None),  # Current time
            "resources": [],
            "summary": {
                "total_resources": 0,
                "by_type": {},
                "regions": set(),
                "accounts": set(),
            },
        }

        states = definition.get("States", {})

        for state_name, state_config in states.items():
            state_type = state_config.get("Type", "")

            # Extract resources from Task states
            if state_type == "Task":
                resource_arn = state_config.get("Resource", "")
                parameters = state_config.get("Parameters", {})

                # First, check for additional resources in parameters (e.g., Lambda function ARNs)
                additional_resources = self._extract_resources_from_parameters(
                    parameters, state_name
                )

                if additional_resources:
                    # If we found specific resources in parameters, use those
                    resources["resources"].extend(additional_resources)
                elif resource_arn:
                    # Only add the generic resource if we didn't find specific ones in parameters
                    resource_info = self._parse_resource_arn(resource_arn, state_name)
                    if resource_info:
                        resources["resources"].append(
                            resource_info
                        )  # Extract resources from Parallel states
            elif state_type == "Parallel":
                branches = state_config.get("Branches", [])
                for i, branch in enumerate(branches):
                    branch_resources = self._extract_workflow_resources(
                        branch,
                        {
                            "name": f"{workflow_details.get('name', '')}-branch-{i+1}",
                            "arn": "",
                        },
                    )
                    resources["resources"].extend(branch_resources["resources"])

            # Extract resources from Map states
            elif state_type == "Map":
                iterator = state_config.get("Iterator", {})
                if iterator:
                    iterator_resources = self._extract_workflow_resources(
                        iterator,
                        {
                            "name": f"{workflow_details.get('name', '')}-iterator",
                            "arn": "",
                        },
                    )
                    resources["resources"].extend(iterator_resources["resources"])

        # Deduplicate resources
        seen_arns = set()
        unique_resources = []
        for resource in resources["resources"]:
            arn = resource.get("arn", "")
            if arn and arn not in seen_arns:
                seen_arns.add(arn)
                unique_resources.append(resource)

        resources["resources"] = unique_resources

        # Generate summary
        resources["summary"]["total_resources"] = len(unique_resources)
        type_counts: dict[str, int] = {}
        regions = set()
        accounts = set()

        for resource in unique_resources:
            resource_type = resource.get("type", "Unknown")
            type_counts[resource_type] = type_counts.get(resource_type, 0) + 1

            if resource.get("region"):
                regions.add(resource["region"])
            if resource.get("account"):
                accounts.add(resource["account"])

        resources["summary"]["by_type"] = type_counts
        resources["summary"]["regions"] = list(regions)
        resources["summary"]["accounts"] = list(accounts)

        return resources

    def _parse_resource_arn(self, resource_arn: str, state_name: str) -> Optional[dict]:
        """Parse AWS resource ARN and extract metadata."""
        try:
            # Handle AWS service integrations (non-ARN resources)
            if not resource_arn.startswith("arn:"):
                return self._parse_service_integration(resource_arn, state_name)

            # Parse standard ARN format: arn:partition:service:region:account:resource-type/resource-id
            parts = resource_arn.split(":")
            if len(parts) < 6:
                return None

            partition = parts[1]
            service = parts[2]
            region = parts[3] or "global"
            account = parts[4] or "unknown"
            resource_part = ":".join(parts[5:])

            # Extract resource type and name/id
            resource_type, resource_name = self._extract_resource_details(
                service, resource_part
            )

            return {
                "arn": resource_arn,
                "type": resource_type,
                "service": service,
                "name": resource_name,
                "region": region,
                "account": account,
                "partition": partition,
                "used_in_state": state_name,
                "full_resource": resource_part,
            }

        except Exception:
            return {
                "arn": resource_arn,
                "type": "Unknown",
                "service": "unknown",
                "name": resource_arn,
                "region": "unknown",
                "account": "unknown",
                "partition": "aws",
                "used_in_state": state_name,
                "full_resource": resource_arn,
            }

    def _extract_resources_from_parameters(  # noqa: C901
        self, parameters: dict, state_name: str
    ) -> list[dict]:
        """Extract additional AWS resources from state parameters."""
        resources = []

        # Look for Lambda function ARNs in parameters
        function_name = parameters.get("FunctionName")
        if function_name and isinstance(function_name, str):
            if function_name.startswith("arn:aws:lambda:"):
                # This is a full Lambda function ARN
                resource_info = self._parse_resource_arn(function_name, state_name)
                if resource_info:
                    resources.append(resource_info)
            elif function_name:
                # This might be a function name, create a placeholder resource
                resources.append(
                    {
                        "arn": function_name,
                        "type": "Lambda Function",
                        "service": "lambda",
                        "name": function_name,
                        "region": "unknown",
                        "account": "unknown",
                        "partition": "aws",
                        "used_in_state": state_name,
                        "full_resource": function_name,
                    }
                )

        # Look for other resource ARNs in parameters (recursive search)
        for key, value in parameters.items():
            if isinstance(value, str) and value.startswith("arn:aws:"):
                # Found an ARN in parameters
                resource_info = self._parse_resource_arn(value, state_name)
                if resource_info:
                    resources.append(resource_info)
            elif isinstance(value, dict):
                # Recursively search nested parameters
                nested_resources = self._extract_resources_from_parameters(
                    value, state_name
                )
                resources.extend(nested_resources)
            elif key in ["TableName", "QueueUrl", "TopicArn", "BucketName"]:
                # Common parameter names that reference AWS resources
                if isinstance(value, str) and value:
                    # Create a resource entry for these common parameter types
                    resource_type = self._get_resource_type_from_param_name(key)
                    resources.append(
                        {
                            "arn": value,
                            "type": resource_type,
                            "service": self._get_service_from_param_name(key),
                            "name": value,
                            "region": "unknown",
                            "account": "unknown",
                            "partition": "aws",
                            "used_in_state": state_name,
                            "full_resource": value,
                        }
                    )

        return resources

    def _get_resource_type_from_param_name(self, param_name: str) -> str:
        """Get resource type from parameter name."""
        mapping = {
            "TableName": "DynamoDB Table",
            "QueueUrl": "SQS Queue",
            "TopicArn": "SNS Topic",
            "BucketName": "S3 Bucket",
            "ClusterName": "ECS Cluster",
            "JobQueue": "Batch Job Queue",
            "JobDefinition": "Batch Job Definition",
        }
        return mapping.get(param_name, "AWS Resource")

    def _get_service_from_param_name(self, param_name: str) -> str:
        """Get AWS service name from parameter name."""
        mapping = {
            "TableName": "dynamodb",
            "QueueUrl": "sqs",
            "TopicArn": "sns",
            "BucketName": "s3",
            "ClusterName": "ecs",
            "JobQueue": "batch",
            "JobDefinition": "batch",
        }
        return mapping.get(param_name, "unknown")

    def _parse_service_integration(
        self, resource: str, state_name: str
    ) -> Optional[dict]:
        """Parse AWS service integrations that don't use ARN format."""
        service_mappings = {
            "lambda": "Lambda Function",
            "ecs": "ECS Task",
            "batch": "Batch Job",
            "glue": "Glue Job",
            "emr": "EMR Cluster",
            "athena": "Athena Query",
            "dynamodb": "DynamoDB",
            "sqs": "SQS Queue",
            "sns": "SNS Topic",
            "s3": "S3 Bucket",
            "eventbridge": "EventBridge",
            "apigateway": "API Gateway",
            "codebuild": "CodeBuild",
        }

        # Extract service name from resource string
        for service_key, service_name in service_mappings.items():
            if service_key in resource.lower():
                return {
                    "arn": resource,
                    "type": service_name,
                    "service": service_key,
                    "name": resource,
                    "region": "unknown",
                    "account": "unknown",
                    "partition": "aws",
                    "used_in_state": state_name,
                    "full_resource": resource,
                }

        return {
            "arn": resource,
            "type": "AWS Service Integration",
            "service": "unknown",
            "name": resource,
            "region": "unknown",
            "account": "unknown",
            "partition": "aws",
            "used_in_state": state_name,
            "full_resource": resource,
        }

    def _extract_resource_details(
        self, service: str, resource_part: str
    ) -> tuple[str, str]:
        """Extract resource type and name from the resource part of an ARN."""
        service_mappings = {
            "lambda": ("Lambda Function", self._extract_lambda_name),
            "states": ("Step Functions", self._extract_stepfunctions_name),
            "ecs": ("ECS Task", self._extract_ecs_name),
            "batch": ("Batch Job", self._extract_batch_name),
            "glue": ("Glue Job", self._extract_glue_name),
            "dynamodb": ("DynamoDB Table", self._extract_dynamodb_name),
            "sqs": ("SQS Queue", self._extract_sqs_name),
            "sns": ("SNS Topic", self._extract_sns_name),
            "s3": ("S3 Bucket", self._extract_s3_name),
            "events": ("EventBridge Rule", self._extract_eventbridge_name),
            "apigateway": ("API Gateway", self._extract_apigateway_name),
            "codebuild": ("CodeBuild Project", self._extract_codebuild_name),
        }

        if service in service_mappings:
            resource_type, extractor_func = service_mappings[service]
            resource_name = extractor_func(resource_part)
            return resource_type, resource_name

        return f"{service.upper()} Resource", resource_part

    def _extract_lambda_name(self, resource_part: str) -> str:
        """Extract Lambda function name from resource part."""
        # Format: function:function-name or function:function-name:alias
        if resource_part.startswith("function:"):
            parts = resource_part.split(":")
            return parts[1] if len(parts) > 1 else resource_part
        return resource_part

    def _extract_stepfunctions_name(self, resource_part: str) -> str:
        """Extract Step Functions state machine name."""
        # Format: stateMachine:name or execution:name
        if ":" in resource_part:
            return resource_part.split(":")[-1]
        return resource_part

    def _extract_ecs_name(self, resource_part: str) -> str:
        """Extract ECS task definition name."""
        # Format: task-definition/family:revision
        if resource_part.startswith("task-definition/"):
            return resource_part.replace("task-definition/", "")
        return resource_part

    def _extract_batch_name(self, resource_part: str) -> str:
        """Extract Batch job definition name."""
        if ":" in resource_part:
            return resource_part.split(":")[-1]
        return resource_part

    def _extract_glue_name(self, resource_part: str) -> str:
        """Extract Glue job name."""
        if resource_part.startswith("job/"):
            return resource_part.replace("job/", "")
        return resource_part

    def _extract_dynamodb_name(self, resource_part: str) -> str:
        """Extract DynamoDB table name."""
        # Format: table/table-name
        if resource_part.startswith("table/"):
            return resource_part.replace("table/", "")
        return resource_part

    def _extract_sqs_name(self, resource_part: str) -> str:
        """Extract SQS queue name."""
        # Format: queue-name (last part of the resource)
        return resource_part.split("/")[-1] if "/" in resource_part else resource_part

    def _extract_sns_name(self, resource_part: str) -> str:
        """Extract SNS topic name."""
        # Format: topic-name (last part)
        return resource_part.split(":")[-1] if ":" in resource_part else resource_part

    def _extract_s3_name(self, resource_part: str) -> str:
        """Extract S3 bucket name."""
        # Format: bucket-name or bucket-name/key
        return resource_part.split("/")[0] if "/" in resource_part else resource_part

    def _extract_eventbridge_name(self, resource_part: str) -> str:
        """Extract EventBridge rule name."""
        # Format: rule/rule-name
        if resource_part.startswith("rule/"):
            return resource_part.replace("rule/", "")
        return resource_part

    def _extract_apigateway_name(self, resource_part: str) -> str:
        """Extract API Gateway name."""
        return resource_part

    def _extract_codebuild_name(self, resource_part: str) -> str:
        """Extract CodeBuild project name."""
        # Format: project/project-name
        if resource_part.startswith("project/"):
            return resource_part.replace("project/", "")
        return resource_part

    def _print_resources_table(self, resources: dict, workflow_name: str) -> None:
        """Print resources in a formatted table."""
        from rich import box
        from rich.table import Table

        # Main resources table
        table = Table(
            title=f"Resources used by workflow: {workflow_name}",
            show_header=True,
            header_style="bold cyan",
            box=box.SIMPLE,
            border_style="dim",
        )
        table.add_column("Type", style="cyan", no_wrap=True)
        table.add_column("Name", style="green")
        table.add_column("ARN / Identifier", style="white", overflow="fold")
        table.add_column("Region", style="yellow", no_wrap=True)
        table.add_column("Used in State", style="magenta")

        resource_list = resources.get("resources", [])

        # Sort resources by type, then by name
        sorted_resources = sorted(
            resource_list, key=lambda x: (x.get("type", ""), x.get("name", ""))
        )

        for resource in sorted_resources:
            table.add_row(
                resource.get("type", "Unknown"),
                resource.get("name", ""),
                resource.get("arn", ""),
                resource.get("region", "unknown"),
                resource.get("used_in_state", ""),
            )

        self.console.print(table)

        # Summary table
        summary = resources.get("summary", {})
        if summary:
            print("\n[bold]📊 Resource Summary:[/bold]")

            summary_table = Table(
                show_header=True,
                header_style="bold cyan",
                box=box.SIMPLE,
                border_style="dim",
            )
            summary_table.add_column("Metric", style="cyan")
            summary_table.add_column("Value", style="white")

            summary_table.add_row(
                "Total Resources", str(summary.get("total_resources", 0))
            )
            summary_table.add_row(
                "Unique Regions", str(len(summary.get("regions", [])))
            )
            summary_table.add_row("AWS Accounts", str(len(summary.get("accounts", []))))

            # Resource type breakdown
            by_type = summary.get("by_type", {})
            for resource_type, count in sorted(by_type.items()):
                summary_table.add_row(f"  {resource_type}", str(count))

            self.console.print(summary_table)

            # Regions and accounts
            if summary.get("regions"):
                print(f"\n[bold]🌍 Regions:[/bold] {', '.join(summary['regions'])}")
            if summary.get("accounts"):
                print(f"[bold]🏢 Accounts:[/bold] {', '.join(summary['accounts'])}")

    def _print_resources_csv(
        self, resources: dict, save_to: Optional[str] = None
    ) -> None:
        """Print or save resources in CSV format."""
        import csv
        import io

        output = io.StringIO()
        writer = csv.writer(output)

        # Write header
        writer.writerow(
            ["Type", "Name", "ARN", "Region", "Account", "Service", "Used_in_State"]
        )

        # Write resource data
        resource_list = resources.get("resources", [])
        for resource in sorted(
            resource_list, key=lambda x: (x.get("type", ""), x.get("name", ""))
        ):
            writer.writerow(
                [
                    resource.get("type", ""),
                    resource.get("name", ""),
                    resource.get("arn", ""),
                    resource.get("region", ""),
                    resource.get("account", ""),
                    resource.get("service", ""),
                    resource.get("used_in_state", ""),
                ]
            )

        csv_content = output.getvalue()
        output.close()

        if save_to:
            self._save_to_file(csv_content, save_to)
            print(f"[green]Resource analysis saved to {save_to}[/green]")
        else:
            print(csv_content)
