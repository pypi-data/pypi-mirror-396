"""Parquet service for managing and analyzing Parquet files."""

import io
import json
import os
import urllib.parse
from typing import Optional

import boto3
import pandas as pd
import pyarrow.parquet as pq
import yaml
from botocore.exceptions import ClientError, NoCredentialsError
from rich import box, print
from rich.console import Console
from rich.table import Table


class ParquetService:
    """Service class for managing and analyzing Parquet files."""

    def __init__(self):
        """Initialize the ParquetService."""
        self.console = Console()

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

    def _is_s3_path(self, path: str) -> bool:
        """Check if path is an S3 path."""
        return path.startswith("s3://")

    def _format_file_size(self, size_bytes: int) -> str:
        """Format file size in human readable format."""
        if size_bytes < 1024:
            return f"{size_bytes} bytes"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.1f} KB"
        else:
            return f"{size_bytes / (1024 * 1024):.1f} MB"

    def _validate_parquet_file(self, path: str) -> tuple[bool, str, Optional[object]]:
        """Validate parquet file exists and return metadata."""
        s3_client = None

        if self._is_s3_path(path):
            try:
                s3_client = boto3.client("s3")
            except NoCredentialsError:
                return (
                    False,
                    "AWS credentials not found. Please configure your AWS credentials.",
                    None,
                )

            # Check if S3 object exists
            parsed_path = urllib.parse.urlparse(path)
            try:
                s3_client.head_object(
                    Bucket=parsed_path.netloc, Key=parsed_path.path.lstrip("/")
                )
            except ClientError as e:
                if e.response["Error"]["Code"] == "404":
                    return False, f"File not found: {path}", None
                else:
                    return False, f"AWS Error: {e.response['Error']['Message']}", None

            if not path.endswith(".parquet"):
                return False, f"File is not a .parquet file: {path}", None

        else:
            path = os.path.abspath(path)
            if not os.path.exists(path):
                return False, f"File not found: {path}", None
            if not path.endswith(".parquet"):
                return False, f"File is not a .parquet file: {path}", None

        return True, "", s3_client

    def _load_parquet_data(
        self, path: str, s3_client=None
    ) -> tuple[pq.ParquetFile, pd.DataFrame, int]:
        """Load parquet file and return metadata."""
        if self._is_s3_path(path):
            # Read from S3
            df = pd.read_parquet(path)

            # Create a ParquetFile for metadata
            parsed_path = urllib.parse.urlparse(path)
            response = s3_client.get_object(
                Bucket=parsed_path.netloc, Key=parsed_path.path.lstrip("/")
            )
            parquet_buffer = io.BytesIO(response["Body"].read())
            parquet_file = pq.ParquetFile(parquet_buffer)
            file_size = response["ContentLength"]
        else:
            parquet_file = pq.ParquetFile(path)
            df = pd.read_parquet(path)
            file_size = os.path.getsize(path)

        return parquet_file, df, file_size

    def describe_file(  # noqa: C901
        self,
        path: str,
        sample: bool = False,
        columns: Optional[str] = None,
        summary: bool = False,
        output_format: str = "table",
    ) -> None:
        """Show schema and metadata of a Parquet file with support for S3 and local paths."""
        try:
            output_format = self._validate_output_format(output_format)

            if output_format == "table":
                if self._is_s3_path(path):
                    print(f"[blue]🔍 Analyzing S3 file: {path}[/blue]")
                else:
                    path = os.path.abspath(path)
                    print(f"[blue]🔍 Analyzing local file: {path}[/blue]")

            # Validate file
            is_valid, error_msg, s3_client = self._validate_parquet_file(path)
            if not is_valid:
                if output_format == "table":
                    print(f"[red]❌ Error: {error_msg}[/red]")
                elif output_format == "json":
                    print(json.dumps({"error": error_msg}, indent=2))
                elif output_format == "yaml":
                    print(yaml.dump({"error": error_msg}))
                elif output_format == "text":
                    print(f"Error: {error_msg}")
                elif output_format == "markdown":
                    print(f"# Parquet File Analysis\n\n**Error:** {error_msg}")
                return

            # Load parquet data
            parquet_file, df, file_size = self._load_parquet_data(path, s3_client)

            # Prepare column selection
            schema = parquet_file.schema_arrow
            available_columns = [field.name for field in schema]

            if columns:
                selected_columns = [col.strip() for col in columns.split(",")]
                missing_columns = [
                    col for col in selected_columns if col not in available_columns
                ]
                if missing_columns and output_format == "table":
                    print(
                        f"[yellow]⚠️ Warning: Columns not found: {missing_columns}[/yellow]"
                    )
                selected_columns = [
                    col for col in selected_columns if col in available_columns
                ]
                if not selected_columns:
                    error_msg = "No valid columns found"
                    if output_format == "table":
                        print(f"[red]❌ {error_msg}[/red]")
                    return
            else:
                selected_columns = available_columns

            # Prepare data structure
            file_info = {
                "filename": os.path.basename(path),
                "path": path,
                "file_size": file_size,
                "file_size_formatted": self._format_file_size(file_size),
                "num_rows": parquet_file.metadata.num_rows,
                "num_columns": parquet_file.metadata.num_columns,
                "num_row_groups": parquet_file.metadata.num_row_groups,
                "schema": [],
                "compression": None,
                "partition_columns": [],
                "sample_data": None,
                "summary_stats": None,
            }

            # Schema information
            for field in schema:
                if field.name in selected_columns:
                    file_info["schema"].append(
                        {
                            "name": field.name,
                            "type": str(field.type),
                            "nullable": field.nullable,
                        }
                    )

            # Compression info
            if parquet_file.metadata.row_group(0).column(0).compression:
                file_info["compression"] = (
                    parquet_file.metadata.row_group(0).column(0).compression
                )

            # Partition information
            if parquet_file.schema.to_arrow_schema().metadata:
                metadata = parquet_file.schema.to_arrow_schema().metadata
                if metadata and b"pandas" in metadata:
                    try:
                        pandas_metadata = json.loads(
                            metadata[b"pandas"].decode("utf-8")
                        )
                        if (
                            "partition_columns" in pandas_metadata
                            and pandas_metadata["partition_columns"]
                        ):
                            file_info["partition_columns"] = pandas_metadata[
                                "partition_columns"
                            ]
                    except Exception:
                        pass

            # Sample data
            if sample:
                sample_df = df.head(5)
                if columns:
                    sample_df = sample_df[selected_columns]
                file_info["sample_data"] = sample_df.to_dict("records")

            # Summary statistics
            if summary:
                stats = {}
                for col in selected_columns:
                    if col in df.columns:  # Ensure column exists in DataFrame
                        col_stats = {
                            "data_type": str(df[col].dtype),
                            "null_count": int(df[col].isnull().sum()),
                            "non_null_count": int(len(df) - df[col].isnull().sum()),
                        }

                        if df[col].dtype in ["int64", "float64", "int32", "float32"]:
                            col_stats.update(
                                {
                                    "min": (
                                        float(df[col].min())
                                        if pd.notna(df[col].min())
                                        else None
                                    ),
                                    "max": (
                                        float(df[col].max())
                                        if pd.notna(df[col].max())
                                        else None
                                    ),
                                    "mean": (
                                        float(df[col].mean())
                                        if pd.notna(df[col].mean())
                                        else None
                                    ),
                                    "std": (
                                        float(df[col].std())
                                        if pd.notna(df[col].std())
                                        else None
                                    ),
                                }
                            )
                        elif df[col].dtype == "object" or pd.api.types.is_string_dtype(
                            df[col]
                        ):
                            unique_count = df[col].nunique()
                            col_stats.update(
                                {
                                    "unique_values": int(unique_count),
                                }
                            )
                            if unique_count > 0:
                                most_common = df[col].value_counts().head(1)
                                if len(most_common) > 0:
                                    col_stats.update(
                                        {
                                            "most_common_value": str(
                                                most_common.index[0]
                                            ),
                                            "most_common_count": int(
                                                most_common.iloc[0]
                                            ),
                                        }
                                    )

                        stats[col] = col_stats
                file_info["summary_stats"] = stats

            # Output in requested format
            if output_format == "json":
                print(json.dumps(file_info, indent=2, default=str))
            elif output_format == "yaml":
                print(yaml.dump(file_info, default_flow_style=False))
            elif output_format == "text":
                self._print_file_info_text(file_info, sample, summary)
            elif output_format == "markdown":
                self._print_file_info_markdown(file_info, sample, summary)
            else:  # table format (default)
                self._print_file_info_table(file_info, sample, summary)

        except ImportError as e:
            error_msg = ""
            if "pandas" in str(e):
                error_msg = "pandas is required. Install with: pip install pandas"
            elif "pyarrow" in str(e):
                error_msg = "pyarrow is required. Install with: pip install pyarrow"
            elif "boto3" in str(e):
                error_msg = (
                    "boto3 is required for S3 support. Install with: pip install boto3"
                )
            else:
                error_msg = f"Import error: {e}"

            if output_format == "table":
                print(f"[red]❌ Error: {error_msg}[/red]")
            else:
                print(f"Error: {error_msg}")

        except Exception as e:
            error_msg = f"Unexpected error: {e}"
            if output_format == "table":
                print(f"[red]❌ Error: {error_msg}[/red]")
            else:
                print(f"Error: {error_msg}")

    def _print_file_info_table(
        self, file_info: dict, sample: bool, summary: bool
    ) -> None:
        """Print file information in table format using Rich."""
        print(
            f"\n[bold cyan]📋 Parquet File Information: {file_info['filename']}[/bold cyan]\n"
        )

        # Basic file details table
        details_table = Table(
            title="📊 File Details",
            show_header=True,
            header_style="bold cyan",
            box=box.SIMPLE,
            border_style="dim",
        )
        details_table.add_column("Property", style="cyan", no_wrap=True)
        details_table.add_column("Value", style="white")

        details_table.add_row("File Size", file_info["file_size_formatted"])
        details_table.add_row("Number of Rows", f"{file_info['num_rows']:,}")
        details_table.add_row("Number of Columns", str(file_info["num_columns"]))
        details_table.add_row("Number of Row Groups", str(file_info["num_row_groups"]))
        if file_info["compression"]:
            details_table.add_row("Compression", file_info["compression"])

        self.console.print(details_table)
        print()

        # Schema table
        schema_table = Table(
            title="🗂️ Schema",
            show_header=True,
            header_style="bold cyan",
            box=box.SIMPLE,
            border_style="dim",
        )
        schema_table.add_column("Column Name", style="green", no_wrap=True)
        schema_table.add_column("Data Type", style="blue")
        schema_table.add_column("Nullable", style="yellow", justify="center")

        for field in file_info["schema"]:
            nullable_str = "✓" if field["nullable"] else "✗"
            schema_table.add_row(
                field["name"],
                field["type"],
                nullable_str,
            )

        self.console.print(schema_table)

        # Partition columns
        if file_info["partition_columns"]:
            print("\n[bold cyan]📁 Partitioned Columns:[/bold cyan]")
            for col in file_info["partition_columns"]:
                print(f"  • {col}")
        else:
            print("\n[bold cyan]📁 Partitioned Columns:[/bold cyan] None")

        # Sample data
        if sample and file_info["sample_data"]:
            print("\n[bold cyan]🔍 Sample Data (first 5 rows):[/bold cyan]")
            sample_table = Table(
                show_header=True,
                header_style="bold cyan",
                box=box.SIMPLE,
                border_style="dim",
            )

            # Add columns
            if file_info["sample_data"]:
                for col_name in file_info["sample_data"][0].keys():
                    sample_table.add_column(col_name, overflow="fold")

                # Add rows
                for row in file_info["sample_data"]:
                    sample_table.add_row(*[str(value) for value in row.values()])

                self.console.print(sample_table)

        # Summary statistics
        if summary and file_info["summary_stats"]:
            print("\n[bold cyan]📈 Summary Statistics:[/bold cyan]")
            for col_name, stats in file_info["summary_stats"].items():
                print(f"\n[bold green]  {col_name}:[/bold green]")
                print(f"    [bold]Data Type:[/bold] {stats['data_type']}")
                print(f"    [bold]Null Count:[/bold] {stats['null_count']:,}")
                print(f"    [bold]Non-Null Count:[/bold] {stats['non_null_count']:,}")

                if "min" in stats:
                    print(f"    [bold]Min:[/bold] {stats['min']}")
                    print(f"    [bold]Max:[/bold] {stats['max']}")
                    print(f"    [bold]Mean:[/bold] {stats['mean']:.2f}")
                    print(f"    [bold]Std:[/bold] {stats['std']:.2f}")
                elif "unique_values" in stats:
                    print(f"    [bold]Unique Values:[/bold] {stats['unique_values']:,}")
                    if "most_common_value" in stats:
                        print(
                            f"    [bold]Most Common:[/bold] '{stats['most_common_value']}' ({stats['most_common_count']} times)"
                        )

        print()

    def _print_file_info_text(
        self, file_info: dict, sample: bool, summary: bool
    ) -> None:
        """Print file information in text format."""
        print(f"Parquet File Information: {file_info['filename']}")
        print("=" * 60)
        print(f"File Size: {file_info['file_size_formatted']}")
        print(f"Number of Rows: {file_info['num_rows']:,}")
        print(f"Number of Columns: {file_info['num_columns']}")
        print(f"Number of Row Groups: {file_info['num_row_groups']}")
        if file_info["compression"]:
            print(f"Compression: {file_info['compression']}")
        print()

        print("Schema:")
        for field in file_info["schema"]:
            nullable_str = "nullable" if field["nullable"] else "not null"
            print(f"  {field['name']}: {field['type']} ({nullable_str})")
        print()

        if file_info["partition_columns"]:
            print("Partitioned Columns:")
            for col in file_info["partition_columns"]:
                print(f"  {col}")
        else:
            print("Partitioned Columns: None")
        print()

        if sample and file_info["sample_data"]:
            print("Sample Data (first 5 rows):")
            df_sample = pd.DataFrame(file_info["sample_data"])
            print(df_sample.to_string(index=False))
            print()

        if summary and file_info["summary_stats"]:
            print("Summary Statistics:")
            for col_name, stats in file_info["summary_stats"].items():
                print(f"\n  {col_name}:")
                print(f"    Data Type: {stats['data_type']}")
                print(f"    Null Count: {stats['null_count']:,}")
                print(f"    Non-Null Count: {stats['non_null_count']:,}")

                if "min" in stats:
                    print(f"    Min: {stats['min']}")
                    print(f"    Max: {stats['max']}")
                    print(f"    Mean: {stats['mean']:.2f}")
                    print(f"    Std: {stats['std']:.2f}")
                elif "unique_values" in stats:
                    print(f"    Unique Values: {stats['unique_values']:,}")
                    if "most_common_value" in stats:
                        print(
                            f"    Most Common: '{stats['most_common_value']}' ({stats['most_common_count']} times)"
                        )

    def _print_file_info_markdown(
        self, file_info: dict, sample: bool, summary: bool
    ) -> None:
        """Print file information in markdown format."""
        print(f"# Parquet File Information: {file_info['filename']}\n")

        print("## Basic Information\n")
        print(f"- **File Size:** {file_info['file_size_formatted']}")
        print(f"- **Number of Rows:** {file_info['num_rows']:,}")
        print(f"- **Number of Columns:** {file_info['num_columns']}")
        print(f"- **Number of Row Groups:** {file_info['num_row_groups']}")
        if file_info["compression"]:
            print(f"- **Compression:** {file_info['compression']}")
        print()

        print("## Schema\n")
        print("| Column Name | Data Type | Nullable |")
        print("|-------------|-----------|----------|")
        for field in file_info["schema"]:
            nullable_str = "Yes" if field["nullable"] else "No"
            print(f"| {field['name']} | {field['type']} | {nullable_str} |")
        print()

        if file_info["partition_columns"]:
            print("## Partitioned Columns\n")
            for col in file_info["partition_columns"]:
                print(f"- {col}")
        else:
            print("## Partitioned Columns\n\nNone")
        print()

        if sample and file_info["sample_data"]:
            print("## Sample Data (first 5 rows)\n")
            if file_info["sample_data"]:
                # Create markdown table
                headers = list(file_info["sample_data"][0].keys())
                print(f"| {' | '.join(headers)} |")
                print(f"| {' | '.join(['---'] * len(headers))} |")
                for row in file_info["sample_data"]:
                    values = [str(value) for value in row.values()]
                    print(f"| {' | '.join(values)} |")
            print()

        if summary and file_info["summary_stats"]:
            print("## Summary Statistics\n")
            for col_name, stats in file_info["summary_stats"].items():
                print(f"### {col_name}\n")
                print(f"- **Data Type:** {stats['data_type']}")
                print(f"- **Null Count:** {stats['null_count']:,}")
                print(f"- **Non-Null Count:** {stats['non_null_count']:,}")

                if "min" in stats:
                    print(f"- **Min:** {stats['min']}")
                    print(f"- **Max:** {stats['max']}")
                    print(f"- **Mean:** {stats['mean']:.2f}")
                    print(f"- **Std:** {stats['std']:.2f}")
                elif "unique_values" in stats:
                    print(f"- **Unique Values:** {stats['unique_values']:,}")
                    if "most_common_value" in stats:
                        print(
                            f"- **Most Common:** '{stats['most_common_value']}' ({stats['most_common_count']} times)"
                        )
                print()

    def select_data(  # noqa: C901
        self,
        path: str,
        columns: Optional[str] = None,
        filter_expr: Optional[str] = None,
        limit: Optional[int] = None,
        output: Optional[str] = None,
        output_format: str = "table",
    ) -> None:
        """Select and filter data from a Parquet file with support for S3 and local paths."""
        try:
            output_format = self._validate_output_format(output_format)

            if output_format == "table":
                if self._is_s3_path(path):
                    print(f"[blue]🔍 Reading S3 file: {path}[/blue]")
                else:
                    path = os.path.abspath(path)
                    print(f"[blue]🔍 Reading local file: {path}[/blue]")

            # Validate file
            is_valid, error_msg, s3_client = self._validate_parquet_file(path)
            if not is_valid:
                if output_format == "table":
                    print(f"[red]❌ Error: {error_msg}[/red]")
                elif output_format == "json":
                    print(json.dumps({"error": error_msg}, indent=2))
                elif output_format == "yaml":
                    print(yaml.dump({"error": error_msg}))
                elif output_format == "text":
                    print(f"Error: {error_msg}")
                elif output_format == "markdown":
                    print(f"# Parquet Data Selection\n\n**Error:** {error_msg}")
                return

            # Read parquet file
            if output_format == "table":
                print("[blue]📊 Loading data...[/blue]")

            df = pd.read_parquet(path)

            if output_format == "table":
                print(f"   [dim]Total rows: {len(df):,}[/dim]")
                print(f"   [dim]Total columns: {len(df.columns)}[/dim]")

            # Prepare selection info
            selection_info = {
                "source_file": os.path.basename(path),
                "source_path": path,
                "original_rows": len(df),
                "original_columns": len(df.columns),
                "selected_columns": None,
                "filter_applied": filter_expr,
                "limit_applied": limit,
                "final_rows": 0,
                "final_columns": 0,
                "data": None,
                "operations": [],
            }

            # Apply filter BEFORE column selection if specified
            if filter_expr:
                if output_format == "table":
                    print(f"[blue]🔍 Applying filter: {filter_expr}[/blue]")

                try:
                    df = df.query(filter_expr)
                    selection_info["operations"].append(
                        f"Applied filter: {filter_expr}"
                    )

                    if output_format == "table":
                        print(f"   [dim]Rows after filter: {len(df):,}[/dim]")

                except Exception as e:
                    error_msg = f"Error in filter expression: {e}"
                    if output_format == "table":
                        print(f"[red]❌ {error_msg}[/red]")
                        print("[yellow]Filter syntax examples:[/yellow]")
                        print("  'column > 100'")
                        print("  'column1 > 100 and column2 < 50'")
                        print("  'column.str.contains(\"text\")'")
                        print("  'active == True' (for boolean columns)")
                        print("  'department == \"Engineering\"' (for string columns)")
                    elif output_format in ["json", "yaml"]:
                        error_data = {
                            "error": error_msg,
                            "filter_examples": [
                                "column > 100",
                                "column1 > 100 and column2 < 50",
                                'column.str.contains("text")',
                                "active == True",
                                'department == "Engineering"',
                            ],
                        }
                        if output_format == "json":
                            print(json.dumps(error_data, indent=2))
                        else:
                            print(yaml.dump(error_data))
                    else:
                        print(f"Error: {error_msg}")
                    return

            # Filter columns if specified
            if columns:
                selected_columns = [col.strip() for col in columns.split(",")]
                missing_columns = [
                    col for col in selected_columns if col not in df.columns
                ]
                if missing_columns:
                    error_msg = f"Columns not found: {missing_columns}. Available columns: {list(df.columns)}"
                    if output_format == "table":
                        print(f"[red]❌ Error: {error_msg}[/red]")
                    elif output_format in ["json", "yaml"]:
                        error_data = {
                            "error": f"Columns not found: {missing_columns}",
                            "available_columns": list(df.columns),
                        }
                        if output_format == "json":
                            print(json.dumps(error_data, indent=2))
                        else:
                            print(yaml.dump(error_data))
                    else:
                        print(f"Error: {error_msg}")
                    return

                df = df[selected_columns]
                selection_info["selected_columns"] = selected_columns
                selection_info["operations"].append(
                    f"Selected {len(selected_columns)} columns"
                )

                if output_format == "table":
                    print(f"   [dim]Selected columns: {len(selected_columns)}[/dim]")

            # Apply limit if specified
            if limit:
                if limit <= 0:
                    error_msg = "Limit must be a positive number"
                    if output_format == "table":
                        print(f"[red]❌ Error: {error_msg}[/red]")
                    else:
                        print(f"Error: {error_msg}")
                    return

                original_rows = len(df)
                df = df.head(limit)
                selection_info["operations"].append(f"Limited to {limit} rows")

                if output_format == "table":
                    print(
                        f"   [dim]Limited to: {len(df):,} rows (from {original_rows:,})[/dim]"
                    )

            # Update final counts
            selection_info["final_rows"] = len(df)
            selection_info["final_columns"] = len(df.columns)

            # Check if we have any data left
            if len(df) == 0:
                if output_format == "table":
                    print("[yellow]⚠️ No data matches the specified criteria[/yellow]")
                elif output_format in ["json", "yaml"]:
                    no_data = {
                        "message": "No data matches the specified criteria",
                        "rows": 0,
                    }
                    if output_format == "json":
                        print(json.dumps(no_data, indent=2))
                    else:
                        print(yaml.dump(no_data))
                else:
                    print("No data matches the specified criteria")
                return

            # Save to file if output specified
            if output:
                self._save_dataframe_to_file(df, output, output_format, s3_client)

            # Prepare data for output
            if output_format in ["json", "yaml"]:
                selection_info["data"] = df.to_dict("records")
            else:
                selection_info["data"] = df

            # Output results
            if output_format == "json":
                print(json.dumps(selection_info, indent=2, default=str))
            elif output_format == "yaml":
                print(yaml.dump(selection_info, default_flow_style=False))
            elif output_format == "text":
                self._print_selection_text(selection_info)
            elif output_format == "markdown":
                self._print_selection_markdown(selection_info)
            else:  # table format (default)
                self._print_selection_table(selection_info)

        except ImportError as e:
            error_msg = ""
            if "pandas" in str(e):
                error_msg = "pandas is required. Install with: pip install pandas"
            elif "pyarrow" in str(e):
                error_msg = "pyarrow is required. Install with: pip install pyarrow"
            elif "boto3" in str(e):
                error_msg = (
                    "boto3 is required for S3 support. Install with: pip install boto3"
                )
            else:
                error_msg = f"Import error: {e}"

            if output_format == "table":
                print(f"[red]❌ Error: {error_msg}[/red]")
            else:
                print(f"Error: {error_msg}")

        except Exception as e:
            error_msg = f"Unexpected error: {e}"
            if output_format == "table":
                print(f"[red]❌ Error: {error_msg}[/red]")
            else:
                print(f"Error: {error_msg}")

    def _save_dataframe_to_file(
        self, df: pd.DataFrame, output: str, output_format: str, s3_client=None
    ) -> None:
        """Save DataFrame to file with proper format."""
        print(f"[blue]💾 Saving results to: {output}[/blue]")

        try:
            if output_format in ["table", "text"]:
                # Save as CSV for table/text formats
                content = df.to_csv(index=False)
                content_type = "text/csv"
            elif output_format == "json":
                content = df.to_json(orient="records", indent=2)
                content_type = "application/json"
            elif output_format == "yaml":
                content = yaml.dump(df.to_dict("records"), default_flow_style=False)
                content_type = "text/yaml"
            elif output_format == "markdown":
                content = df.to_markdown(index=False)
                content_type = "text/markdown"
            else:
                content = df.to_csv(index=False)
                content_type = "text/csv"

            if self._is_s3_path(output):
                # Save to S3
                if s3_client is None:
                    s3_client = boto3.client("s3")

                output_parsed = urllib.parse.urlparse(output)
                s3_client.put_object(
                    Bucket=output_parsed.netloc,
                    Key=output_parsed.path.lstrip("/"),
                    Body=content.encode("utf-8"),
                    ContentType=content_type,
                )
            else:
                # Save to local file
                output_dir = os.path.dirname(output)
                if output_dir:
                    os.makedirs(output_dir, exist_ok=True)

                with open(output, "w", encoding="utf-8") as f:
                    f.write(content)

            print(f"[green]✅ Results saved to: {output}[/green]")

        except Exception as e:
            print(f"[red]❌ Error saving file: {e}[/red]")

    def _print_selection_table(self, selection_info: dict) -> None:
        """Print selection results in table format using Rich."""
        df = selection_info["data"]

        print("\n[bold cyan]📋 Data Selection Results[/bold cyan]\n")

        # Operations summary table
        if selection_info["operations"]:
            ops_table = Table(
                title="🔧 Operations Applied",
                show_header=True,
                header_style="bold cyan",
                box=box.SIMPLE,
                border_style="dim",
            )
            ops_table.add_column("Operation", style="green")

            for i, op in enumerate(selection_info["operations"], 1):
                ops_table.add_row(f"{i}. {op}")

            self.console.print(ops_table)
            print()

        # Summary table
        summary_table = Table(
            title="📊 Selection Summary",
            show_header=True,
            header_style="bold cyan",
            box=box.SIMPLE,
            border_style="dim",
        )
        summary_table.add_column("Metric", style="cyan", no_wrap=True)
        summary_table.add_column("Value", style="white")

        summary_table.add_row("Source File", selection_info["source_file"])
        summary_table.add_row("Original Rows", f"{selection_info['original_rows']:,}")
        summary_table.add_row(
            "Original Columns", str(selection_info["original_columns"])
        )
        summary_table.add_row("Final Rows", f"{selection_info['final_rows']:,}")
        summary_table.add_row("Final Columns", str(selection_info["final_columns"]))

        self.console.print(summary_table)

        # Data table
        print("\n[bold cyan]📋 Results Data:[/bold cyan]")

        # Limit display to 50 rows for readability
        display_df = df.head(50) if len(df) > 50 else df

        data_table = Table(
            show_header=True,
            header_style="bold cyan",
            box=box.SIMPLE,
            border_style="dim",
        )

        # Add columns
        for col in display_df.columns:
            data_table.add_column(str(col), overflow="fold")

        # Add rows
        for _, row in display_df.iterrows():
            data_table.add_row(*[str(value) for value in row.values])

        self.console.print(data_table)

        if len(df) > 50:
            print(f"\n[dim]... and {len(df) - 50:,} more rows[/dim]")

        print()

    def _print_selection_text(self, selection_info: dict) -> None:
        """Print selection results in text format."""
        df = selection_info["data"]

        print(f"Data Selection Results: {selection_info['source_file']}")
        print("=" * 60)

        if selection_info["operations"]:
            print("Operations Applied:")
            for i, op in enumerate(selection_info["operations"], 1):
                print(f"  {i}. {op}")
            print()

        print("Selection Summary:")
        print(f"  Source File: {selection_info['source_file']}")
        print(f"  Original Rows: {selection_info['original_rows']:,}")
        print(f"  Original Columns: {selection_info['original_columns']}")
        print(f"  Final Rows: {selection_info['final_rows']:,}")
        print(f"  Final Columns: {selection_info['final_columns']}")
        print()

        print("Results Data:")
        if len(df) > 50:
            print(f"Showing first 50 rows of {len(df):,} total rows:")
            display_df = df.head(50)
        else:
            display_df = df

        print(display_df.to_string(index=False))

        if len(df) > 50:
            print(f"\n... and {len(df) - 50:,} more rows")

    def _print_selection_markdown(self, selection_info: dict) -> None:
        """Print selection results in markdown format."""
        df = selection_info["data"]

        print(f"# Data Selection Results: {selection_info['source_file']}\n")

        if selection_info["operations"]:
            print("## Operations Applied\n")
            for i, op in enumerate(selection_info["operations"], 1):
                print(f"{i}. {op}")
            print()

        print("## Selection Summary\n")
        print(f"- **Source File:** {selection_info['source_file']}")
        print(f"- **Original Rows:** {selection_info['original_rows']:,}")
        print(f"- **Original Columns:** {selection_info['original_columns']}")
        print(f"- **Final Rows:** {selection_info['final_rows']:,}")
        print(f"- **Final Columns:** {selection_info['final_columns']}")
        print()

        print("## Results Data\n")

        if len(df) > 50:
            print(f"*Showing first 50 rows of {len(df):,} total rows*\n")
            display_df = df.head(50)
        else:
            display_df = df

        # Create markdown table
        if not display_df.empty:
            headers = list(display_df.columns)
            print(f"| {' | '.join(headers)} |")
            print(f"| {' | '.join(['---'] * len(headers))} |")
            for _, row in display_df.iterrows():
                values = [str(value) for value in row.values]
                print(f"| {' | '.join(values)} |")

        if len(df) > 50:
            print(f"\n*... and {len(df) - 50:,} more rows*")

    def convert_files(  # noqa: C901
        self,
        path: str,
        target_format: str,
        output: Optional[str] = None,
        recursive: bool = False,
        flatten: bool = False,
        columns: Optional[str] = None,
        overwrite: bool = False,
        output_format: str = "table",
    ) -> None:
        """Convert between Parquet, CSV, and JSON formats with support for S3 and local paths."""
        try:
            output_format = self._validate_output_format(output_format)
            target_format = target_format.lower()

            # Validate target format
            if target_format not in ["csv", "json", "parquet"]:
                error_msg = "Target format must be 'csv', 'json', or 'parquet'"
                if output_format == "table":
                    print(f"[red]❌ Error: {error_msg}[/red]")
                else:
                    print(f"Error: {error_msg}")
                return

            if output_format == "table":
                if self._is_s3_path(path):
                    print(f"[blue]🔍 Analyzing S3 path: {path}[/blue]")
                else:
                    path = os.path.abspath(path)
                    print(f"[blue]🔍 Analyzing local path: {path}[/blue]")

            # Get supported input extensions based on target format
            def get_supported_extensions(target_fmt):
                if target_fmt == "parquet":
                    return ["csv", "json"]
                elif target_fmt == "csv":
                    return ["parquet", "json"]
                elif target_fmt == "json":
                    return ["parquet", "csv"]
                else:
                    return ["parquet"]

            # Collect input files
            input_files = []
            supported_extensions = get_supported_extensions(target_format)

            # Initialize S3 client if needed
            s3_client = None
            if self._is_s3_path(path):
                try:
                    s3_client = boto3.client("s3")
                except Exception as e:
                    error_msg = f"Failed to initialize S3 client: {e}"
                    if output_format == "table":
                        print(f"[red]❌ Error: {error_msg}[/red]")
                    else:
                        print(f"Error: {error_msg}")
                    return

            # File discovery logic (simplified for brevity)
            input_files = self._discover_input_files(
                path, supported_extensions, recursive, s3_client, output_format
            )

            if not input_files:
                if output_format == "table":
                    print("[red]❌ No supported files found[/red]")
                    print(
                        f"[yellow]   Supported extensions: {', '.join(['.' + ext for ext in supported_extensions])}[/yellow]"
                    )
                else:
                    print("No supported files found")
                return

            if output_format == "table":
                print(f"[blue]📂 Found {len(input_files)} file(s) to convert[/blue]")

            # Process each file
            conversion_results = self._process_conversions(
                input_files,
                target_format,
                output,
                flatten,
                columns,
                overwrite,
                s3_client,
                output_format,
            )

            # Display results
            self._display_conversion_results(conversion_results, output_format)

        except Exception as e:
            error_msg = f"Conversion failed: {e}"
            if output_format == "table":
                print(f"[red]❌ Error: {error_msg}[/red]")
            else:
                print(f"Error: {error_msg}")

    def diff_files(  # noqa: C901
        self,
        expected_path: str,
        actual_path: str,
        columns: Optional[str] = None,
        output: Optional[str] = None,
        tolerance: Optional[float] = None,
        ignore_order: bool = False,
        sample_diff: int = 10,
        key_columns: Optional[str] = None,
        output_format: str = "table",
    ) -> None:
        """Compare two Parquet files and show detailed differences."""
        try:
            output_format = self._validate_output_format(output_format)

            if output_format == "table":
                print("[blue]🔍 Comparing files:[/blue]")
                print(f"  [cyan]Expected:[/cyan] {expected_path}")
                print(f"  [cyan]Actual:[/cyan] {actual_path}")

            # Validate both files
            is_valid_exp, error_exp, s3_client_exp = self._validate_parquet_file(
                expected_path
            )
            is_valid_act, error_act, s3_client_act = self._validate_parquet_file(
                actual_path
            )

            if not is_valid_exp:
                error_msg = f"Expected file error: {error_exp}"
                if output_format == "table":
                    print(f"[red]❌ {error_msg}[/red]")
                else:
                    print(f"Error: {error_msg}")
                return

            if not is_valid_act:
                error_msg = f"Actual file error: {error_act}"
                if output_format == "table":
                    print(f"[red]❌ {error_msg}[/red]")
                else:
                    print(f"Error: {error_msg}")
                return

            # Load both files
            if output_format == "table":
                print("\n[blue]📊 Loading data...[/blue]")

            try:
                df_expected = pd.read_parquet(expected_path)
                if output_format == "table":
                    print(
                        f"  [dim]Expected: {len(df_expected):,} rows, {len(df_expected.columns)} columns[/dim]"
                    )
            except Exception as e:
                error_msg = f"Error reading expected file: {e}"
                if output_format == "table":
                    print(f"[red]❌ {error_msg}[/red]")
                else:
                    print(f"Error: {error_msg}")
                return

            try:
                df_actual = pd.read_parquet(actual_path)
                if output_format == "table":
                    print(
                        f"  [dim]Actual: {len(df_actual):,} rows, {len(df_actual.columns)} columns[/dim]"
                    )
            except Exception as e:
                error_msg = f"Error reading actual file: {e}"
                if output_format == "table":
                    print(f"[red]❌ {error_msg}[/red]")
                else:
                    print(f"Error: {error_msg}")
                return

            # Perform comparison
            comparison_result = self._perform_file_comparison(
                df_expected,
                df_actual,
                columns,
                tolerance,
                ignore_order,
                sample_diff,
                key_columns,
                output_format,
            )

            # Save results if output specified
            if output and not comparison_result["identical"]:
                self._save_diff_results(
                    comparison_result, output, output_format, expected_path, actual_path
                )

            # Display results
            self._display_diff_results(comparison_result, output_format)

        except Exception as e:
            error_msg = f"Comparison failed: {e}"
            if output_format == "table":
                print(f"[red]❌ Error: {error_msg}[/red]")
            else:
                print(f"Error: {error_msg}")

    def _discover_input_files(
        self,
        path: str,
        supported_extensions: list,
        recursive: bool,
        s3_client=None,
        output_format: str = "table",
    ) -> list:
        """Discover input files based on path and options."""
        input_files = []

        def get_file_extension(file_path):
            return file_path.lower().split(".")[-1] if "." in file_path else ""

        if self._is_s3_path(path):
            # S3 path handling (simplified)
            parsed_url = urllib.parse.urlparse(path)
            bucket = parsed_url.netloc
            key = parsed_url.path.lstrip("/")

            try:
                # Try as single file first
                s3_client.head_object(Bucket=bucket, Key=key)
                file_ext = get_file_extension(path)
                if file_ext in supported_extensions:
                    input_files = [path]
                else:
                    if output_format == "table":
                        print(
                            f"[red]❌ Error: File must be one of: {', '.join(['.' + ext for ext in supported_extensions])}[/red]"
                        )
            except Exception:
                # Try as directory if recursive
                if recursive:
                    # List objects with prefix (simplified)
                    prefix = key if key.endswith("/") else f"{key}/"
                    paginator = s3_client.get_paginator("list_objects_v2")

                    for page in paginator.paginate(Bucket=bucket, Prefix=prefix):
                        if "Contents" in page:
                            for obj in page["Contents"]:
                                file_ext = get_file_extension(obj["Key"])
                                if file_ext in supported_extensions:
                                    input_files.append(f"s3://{bucket}/{obj['Key']}")
                else:
                    if output_format == "table":
                        print(
                            "[red]❌ Error: Use --recursive flag to process directories[/red]"
                        )
        else:
            # Local path handling
            from pathlib import Path

            if os.path.isfile(path):
                file_ext = get_file_extension(path)
                if file_ext in supported_extensions:
                    input_files = [path]
                else:
                    if output_format == "table":
                        print(
                            f"[red]❌ Error: File must be one of: {', '.join(['.' + ext for ext in supported_extensions])}[/red]"
                        )
            elif os.path.isdir(path):
                if not recursive:
                    if output_format == "table":
                        print(
                            "[red]❌ Error: Use --recursive flag to process directories[/red]"
                        )
                else:
                    path_obj = Path(path)
                    for ext in supported_extensions:
                        pattern = f"*.{ext}"
                        file_generator = (
                            path_obj.rglob(pattern)
                            if recursive
                            else path_obj.glob(pattern)
                        )
                        input_files.extend([str(f) for f in file_generator])
            else:
                if output_format == "table":
                    print(f"[red]❌ Error: Path not found: {path}[/red]")

        return input_files

    def _process_conversions(
        self,
        input_files: list,
        target_format: str,
        output: Optional[str],
        flatten: bool,
        columns: Optional[str],
        overwrite: bool,
        s3_client=None,
        output_format: str = "table",
    ) -> dict:
        """Process file conversions and return results."""
        results = {"successful": 0, "failed": 0, "conversions": [], "errors": []}

        for input_file in input_files:
            try:
                if output_format == "table":
                    print(f"[blue]🔄 Processing: {input_file}[/blue]")

                # Load file based on extension
                file_ext = (
                    input_file.lower().split(".")[-1] if "." in input_file else ""
                )

                if file_ext == "parquet":
                    df = pd.read_parquet(input_file)
                elif file_ext == "csv":
                    df = pd.read_csv(input_file)
                elif file_ext == "json":
                    df = pd.read_json(input_file)
                else:
                    results["errors"].append(f"Unsupported file type: {input_file}")
                    results["failed"] += 1
                    continue

                # Process columns if specified
                if columns:
                    selected_columns = [col.strip() for col in columns.split(",")]
                    missing_columns = [
                        col for col in selected_columns if col not in df.columns
                    ]
                    if missing_columns:
                        if output_format == "table":
                            print(
                                f"[yellow]⚠️ Warning: Columns not found in {input_file}: {missing_columns}[/yellow]"
                            )
                        selected_columns = [
                            col for col in selected_columns if col in df.columns
                        ]

                    if selected_columns:
                        df = df[selected_columns]
                    else:
                        results["errors"].append(
                            f"No valid columns found for {input_file}"
                        )
                        results["failed"] += 1
                        continue

                # Flatten if requested
                if flatten:
                    df = pd.json_normalize(df.to_dict("records"))

                # Determine output path
                output_path = self._determine_output_path(
                    input_file, target_format, output, len(input_files)
                )

                # Check if output exists
                if not overwrite and self._output_exists(output_path, s3_client):
                    if output_format == "table":
                        print(
                            f"[yellow]⚠️ Output file exists: {output_path}. Use --overwrite to replace.[/yellow]"
                        )
                    continue

                # Save file
                self._save_converted_file(df, output_path, target_format, s3_client)

                # Get file size for confirmation
                file_size = self._get_file_size(output_path, s3_client)
                size_str = self._format_file_size(file_size)

                conversion_info = {
                    "input": input_file,
                    "output": output_path,
                    "size": size_str,
                    "rows": len(df),
                    "columns": len(df.columns),
                }
                results["conversions"].append(conversion_info)

                if output_format == "table":
                    print(
                        f"[green]✅ Converted: {input_file} -> {output_path} ({size_str})[/green]"
                    )
                    print(f"   [dim]Rows: {len(df)}, Columns: {len(df.columns)}[/dim]")

                results["successful"] += 1

            except Exception as e:
                error_msg = f"Error processing {input_file}: {e}"
                results["errors"].append(error_msg)
                results["failed"] += 1
                if output_format == "table":
                    print(f"[red]❌ {error_msg}[/red]")

        return results

    def _perform_file_comparison(
        self,
        df_expected: pd.DataFrame,
        df_actual: pd.DataFrame,
        columns: Optional[str],
        tolerance: Optional[float],
        ignore_order: bool,
        sample_diff: int,
        key_columns: Optional[str],
        output_format: str,
    ) -> dict:
        """Perform detailed file comparison and return results."""
        result = {
            "identical": True,
            "schema_differences": {},
            "row_count_difference": 0,
            "data_differences": [],
            "summary": {},
        }

        # Filter columns if specified
        if columns:
            selected_columns = [col.strip() for col in columns.split(",")]

            # Validate columns exist
            missing_expected = [
                col for col in selected_columns if col not in df_expected.columns
            ]
            missing_actual = [
                col for col in selected_columns if col not in df_actual.columns
            ]

            if missing_expected or missing_actual:
                error_msg = "Column validation failed"
                if missing_expected:
                    error_msg += f" - Missing in expected: {missing_expected}"
                if missing_actual:
                    error_msg += f" - Missing in actual: {missing_actual}"
                raise ValueError(error_msg)

            df_expected = df_expected[selected_columns]
            df_actual = df_actual[selected_columns]

            if output_format == "table":
                print(
                    f"  [dim]Comparing {len(selected_columns)} selected columns[/dim]"
                )

        # Schema comparison
        schema_diff = self._compare_schemas(df_expected, df_actual, output_format)
        result["schema_differences"] = schema_diff
        if not schema_diff["columns_match"] or schema_diff["dtype_differences"]:
            result["identical"] = False

        # Row count comparison
        row_diff = len(df_actual) - len(df_expected)
        result["row_count_difference"] = row_diff
        if row_diff != 0:
            result["identical"] = False

        # Data comparison
        if not df_expected.empty and not df_actual.empty:
            data_diff = self._compare_data(
                df_expected,
                df_actual,
                tolerance,
                ignore_order,
                key_columns,
                sample_diff,
                output_format,
            )
            result["data_differences"] = data_diff
            if data_diff:
                result["identical"] = False

        result["summary"] = {
            "files_identical": result["identical"],
            "total_differences": len(result["data_differences"]),
            "tolerance_used": tolerance,
            "order_ignored": ignore_order,
        }

        return result

    def _compare_schemas(
        self, df_expected: pd.DataFrame, df_actual: pd.DataFrame, output_format: str
    ) -> dict:
        """Compare schemas of two dataframes."""
        if output_format == "table":
            print("\n[cyan]📋 Schema Comparison:[/cyan]")

        expected_cols = set(df_expected.columns)
        actual_cols = set(df_actual.columns)

        schema_result = {
            "columns_match": expected_cols == actual_cols,
            "missing_in_actual": list(expected_cols - actual_cols),
            "extra_in_actual": list(actual_cols - expected_cols),
            "dtype_differences": [],
        }

        if schema_result["columns_match"]:
            if output_format == "table":
                print("  [green]✅ Column names match[/green]")
        else:
            if output_format == "table":
                if schema_result["missing_in_actual"]:
                    print(
                        f"  [red]❌ Columns missing in actual: {schema_result['missing_in_actual']}[/red]"
                    )
                if schema_result["extra_in_actual"]:
                    print(
                        f"  [red]❌ Extra columns in actual: {schema_result['extra_in_actual']}[/red]"
                    )

        # Check data types for common columns
        common_cols = expected_cols & actual_cols
        if common_cols:
            dtype_diffs = []
            for col in common_cols:
                if str(df_expected[col].dtype) != str(df_actual[col].dtype):
                    diff_info = {
                        "column": col,
                        "expected_type": str(df_expected[col].dtype),
                        "actual_type": str(df_actual[col].dtype),
                    }
                    dtype_diffs.append(diff_info)

            schema_result["dtype_differences"] = dtype_diffs

            if dtype_diffs:
                if output_format == "table":
                    print("  [red]❌ Data type differences:[/red]")
                    for diff in dtype_diffs:
                        print(
                            f"    [yellow]{diff['column']}: {diff['expected_type']} vs {diff['actual_type']}[/yellow]"
                        )
            else:
                if output_format == "table":
                    print("  [green]✅ Data types match for common columns[/green]")

        return schema_result

    def _compare_data(
        self,
        df_expected: pd.DataFrame,
        df_actual: pd.DataFrame,
        tolerance: Optional[float],
        ignore_order: bool,
        key_columns: Optional[str],
        sample_diff: int,
        output_format: str,
    ) -> list:
        """Compare data content of two dataframes."""
        if output_format == "table":
            print("\n[cyan]🔍 Data Comparison:[/cyan]")

        # Handle row ordering
        df_exp_compare = df_expected.copy()
        df_act_compare = df_actual.copy()

        if ignore_order:
            if output_format == "table":
                print(
                    "  [blue]🔄 Sorting rows for order-independent comparison...[/blue]"
                )

            if key_columns:
                key_cols = [col.strip() for col in key_columns.split(",")]
                missing_keys = [
                    col
                    for col in key_cols
                    if col not in df_exp_compare.columns
                    or col not in df_act_compare.columns
                ]
                if missing_keys:
                    raise ValueError(f"Key columns not found: {missing_keys}")

                df_exp_compare = df_exp_compare.sort_values(key_cols).reset_index(
                    drop=True
                )
                df_act_compare = df_act_compare.sort_values(key_cols).reset_index(
                    drop=True
                )
            else:
                # Sort by all columns
                common_cols = list(
                    set(df_exp_compare.columns) & set(df_act_compare.columns)
                )
                df_exp_compare = df_exp_compare.sort_values(common_cols).reset_index(
                    drop=True
                )
                df_act_compare = df_act_compare.sort_values(common_cols).reset_index(
                    drop=True
                )

        # Find differences
        min_rows = min(len(df_exp_compare), len(df_act_compare))
        differences = []

        if min_rows > 0:
            df_exp_subset = df_exp_compare.head(min_rows)
            df_act_subset = df_act_compare.head(min_rows)

            for idx in range(min_rows):
                row_diffs = {}

                for col in df_exp_subset.columns:
                    if col not in df_act_subset.columns:
                        continue

                    exp_val = df_exp_subset.iloc[idx][col]
                    act_val = df_act_subset.iloc[idx][col]

                    if pd.isna(exp_val) and pd.isna(act_val):
                        continue
                    elif pd.isna(exp_val) or pd.isna(act_val):
                        row_diffs[col] = {"expected": exp_val, "actual": act_val}
                    elif tolerance is not None and pd.api.types.is_numeric_dtype(
                        df_exp_subset[col]
                    ):
                        try:
                            if abs(float(exp_val) - float(act_val)) > tolerance:
                                row_diffs[col] = {
                                    "expected": exp_val,
                                    "actual": act_val,
                                }
                        except (ValueError, TypeError):
                            if exp_val != act_val:
                                row_diffs[col] = {
                                    "expected": exp_val,
                                    "actual": act_val,
                                }
                    else:
                        if exp_val != act_val:
                            row_diffs[col] = {"expected": exp_val, "actual": act_val}

                if row_diffs:
                    differences.append({"row_index": idx, "differences": row_diffs})

        # Display comparison results
        if differences:
            if output_format == "table":
                print(
                    f"  [red]❌ Data differences found: {len(differences)} different rows[/red]"
                )
                if tolerance is not None:
                    print(f"    [dim](using tolerance: {tolerance})[/dim]")
        else:
            if output_format == "table":
                print("  [green]✅ Data content matches[/green]")

        return differences[:sample_diff] if differences else []

    def _display_conversion_results(self, results: dict, output_format: str) -> None:
        """Display conversion results in the specified format."""
        if output_format == "table":
            print("\n[cyan]📊 Conversion Summary:[/cyan]")
            print(f"  [green]✅ Successful: {results['successful']}[/green]")
            if results["failed"] > 0:
                print(f"  [red]❌ Failed: {results['failed']}[/red]")
        elif output_format in ["json", "yaml"]:
            if output_format == "json":
                print(json.dumps(results, indent=2, default=str))
            else:
                print(yaml.dump(results, default_flow_style=False))
        else:
            print("Conversion Summary:")
            print(f"  Successful: {results['successful']}")
            if results["failed"] > 0:
                print(f"  Failed: {results['failed']}")

    def _display_diff_results(self, result: dict, output_format: str) -> None:
        """Display comparison results in the specified format."""
        if output_format == "table":
            print("\n[cyan]📊 Comparison Summary:[/cyan]")
            if result["identical"]:
                print("  [green]✅ Files are identical[/green]")
            else:
                print("  [red]❌ Files are different[/red]")

                # Show sample differences
                if result["data_differences"]:
                    print(
                        f"\n[yellow]📝 Sample Differences (showing first {len(result['data_differences'])}):[/yellow]"
                    )
                    for diff_row in result["data_differences"]:
                        print(f"\n  [bold]Row {diff_row['row_index']}:[/bold]")
                        for col, diff_detail in diff_row["differences"].items():
                            print(
                                f"    [cyan]{col}:[/cyan] {diff_detail['expected']} vs {diff_detail['actual']}"
                            )

                if not result["identical"]:
                    print(
                        "\n[dim]💡 Tip: Use --ignore-order to ignore row ordering[/dim]"
                    )
                    print(
                        "[dim]💡 Tip: Use --tolerance for numerical comparisons[/dim]"
                    )
                    print("[dim]💡 Tip: Use --key-columns to specify sort keys[/dim]")
        elif output_format in ["json", "yaml"]:
            if output_format == "json":
                print(json.dumps(result, indent=2, default=str))
            else:
                print(yaml.dump(result, default_flow_style=False))
        else:
            print("Comparison Summary:")
            if result["identical"]:
                print("  Files are identical")
            else:
                print("  Files are different")

    def _determine_output_path(
        self,
        input_file: str,
        target_format: str,
        output: Optional[str],
        total_files: int,
    ) -> str:
        """Determine the output path for a converted file."""
        if output:
            if self._is_s3_path(output) or output.startswith("/") or total_files == 1:
                output_path = output
                if not output_path.endswith(f".{target_format}"):
                    output_path = f"{output_path}.{target_format}"
            else:
                filename = os.path.basename(input_file)
                if "." in filename:
                    filename = ".".join(filename.split(".")[:-1]) + f".{target_format}"
                else:
                    filename = f"{filename}.{target_format}"
                output_path = os.path.join(output, filename)
        else:
            if "." in input_file:
                output_path = ".".join(input_file.split(".")[:-1]) + f".{target_format}"
            else:
                output_path = f"{input_file}.{target_format}"

        return output_path

    def _output_exists(self, output_path: str, s3_client=None) -> bool:
        """Check if output file already exists."""
        if self._is_s3_path(output_path):
            if s3_client is None:
                s3_client = boto3.client("s3")
            try:
                output_parsed = urllib.parse.urlparse(output_path)
                s3_client.head_object(
                    Bucket=output_parsed.netloc, Key=output_parsed.path.lstrip("/")
                )
                return True
            except Exception:
                return False
        else:
            return os.path.exists(output_path)

    def _save_converted_file(
        self, df: pd.DataFrame, output_path: str, target_format: str, s3_client=None
    ) -> None:
        """Save converted dataframe to file."""
        if not self._is_s3_path(output_path):
            output_dir = os.path.dirname(output_path)
            if output_dir:
                os.makedirs(output_dir, exist_ok=True)

        if target_format == "csv":
            if self._is_s3_path(output_path):
                if s3_client is None:
                    s3_client = boto3.client("s3")
                csv_buffer = io.StringIO()
                df.to_csv(csv_buffer, index=False)
                output_parsed = urllib.parse.urlparse(output_path)
                s3_client.put_object(
                    Bucket=output_parsed.netloc,
                    Key=output_parsed.path.lstrip("/"),
                    Body=csv_buffer.getvalue().encode("utf-8"),
                    ContentType="text/csv",
                )
            else:
                df.to_csv(output_path, index=False)
        elif target_format == "json":
            if self._is_s3_path(output_path):
                if s3_client is None:
                    s3_client = boto3.client("s3")
                json_content = df.to_json(orient="records", indent=2)
                output_parsed = urllib.parse.urlparse(output_path)
                s3_client.put_object(
                    Bucket=output_parsed.netloc,
                    Key=output_parsed.path.lstrip("/"),
                    Body=json_content.encode("utf-8"),
                    ContentType="application/json",
                )
            else:
                df.to_json(output_path, orient="records", indent=2)
        elif target_format == "parquet":
            df.to_parquet(output_path, index=False)

    def _get_file_size(self, file_path: str, s3_client=None) -> int:
        """Get file size in bytes."""
        if self._is_s3_path(file_path):
            if s3_client is None:
                s3_client = boto3.client("s3")
            try:
                output_parsed = urllib.parse.urlparse(file_path)
                response = s3_client.head_object(
                    Bucket=output_parsed.netloc, Key=output_parsed.path.lstrip("/")
                )
                return response["ContentLength"]
            except Exception:
                return 0
        else:
            try:
                return os.path.getsize(file_path)
            except Exception:
                return 0

    def _save_diff_results(
        self,
        result: dict,
        output_path: str,
        output_format: str,
        expected_path: str,
        actual_path: str,
    ) -> None:
        """Save comparison results to file."""
        print(f"[blue]💾 Saving differences to: {output_path}[/blue]")

        try:
            diff_summary = {
                "comparison_timestamp": pd.Timestamp.now().isoformat(),
                "expected_file": expected_path,
                "actual_file": actual_path,
                "files_identical": result["identical"],
                "schema_differences": result["schema_differences"],
                "row_count_difference": result["row_count_difference"],
                "data_differences_count": len(result["data_differences"]),
                "sample_differences": result["data_differences"],
                "summary": result["summary"],
            }

            if self._is_s3_path(output_path):
                s3_client = boto3.client("s3")
                content = json.dumps(diff_summary, indent=2, default=str)
                output_parsed = urllib.parse.urlparse(output_path)
                s3_client.put_object(
                    Bucket=output_parsed.netloc,
                    Key=output_parsed.path.lstrip("/"),
                    Body=content.encode("utf-8"),
                    ContentType="application/json",
                )
            else:
                output_dir = os.path.dirname(output_path)
                if output_dir:
                    os.makedirs(output_dir, exist_ok=True)

                with open(output_path, "w", encoding="utf-8") as f:
                    json.dump(diff_summary, f, indent=2, default=str)

            print(f"[green]✅ Differences saved to: {output_path}[/green]")

        except Exception as e:
            print(f"[red]❌ Error saving results: {e}[/red]")
