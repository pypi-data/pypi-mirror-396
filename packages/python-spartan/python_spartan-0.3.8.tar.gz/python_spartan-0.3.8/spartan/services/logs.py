"""Logs service for unified AWS CloudWatch log management across multiple services.

This module provides comprehensive CloudWatch log access for Lambda, Glue, ECS,
Step Functions, and direct log group access with consistent filtering and formatting.
"""

import json
import re
import time
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import boto3
import yaml
from botocore.exceptions import ClientError
from rich import print
from rich.console import Console


class LogsService:
    """Service for unified CloudWatch logs management across AWS services."""

    def __init__(
        self,
        region: Optional[str] = None,
        profile: Optional[str] = None,
    ):
        """Initialize the logs service with AWS configuration.

        Args:
            region: AWS region to use
            profile: AWS profile to use
        """
        self.region = region
        self.profile = profile
        self.console = Console()

        # Initialize AWS session and clients
        try:
            if profile:
                self.session = boto3.Session(profile_name=profile)
            else:
                self.session = boto3.Session()

            self.logs_client = self.session.client("logs", region_name=region)
            self.lambda_client = self.session.client("lambda", region_name=region)
            self.glue_client = self.session.client("glue", region_name=region)
            self.ecs_client = self.session.client("ecs", region_name=region)
            self.stepfunctions_client = self.session.client(
                "stepfunctions", region_name=region
            )

        except Exception as e:
            print(f"[red]Error initializing AWS clients: {e}[/red]")
            self.logs_client = None
            self.lambda_client = None
            self.glue_client = None
            self.ecs_client = None
            self.stepfunctions_client = None

    def _parse_time_filter(self, time_str: str) -> Optional[datetime]:
        """Parse time filter supporting relative and absolute formats.

        Args:
            time_str: Time string (e.g., '5m', '1h', '2d', ISO format)

        Returns:
            datetime object or None if invalid
        """
        if not time_str:
            return None

        # Handle relative time (5m, 1h, 2d)
        if re.match(r"^\d+[mhd]$", time_str):
            value = int(time_str[:-1])
            unit = time_str[-1]

            if unit == "m":
                return datetime.utcnow() - timedelta(minutes=value)
            elif unit == "h":
                return datetime.utcnow() - timedelta(hours=value)
            elif unit == "d":
                return datetime.utcnow() - timedelta(days=value)

        # Handle ISO format
        try:
            return datetime.fromisoformat(time_str.replace("Z", "+00:00"))
        except ValueError:
            try:
                # Try parsing without timezone
                return datetime.fromisoformat(time_str)
            except ValueError:
                print(f"[red]Invalid time format: {time_str}[/red]")
                return None

    def _format_log_event(
        self,
        event: Dict[str, Any],
        format_type: str = "text",
        highlight_pattern: Optional[str] = None,
        mask_secrets: bool = True,
        timestamps_only: bool = False,
    ) -> str:
        """Format a single log event for display.

        Args:
            event: CloudWatch log event
            format_type: Output format (text, json, yaml)
            highlight_pattern: Pattern to highlight in log messages
            mask_secrets: Whether to mask potential secrets in logs
            timestamps_only: Show only timestamps and basic info for CI pipelines

        Returns:
            Formatted log event string
        """
        timestamp = datetime.fromtimestamp(event["timestamp"] / 1000)
        message = event["message"].strip()

        # Mask potential secrets if enabled
        if mask_secrets:
            message = self._mask_secrets(message)

        if timestamps_only:
            # Minimal output for CI pipelines
            formatted_time = timestamp.strftime("%Y-%m-%d %H:%M:%S")
            return f"{formatted_time} {len(message)} chars"

        if format_type == "json":
            return json.dumps(
                {
                    "timestamp": timestamp.isoformat(),
                    "message": message,
                    "logStream": event.get("logStreamName", ""),
                },
                indent=2,
            )
        elif format_type == "yaml":
            return yaml.dump(
                {
                    "timestamp": timestamp.isoformat(),
                    "message": message,
                    "logStream": event.get("logStreamName", ""),
                },
                default_flow_style=False,
            )
        else:  # text format
            formatted_time = timestamp.strftime("%Y-%m-%d %H:%M:%S")
            formatted_msg = f"[dim]{formatted_time}[/dim] {message}"

            # Apply highlighting if pattern provided
            if highlight_pattern and highlight_pattern.upper() in message.upper():
                formatted_msg = formatted_msg.replace(
                    highlight_pattern.upper(), f"[red]{highlight_pattern.upper()}[/red]"
                )
                formatted_msg = formatted_msg.replace(
                    highlight_pattern.lower(), f"[red]{highlight_pattern.lower()}[/red]"
                )

            return formatted_msg

    def _mask_secrets(self, message: str) -> str:
        """Mask potential secrets in log messages.

        Args:
            message: Log message to process

        Returns:
            Message with masked secrets
        """
        import re

        # Common secret patterns
        patterns = [
            # AWS Access Keys
            (r"AKIA[0-9A-Z]{16}", "AKIA****************"),
            # AWS Secret Keys (40 char base64)
            (r"[A-Za-z0-9/+=]{40}", "*" * 40),
            # Generic API keys
            (r"[Aa]pi[_-]?[Kk]ey[\"'\s]*[:=][\"'\s]*[A-Za-z0-9]{20,}", "api_key=***"),
            # Tokens
            (r"[Tt]oken[\"'\s]*[:=][\"'\s]*[A-Za-z0-9]{20,}", "token=***"),
            # Passwords
            (r"[Pp]assword[\"'\s]*[:=][\"'\s]*[^\s\"']{8,}", "password=***"),
            # Email addresses (partial masking)
            (r"([a-zA-Z0-9._%+-]+)@([a-zA-Z0-9.-]+\.[a-zA-Z]{2,})", r"\1***@\2"),
        ]

        masked_message = message
        for pattern, replacement in patterns:
            masked_message = re.sub(pattern, replacement, masked_message)

        return masked_message

    def _write_to_file(self, content: str, output_path: str) -> None:
        """Write content to a file.

        Args:
            content: Content to write
            output_path: File path to write to
        """
        try:
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"[green]Logs saved to: {output_path}[/green]")
        except Exception as e:
            print(f"[red]Error writing to file {output_path}: {e}[/red]")

    def lambda_logs(
        self,
        function_name: str,
        start_time: Optional[str] = None,
        end_time: Optional[str] = None,
        filter_pattern: Optional[str] = None,
        tail: bool = False,
        limit: int = 100,
        format_type: str = "text",
        output: Optional[str] = None,
        highlight: Optional[str] = None,
        mask_secrets: bool = True,
        timestamps_only: bool = False,
    ) -> None:
        """Fetch or tail logs from a Lambda function.

        Args:
            function_name: Lambda function name
            start_time: Start time filter
            end_time: End time filter
            filter_pattern: CloudWatch filter pattern
            tail: Whether to stream logs live
            limit: Maximum number of log events
            format_type: Output format (text, json, yaml)
            output: File path to save logs
            highlight: Pattern to highlight in logs
            mask_secrets: Whether to mask potential secrets
            timestamps_only: Show minimal output for CI pipelines
        """
        if not self.logs_client or not self.lambda_client:
            print("[red]Error: AWS clients not initialized[/red]")
            return

        try:
            # Get function configuration to derive log group
            function_response = self.lambda_client.get_function_configuration(
                FunctionName=function_name
            )
            log_group_name = f"/aws/lambda/{function_response['FunctionName']}"

            self.log_group_logs(
                log_group_name=log_group_name,
                start_time=start_time,
                end_time=end_time,
                filter_pattern=filter_pattern,
                tail=tail,
                limit=limit,
                format_type=format_type,
                output=output,
                highlight=highlight,
                mask_secrets=mask_secrets,
                timestamps_only=timestamps_only,
            )

        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            if error_code == "ResourceNotFoundException":
                print(f"[red]Lambda function '{function_name}' not found[/red]")
            else:
                print(f"[red]AWS Error: {e.response['Error']['Message']}[/red]")
        except Exception as e:
            print(f"[red]Error fetching Lambda logs: {e}[/red]")

    def glue_logs(
        self,
        job_name: str,
        run_id: str,
        start_time: Optional[str] = None,
        end_time: Optional[str] = None,
        filter_pattern: Optional[str] = None,
        tail: bool = False,
        limit: int = 100,
        format_type: str = "text",
        output: Optional[str] = None,
        highlight: Optional[str] = None,
    ) -> None:
        """Retrieve logs from a specific Glue job run.

        Args:
            job_name: Glue job name
            run_id: Job run ID
            start_time: Start time filter
            end_time: End time filter
            filter_pattern: CloudWatch filter pattern
            tail: Whether to stream logs live
            limit: Maximum number of log events
            format_type: Output format (text, json, yaml)
            output: File path to save logs
            highlight: Pattern to highlight in logs
        """
        if not self.logs_client or not self.glue_client:
            print("[red]Error: AWS clients not initialized[/red]")
            return

        try:
            # Derive log group name for Glue job
            log_group_name = "/aws-glue/jobs/logs-v2"

            # Use job run specific log stream pattern
            log_stream_prefix = run_id

            self._fetch_logs_with_stream_filter(
                log_group_name=log_group_name,
                log_stream_prefix=log_stream_prefix,
                start_time=start_time,
                end_time=end_time,
                filter_pattern=filter_pattern,
                tail=tail,
                limit=limit,
                format_type=format_type,
                output=output,
                highlight=highlight,
            )

        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            if error_code == "EntityNotFoundException":
                print(f"[red]Job run '{run_id}' not found for job '{job_name}'[/red]")
            else:
                print(f"[red]AWS Error: {e.response['Error']['Message']}[/red]")
        except Exception as e:
            print(f"[red]Error fetching Glue logs: {e}[/red]")

    def ecs_logs(
        self,
        task_id: str,
        cluster: Optional[str] = None,
        container: Optional[str] = None,
        start_time: Optional[str] = None,
        end_time: Optional[str] = None,
        filter_pattern: Optional[str] = None,
        tail: bool = False,
        limit: int = 100,
        format_type: str = "text",
        output: Optional[str] = None,
        highlight: Optional[str] = None,
    ) -> None:
        """Fetch logs from an ECS task.

        Args:
            task_id: ECS task ID or ARN
            cluster: ECS cluster name (optional)
            container: Specific container name (optional)
            start_time: Start time filter
            end_time: End time filter
            filter_pattern: CloudWatch filter pattern
            tail: Whether to stream logs live
            limit: Maximum number of log events
            format_type: Output format (text, json, yaml)
            output: File path to save logs
            highlight: Pattern to highlight in logs
        """
        if not self.logs_client or not self.ecs_client:
            print("[red]Error: AWS clients not initialized[/red]")
            return

        try:
            # Get task details to find log group
            if cluster:
                task_response = self.ecs_client.describe_tasks(
                    cluster=cluster, tasks=[task_id]
                )
            else:
                # Try to find the task across clusters
                clusters_response = self.ecs_client.list_clusters()
                task_response = None

                for cluster_arn in clusters_response.get("clusterArns", []):
                    try:
                        task_response = self.ecs_client.describe_tasks(
                            cluster=cluster_arn, tasks=[task_id]
                        )
                        if task_response.get("tasks"):
                            break
                    except ClientError:
                        continue

            if not task_response or not task_response.get("tasks"):
                print(f"[red]Task '{task_id}' not found[/red]")
                return

            task = task_response["tasks"][0]
            task_def_arn = task.get("taskDefinitionArn")

            if not task_def_arn:
                print("[red]Task definition ARN not found[/red]")
                return

            # Get task definition to find log configuration
            task_def_response = self.ecs_client.describe_task_definition(
                taskDefinition=task_def_arn
            )

            containers = task_def_response["taskDefinition"].get(
                "containerDefinitions", []
            )

            # Find container and its log configuration
            target_containers = []
            if container:
                target_containers = [c for c in containers if c["name"] == container]
                if not target_containers:
                    print(f"[red]Container '{container}' not found in task[/red]")
                    return
            else:
                target_containers = containers

            for container_def in target_containers:
                log_config = container_def.get("logConfiguration", {})
                if log_config.get("logDriver") == "awslogs":
                    log_group = log_config["options"].get("awslogs-group")
                    log_stream_prefix = log_config["options"].get(
                        "awslogs-stream-prefix", ""
                    )

                    if log_group:
                        container_name = container_def["name"]
                        print(
                            f"[blue]Fetching logs for container '{container_name}'...[/blue]"
                        )

                        # Construct log stream name
                        task_id_short = (
                            task_id.split("/")[-1] if "/" in task_id else task_id
                        )
                        log_stream_name = (
                            f"{log_stream_prefix}/{container_name}/{task_id_short}"
                        )

                        self._fetch_logs_with_stream_filter(
                            log_group_name=log_group,
                            log_stream_prefix=log_stream_name,
                            start_time=start_time,
                            end_time=end_time,
                            filter_pattern=filter_pattern,
                            tail=tail,
                            limit=limit,
                            format_type=format_type,
                            output=output,
                            highlight=highlight,
                        )
                    else:
                        print(
                            f"[yellow]No CloudWatch log group configured for container '{container_def['name']}'[/yellow]"
                        )

        except ClientError as e:
            print(f"[red]AWS Error: {e.response['Error']['Message']}[/red]")
        except Exception as e:
            print(f"[red]Error fetching ECS logs: {e}[/red]")

    def step_logs(
        self,
        execution_id: str,
        start_time: Optional[str] = None,
        end_time: Optional[str] = None,
        filter_pattern: Optional[str] = None,
        tail: bool = False,
        limit: int = 100,
        format_type: str = "text",
        output: Optional[str] = None,
        highlight: Optional[str] = None,
    ) -> None:
        """View logs and output for a Step Function execution.

        Args:
            execution_id: Step Function execution ARN or name
            start_time: Start time filter
            end_time: End time filter
            filter_pattern: CloudWatch filter pattern
            tail: Whether to stream logs live
            limit: Maximum number of log events
            format_type: Output format (text, json, yaml)
            output: File path to save logs
            highlight: Pattern to highlight in logs
        """
        if not self.logs_client or not self.stepfunctions_client:
            print("[red]Error: AWS clients not initialized[/red]")
            return

        try:
            # Get execution details
            execution_response = self.stepfunctions_client.describe_execution(
                executionArn=execution_id
            )

            execution_arn = execution_response["executionArn"]
            state_machine_arn = execution_response["stateMachineArn"]

            # Get state machine details to find log group
            state_machine_response = self.stepfunctions_client.describe_state_machine(
                stateMachineArn=state_machine_arn
            )

            logging_config = state_machine_response.get("loggingConfiguration", {})
            log_groups = logging_config.get("destinations", [])

            if not log_groups:
                print(
                    "[yellow]No CloudWatch logging configured for this state machine[/yellow]"
                )
                return

            # Extract execution name from ARN for log stream filtering
            execution_name = execution_arn.split(":")[-1]

            for log_dest in log_groups:
                log_group_name = log_dest.get("cloudWatchLogsLogGroup", {}).get(
                    "logGroupArn", ""
                )
                if log_group_name:
                    # Extract just the log group name from ARN
                    log_group_name = log_group_name.split(":")[-1]

                    print(
                        f"[blue]Fetching Step Function execution logs from '{log_group_name}'...[/blue]"
                    )

                    self._fetch_logs_with_stream_filter(
                        log_group_name=log_group_name,
                        log_stream_prefix=execution_name,
                        start_time=start_time,
                        end_time=end_time,
                        filter_pattern=filter_pattern,
                        tail=tail,
                        limit=limit,
                        format_type=format_type,
                        output=output,
                        highlight=highlight,
                    )

        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            if error_code == "ExecutionDoesNotExist":
                print(f"[red]Step Function execution '{execution_id}' not found[/red]")
            else:
                print(f"[red]AWS Error: {e.response['Error']['Message']}[/red]")
        except Exception as e:
            print(f"[red]Error fetching Step Function logs: {e}[/red]")

    def log_group_logs(
        self,
        log_group_name: str,
        start_time: Optional[str] = None,
        end_time: Optional[str] = None,
        filter_pattern: Optional[str] = None,
        tail: bool = False,
        limit: int = 100,
        format_type: str = "text",
        output: Optional[str] = None,
        highlight: Optional[str] = None,
        mask_secrets: bool = True,
        timestamps_only: bool = False,
    ) -> None:
        """Raw access to any CloudWatch log group.

        Args:
            log_group_name: CloudWatch log group name
            start_time: Start time filter
            end_time: End time filter
            filter_pattern: CloudWatch filter pattern
            tail: Whether to stream logs live
            limit: Maximum number of log events
            format_type: Output format (text, json, yaml)
            output: File path to save logs
            highlight: Pattern to highlight in logs
            mask_secrets: Whether to mask potential secrets
            timestamps_only: Show minimal output for CI pipelines
        """
        self._fetch_logs_with_stream_filter(
            log_group_name=log_group_name,
            log_stream_prefix=None,
            start_time=start_time,
            end_time=end_time,
            filter_pattern=filter_pattern,
            tail=tail,
            limit=limit,
            format_type=format_type,
            output=output,
            highlight=highlight,
            mask_secrets=mask_secrets,
            timestamps_only=timestamps_only,
        )

    def search_logs(
        self,
        log_groups: List[str],
        pattern: str,
        start_time: Optional[str] = None,
        end_time: Optional[str] = None,
        limit: int = 100,
        format_type: str = "text",
        output: Optional[str] = None,
        highlight: Optional[str] = None,
    ) -> None:
        """Grep-like filtering across one or more log groups using a pattern.

        Args:
            log_groups: List of log group names to search
            pattern: Search pattern
            start_time: Start time filter
            end_time: End time filter
            limit: Maximum number of log events
            format_type: Output format (text, json, yaml)
            output: File path to save logs
            highlight: Pattern to highlight in logs
        """
        if not self.logs_client:
            print("[red]Error: AWS logs client not initialized[/red]")
            return

        all_events = []

        for log_group_name in log_groups:
            print(f"[blue]Searching in log group: {log_group_name}[/blue]")

            try:
                # Use the pattern as a filter pattern
                events = self._fetch_log_events(
                    log_group_name=log_group_name,
                    log_stream_prefix=None,
                    start_time=start_time,
                    end_time=end_time,
                    filter_pattern=pattern,
                    limit=limit,
                )

                for event in events:
                    event["log_group"] = log_group_name
                    all_events.append(event)

            except ClientError as e:
                error_code = e.response["Error"]["Code"]
                if error_code == "ResourceNotFoundException":
                    print(f"[yellow]Log group '{log_group_name}' not found[/yellow]")
                else:
                    print(
                        f"[red]Error searching {log_group_name}: {e.response['Error']['Message']}[/red]"
                    )
            except Exception as e:
                print(f"[red]Error searching {log_group_name}: {e}[/red]")

        # Sort all events by timestamp
        all_events.sort(key=lambda x: x["timestamp"])

        # Apply limit across all groups
        if len(all_events) > limit:
            all_events = all_events[-limit:]

        self._output_log_events(
            events=all_events,
            format_type=format_type,
            output=output,
            highlight=highlight or pattern,
            mask_secrets=True,
            timestamps_only=False,
        )

        print(
            f"\n[green]Found {len(all_events)} matching events across {len(log_groups)} log groups[/green]"
        )

    def _fetch_logs_with_stream_filter(
        self,
        log_group_name: str,
        log_stream_prefix: Optional[str] = None,
        start_time: Optional[str] = None,
        end_time: Optional[str] = None,
        filter_pattern: Optional[str] = None,
        tail: bool = False,
        limit: int = 100,
        format_type: str = "text",
        output: Optional[str] = None,
        highlight: Optional[str] = None,
        mask_secrets: bool = True,
        timestamps_only: bool = False,
    ) -> None:
        """Fetch logs with optional stream filtering and tailing support."""
        if not self.logs_client:
            print("[red]Error: AWS logs client not initialized[/red]")
            return

        try:
            if tail:
                self._tail_logs(
                    log_group_name=log_group_name,
                    log_stream_prefix=log_stream_prefix,
                    filter_pattern=filter_pattern,
                    format_type=format_type,
                    highlight=highlight,
                    mask_secrets=mask_secrets,
                    timestamps_only=timestamps_only,
                )
            else:
                events = self._fetch_log_events(
                    log_group_name=log_group_name,
                    log_stream_prefix=log_stream_prefix,
                    start_time=start_time,
                    end_time=end_time,
                    filter_pattern=filter_pattern,
                    limit=limit,
                )

                self._output_log_events(
                    events=events,
                    format_type=format_type,
                    output=output,
                    highlight=highlight,
                    mask_secrets=mask_secrets,
                    timestamps_only=timestamps_only,
                )

                print(f"\n[green]Retrieved {len(events)} log events[/green]")

        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            if error_code == "ResourceNotFoundException":
                print(f"[red]Log group '{log_group_name}' not found[/red]")
            else:
                print(f"[red]AWS Error: {e.response['Error']['Message']}[/red]")
        except Exception as e:
            print(f"[red]Error fetching logs: {e}[/red]")

    def _fetch_log_events(
        self,
        log_group_name: str,
        log_stream_prefix: Optional[str] = None,
        start_time: Optional[str] = None,
        end_time: Optional[str] = None,
        filter_pattern: Optional[str] = None,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """Fetch log events from CloudWatch Logs."""
        # Parse time filters
        start_timestamp = self._get_timestamp(start_time)
        end_timestamp = self._get_timestamp(end_time)

        # Build filter_log_events parameters
        kwargs = self._build_filter_kwargs(
            log_group_name,
            log_stream_prefix,
            start_timestamp,
            end_timestamp,
            filter_pattern,
            limit,
        )

        events = []
        paginator = self.logs_client.get_paginator("filter_log_events")

        for page in paginator.paginate(**kwargs):
            events.extend(page.get("events", []))
            if len(events) >= limit:
                break

        return events[:limit]

    def _get_timestamp(self, time_str: Optional[str]) -> Optional[int]:
        """Convert time string to timestamp."""
        if not time_str:
            return None

        dt = self._parse_time_filter(time_str)
        return int(dt.timestamp() * 1000) if dt else None

    def _build_filter_kwargs(
        self,
        log_group_name: str,
        log_stream_prefix: Optional[str],
        start_timestamp: Optional[int],
        end_timestamp: Optional[int],
        filter_pattern: Optional[str],
        limit: int,
    ) -> Dict[str, Any]:
        """Build kwargs for filter_log_events."""
        kwargs = {
            "logGroupName": log_group_name,
            "limit": limit,
        }

        if log_stream_prefix:
            kwargs["logStreamNamePrefix"] = log_stream_prefix
        if start_timestamp:
            kwargs["startTime"] = start_timestamp
        if end_timestamp:
            kwargs["endTime"] = end_timestamp
        if filter_pattern:
            kwargs["filterPattern"] = filter_pattern

        return kwargs

    def _tail_logs(
        self,
        log_group_name: str,
        log_stream_prefix: Optional[str] = None,
        filter_pattern: Optional[str] = None,
        format_type: str = "text",
        highlight: Optional[str] = None,
        mask_secrets: bool = True,
        timestamps_only: bool = False,
        poll_interval: int = 2,
    ) -> None:
        """Tail logs in real-time."""
        print(
            f"[blue]Tailing logs from '{log_group_name}'... (Press Ctrl+C to stop)[/blue]"
        )

        last_timestamp = int(
            (datetime.utcnow() - timedelta(minutes=1)).timestamp() * 1000
        )

        try:
            while True:
                kwargs = {
                    "logGroupName": log_group_name,
                    "startTime": last_timestamp,
                    "limit": 50,
                }

                if log_stream_prefix:
                    kwargs["logStreamNamePrefix"] = log_stream_prefix
                if filter_pattern:
                    kwargs["filterPattern"] = filter_pattern

                try:
                    response = self.logs_client.filter_log_events(**kwargs)
                    events = response.get("events", [])

                    for event in events:
                        formatted_event = self._format_log_event(
                            event, format_type, highlight, mask_secrets, timestamps_only
                        )
                        print(formatted_event)
                        last_timestamp = max(last_timestamp, event["timestamp"] + 1)

                except ClientError as e:
                    if e.response["Error"]["Code"] != "ResourceNotFoundException":
                        print(
                            f"[red]Error tailing logs: {e.response['Error']['Message']}[/red]"
                        )

                time.sleep(poll_interval)

        except KeyboardInterrupt:
            print("\n[yellow]Stopped tailing logs[/yellow]")

    def _output_log_events(
        self,
        events: List[Dict[str, Any]],
        format_type: str = "text",
        output: Optional[str] = None,
        highlight: Optional[str] = None,
        mask_secrets: bool = True,
        timestamps_only: bool = False,
    ) -> None:
        """Output log events in the specified format."""
        if not events:
            print("[yellow]No log events found[/yellow]")
            return

        formatted_output = []

        for event in events:
            formatted_event = self._format_log_event(
                event, format_type, highlight, mask_secrets, timestamps_only
            )
            formatted_output.append(formatted_event)

        # Join output
        if format_type in ["json", "yaml"]:
            output_content = "\n".join(formatted_output)
        else:
            output_content = "\n".join(formatted_output)

        # Write to file if requested
        if output:
            self._write_to_file(output_content, output)
        else:
            print(output_content)
