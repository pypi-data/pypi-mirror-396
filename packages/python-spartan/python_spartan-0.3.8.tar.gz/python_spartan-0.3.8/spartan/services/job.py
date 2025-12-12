"""Job service for AWS Glue job management.

This module provides comprehensive AWS Glue job management capabilities
including listing jobs, filtering, sorting, and detailed job information.
"""

import csv
import io
import json
from datetime import datetime
from typing import Any, Dict, List, Optional

import boto3
import yaml
from botocore.exceptions import ClientError, NoCredentialsError
from rich import box, print
from rich.console import Console
from rich.table import Table

from spartan.utils.filters import FilterUtility, SortUtility


class JobService:
    """Service for managing AWS Glue jobs."""

    def __init__(
        self,
        region: Optional[str] = None,
        profile: Optional[str] = None,
    ):
        """Initialize the JobService.

        Args:
            region: AWS region
            profile: AWS profile
        """
        # Store configuration
        self.region = region
        self.profile = profile

        # AWS client setup
        try:
            session = (
                boto3.Session(profile_name=profile) if profile else boto3.Session()
            )
            self.glue_client = session.client("glue", region_name=region)
            self.session = session
            self.console = Console()
        except NoCredentialsError:
            print(
                "[red]Error: AWS credentials not found. Please configure your AWS credentials.[/red]"
            )
            self.glue_client = None
            self.session = None
            self.console = Console()
        except Exception as e:
            print(f"[red]Error initializing Glue client: {e}[/red]")
            self.glue_client = None
            self.session = None
            self.console = Console()

    def create_job(  # noqa: C901
        self,
        job_name: str,
        script_location: str,
        role: str,
        job_type: str = "glueetl",
        description: Optional[str] = None,
        glue_version: str = "4.0",
        worker_type: str = "G.1X",
        number_of_workers: int = 2,
        max_retries: int = 1,
        timeout: int = 2880,
        default_arguments: Optional[Dict[str, str]] = None,
        connections: Optional[List[str]] = None,
        security_configuration: Optional[str] = None,
        tags: Optional[Dict[str, str]] = None,
        execution_class: str = "STANDARD",
        dry_run: bool = False,
    ) -> bool:
        """Create a new AWS Glue job.

        Args:
            job_name: Name of the job (required)
            script_location: S3 path to the job script (required)
            role: IAM role ARN for the job (required)
            job_type: Job type (glueetl, pythonshell, gluestreaming, glueray)
            description: Job description
            glue_version: AWS Glue version (e.g., 4.0, 3.0)
            worker_type: Worker type (G.1X, G.2X, G.4X, G.8X, G.025X, Z.2X)
            number_of_workers: Number of workers
            max_retries: Maximum retry attempts
            timeout: Job timeout in minutes (max 10080)
            default_arguments: Default job arguments
            connections: List of connection names
            security_configuration: Security configuration name
            tags: Job tags
            execution_class: STANDARD or FLEX
            dry_run: Show what would be created without actually creating

        Returns:
            bool: True if job creation successful, False otherwise
        """
        if not self.glue_client:
            print("[red]AWS Glue client not available[/red]")
            return False

        try:
            # Validate required parameters
            if not all([job_name, script_location, role]):
                print(
                    "[red]Missing required parameters: job_name, script_location, and role are required[/red]"
                )
                return False

            # Validate job name format
            if not job_name.replace("-", "").replace("_", "").isalnum():
                print(
                    "[red]Job name must contain only alphanumeric characters, hyphens, and underscores[/red]"
                )
                return False

            # Validate script location format
            if not script_location.startswith("s3://"):
                print(
                    "[red]Script location must be a valid S3 URI (e.g., s3://bucket/path/script.py)[/red]"
                )
                return False

            # Validate worker type
            valid_worker_types = [
                "Standard",
                "G.1X",
                "G.2X",
                "G.4X",
                "G.8X",
                "G.025X",
                "Z.2X",
            ]
            if worker_type not in valid_worker_types:
                print(
                    f"[red]Invalid worker type. Valid types: {', '.join(valid_worker_types)}[/red]"
                )
                return False

            # Validate job type
            valid_job_types = ["glueetl", "pythonshell", "gluestreaming", "glueray"]
            if job_type not in valid_job_types:
                print(
                    f"[red]Invalid job type. Valid types: {', '.join(valid_job_types)}[/red]"
                )
                return False

            # Validate execution class
            valid_execution_classes = ["STANDARD", "FLEX"]
            if execution_class not in valid_execution_classes:
                print(
                    f"[red]Invalid execution class. Valid classes: {', '.join(valid_execution_classes)}[/red]"
                )
                return False

            # Validate timeout
            if timeout > 10080:  # 7 days max
                print("[red]Timeout cannot exceed 10080 minutes (7 days)[/red]")
                return False

            print(f"[blue]Creating AWS Glue job: {job_name}[/blue]")

            # Prepare job parameters
            job_params = {
                "Name": job_name,
                "Role": role,
                "Command": {
                    "Name": job_type,
                    "ScriptLocation": script_location,
                },
                "GlueVersion": glue_version,
                "MaxRetries": max_retries,
                "Timeout": timeout,
                "ExecutionClass": execution_class,
            }

            # Add optional parameters
            if description:
                job_params["Description"] = description

            if (
                job_type != "pythonshell"
            ):  # Worker config not valid for Python shell jobs
                job_params["WorkerType"] = worker_type
                job_params["NumberOfWorkers"] = number_of_workers

            if default_arguments:
                job_params["DefaultArguments"] = default_arguments

            if connections:
                job_params["Connections"] = {"Connections": connections}

            if security_configuration:
                job_params["SecurityConfiguration"] = security_configuration

            if tags:
                job_params["Tags"] = tags

            # Display configuration
            print("\n[cyan]Job Configuration:[/cyan]")
            print(f"  Name: {job_name}")
            print(f"  Script Location: {script_location}")
            print(f"  Role: {role}")
            print(f"  Job Type: {job_type}")
            print(f"  Glue Version: {glue_version}")
            if job_type != "pythonshell":
                print(f"  Worker Type: {worker_type}")
                print(f"  Number of Workers: {number_of_workers}")
            print(f"  Max Retries: {max_retries}")
            print(f"  Timeout: {timeout} minutes")
            print(f"  Execution Class: {execution_class}")

            if description:
                print(f"  Description: {description}")

            if default_arguments:
                print("  Default Arguments:")
                for key, value in default_arguments.items():
                    print(f"    {key}: {value}")

            if connections:
                print(f"  Connections: {', '.join(connections)}")

            if security_configuration:
                print(f"  Security Configuration: {security_configuration}")

            if tags:
                print("  Tags:")
                for key, value in tags.items():
                    print(f"    {key}: {value}")

            if dry_run:
                print(
                    "\n[yellow]DRY RUN: Job would be created with the above configuration[/yellow]"
                )
                return True

            # Check if job already exists
            try:
                self.glue_client.get_job(JobName=job_name)
                print(f"\n[yellow]⚠️ Job '{job_name}' already exists[/yellow]")
                print(
                    "Use 'spartan job describe' to view the existing job configuration"
                )
                return False
            except ClientError as e:
                if e.response["Error"]["Code"] != "EntityNotFoundException":
                    raise

            # Create the job
            print("\n[blue]Creating job...[/blue]")
            response = self.glue_client.create_job(**job_params)

            print(f"[green]✅ Successfully created job: {response['Name']}[/green]")

            # Display next steps
            print("\n[cyan]Next Steps:[/cyan]")
            print(f"  • View job details: spartan job describe {job_name}")
            print(f"  • Start job run: aws glue start-job-run --job-name {job_name}")
            print("  • List all jobs: spartan job list")

            return True

        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            error_message = e.response["Error"]["Message"]

            if error_code == "InvalidInputException":
                print(f"[red]Invalid input: {error_message}[/red]")
            elif error_code == "AlreadyExistsException":
                print(f"[red]Job '{job_name}' already exists[/red]")
            elif error_code == "ResourceNumberLimitExceededException":
                print(
                    "[red]Resource limit exceeded. You have reached the maximum number of jobs[/red]"
                )
            elif error_code == "AccessDeniedException":
                print(
                    "[red]Access denied. Check your IAM permissions for AWS Glue[/red]"
                )
            else:
                print(f"[red]AWS Error ({error_code}): {error_message}[/red]")
            return False

        except Exception as e:
            print(f"[red]Error creating job: {e}[/red]")
            return False

    def clone_job(  # noqa: C901
        self,
        source_job_name: str,
        target_job_name: str,
        override_script: Optional[str] = None,
        add_tags: Optional[Dict[str, str]] = None,
        dry_run: bool = False,
    ) -> bool:
        """Clone an existing AWS Glue job with optional parameter overrides.

        Args:
            source_job_name: Name of the existing job to clone (required)
            target_job_name: Name for the new cloned job (required)
            override_script: Optional S3 path to replace the script location
            add_tags: Additional tags to attach to the cloned job
            dry_run: Show what would be cloned without actually creating

        Returns:
            bool: True if job cloning successful, False otherwise
        """
        if not self.glue_client:
            print("[red]AWS Glue client not available[/red]")
            return False

        try:
            # Validate required parameters
            if not all([source_job_name, target_job_name]):
                print(
                    "[red]Missing required parameters: source_job_name and target_job_name are required[/red]"
                )
                return False

            # Validate target job name format
            if not target_job_name.replace("-", "").replace("_", "").isalnum():
                print(
                    "[red]Target job name must contain only alphanumeric characters, hyphens, and underscores[/red]"
                )
                return False

            # Validate override script location format if provided
            if override_script and not override_script.startswith("s3://"):
                print(
                    "[red]Override script location must be a valid S3 URI (e.g., s3://bucket/path/script.py)[/red]"
                )
                return False

            print(
                f"[blue]Cloning AWS Glue job: {source_job_name} → {target_job_name}[/blue]"
            )

            # Get the source job configuration
            try:
                source_response = self.glue_client.get_job(JobName=source_job_name)
                source_job = source_response["Job"]
            except ClientError as e:
                if e.response["Error"]["Code"] == "EntityNotFoundException":
                    print(f"[red]Source job '{source_job_name}' not found[/red]")
                    return False
                else:
                    raise

            # Check if target job already exists
            try:
                self.glue_client.get_job(JobName=target_job_name)
                print(
                    f"\n[yellow]⚠️ Target job '{target_job_name}' already exists[/yellow]"
                )
                print(
                    "Use 'spartan job describe' to view the existing job configuration"
                )
                return False
            except ClientError as e:
                if e.response["Error"]["Code"] != "EntityNotFoundException":
                    raise

            # Prepare job parameters by cloning from source
            job_params = {
                "Name": target_job_name,
                "Role": source_job["Role"],
                "Command": source_job["Command"].copy(),
                "GlueVersion": source_job.get("GlueVersion", "4.0"),
                "MaxRetries": source_job.get("MaxRetries", 1),
                "Timeout": source_job.get("Timeout", 2880),
                "ExecutionClass": source_job.get("ExecutionClass", "STANDARD"),
            }

            # Override script location if provided
            if override_script:
                job_params["Command"]["ScriptLocation"] = override_script

            # Copy optional parameters from source job
            if "Description" in source_job:
                job_params["Description"] = source_job["Description"]

            if "WorkerType" in source_job:
                job_params["WorkerType"] = source_job["WorkerType"]

            if "NumberOfWorkers" in source_job:
                job_params["NumberOfWorkers"] = source_job["NumberOfWorkers"]

            if "DefaultArguments" in source_job:
                job_params["DefaultArguments"] = source_job["DefaultArguments"].copy()

            if "Connections" in source_job:
                job_params["Connections"] = source_job["Connections"].copy()

            if "SecurityConfiguration" in source_job:
                job_params["SecurityConfiguration"] = source_job[
                    "SecurityConfiguration"
                ]

            # Handle tags - merge source tags with additional tags
            merged_tags = {}
            if "Tags" in source_job:
                merged_tags.update(source_job["Tags"])

            if add_tags:
                merged_tags.update(add_tags)

            if merged_tags:
                job_params["Tags"] = merged_tags

            # Display cloning configuration
            print("\n[cyan]Cloning Configuration:[/cyan]")
            print(f"  Source Job: {source_job_name}")
            print(f"  Target Job: {target_job_name}")
            print(f"  Script Location: {job_params['Command']['ScriptLocation']}")
            print(f"  Role: {job_params['Role']}")
            print(f"  Job Type: {job_params['Command']['Name']}")
            print(f"  Glue Version: {job_params['GlueVersion']}")

            if "WorkerType" in job_params:
                print(f"  Worker Type: {job_params['WorkerType']}")
            if "NumberOfWorkers" in job_params:
                print(f"  Number of Workers: {job_params['NumberOfWorkers']}")

            print(f"  Max Retries: {job_params['MaxRetries']}")
            print(f"  Timeout: {job_params['Timeout']} minutes")
            print(f"  Execution Class: {job_params['ExecutionClass']}")

            if "Description" in job_params:
                print(f"  Description: {job_params['Description']}")

            if "DefaultArguments" in job_params:
                print("  Default Arguments:")
                for key, value in job_params["DefaultArguments"].items():
                    print(f"    {key}: {value}")

            if "Connections" in job_params and job_params["Connections"].get(
                "Connections"
            ):
                print(
                    f"  Connections: {', '.join(job_params['Connections']['Connections'])}"
                )

            if "SecurityConfiguration" in job_params:
                print(
                    f"  Security Configuration: {job_params['SecurityConfiguration']}"
                )

            if merged_tags:
                print("  Tags:")
                for key, value in merged_tags.items():
                    print(f"    {key}: {value}")

            # Show what was overridden
            if override_script:
                print(f"\n[yellow]📝 Script Override: {override_script}[/yellow]")

            if add_tags:
                print(f"\n[yellow]🏷️ Additional Tags: {add_tags}[/yellow]")

            if dry_run:
                print(
                    "\n[yellow]DRY RUN: Job would be cloned with the above configuration[/yellow]"
                )
                return True

            # Create the cloned job
            print("\n[blue]Creating cloned job...[/blue]")
            response = self.glue_client.create_job(**job_params)

            print(
                f"[green]✅ Successfully cloned job: {source_job_name} → {response['Name']}[/green]"
            )

            # Display next steps
            print("\n[cyan]Next Steps:[/cyan]")
            print(
                f"  • View cloned job details: spartan job describe {target_job_name}"
            )
            print(
                f"  • Start job run: aws glue start-job-run --job-name {target_job_name}"
            )
            print(f"  • Compare with source: spartan job describe {source_job_name}")

            return True

        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            error_message = e.response["Error"]["Message"]

            if error_code == "InvalidInputException":
                print(f"[red]Invalid input: {error_message}[/red]")
            elif error_code == "AlreadyExistsException":
                print(f"[red]Target job '{target_job_name}' already exists[/red]")
            elif error_code == "ResourceNumberLimitExceededException":
                print(
                    "[red]Resource limit exceeded. You have reached the maximum number of jobs[/red]"
                )
            elif error_code == "AccessDeniedException":
                print(
                    "[red]Access denied. Check your IAM permissions for AWS Glue[/red]"
                )
            else:
                print(f"[red]AWS Error ({error_code}): {error_message}[/red]")
            return False

        except Exception as e:
            print(f"[red]Error cloning job: {e}[/red]")
            return False

    def start_job(  # noqa: C901
        self,
        job_name: str,
        job_run_id: Optional[str] = None,
        arguments: Optional[Dict[str, str]] = None,
        allocated_capacity: Optional[int] = None,
        timeout: Optional[int] = None,
        max_retries: Optional[int] = None,
        security_configuration: Optional[str] = None,
        notification_property: Optional[Dict[str, int]] = None,
        worker_type: Optional[str] = None,
        number_of_workers: Optional[int] = None,
        execution_class: Optional[str] = None,
        wait: bool = False,
        poll_interval: int = 30,
        dry_run: bool = False,
    ) -> bool:
        """Start an AWS Glue job run with optional parameter overrides.

        Args:
            job_name: Name of the job to start (required)
            job_run_id: Optional job run ID (if not provided, auto-generated)
            arguments: Job arguments as key-value pairs
            allocated_capacity: Number of AWS Glue data processing units (DPUs)
            timeout: Job timeout in minutes
            max_retries: Maximum number of retries
            security_configuration: Security configuration name
            notification_property: Notification settings
            worker_type: Worker type (G.1X, G.2X, etc.)
            number_of_workers: Number of workers
            execution_class: STANDARD or FLEX
            wait: Wait for job to complete
            poll_interval: Time in seconds between status checks (default: 30)
            dry_run: Show what would be started without actually starting

        Returns:
            bool: True if job start successful, False otherwise
        """
        if not self.glue_client:
            print("[red]AWS Glue client not available[/red]")
            return False

        try:
            # Validate required parameters
            if not job_name:
                print("[red]Missing required parameter: job_name is required[/red]")
                return False

            # Validate job name format
            if not job_name.replace("-", "").replace("_", "").isalnum():
                print(
                    "[red]Job name must contain only alphanumeric characters, hyphens, and underscores[/red]"
                )
                return False

            print(f"[blue]Starting AWS Glue job: {job_name}[/blue]")

            # Check if job exists
            try:
                job_response = self.glue_client.get_job(JobName=job_name)
                job_info = job_response["Job"]
            except ClientError as e:
                if e.response["Error"]["Code"] == "EntityNotFoundException":
                    print(f"[red]Job '{job_name}' not found[/red]")
                    return False
                else:
                    raise

            # Prepare job run parameters
            job_run_params: Dict[str, Any] = {"JobName": job_name}

            # Add optional parameters
            if job_run_id:
                job_run_params["JobRunId"] = job_run_id

            if arguments:
                job_run_params["Arguments"] = arguments

            if allocated_capacity is not None:
                job_run_params["AllocatedCapacity"] = allocated_capacity

            if timeout is not None:
                job_run_params["Timeout"] = timeout

            if max_retries is not None:
                job_run_params["MaxRetries"] = max_retries

            if security_configuration:
                job_run_params["SecurityConfiguration"] = security_configuration

            if notification_property:
                job_run_params["NotificationProperty"] = notification_property

            if worker_type:
                job_run_params["WorkerType"] = worker_type

            if number_of_workers is not None:
                job_run_params["NumberOfWorkers"] = number_of_workers

            if execution_class:
                job_run_params["ExecutionClass"] = execution_class

            # Display job start configuration
            print("\n[cyan]Job Start Configuration:[/cyan]")
            print(f"  Job Name: {job_name}")
            print(f"  Job Type: {job_info.get('Command', {}).get('Name', 'N/A')}")
            print(
                f"  Script Location: {job_info.get('Command', {}).get('ScriptLocation', 'N/A')}"
            )
            print(f"  Role: {job_info.get('Role', 'N/A')}")

            if job_run_id:
                print(f"  Job Run ID: {job_run_id}")

            if arguments:
                print("  Arguments:")
                for key, value in arguments.items():
                    print(f"    {key}: {value}")

            if worker_type:
                print(f"  Worker Type: {worker_type}")
            else:
                print(f"  Worker Type: {job_info.get('WorkerType', 'N/A')}")

            if number_of_workers is not None:
                print(f"  Number of Workers: {number_of_workers}")
            else:
                print(f"  Number of Workers: {job_info.get('NumberOfWorkers', 'N/A')}")

            if timeout is not None:
                print(f"  Timeout: {timeout} minutes")
            else:
                print(f"  Timeout: {job_info.get('Timeout', 'N/A')} minutes")

            if max_retries is not None:
                print(f"  Max Retries: {max_retries}")
            else:
                print(f"  Max Retries: {job_info.get('MaxRetries', 'N/A')}")

            if execution_class:
                print(f"  Execution Class: {execution_class}")
            else:
                print(
                    f"  Execution Class: {job_info.get('ExecutionClass', 'STANDARD')}"
                )

            if security_configuration:
                print(f"  Security Configuration: {security_configuration}")

            if notification_property:
                print(f"  Notification Property: {notification_property}")

            if dry_run:
                print(
                    "\n[yellow]DRY RUN: Job would be started with the above configuration[/yellow]"
                )
                return True

            # Start the job run
            print("\n[blue]Starting job run...[/blue]")
            response = self.glue_client.start_job_run(**job_run_params)

            job_run_id_result = response["JobRunId"]
            print(
                f"[green]✅ Successfully started job run: {job_run_id_result}[/green]"
            )

            # Wait for job completion if requested
            if wait and not dry_run:
                print(
                    f"\n[cyan]Waiting for job to complete (polling every {poll_interval} seconds)...[/cyan]"
                )
                final_state = self._wait_for_job_completion(
                    job_name, job_run_id_result, poll_interval
                )

                if final_state == "SUCCEEDED":
                    print("[green]🎉 Job completed successfully![/green]")
                    return True
                elif final_state in ["FAILED", "TIMEOUT", "STOPPED"]:
                    print(f"[red]❌ Job finished with status: {final_state}[/red]")
                    print(
                        f"[yellow]💡 View logs: spartan job logs --name {job_name} --run-id {job_run_id_result}[/yellow]"
                    )
                    return False
                else:
                    print(
                        f"[yellow]⚠️ Job finished with unexpected status: {final_state}[/yellow]"
                    )
                    return False

            # Display next steps
            print("\n[cyan]Next Steps:[/cyan]")
            print(
                f"  • Check job run status: aws glue get-job-run --job-name {job_name} --run-id {job_run_id_result}"
            )
            print(f"  • View job runs: aws glue get-job-runs --job-name {job_name}")
            print(f"  • View job details: spartan job describe {job_name}")
            print(
                "  • Monitor in AWS Console: https://console.aws.amazon.com/glue/home#etl:tab=jobs"
            )

            return True

        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            error_message = e.response["Error"]["Message"]

            if error_code == "InvalidInputException":
                print(f"[red]Invalid input: {error_message}[/red]")
            elif error_code == "ResourceNumberLimitExceededException":
                print(
                    "[red]Resource limit exceeded. You have reached the maximum number of concurrent job runs[/red]"
                )
            elif error_code == "AccessDeniedException":
                print(
                    "[red]Access denied. Check your IAM permissions for AWS Glue[/red]"
                )
            elif error_code == "InternalServiceException":
                print("[red]Internal service error. Please try again later[/red]")
            elif error_code == "OperationTimeoutException":
                print("[red]Operation timed out. Please try again[/red]")
            else:
                print(f"[red]AWS Error ({error_code}): {error_message}[/red]")
            return False

        except Exception as e:
            print(f"[red]Error starting job: {e}[/red]")
            return False

    def _wait_for_job_completion(
        self, job_name: str, job_run_id: str, poll_interval: int
    ) -> str:
        """Wait for AWS Glue job to complete and return final status.

        Args:
            job_name: Name of the AWS Glue job
            job_run_id: Job run ID to monitor
            poll_interval: Time in seconds between status checks

        Returns:
            str: Final job run state
        """
        import time

        terminal_states = {"SUCCEEDED", "FAILED", "STOPPED", "TIMEOUT"}
        start_time = time.time()
        last_state = None

        try:
            while True:
                # Get current job run status
                response = self.glue_client.get_job_run(
                    JobName=job_name, RunId=job_run_id
                )
                job_run = response["JobRun"]
                current_state = job_run.get("JobRunState", "UNKNOWN")

                # Display status change
                if current_state != last_state:
                    elapsed_time = int(time.time() - start_time)
                    self._display_job_status(current_state, elapsed_time, job_run)
                    last_state = current_state

                # Check if job has reached terminal state
                if current_state in terminal_states:
                    return current_state

                # Wait before next poll
                time.sleep(poll_interval)

        except KeyboardInterrupt:
            print(
                "\n[yellow]⚠️ Monitoring interrupted by user. Job may still be running.[/yellow]"
            )
            print(
                f"[cyan]💡 Check status: spartan job logs --name {job_name} --run-id {job_run_id}[/cyan]"
            )
            return "INTERRUPTED"
        except Exception as e:
            print(f"\n[red]Error monitoring job: {e}[/red]")
            return "ERROR"

    def _display_job_status(self, state: str, elapsed_time: int, job_run: dict) -> None:
        """Display job status with color coding and elapsed time.

        Args:
            state: Current job state
            elapsed_time: Elapsed time in seconds
            job_run: Job run details from AWS
        """
        elapsed_str = f"{elapsed_time // 60:02d}:{elapsed_time % 60:02d}"

        status_messages = {
            "STARTING": f"[blue]⏳ [{elapsed_str}] Job is starting...[/blue]",
            "RUNNING": f"[yellow]🏃 [{elapsed_str}] Job is running...[/yellow]",
            "STOPPING": f"[yellow]🛑 [{elapsed_str}] Job is stopping...[/yellow]",
            "SUCCEEDED": f"[green]✅ [{elapsed_str}] Job completed successfully![/green]",
            "TIMEOUT": f"[red]⏱️ [{elapsed_str}] Job timed out![/red]",
            "STOPPED": f"[yellow]🛑 [{elapsed_str}] Job was stopped![/yellow]",
        }

        if state in status_messages:
            print(status_messages[state])
        elif state == "FAILED":
            print(f"[red]❌ [{elapsed_str}] Job failed![/red]")
            # Show error details if available
            error_details = job_run.get("ErrorDetails", {})
            if error_details:
                error_message = error_details.get("ErrorMessage", "Unknown error")
                print(f"[red]Error: {error_message}[/red]")
        else:
            print(f"[dim]📊 [{elapsed_str}] Job state: {state}[/dim]")

    def stop_job(  # noqa: C901
        self,
        job_name: str,
        run_id: str,
        dry_run: bool = False,
    ) -> bool:
        """Stop a running AWS Glue job run.

        Args:
            job_name: Name of the AWS Glue job
            run_id: Job run ID to stop
            dry_run: Show what would be stopped without actually stopping

        Returns:
            bool: True if job stop successful, False otherwise
        """
        if not self.glue_client:
            print("[red]AWS Glue client not available[/red]")
            return False

        try:
            # Validate required parameters
            if not job_name or not run_id:
                print("[red]Both job name and run ID are required[/red]")
                return False

            # Validate job name format
            if not job_name.replace("-", "").replace("_", "").isalnum():
                print(
                    "[red]Job name must contain only alphanumeric characters, hyphens, and underscores[/red]"
                )
                return False

            print(
                f"[blue]Stopping AWS Glue job run: {job_name} (Run ID: {run_id})[/blue]"
            )

            # Check if job run exists and get current status
            try:
                job_run_response = self.glue_client.get_job_run(
                    JobName=job_name, RunId=run_id
                )
                job_run = job_run_response["JobRun"]
                current_state = job_run.get("JobRunState", "UNKNOWN")

                print(f"[cyan]Current Job Run Status: {current_state}[/cyan]")

                # Check if job run can be stopped
                if current_state in ["SUCCEEDED", "FAILED", "STOPPED", "TIMEOUT"]:
                    print(
                        f"[yellow]Job run is already in terminal state: {current_state}[/yellow]"
                    )
                    print(
                        "[yellow]Cannot stop a job run that has already completed[/yellow]"
                    )
                    return True  # Not an error, just already completed

                if current_state not in ["STARTING", "RUNNING", "STOPPING"]:
                    print(
                        f"[yellow]Job run is in state '{current_state}' and may not be stoppable[/yellow]"
                    )

            except ClientError as e:
                if e.response["Error"]["Code"] == "EntityNotFoundException":
                    print(
                        f"[red]Job run '{run_id}' not found for job '{job_name}'[/red]"
                    )
                    return False
                else:
                    raise

            # Display job stop configuration
            print("\n[cyan]Job Stop Configuration:[/cyan]")
            print(f"  Job Name: {job_name}")
            print(f"  Job Run ID: {run_id}")
            print(f"  Current State: {current_state}")

            if job_run.get("StartedOn"):
                started_time = job_run["StartedOn"].strftime("%Y-%m-%d %H:%M:%S UTC")
                print(f"  Started On: {started_time}")

            if job_run.get("LastModifiedOn"):
                modified_time = job_run["LastModifiedOn"].strftime(
                    "%Y-%m-%d %H:%M:%S UTC"
                )
                print(f"  Last Modified: {modified_time}")

            if dry_run:
                print(
                    "\n[yellow]DRY RUN: Job run would be stopped with the above configuration[/yellow]"
                )
                return True

            # Stop the job run
            print("\n[blue]Stopping job run...[/blue]")
            response = self.glue_client.batch_stop_job_run(
                JobName=job_name, JobRunIds=[run_id]
            )

            # Check the response for success/failure
            successful_submissions = response.get("SuccessfulSubmissions", [])
            errors = response.get("Errors", [])

            if successful_submissions:
                print(
                    f"[green]✅ Successfully submitted stop request for job run: {run_id}[/green]"
                )
                print(
                    "[cyan]Note: The job run may take a few moments to actually stop[/cyan]"
                )

            if errors:
                for error in errors:
                    error_job_run_id = error.get("JobRunId", "unknown")
                    error_code = error.get("ErrorDetail", {}).get(
                        "ErrorCode", "Unknown"
                    )
                    error_message = error.get("ErrorDetail", {}).get(
                        "ErrorMessage", "Unknown error"
                    )
                    print(
                        f"[red]Error stopping job run {error_job_run_id}: ({error_code}) {error_message}[/red]"
                    )
                return False

            # Display next steps
            print("\n[cyan]Next Steps:[/cyan]")
            print(
                f"  • Check job run status: aws glue get-job-run --job-name {job_name} --run-id {run_id}"
            )
            print(f"  • View job runs: aws glue get-job-runs --job-name {job_name}")
            print(f"  • View job details: spartan job describe {job_name}")
            print(
                "  • Monitor in AWS Console: https://console.aws.amazon.com/glue/home#etl:tab=jobs"
            )

            return True

        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            error_message = e.response["Error"]["Message"]

            if error_code == "InvalidInputException":
                print(f"[red]Invalid input: {error_message}[/red]")
            elif error_code == "AccessDeniedException":
                print(
                    "[red]Access denied. Check your IAM permissions for AWS Glue[/red]"
                )
            elif error_code == "InternalServiceException":
                print("[red]Internal service error. Please try again later[/red]")
            elif error_code == "OperationTimeoutException":
                print("[red]Operation timed out. Please try again[/red]")
            elif error_code == "ConcurrentRunsExceededException":
                print("[red]Cannot stop job run due to concurrent operations[/red]")
            else:
                print(f"[red]AWS Error ({error_code}): {error_message}[/red]")
            return False

        except Exception as e:
            print(f"[red]Error stopping job: {e}[/red]")
            return False

    def get_job_logs(  # noqa: C901
        self,
        job_name: str,
        run_id: str,
        log_group: Optional[str] = None,
        start_time: Optional[str] = None,
        end_time: Optional[str] = None,
        follow: bool = False,
        max_lines: int = 100,
    ) -> bool:
        """Retrieve AWS Glue job run logs from CloudWatch.

        Args:
            job_name: Name of the AWS Glue job
            run_id: Job run ID
            log_group: Optional CloudWatch log group (auto-detected if not provided)
            start_time: Start time for log retrieval (ISO format or relative like '1h', '30m')
            end_time: End time for log retrieval (ISO format)
            follow: Follow logs in real-time (for running jobs)
            max_lines: Maximum number of log lines to retrieve

        Returns:
            bool: True if logs retrieved successfully, False otherwise
        """
        if not self.glue_client:
            print("[red]AWS Glue client not available[/red]")
            return False

        try:
            # Validate required parameters
            if not job_name or not run_id:
                print("[red]Both job name and run ID are required[/red]")
                return False

            print(
                f"[blue]Retrieving logs for AWS Glue job: {job_name} (Run ID: {run_id})[/blue]"
            )

            # Get job run details to verify it exists and get status
            try:
                job_run_response = self.glue_client.get_job_run(
                    JobName=job_name, RunId=run_id
                )
                job_run = job_run_response["JobRun"]
                job_state = job_run.get("JobRunState", "UNKNOWN")

                print(f"[cyan]Job Run Status: {job_state}[/cyan]")

                if job_state in ["STARTING", "RUNNING"]:
                    print(
                        "[yellow]Note: Job is still running. Logs may be incomplete.[/yellow]"
                    )
                elif job_state == "FAILED":
                    error_details = job_run.get("ErrorDetails", {})
                    if error_details:
                        print(
                            f"[red]Job failed with error: {error_details.get('ErrorMessage', 'Unknown error')}[/red]"
                        )

            except ClientError as e:
                if e.response["Error"]["Code"] == "EntityNotFoundException":
                    print(
                        f"[red]Job run '{run_id}' not found for job '{job_name}'[/red]"
                    )
                    return False
                else:
                    raise

            # Create CloudWatch logs client
            try:
                if self.session:
                    logs_client = self.session.client("logs")
                else:
                    logs_client = boto3.client("logs", region_name=self.region)
            except Exception as e:
                print(f"[red]Error creating CloudWatch logs client: {e}[/red]")
                return False

            # Determine log group if not provided
            if not log_group:
                # AWS Glue job logs are typically in /aws-glue/jobs/logs-v2/
                log_group = "/aws-glue/jobs/logs-v2/"
                print(f"[cyan]Using default log group: {log_group}[/cyan]")

            # List log streams for this job run
            try:
                log_streams = []

                # Try common log stream patterns for AWS Glue
                possible_streams = [
                    f"{job_name}-{run_id}",
                    f"glue-{job_name}-{run_id}",
                    f"{run_id}",
                ]

                # Get all log streams and filter for our job run
                paginator = logs_client.get_paginator("describe_log_streams")

                for page in paginator.paginate(logGroupName=log_group):
                    for stream in page["logStreams"]:
                        stream_name = stream["logStreamName"]
                        # Check if stream name contains our run ID or job name
                        if run_id in stream_name or any(
                            pattern in stream_name for pattern in possible_streams
                        ):
                            log_streams.append(stream)

                if not log_streams:
                    print(
                        f"[yellow]No log streams found for job run {run_id} in log group {log_group}[/yellow]"
                    )
                    print("[cyan]Available log streams:[/cyan]")

                    # Show available streams for debugging
                    paginator = logs_client.get_paginator("describe_log_streams")
                    stream_count = 0
                    for page in paginator.paginate(logGroupName=log_group):
                        for stream in page["logStreams"]:
                            if stream_count < 10:  # Limit output
                                print(f"  - {stream['logStreamName']}")
                                stream_count += 1
                            else:
                                print(
                                    f"  ... and {len(page['logStreams']) - 10} more streams"
                                )
                                break
                        if stream_count >= 10:
                            break
                    return False

                print(f"[green]Found {len(log_streams)} log stream(s)[/green]")

            except ClientError as e:
                if e.response["Error"]["Code"] == "ResourceNotFoundException":
                    print(f"[red]Log group '{log_group}' not found[/red]")
                    print("[cyan]Common AWS Glue log groups:[/cyan]")
                    print("  - /aws-glue/jobs/logs-v2/")
                    print("  - /aws-glue/jobs/error/")
                    print("  - /aws-glue/jobs/output/")
                    return False
                else:
                    raise

            # Parse time filters if provided
            start_time_ms = None
            end_time_ms = None

            if start_time:
                start_time_ms = self._parse_time_filter(start_time)

            if end_time:
                end_time_ms = self._parse_time_filter(end_time)

            # Retrieve logs from all relevant streams
            all_events = []

            for stream in log_streams:
                stream_name = stream["logStreamName"]
                print(f"[cyan]Retrieving logs from stream: {stream_name}[/cyan]")

                try:
                    kwargs = {
                        "logGroupName": log_group,
                        "logStreamName": stream_name,
                        "limit": max_lines,
                    }

                    if start_time_ms:
                        kwargs["startTime"] = start_time_ms

                    if end_time_ms:
                        kwargs["endTime"] = end_time_ms

                    response = logs_client.get_log_events(**kwargs)
                    events = response.get("events", [])

                    for event in events:
                        event["logStreamName"] = stream_name
                        all_events.append(event)

                except ClientError as e:
                    print(
                        f"[yellow]Warning: Could not retrieve logs from stream {stream_name}: {e}[/yellow]"
                    )
                    continue

            if not all_events:
                print("[yellow]No log events found for the specified criteria[/yellow]")
                return True

            # Sort events by timestamp
            all_events.sort(key=lambda x: x["timestamp"])

            # Display logs
            print(f"\n[cyan]📋 Job Logs ({len(all_events)} events):[/cyan]")
            print("=" * 80)

            for event in all_events[:max_lines]:
                timestamp = datetime.fromtimestamp(event["timestamp"] / 1000).strftime(
                    "%Y-%m-%d %H:%M:%S"
                )
                stream_name = event.get("logStreamName", "unknown")
                message = event["message"].rstrip("\n")

                # Color code log levels
                if any(level in message.upper() for level in ["ERROR", "FATAL"]):
                    print(f"[red]{timestamp} [{stream_name}] {message}[/red]")
                elif any(level in message.upper() for level in ["WARN", "WARNING"]):
                    print(f"[yellow]{timestamp} [{stream_name}] {message}[/yellow]")
                elif any(level in message.upper() for level in ["INFO"]):
                    print(f"[blue]{timestamp} [{stream_name}] {message}[/blue]")
                elif any(level in message.upper() for level in ["DEBUG"]):
                    print(f"[dim]{timestamp} [{stream_name}] {message}[/dim]")
                else:
                    print(f"{timestamp} [{stream_name}] {message}")

            if len(all_events) > max_lines:
                print(
                    f"\n[yellow]Note: Showing first {max_lines} of {len(all_events)} log events. Use --max-lines to see more.[/yellow]"
                )

            # Show follow option for running jobs
            if follow and job_run.get("JobRunState") in ["STARTING", "RUNNING"]:
                print("\n[cyan]To follow logs in real-time, use:[/cyan]")
                print(
                    f"aws logs tail {log_group} --follow --log-stream-names {','.join([s['logStreamName'] for s in log_streams])}"
                )

            return True

        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            error_message = e.response["Error"]["Message"]

            if error_code == "AccessDeniedException":
                print(
                    "[red]Access denied. Check your IAM permissions for CloudWatch Logs[/red]"
                )
            elif error_code == "InvalidParameterException":
                print(f"[red]Invalid parameter: {error_message}[/red]")
            elif error_code == "ResourceNotFoundException":
                print(f"[red]Resource not found: {error_message}[/red]")
            else:
                print(f"[red]AWS Error ({error_code}): {error_message}[/red]")
            return False

        except Exception as e:
            print(f"[red]Error retrieving logs: {e}[/red]")
            return False

    def _parse_time_filter(self, time_str: str) -> int:
        """Parse time filter string to milliseconds timestamp.

        Supports:
        - Relative times: '1h', '30m', '2d'
        - ISO format: '2024-01-15T10:30:00'
        - Unix timestamp: '1642244400'
        """
        # Try relative time first
        relative_ms = self._parse_relative_time(time_str)
        if relative_ms:
            return relative_ms

        # Try ISO format
        iso_ms = self._parse_iso_time(time_str)
        if iso_ms:
            return iso_ms

        # Try unix timestamp
        unix_ms = self._parse_unix_time(time_str)
        if unix_ms:
            return unix_ms

        raise ValueError(f"Unable to parse time filter: {time_str}")

    def _parse_relative_time(self, time_str: str) -> Optional[int]:
        """Parse relative time like '1h', '30m', '2d'."""
        import re
        from datetime import timedelta

        relative_match = re.match(r"^(\d+)([hmd])$", time_str.lower())
        if not relative_match:
            return None

        amount = int(relative_match.group(1))
        unit = relative_match.group(2)

        now = datetime.now()
        if unit == "h":
            target_time = now - timedelta(hours=amount)
        elif unit == "m":
            target_time = now - timedelta(minutes=amount)
        elif unit == "d":
            target_time = now - timedelta(days=amount)
        else:
            return None

        return int(target_time.timestamp() * 1000)

    def _parse_iso_time(self, time_str: str) -> Optional[int]:
        """Parse ISO format time."""
        try:
            try:
                from dateutil import parser  # type: ignore

                dt = parser.parse(time_str)
                return int(dt.timestamp() * 1000)
            except ImportError:
                # Fallback without dateutil
                dt = datetime.fromisoformat(time_str.replace("Z", "+00:00"))
                return int(dt.timestamp() * 1000)
        except (ValueError, ImportError):
            return None

    def _parse_unix_time(self, time_str: str) -> Optional[int]:
        """Parse unix timestamp."""
        try:
            return int(float(time_str) * 1000)
        except ValueError:
            return None

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

    def list_jobs(  # noqa: C901
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
        """List all AWS Glue jobs with filtering options.

        Args:
            output_format: Output format (table, json, yaml, markdown, csv)
            prefix_filter: Filter jobs by name prefix
            regex_match: Filter jobs by regex pattern
            contains_filter: Filter jobs by substring
            sort_by: Sort by field (name, created_date, modified_date, glue_version)
            sort_order: Sort order (asc, desc)
            limit: Limit the number of results shown
            show_filters: Show which filters were applied in the output
            save_to: Save the results to a file (.json, .yaml, .csv, etc.)
        """
        if not self.glue_client:
            print(
                "[red]Error: Glue client not initialized. Please check your AWS credentials.[/red]"
            )
            return

        try:
            # Validate inputs
            if not self._validate_inputs(output_format, sort_by, sort_order, limit):
                return

            if output_format == "table":
                print("[blue]Fetching AWS Glue jobs...[/blue]")

            # Get and process job data
            job_data = self._get_job_data()
            if not job_data:
                self._handle_no_jobs_found(output_format)
                return

            # Apply filters and sorting
            filtered_data, applied_filters = self._process_job_data(
                job_data,
                prefix_filter,
                regex_match,
                contains_filter,
                sort_by,
                sort_order,
                limit,
            )

            if not filtered_data and applied_filters:
                self._handle_no_jobs_found(output_format, filtered=True)
                return

            # Output results
            self._output_results(
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
            print(f"[red]Error listing jobs: {e}[/red]")

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
            "created_date",
            "modified_date",
            "glue_version",
            "worker_type",
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

    def _get_job_data(self) -> List[Dict]:
        """Get and process raw job data from AWS Glue."""
        all_jobs = []
        next_token = None

        while True:
            try:
                if next_token:
                    response = self.glue_client.get_jobs(NextToken=next_token)
                else:
                    response = self.glue_client.get_jobs()

                jobs = response.get("Jobs", [])
                for job in jobs:
                    job_info = {
                        "name": job.get("Name", "N/A"),
                        "role": job.get("Role", "N/A"),
                        "glue_version": job.get("GlueVersion", "N/A"),
                        "worker_type": job.get("WorkerType", "N/A"),
                        "number_of_workers": job.get("NumberOfWorkers", 0),
                        "max_retries": job.get("MaxRetries", 0),
                        "timeout": job.get("Timeout", 0),
                        "description": job.get("Description", ""),
                        "created_date": self._format_date(job.get("CreatedOn")),
                        "modified_date": self._format_date(job.get("LastModifiedOn")),
                        "CreatedOn": job.get("CreatedOn"),  # Keep original for sorting
                        "LastModifiedOn": job.get(
                            "LastModifiedOn"
                        ),  # Keep original for sorting
                    }
                    all_jobs.append(job_info)

                next_token = response.get("NextToken")
                if not next_token:
                    break

            except Exception as e:
                print(f"[red]Error fetching jobs: {e}[/red]")
                break

        return all_jobs

    def _process_job_data(
        self,
        job_data: List[Dict],
        prefix_filter: Optional[str],
        regex_match: Optional[str],
        contains_filter: Optional[str],
        sort_by: str,
        sort_order: str,
        limit: Optional[int],
    ) -> tuple[List[Dict], Dict]:
        """Apply filters, sorting, and limiting to job data."""
        original_count = len(job_data)

        # Apply filters
        if prefix_filter:
            job_data = FilterUtility.apply_prefix_filter(
                job_data, "name", prefix_filter
            )
        if regex_match:
            job_data = FilterUtility.apply_regex_filter(job_data, "name", regex_match)
        if contains_filter:
            job_data = FilterUtility.apply_contains_filter(
                job_data, "name", contains_filter, case_sensitive=False
            )

        # Apply sorting
        reverse = sort_order.lower() == "desc"
        if sort_by == "created_date":
            job_data = SortUtility.sort_by_date(job_data, "CreatedOn", reverse=reverse)
        elif sort_by == "modified_date":
            job_data = SortUtility.sort_by_date(
                job_data, "LastModifiedOn", reverse=reverse
            )
        elif sort_by == "name":
            job_data = SortUtility.sort_items(
                job_data, "name", reverse=reverse, case_sensitive=False
            )
        elif sort_by in ["glue_version", "worker_type"]:
            job_data = SortUtility.sort_items(
                job_data, sort_by, reverse=reverse, case_sensitive=False
            )

        # Apply limit
        if limit:
            job_data = job_data[:limit]

        # Prepare filter info
        applied_filters = self._build_applied_filters(
            prefix_filter, regex_match, contains_filter, limit, original_count
        )

        return job_data, applied_filters

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

    def _output_results(
        self,
        job_data: List[Dict],
        output_format: str,
        show_filters: bool,
        applied_filters: Dict,
        sort_by: str,
        sort_order: str,
        save_to: Optional[str],
    ) -> None:
        """Output results in the requested format."""
        if output_format == "csv":
            self._print_jobs_csv(job_data, show_filters, applied_filters, save_to)
        elif output_format == "table":
            self._print_jobs_table(
                job_data, show_filters, applied_filters, sort_by, sort_order
            )
        elif output_format == "json":
            self._output_json(
                job_data, show_filters, applied_filters, sort_by, sort_order, save_to
            )
        elif output_format == "yaml":
            self._output_yaml(
                job_data, show_filters, applied_filters, sort_by, sort_order, save_to
            )
        elif output_format == "markdown":
            self._print_jobs_markdown(
                job_data, show_filters, applied_filters, sort_by, sort_order, save_to
            )

    def _print_jobs_table(
        self,
        job_data: List[Dict],
        show_filters: bool = False,
        applied_filters: Dict = None,
        sort_by: str = "name",
        sort_order: str = "asc",
    ) -> None:
        """Print jobs in a formatted table."""
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
        table.add_column("Job Name", style="bright_blue", no_wrap=False)
        table.add_column("Glue Version", style="yellow")
        table.add_column("Worker Type", style="green")
        table.add_column("Workers", justify="right", style="magenta")
        table.add_column("Created", style="dim")

        for job in job_data:
            table.add_row(
                job["name"],
                job["glue_version"],
                job["worker_type"],
                str(job["number_of_workers"]),
                job["created_date"],
            )

        self.console.print(
            f"🔧 [bold]AWS Glue Jobs[/bold] ([bright_yellow]{len(job_data)}[/bright_yellow] found)"
        )
        if sort_by:
            self.console.print(f"[dim]Sorted by: {sort_by} ({sort_order})[/dim]")
        self.console.print()
        self.console.print(table)

    def _handle_no_jobs_found(self, output_format: str, filtered: bool = False) -> None:
        """Handle the case when no jobs are found."""
        if filtered:
            message = "No AWS Glue jobs match the specified filters."
            json_message = {
                "jobs": [],
                "count": 0,
                "message": "No jobs match the filters",
            }
            yaml_message = {
                "jobs": [],
                "count": 0,
                "message": "No jobs match the filters",
            }
            markdown_message = "# AWS Glue Jobs\n\nNo jobs match the specified filters."
        else:
            message = "No AWS Glue jobs found in the current account."
            json_message = {"jobs": [], "count": 0, "message": "No jobs found"}
            yaml_message = {"jobs": [], "count": 0, "message": "No jobs found"}
            markdown_message = (
                "# AWS Glue Jobs\n\nNo jobs found in the current account."
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
                "job_name,glue_version,worker_type,number_of_workers,created_date,modified_date"
            )

    def _print_jobs_csv(
        self,
        job_data: List[Dict],
        show_filters: bool = False,
        applied_filters: Dict = None,
        save_to: Optional[str] = None,
    ) -> None:
        """Print jobs in CSV format."""
        output = io.StringIO()
        writer = csv.writer(output)

        # Write header
        writer.writerow(
            [
                "job_name",
                "glue_version",
                "worker_type",
                "number_of_workers",
                "created_date",
                "modified_date",
                "description",
            ]
        )

        # Write data
        for job in job_data:
            writer.writerow(
                [
                    job["name"],
                    job["glue_version"],
                    job["worker_type"],
                    job["number_of_workers"],
                    job["created_date"],
                    job["modified_date"],
                    job["description"],
                ]
            )

        csv_content = output.getvalue()

        if save_to:
            self._save_to_file(csv_content, save_to)
        else:
            if show_filters and applied_filters:
                print(f"# Applied filters: {applied_filters}")
            print(csv_content.strip())

    def _output_json(
        self,
        job_data: List[Dict],
        show_filters: bool,
        applied_filters: Dict,
        sort_by: str,
        sort_order: str,
        save_to: Optional[str],
    ) -> None:
        """Output results in JSON format."""
        output_data = {
            "jobs": job_data,
            "count": len(job_data),
            "sort": {"by": sort_by, "order": sort_order},
        }
        if show_filters and applied_filters:
            output_data["applied_filters"] = applied_filters

        output_str = json.dumps(output_data, indent=2, default=str)
        if save_to:
            self._save_to_file(output_str, save_to)
        else:
            print(output_str)

    def _output_yaml(
        self,
        job_data: List[Dict],
        show_filters: bool,
        applied_filters: Dict,
        sort_by: str,
        sort_order: str,
        save_to: Optional[str],
    ) -> None:
        """Output results in YAML format."""
        output_data = {
            "jobs": job_data,
            "count": len(job_data),
            "sort": {"by": sort_by, "order": sort_order},
        }
        if show_filters and applied_filters:
            output_data["applied_filters"] = applied_filters

        output_str = yaml.dump(output_data, default_flow_style=False)
        if save_to:
            self._save_to_file(output_str, save_to)
        else:
            print(output_str)

    def _print_jobs_markdown(
        self,
        job_data: List[Dict],
        show_filters: bool = False,
        applied_filters: Dict = None,
        sort_by: str = "name",
        sort_order: str = "asc",
        save_to: Optional[str] = None,
    ) -> None:
        """Print jobs in markdown format."""
        output_lines = ["# AWS Glue Jobs\n"]

        # Print filter information if any
        if show_filters and applied_filters:
            output_lines.append("## Applied Filters\n")
            for key, value in applied_filters.items():
                output_lines.append(f"- **{key.title()}:** `{value}`")
            output_lines.append("")

        output_lines.append("## Jobs\n")
        output_lines.append(
            "| Job Name | Glue Version | Worker Type | Workers | Created | Description |"
        )
        output_lines.append(
            "|----------|--------------|-------------|---------|---------|-------------|"
        )

        for job in job_data:
            desc = (
                job["description"][:50] + "..."
                if len(job["description"]) > 50
                else job["description"]
            )
            output_lines.append(
                f"| {job['name']} | {job['glue_version']} | {job['worker_type']} | "
                f"{job['number_of_workers']} | {job['created_date']} | {desc} |"
            )

        output_lines.append(f"\n**Total:** {len(job_data)} job(s)")
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

    def diff_jobs(  # noqa: C901
        self,
        source_job: str,
        target_job: str,
        fields: Optional[List[str]] = None,
        output_format: str = "table",
        show_equal: bool = False,
        ignore_fields: Optional[List[str]] = None,
        save_to: Optional[str] = None,
        dry_run: bool = False,
    ) -> bool:
        """Compare two AWS Glue job definitions to identify configuration differences.

        Args:
            source_job: Name of the first job to compare (required)
            target_job: Name of the second job to compare (required)
            fields: Specific fields to include in comparison
            output_format: Output format (table, json, yaml, markdown)
            show_equal: Display matching fields in addition to differences
            ignore_fields: Fields to exclude from comparison
            save_to: Save results to a file
            dry_run: Show what would be compared without actually comparing

        Returns:
            bool: True if comparison successful, False otherwise
        """
        if not self.glue_client:
            print("[red]AWS Glue client not available[/red]")
            return False

        try:
            # Validate required parameters
            if not source_job or not target_job:
                print("[red]Both source and target job names are required[/red]")
                return False

            # Validate job name formats
            for job_name in [source_job, target_job]:
                if not job_name.replace("-", "").replace("_", "").isalnum():
                    print(
                        f"[red]Job name '{job_name}' must contain only alphanumeric characters, hyphens, and underscores[/red]"
                    )
                    return False

            # Validate output format
            valid_formats = ["table", "json", "yaml", "markdown"]
            if output_format not in valid_formats:
                print(
                    f"[red]Invalid output format. Valid formats: {', '.join(valid_formats)}[/red]"
                )
                return False

            print(f"[blue]Comparing AWS Glue jobs: {source_job} ⟷ {target_job}[/blue]")

            if dry_run:
                print("\n[cyan]Diff Configuration:[/cyan]")
                print(f"  Source Job: {source_job}")
                print(f"  Target Job: {target_job}")
                print(f"  Output Format: {output_format}")
                print(f"  Show Equal Fields: {show_equal}")
                if fields:
                    print(f"  Include Fields: {', '.join(fields)}")
                if ignore_fields:
                    print(f"  Ignore Fields: {', '.join(ignore_fields)}")
                if save_to:
                    print(f"  Save To: {save_to}")
                print(
                    "\n[yellow]DRY RUN: Jobs would be compared with the above configuration[/yellow]"
                )
                return True

            # Get both job definitions
            try:
                source_response = self.glue_client.get_job(JobName=source_job)
                source_job_def = source_response["Job"]
            except ClientError as e:
                if e.response["Error"]["Code"] == "EntityNotFoundException":
                    print(f"[red]Source job '{source_job}' not found[/red]")
                    return False
                else:
                    raise

            try:
                target_response = self.glue_client.get_job(JobName=target_job)
                target_job_def = target_response["Job"]
            except ClientError as e:
                if e.response["Error"]["Code"] == "EntityNotFoundException":
                    print(f"[red]Target job '{target_job}' not found[/red]")
                    return False
                else:
                    raise

            # Perform the comparison
            diff_result = self._compare_job_definitions(
                source_job_def,
                target_job_def,
                source_job,
                target_job,
                fields,
                ignore_fields,
                show_equal,
            )

            # Display results based on output format
            if output_format == "table":
                self._display_diff_table(diff_result, source_job, target_job)
            elif output_format == "json":
                self._display_diff_json(diff_result)
            elif output_format == "yaml":
                self._display_diff_yaml(diff_result)
            elif output_format == "markdown":
                self._display_diff_markdown(diff_result, source_job, target_job)

            # Save to file if requested
            if save_to:
                self._save_diff_to_file(diff_result, save_to, output_format)

            # Summary
            different_count = sum(
                1
                for item in diff_result["differences"]
                if item["status"] == "different"
            )
            equal_count = sum(
                1 for item in diff_result["differences"] if item["status"] == "equal"
            )

            print("\n[cyan]Summary:[/cyan]")
            print(f"  Different fields: {different_count}")
            print(f"  Equal fields: {equal_count}")
            print(f"  Total compared: {len(diff_result['differences'])}")

            if different_count > 0:
                print(f"[yellow]⚠️ Jobs have {different_count} difference(s)[/yellow]")
            else:
                print("[green]✅ Jobs are identical[/green]")

            return True

        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            error_message = e.response["Error"]["Message"]

            if error_code == "AccessDeniedException":
                print(
                    "[red]Access denied. Check your IAM permissions for AWS Glue[/red]"
                )
            elif error_code == "InvalidInputException":
                print(f"[red]Invalid input: {error_message}[/red]")
            else:
                print(f"[red]AWS Error ({error_code}): {error_message}[/red]")
            return False

        except Exception as e:
            print(f"[red]Error comparing jobs: {e}[/red]")
            return False

    def _compare_job_definitions(
        self,
        source_job: dict,
        target_job: dict,
        source_name: str,
        target_name: str,
        fields: Optional[List[str]] = None,
        ignore_fields: Optional[List[str]] = None,
        show_equal: bool = False,
    ) -> dict:
        """Compare two job definitions and return structured diff result."""
        # Define all comparable fields
        all_fields = {
            "Name": lambda job: job.get("Name", "N/A"),
            "Role": lambda job: job.get("Role", "N/A"),
            "ScriptLocation": lambda job: job.get("Command", {}).get(
                "ScriptLocation", "N/A"
            ),
            "JobType": lambda job: job.get("Command", {}).get("Name", "N/A"),
            "GlueVersion": lambda job: job.get("GlueVersion", "N/A"),
            "PythonVersion": lambda job: job.get("Command", {}).get(
                "PythonVersion", "N/A"
            ),
            "WorkerType": lambda job: job.get("WorkerType", "N/A"),
            "NumberOfWorkers": lambda job: job.get("NumberOfWorkers", "N/A"),
            "MaxCapacity": lambda job: job.get("MaxCapacity", "N/A"),
            "MaxRetries": lambda job: job.get("MaxRetries", "N/A"),
            "Timeout": lambda job: job.get("Timeout", "N/A"),
            "ExecutionClass": lambda job: job.get("ExecutionClass", "N/A"),
            "DefaultArguments": lambda job: job.get("DefaultArguments", {}),
            "Connections": lambda job: job.get("Connections", {}).get(
                "Connections", []
            ),
            "SecurityConfiguration": lambda job: job.get(
                "SecurityConfiguration", "N/A"
            ),
            "Tags": lambda job: job.get("Tags", {}),
            "Description": lambda job: job.get("Description", "N/A"),
            "CreatedOn": lambda job: self._format_date(job.get("CreatedOn")),
            "LastModifiedOn": lambda job: self._format_date(job.get("LastModifiedOn")),
        }

        # Apply field filters
        if fields:
            # Only include specified fields
            filtered_fields = {k: v for k, v in all_fields.items() if k in fields}
        else:
            # Include all fields except ignored ones
            ignored = ignore_fields or []
            filtered_fields = {k: v for k, v in all_fields.items() if k not in ignored}

        # Compare each field
        differences = []

        for field_name, extractor in filtered_fields.items():
            source_value = extractor(source_job)
            target_value = extractor(target_job)

            # Determine if values are equal
            if self._values_equal(source_value, target_value):
                status = "equal"
            else:
                status = "different"

            # Include in results based on show_equal setting
            if status == "different" or show_equal:
                differences.append(
                    {
                        "field": field_name,
                        "status": status,
                        "source_value": source_value,
                        "target_value": target_value,
                        "source_name": source_name,
                        "target_name": target_name,
                    }
                )

        return {
            "source_job": source_name,
            "target_job": target_name,
            "differences": differences,
            "summary": {
                "total_fields": len(filtered_fields),
                "different_fields": sum(
                    1 for d in differences if d["status"] == "different"
                ),
                "equal_fields": sum(1 for d in differences if d["status"] == "equal"),
            },
        }

    def _values_equal(self, value1, value2) -> bool:
        """Compare two values for equality, handling different data types."""
        # Handle None/N/A cases
        if value1 == "N/A" and value2 == "N/A":
            return True
        if value1 == "N/A" or value2 == "N/A":
            return False

        # Handle dictionaries
        if isinstance(value1, dict) and isinstance(value2, dict):
            return value1 == value2

        # Handle lists
        if isinstance(value1, list) and isinstance(value2, list):
            return sorted(value1) == sorted(value2)

        # Handle strings and other types
        return str(value1) == str(value2)

    def _display_diff_table(
        self, diff_result: dict, source_name: str, target_name: str
    ) -> None:
        """Display diff results in table format."""
        from rich.table import Table

        print(f"\n[cyan]Comparing: {source_name} ⟷ {target_name}[/cyan]\n")

        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Field", style="cyan", no_wrap=True)
        table.add_column("Status", justify="center")
        table.add_column(source_name, style="blue")
        table.add_column(target_name, style="green")

        for diff in diff_result["differences"]:
            if diff["status"] == "equal":
                status = "[green]✅ same[/green]"
                source_val = str(diff["source_value"])
                target_val = str(diff["target_value"])
            else:
                status = "[red]❌ different[/red]"
                source_val = (
                    f"[yellow]{self._format_diff_value(diff['source_value'])}[/yellow]"
                )
                target_val = (
                    f"[yellow]{self._format_diff_value(diff['target_value'])}[/yellow]"
                )

            table.add_row(diff["field"], status, source_val, target_val)

        self.console.print(table)

    def _display_diff_json(self, diff_result: dict) -> None:
        """Display diff results in JSON format."""
        import json

        json_output = json.dumps(diff_result, indent=2, default=str)
        print(json_output)

    def _display_diff_yaml(self, diff_result: dict) -> None:
        """Display diff results in YAML format."""
        try:
            import yaml

            yaml_output = yaml.dump(
                diff_result, default_flow_style=False, sort_keys=False
            )
            print(yaml_output)
        except ImportError:
            print(
                "[red]PyYAML not installed. Please install it to use YAML output format.[/red]"
            )
            # Fall back to JSON
            self._display_diff_json(diff_result)

    def _display_diff_markdown(
        self, diff_result: dict, source_name: str, target_name: str
    ) -> None:
        """Display diff results in Markdown format."""
        print(f"# Job Comparison: {source_name} ⟷ {target_name}")
        print()
        print("| Field | Status | Source | Target |")
        print("|-------|--------|--------|--------|")

        for diff in diff_result["differences"]:
            status = "✅ Same" if diff["status"] == "equal" else "❌ Different"
            source_val = self._format_diff_value(diff["source_value"])
            target_val = self._format_diff_value(diff["target_value"])

            print(f"| {diff['field']} | {status} | {source_val} | {target_val} |")

        print()
        print("## Summary")
        print(f"- Total fields compared: {diff_result['summary']['total_fields']}")
        print(f"- Different fields: {diff_result['summary']['different_fields']}")
        print(f"- Equal fields: {diff_result['summary']['equal_fields']}")

    def _format_diff_value(self, value) -> str:
        """Format a value for display in diff output."""
        if value == "N/A":
            return "N/A"
        elif isinstance(value, dict):
            if not value:
                return "{}"
            # Show dict as key-value pairs
            items = [f"{k}={v}" for k, v in value.items()]
            return ", ".join(items[:3]) + ("..." if len(items) > 3 else "")
        elif isinstance(value, list):
            if not value:
                return "[]"
            return ", ".join(str(v) for v in value[:3]) + (
                "..." if len(value) > 3 else ""
            )
        else:
            return str(value)

    def _save_diff_to_file(
        self, diff_result: dict, file_path: str, output_format: str
    ) -> None:
        """Save diff results to a file."""
        try:
            if output_format == "json" or file_path.endswith(".json"):
                import json

                content = json.dumps(diff_result, indent=2, default=str)
            elif output_format == "yaml" or file_path.endswith((".yaml", ".yml")):
                try:
                    import yaml

                    content = yaml.dump(
                        diff_result, default_flow_style=False, sort_keys=False
                    )
                except ImportError:
                    print(
                        "[yellow]PyYAML not installed, saving as JSON instead[/yellow]"
                    )
                    import json

                    content = json.dumps(diff_result, indent=2, default=str)
            elif output_format == "markdown" or file_path.endswith(".md"):
                content = self._generate_markdown_diff(diff_result)
            else:
                # Default to JSON
                import json

                content = json.dumps(diff_result, indent=2, default=str)

            self._save_to_file(content, file_path)

        except Exception as e:
            print(f"[red]Error saving diff to file: {e}[/red]")

    def _generate_markdown_diff(self, diff_result: dict) -> str:
        """Generate markdown content for diff results."""
        lines = [
            f"# Job Comparison: {diff_result['source_job']} ⟷ {diff_result['target_job']}",
            "",
            "| Field | Status | Source | Target |",
            "|-------|--------|--------|--------|",
        ]

        for diff in diff_result["differences"]:
            status = "✅ Same" if diff["status"] == "equal" else "❌ Different"
            source_val = self._format_diff_value(diff["source_value"])
            target_val = self._format_diff_value(diff["target_value"])

            lines.append(
                f"| {diff['field']} | {status} | {source_val} | {target_val} |"
            )

        lines.extend(
            [
                "",
                "## Summary",
                f"- Total fields compared: {diff_result['summary']['total_fields']}",
                f"- Different fields: {diff_result['summary']['different_fields']}",
                f"- Equal fields: {diff_result['summary']['equal_fields']}",
            ]
        )

        return "\n".join(lines)

    def list_job_runs(
        self,
        job_name: Optional[str] = None,
        limit: int = 50,
        status: Optional[str] = None,
        output_format: str = "table",
    ) -> bool:
        """List AWS Glue job runs with optional filtering.

        Args:
            job_name: Filter by specific job name. If None, lists runs for all jobs
            limit: Maximum number of runs to display
            status: Filter by run status
            output_format: Output format (table, json, yaml, csv)

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if job_name:
                job_runs = self._get_job_runs_for_specific_job(job_name, limit, status)
            else:
                job_runs = self._get_job_runs_for_all_jobs(limit, status)

            if not job_runs:
                self._display_no_runs_message(job_name, status)
                return True

            # Sort by StartedOn timestamp (most recent first)
            job_runs.sort(key=lambda x: x.get("StartedOn", datetime.min), reverse=True)

            # Limit results
            job_runs = job_runs[:limit]

            # Output results
            self._output_job_runs(job_runs, output_format)
            return True

        except ClientError as e:
            print(f"[red]AWS Error: {e}[/red]")
            return False
        except Exception as e:
            print(f"[red]Error listing job runs: {e}[/red]")
            return False

    def _get_job_runs_for_specific_job(
        self, job_name: str, limit: int, status: Optional[str]
    ) -> List[Dict]:
        """Get job runs for a specific job."""
        job_runs = []
        paginator = self.glue_client.get_paginator("get_job_runs")
        page_iterator = paginator.paginate(
            JobName=job_name, PaginationConfig={"MaxItems": limit}
        )

        for page in page_iterator:
            for run in page.get("JobRuns", []):
                if not status or run.get("JobRunState") == status:
                    job_runs.append(run)

        return job_runs

    def _get_job_runs_for_all_jobs(
        self, limit: int, status: Optional[str]
    ) -> List[Dict]:
        """Get job runs for all jobs."""
        # First get all job names
        jobs_paginator = self.glue_client.get_paginator("get_jobs")
        jobs_iterator = jobs_paginator.paginate()

        all_jobs = []
        for page in jobs_iterator:
            all_jobs.extend(page.get("Jobs", []))

        # Then get runs for each job
        job_runs: List[Dict] = []
        runs_per_job = max(1, limit // max(1, len(all_jobs)))

        for job in all_jobs:
            if len(job_runs) >= limit:
                break

            try:
                response = self.glue_client.get_job_runs(
                    JobName=job["Name"],
                    MaxResults=min(runs_per_job, limit - len(job_runs)),
                )

                for run in response.get("JobRuns", []):
                    if not status or run.get("JobRunState") == status:
                        job_runs.append(run)

            except ClientError as e:
                if "EntityNotFoundException" not in str(e):
                    print(
                        f"[yellow]Warning: Could not get runs for job {job['Name']}: {e}[/yellow]"
                    )
                continue

        return job_runs

    def _display_no_runs_message(
        self, job_name: Optional[str], status: Optional[str]
    ) -> None:
        """Display message when no job runs are found."""
        filter_desc = []
        if job_name:
            filter_desc.append(f"job '{job_name}'")
        if status:
            filter_desc.append(f"status '{status}'")

        filter_text = " with " + " and ".join(filter_desc) if filter_desc else ""
        print(f"[yellow]No job runs found{filter_text}[/yellow]")

    def _output_job_runs(self, job_runs: List[Dict], output_format: str) -> None:
        """Output job runs in the specified format."""
        if output_format == "table":
            self._print_job_runs_table(job_runs)
        elif output_format == "json":
            self._print_job_runs_json(job_runs)
        elif output_format == "yaml":
            self._print_job_runs_yaml(job_runs)
        elif output_format == "csv":
            self._print_job_runs_csv(job_runs)

    def _print_job_runs_table(self, job_runs: List[Dict]) -> None:
        """Print job runs in table format."""
        table = Table(
            title="AWS Glue Job Runs",
            box=box.SIMPLE,
            title_style="bold blue",
            header_style="bold cyan",
            show_lines=True,
        )

        table.add_column("Job Name", style="bold", no_wrap=True, width=30)
        table.add_column("Run ID", no_wrap=True, width=36)
        table.add_column("Status", justify="center", width=12)
        table.add_column("Started", justify="center", width=20)
        table.add_column("Duration", justify="center", width=15)
        table.add_column("Worker Type", justify="center", width=12)
        table.add_column("Workers", justify="center", width=8)
        table.add_column("Error", style="red", width=60)

        for run in job_runs:
            # Status styling
            status = run.get("JobRunState", "UNKNOWN")
            status_color = {
                "SUCCEEDED": "green",
                "FAILED": "red",
                "TIMEOUT": "red",
                "RUNNING": "blue",
                "STARTING": "yellow",
                "STOPPING": "orange",
                "STOPPED": "gray",
            }.get(status, "white")

            # Duration calculation
            duration = "—"
            if run.get("StartedOn") and run.get("CompletedOn"):
                delta = run["CompletedOn"] - run["StartedOn"]
                duration = str(delta).split(".")[0]  # Remove microseconds
            elif run.get("StartedOn") and status in ["RUNNING", "STARTING"]:
                from datetime import datetime, timezone

                delta = datetime.now(timezone.utc) - run["StartedOn"]
                duration = f"{str(delta).split('.')[0]} (running)"

            # Error message
            error_msg = ""
            if status in ["FAILED", "TIMEOUT"] and run.get("ErrorMessage"):
                error_msg = run["ErrorMessage"]

            table.add_row(
                run.get("JobName", "—"),
                run.get("Id", "—"),
                f"[{status_color}]{status}[/{status_color}]",
                (
                    run["StartedOn"].strftime("%Y-%m-%d %H:%M:%S")
                    if run.get("StartedOn")
                    else "—"
                ),
                duration,
                run.get("WorkerType", "—"),
                str(run.get("NumberOfWorkers", "—")),
                error_msg,
            )

        print(table)

    def _print_job_runs_json(self, job_runs: List[Dict]) -> None:
        """Print job runs in JSON format."""
        # Convert datetime objects to strings for JSON serialization
        serializable_runs = []
        for run in job_runs:
            serializable_run = {}
            for key, value in run.items():
                if isinstance(value, datetime):
                    serializable_run[key] = value.isoformat()
                else:
                    serializable_run[key] = value
            serializable_runs.append(serializable_run)

        print(json.dumps(serializable_runs, indent=2, default=str))

    def _print_job_runs_yaml(self, job_runs: List[Dict]) -> None:
        """Print job runs in YAML format."""
        try:
            # Convert datetime objects to strings for YAML serialization
            serializable_runs = []
            for run in job_runs:
                serializable_run = {}
                for key, value in run.items():
                    if isinstance(value, datetime):
                        serializable_run[key] = value.isoformat()
                    else:
                        serializable_run[key] = value
                serializable_runs.append(serializable_run)

            print(
                yaml.dump(serializable_runs, default_flow_style=False, sort_keys=False)
            )
        except ImportError:
            print("[yellow]PyYAML not installed, falling back to JSON format[/yellow]")
            self._print_job_runs_json(job_runs)

    def _print_job_runs_csv(self, job_runs: List[Dict]) -> None:
        """Print job runs in CSV format."""
        if not job_runs:
            return

        # Define CSV columns
        columns = [
            "JobName",
            "Id",
            "JobRunState",
            "StartedOn",
            "CompletedOn",
            "WorkerType",
            "NumberOfWorkers",
            "ErrorMessage",
        ]

        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=columns, extrasaction="ignore")
        writer.writeheader()

        for run in job_runs:
            # Convert datetime objects to strings
            csv_run = {}
            for col in columns:
                value = run.get(col, "")
                if isinstance(value, datetime):
                    csv_run[col] = value.isoformat()
                else:
                    csv_run[col] = str(value) if value is not None else ""
            writer.writerow(csv_run)

        print(output.getvalue().strip())

    def describe_job_run(
        self,
        job_name: str,
        run_id: str,
        output_format: str = "table",
    ) -> bool:
        """Get detailed information about a specific job run.

        Args:
            job_name: Name of the AWS Glue job
            run_id: ID of the job run to describe
            output_format: Output format (table, json, yaml)

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Get job run details
            response = self.glue_client.get_job_run(JobName=job_name, RunId=run_id)

            job_run = response.get("JobRun", {})

            if not job_run:
                print(f"[red]Job run '{run_id}' not found for job '{job_name}'[/red]")
                return False

            # Output results
            if output_format == "table":
                self._print_job_run_details_table(job_run)
            elif output_format == "json":
                self._print_job_run_details_json(job_run)
            elif output_format == "yaml":
                self._print_job_run_details_yaml(job_run)

            return True

        except ClientError as e:
            error_code = e.response.get("Error", {}).get("Code", "")
            if error_code == "EntityNotFoundException":
                print(f"[red]Job run '{run_id}' not found for job '{job_name}'[/red]")
            else:
                print(f"[red]AWS Error: {e}[/red]")
            return False
        except Exception as e:
            print(f"[red]Error describing job run: {e}[/red]")
            return False

    def _print_job_run_details_table(self, job_run: Dict) -> None:
        """Print job run details in table format."""
        from rich.panel import Panel

        # Basic information table
        basic_table = Table(
            title="Job Run Details",
            box=box.SIMPLE,
            title_style="bold blue",
            header_style="bold cyan",
        )
        basic_table.add_column("Property", style="bold", width=20)
        basic_table.add_column("Value", width=60)

        # Job run state with color
        state = job_run.get("JobRunState", "UNKNOWN")
        state_color = {
            "SUCCEEDED": "green",
            "FAILED": "red",
            "TIMEOUT": "red",
            "RUNNING": "blue",
            "STARTING": "yellow",
            "STOPPING": "orange",
            "STOPPED": "gray",
        }.get(state, "white")

        basic_table.add_row("Job Name", job_run.get("JobName", "—"))
        basic_table.add_row("Run ID", job_run.get("Id", "—"))
        basic_table.add_row("State", f"[{state_color}]{state}[/{state_color}]")
        started_on = job_run.get("StartedOn")
        basic_table.add_row(
            "Started On",
            (started_on.strftime("%Y-%m-%d %H:%M:%S UTC") if started_on else "—"),
        )
        completed_on = job_run.get("CompletedOn")
        basic_table.add_row(
            "Completed On",
            (completed_on.strftime("%Y-%m-%d %H:%M:%S UTC") if completed_on else "—"),
        )

        # Calculate duration
        duration = "—"
        if job_run.get("StartedOn") and job_run.get("CompletedOn"):
            delta = job_run["CompletedOn"] - job_run["StartedOn"]
            duration = str(delta).split(".")[0]
        elif job_run.get("StartedOn") and state in ["RUNNING", "STARTING"]:
            from datetime import datetime, timezone

            delta = datetime.now(timezone.utc) - job_run["StartedOn"]
            duration = f"{str(delta).split('.')[0]} (running)"

        basic_table.add_row("Duration", duration)
        basic_table.add_row(
            "Execution Time", f"{job_run.get('ExecutionTime', 0)} seconds"
        )

        print(basic_table)
        print()

        # Resource allocation table
        resource_table = Table(
            title="Resource Allocation",
            box=box.SIMPLE,
            title_style="bold green",
            header_style="bold cyan",
        )
        resource_table.add_column("Property", style="bold", width=20)
        resource_table.add_column("Value", width=60)

        resource_table.add_row("Worker Type", job_run.get("WorkerType", "—"))
        resource_table.add_row(
            "Number of Workers", str(job_run.get("NumberOfWorkers", "—"))
        )
        resource_table.add_row("Max Capacity", str(job_run.get("MaxCapacity", "—")))
        resource_table.add_row("Timeout", f"{job_run.get('Timeout', '—')} minutes")
        resource_table.add_row("Glue Version", job_run.get("GlueVersion", "—"))

        print(resource_table)
        print()

        # Arguments table
        if job_run.get("Arguments"):
            args_table = Table(
                title="Job Arguments",
                box=box.SIMPLE,
                title_style="bold magenta",
                header_style="bold cyan",
            )
            args_table.add_column("Argument", style="bold", width=30)
            args_table.add_column("Value", width=50)

            for key, value in job_run.get("Arguments", {}).items():
                args_table.add_row(key, str(value))

            print(args_table)
            print()

        # Error information
        if job_run.get("ErrorMessage"):
            error_panel = Panel(
                job_run.get("ErrorMessage", ""),
                title="[red]Error Message[/red]",
                border_style="red",
            )
            print(error_panel)
            print()

        # Log groups information
        if job_run.get("LogGroupName"):
            log_table = Table(
                title="CloudWatch Logs",
                box=box.SIMPLE,
                title_style="bold yellow",
                header_style="bold cyan",
            )
            log_table.add_column("Type", style="bold", width=15)
            log_table.add_column("Log Group", width=65)

            log_table.add_row("CloudWatch", job_run.get("LogGroupName", "—"))

            # Generate potential log stream names
            if job_run.get("Id"):
                log_table.add_row("Output Stream", f"{job_run['Id']}/output")
                log_table.add_row("Error Stream", f"{job_run['Id']}/error")
                log_table.add_row("Driver Stream", f"{job_run['Id']}/driver")

            print(log_table)

    def _print_job_run_details_json(self, job_run: Dict) -> None:
        """Print job run details in JSON format."""
        # Convert datetime objects to strings for JSON serialization
        serializable_run = {}
        for key, value in job_run.items():
            if isinstance(value, datetime):
                serializable_run[key] = value.isoformat()
            else:
                serializable_run[key] = value

        print(json.dumps(serializable_run, indent=2, default=str))

    def _print_job_run_details_yaml(self, job_run: Dict) -> None:
        """Print job run details in YAML format."""
        try:
            # Convert datetime objects to strings for YAML serialization
            serializable_run = {}
            for key, value in job_run.items():
                if isinstance(value, datetime):
                    serializable_run[key] = value.isoformat()
                else:
                    serializable_run[key] = value

            print(
                yaml.dump(serializable_run, default_flow_style=False, sort_keys=False)
            )
        except ImportError:
            print("[yellow]PyYAML not installed, falling back to JSON format[/yellow]")
            self._print_job_run_details_json(job_run)
