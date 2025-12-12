"""Notebook service for managing Jupyter notebooks with local and S3 support."""

import os


class NotebookService:
    """Service class for managing notebook operations including S3 integration."""

    def __init__(self):
        """Initialize the NotebookService with default paths and configurations."""
        self.home_directory = os.path.dirname(
            os.path.dirname(os.path.abspath(__file__))
        )
        self.current_directory = os.getcwd()
        self.notebooks_folder = "notebooks"
        self.source_stub = os.path.join(
            self.home_directory, "stubs", "notebook", "setup.stub"
        )
        self.template_stub = os.path.join(
            self.home_directory, "stubs", "notebook", "template.stub"
        )
        self.notebooks_path = os.path.join(
            self.current_directory, self.notebooks_folder
        )
        self.setup_file_path = os.path.join(self.notebooks_path, "setup.py")
        self.init_file_path = os.path.join(self.notebooks_path, "__init__.py")

    def init_notebooks(self):
        """Initialize notebooks folder and create setup.py file."""
        # Create notebooks folder if it doesn't exist
        if not os.path.exists(self.notebooks_path):
            try:
                os.makedirs(self.notebooks_path)
                print(f"Created '{self.notebooks_folder}' folder.")
            except OSError as e:
                print(f"Error creating notebooks directory: {e}")
                return
        else:
            print(f"'{self.notebooks_folder}' folder already exists.")

        # Create setup.py file if it doesn't exist
        if not os.path.exists(self.setup_file_path):
            try:
                with open(self.source_stub, "r") as source_file:
                    setup_stub_content = source_file.read()
            except FileNotFoundError:
                print(f"Stub file '{self.source_stub}' not found.")
                return
            except Exception as e:
                print(f"An error occurred while reading the stub file: {e}")
                return

            try:
                with open(self.setup_file_path, "w") as destination_file:
                    destination_file.write(setup_stub_content)
                print(f"File '{self.setup_file_path}' created successfully.")
            except Exception as e:
                print(f"An error occurred while writing the setup.py file: {e}")
        else:
            print(f"File '{self.setup_file_path}' already exists. Skipping creation.")

        # Create __init__.py file if it doesn't exist
        if not os.path.exists(self.init_file_path):
            init_content = '"""Notebooks package for the Spartan Framework."""\n'
            try:
                with open(self.init_file_path, "w") as init_file:
                    init_file.write(init_content)
                print(f"File '{self.init_file_path}' created successfully.")
            except Exception as e:
                print(f"An error occurred while writing the __init__.py file: {e}")
        else:
            print(f"File '{self.init_file_path}' already exists. Skipping creation.")

    def create_notebook(self, notebook_name: str):
        """Create a new notebook file using the template stub."""
        # Ensure notebooks folder exists
        if not os.path.exists(self.notebooks_path):
            print(
                "Notebooks folder doesn't exist. Please run 'spartan notebook init' first."
            )
            return

        # Ensure setup.py and __init__.py exist
        missing_files = []
        if not os.path.exists(self.setup_file_path):
            missing_files.append("setup.py")
        if not os.path.exists(self.init_file_path):
            missing_files.append("__init__.py")

        if missing_files:
            print(f"Missing required files: {', '.join(missing_files)}")
            print(
                "Please run 'spartan notebook init' first to initialize the notebooks environment."
            )
            return

        # Clean the notebook name and add .ipynb extension
        clean_name = notebook_name.replace(" ", "_").lower()
        if not clean_name.endswith(".ipynb"):
            clean_name += ".ipynb"

        notebook_path = os.path.join(self.notebooks_path, clean_name)

        # Check if notebook already exists
        if os.path.exists(notebook_path):
            print(f"Notebook '{clean_name}' already exists. Skipping creation.")
            return

        # Read the template stub
        try:
            with open(self.template_stub, "r") as template_file:
                template_content = template_file.read()
        except FileNotFoundError:
            print(f"Template stub file '{self.template_stub}' not found.")
            return
        except Exception as e:
            print(f"An error occurred while reading the template stub: {e}")
            return

        # Create the notebook file
        try:
            with open(notebook_path, "w") as notebook_file:
                notebook_file.write(template_content)
            print(f"Notebook '{clean_name}' created successfully at '{notebook_path}'.")
        except Exception as e:
            print(f"An error occurred while creating the notebook: {e}")

    def list_notebooks(self, path: str = "."):
        """List notebook files from local directory or S3 bucket.

        Args:
            path: Path to list notebooks from. Can be:
                - "." for current notebooks folder (default)
                - Local directory path
                - S3 bucket path (must end with '/' and not be a file)
        """
        # Check if it's an S3 path
        if path.startswith("s3://"):
            self._list_notebooks_s3(path)
        else:
            self._list_notebooks_local(path)

    def _list_notebooks_local(self, path: str = "."):
        r"""List all notebook files (\*.ipynb) in a local directory."""
        # Determine the target directory
        if path == ".":
            target_path = self.notebooks_path
            display_path = "notebooks folder"
        else:
            target_path = os.path.abspath(path)
            display_path = f"directory '{target_path}'"

        # Check if target path exists
        if not os.path.exists(target_path):
            if path == ".":
                print(
                    "Notebooks folder doesn't exist. Please run 'spartan notebook init' first."
                )
            else:
                print(f"Directory '{target_path}' doesn't exist.")
            return

        # Check if target path is actually a directory
        if not os.path.isdir(target_path):
            print(f"'{target_path}' is not a directory.")
            return

        try:
            # Get all files in the target directory
            all_files = os.listdir(target_path)

            # Filter for .ipynb files
            notebook_files = [f for f in all_files if f.endswith(".ipynb")]

            if not notebook_files:
                print(f"No notebook files found in the {display_path}.")
                if path == ".":
                    print("Use 'spartan note create <name>' to create a new notebook.")
                return

            # Sort the files for consistent output
            notebook_files.sort()

            print(f"Found {len(notebook_files)} notebook(s) in the {display_path}:")
            print()
            for i, notebook in enumerate(notebook_files, 1):
                # Get file size and modification time for additional info
                notebook_path = os.path.join(target_path, notebook)
                try:
                    stat_info = os.stat(notebook_path)
                    file_size = stat_info.st_size

                    # Format file size
                    if file_size < 1024:
                        size_str = f"{file_size} B"
                    elif file_size < 1024 * 1024:
                        size_str = f"{file_size / 1024:.1f} KB"
                    else:
                        size_str = f"{file_size / (1024 * 1024):.1f} MB"

                    print(f"  {i}. {notebook} ({size_str})")
                except OSError:
                    # If we can't get file stats, just show the name
                    print(f"  {i}. {notebook}")

        except PermissionError:
            print(f"Permission denied: Cannot access the {display_path}.")
        except Exception as e:
            print(f"An error occurred while listing notebooks: {e}")

    def _list_notebooks_s3(self, s3_path: str):
        """List notebook files from S3 bucket."""
        # Validate S3 path format
        if not s3_path.startswith("s3://"):
            print("Error: S3 path must start with 's3://'")
            return

        # Ensure path ends with '/' (must be a folder, not a file)
        if not s3_path.endswith("/"):
            print("Error: S3 path must end with '/' to indicate a folder")
            return

        # Parse bucket and prefix from S3 path
        try:
            # Remove s3:// prefix
            path_without_protocol = s3_path[5:]

            if "/" not in path_without_protocol:
                print(
                    "Error: Invalid S3 path format. Expected: s3://bucket-name/folder/"
                )
                return

            bucket_name = path_without_protocol.split("/")[0]
            prefix = "/".join(path_without_protocol.split("/")[1:])

            if not bucket_name:
                print("Error: Bucket name cannot be empty")
                return

        except Exception as e:
            print(f"Error: Invalid S3 path format: {e}")
            return

        try:
            import boto3
            from botocore.exceptions import ClientError, NoCredentialsError

            # Initialize S3 client
            s3_client = boto3.client("s3")

            # Check if bucket exists
            try:
                s3_client.head_bucket(Bucket=bucket_name)
            except ClientError as e:
                error_code = e.response["Error"]["Code"]
                if error_code == "404":
                    print(f"Error: S3 bucket '{bucket_name}' does not exist")
                elif error_code == "403":
                    print(
                        f"Error: Access denied to S3 bucket '{bucket_name}'. Check your permissions."
                    )
                else:
                    print(f"Error: Failed to access S3 bucket '{bucket_name}': {e}")
                return
            except NoCredentialsError:
                print(
                    "Error: AWS credentials not found. Please configure your AWS credentials."
                )
                return

            # List objects in the bucket with the given prefix
            try:
                response = s3_client.list_objects_v2(
                    Bucket=bucket_name, Prefix=prefix, Delimiter="/"
                )

                # Collect notebook files
                notebook_files = []

                if "Contents" in response:
                    for obj in response["Contents"]:
                        key = obj["Key"]
                        # Only include files that end with .ipynb and are not directories
                        if key.endswith(".ipynb") and not key.endswith("/"):
                            # Get just the filename (not the full path)
                            filename = key.split("/")[-1]
                            file_size = obj["Size"]
                            last_modified = obj["LastModified"]
                            notebook_files.append(
                                {
                                    "name": filename,
                                    "key": key,
                                    "size": file_size,
                                    "modified": last_modified,
                                }
                            )

                if not notebook_files:
                    print(f"No notebook files found in S3 path: {s3_path}")
                    return

                # Sort by name
                notebook_files.sort(key=lambda x: x["name"])

                print(f"Found {len(notebook_files)} notebook(s) in S3 path: {s3_path}")
                print()

                for i, notebook in enumerate(notebook_files, 1):
                    # Format file size
                    file_size = notebook["size"]
                    if file_size < 1024:
                        size_str = f"{file_size} B"
                    elif file_size < 1024 * 1024:
                        size_str = f"{file_size / 1024:.1f} KB"
                    else:
                        size_str = f"{file_size / (1024 * 1024):.1f} MB"

                    # Format date
                    modified_str = notebook["modified"].strftime("%Y-%m-%d %H:%M:%S")

                    print(f"  {i}. {notebook['name']} ({size_str}) - {modified_str}")

            except ClientError as e:
                print(f"Error: Failed to list objects in S3 bucket: {e}")
            except Exception as e:
                print(f"Error: An unexpected error occurred: {e}")

        except ImportError:
            print(
                "Error: boto3 library is required for S3 operations. Please install it with: pip install boto3"
            )
        except NoCredentialsError:
            print(
                "Error: AWS credentials not found. Please configure your AWS credentials."
            )
        except Exception as e:
            print(f"Error: Failed to access S3: {e}")

    def upload_notebooks(self, local_path: str, s3_path: str):
        """Upload notebook files to S3."""
        import glob

        import boto3
        from botocore.exceptions import ClientError, NoCredentialsError

        # Validate S3 path format
        if not s3_path.startswith("s3://"):
            print("Error: S3 path must start with 's3://'")
            return

        # Parse S3 path
        try:
            s3_parts = s3_path.replace("s3://", "").split("/", 1)
            bucket = s3_parts[0]
            prefix = s3_parts[1] if len(s3_parts) > 1 else ""
        except Exception:
            print("Error: Invalid S3 path format. Use: s3://bucket/prefix/")
            return

        # Check if notebooks folder exists
        if not os.path.exists(self.notebooks_path):
            print(
                "Notebooks folder doesn't exist. Please run 'spartan notebook init' first."
            )
            return

        # Resolve local path
        if local_path.startswith("notebooks/") or local_path == "notebooks":
            # Relative to current directory
            full_local_path = os.path.join(self.current_directory, local_path)
        elif local_path.startswith("/"):
            # Absolute path
            full_local_path = local_path
        else:
            # Assume it's relative to notebooks folder
            full_local_path = os.path.join(self.notebooks_path, local_path)

        # Check if local path exists
        if not os.path.exists(full_local_path):
            print(f"Error: Local path '{full_local_path}' does not exist.")
            return

        try:
            # Initialize S3 client
            s3_client = boto3.client("s3")

            # Test S3 connection and bucket access
            try:
                s3_client.head_bucket(Bucket=bucket)
            except ClientError as e:
                error_code = e.response["Error"]["Code"]
                if error_code == "404":
                    print(f"Error: S3 bucket '{bucket}' does not exist.")
                elif error_code == "403":
                    print(
                        f"Error: Access denied to S3 bucket '{bucket}'. Check your permissions."
                    )
                else:
                    print(f"Error: Cannot access S3 bucket '{bucket}': {e}")
                return

            uploaded_files = []

            if os.path.isfile(full_local_path):
                # Upload single file
                if not full_local_path.endswith(".ipynb"):
                    print(
                        "Warning: File is not a notebook (.ipynb). Uploading anyway..."
                    )

                file_name = os.path.basename(full_local_path)
                s3_key = f"{prefix.rstrip('/')}/{file_name}" if prefix else file_name

                print(f"Uploading '{full_local_path}' to 's3://{bucket}/{s3_key}'...")
                s3_client.upload_file(full_local_path, bucket, s3_key)
                uploaded_files.append(s3_key)

            elif os.path.isdir(full_local_path):
                # Upload directory recursively
                # Find all .ipynb files in the directory
                pattern = os.path.join(full_local_path, "**", "*.ipynb")
                notebook_files = glob.glob(pattern, recursive=True)

                if not notebook_files:
                    print(f"No notebook files (.ipynb) found in '{full_local_path}'.")
                    return

                print(f"Found {len(notebook_files)} notebook file(s) to upload...")

                for notebook_file in notebook_files:
                    # Calculate relative path from the base directory
                    rel_path = os.path.relpath(notebook_file, full_local_path)
                    s3_key = f"{prefix.rstrip('/')}/{rel_path}" if prefix else rel_path
                    s3_key = s3_key.replace("\\", "/")  # Handle Windows paths

                    print(
                        f"  Uploading '{notebook_file}' to 's3://{bucket}/{s3_key}'..."
                    )
                    s3_client.upload_file(notebook_file, bucket, s3_key)
                    uploaded_files.append(s3_key)

            print(f"\nSuccessfully uploaded {len(uploaded_files)} file(s) to S3:")
            for s3_key in uploaded_files:
                print(f"  s3://{bucket}/{s3_key}")

        except NoCredentialsError:
            print(
                "Error: AWS credentials not found. Please configure your AWS credentials."
            )
        except ClientError as e:
            print(f"Error: AWS S3 operation failed: {e}")
        except Exception as e:
            print(f"Error: An unexpected error occurred during upload: {e}")

    def download_notebooks(self, s3_path, recursive=False):
        """Download notebooks from S3 to the local notebooks folder.

        Args:
            s3_path (str): S3 path in format s3://bucket/prefix/ or s3://bucket/key
            recursive (bool): If True, download all files recursively from the S3 prefix
        """
        # Validate S3 path format
        if not s3_path.startswith("s3://"):
            print("Error: S3 path must start with 's3://'")
            return

        # Parse S3 path
        s3_parts = s3_path.replace("s3://", "").split("/", 1)
        if not s3_parts[0]:
            print("Error: Invalid S3 path format. Expected format: s3://bucket/prefix/")
            return

        bucket = s3_parts[0]
        prefix = s3_parts[1] if len(s3_parts) > 1 else ""

        # Check if notebooks folder exists
        if not os.path.exists(self.notebooks_path):
            print(
                "Notebooks folder doesn't exist. Please run 'spartan notebook init' first."
            )
            return

        if not os.path.isdir(self.notebooks_path):
            print(f"Error: '{self.notebooks_path}' is not a directory.")
            return

        # For non-recursive downloads, validate that we have a filename
        if not recursive and not prefix.strip():
            print("Error: S3 path must include a file name for single file download.")
            return

        try:
            import boto3
            from botocore.exceptions import ClientError, NoCredentialsError
        except ImportError:
            print(
                "Error: boto3 is required for S3 operations. Install it with: pip install boto3"
            )
            return

        try:
            # Initialize S3 client
            s3_client = boto3.client("s3")

            # Test S3 connection and bucket access
            try:
                s3_client.head_bucket(Bucket=bucket)
            except ClientError as e:
                error_code = e.response["Error"]["Code"]
                if error_code == "404":
                    print(f"Error: S3 bucket '{bucket}' does not exist.")
                elif error_code == "403":
                    print(
                        f"Error: Access denied to S3 bucket '{bucket}'. Check your permissions."
                    )
                else:
                    print(f"Error: Cannot access S3 bucket '{bucket}': {e}")
                return

            downloaded_files = []

            if recursive:
                # Download all files with the given prefix
                print(f"Downloading files recursively from 's3://{bucket}/{prefix}'...")

                # List all objects with the prefix
                try:
                    paginator = s3_client.get_paginator("list_objects_v2")
                    pages = paginator.paginate(Bucket=bucket, Prefix=prefix)

                    objects_found = False
                    for page in pages:
                        if "Contents" in page:
                            objects_found = True
                            for obj in page["Contents"]:
                                s3_key = obj["Key"]

                                # Skip directories (keys ending with /)
                                if s3_key.endswith("/"):
                                    continue

                                # Only download .ipynb files for notebooks
                                if not s3_key.endswith(".ipynb"):
                                    print(f"  Skipping non-notebook file: {s3_key}")
                                    continue

                                # Calculate local file path
                                # Remove the prefix from the key to get relative path
                                if prefix and s3_key.startswith(prefix):
                                    rel_path = s3_key[len(prefix) :].lstrip("/")
                                else:
                                    rel_path = s3_key

                                local_file_path = os.path.join(
                                    self.notebooks_path, rel_path
                                )

                                # Create local directories if needed
                                local_dir = os.path.dirname(local_file_path)
                                if local_dir and not os.path.exists(local_dir):
                                    os.makedirs(local_dir)

                                # Check if file already exists
                                if os.path.exists(local_file_path):
                                    print(
                                        f"  File '{rel_path}' already exists. Overwriting..."
                                    )

                                print(
                                    f"  Downloading 's3://{bucket}/{s3_key}' to '{local_file_path}'..."
                                )
                                s3_client.download_file(bucket, s3_key, local_file_path)
                                downloaded_files.append(rel_path)

                    if not objects_found:
                        print(f"No objects found at 's3://{bucket}/{prefix}'")
                        return

                except ClientError as e:
                    print(f"Error listing objects in S3: {e}")
                    return
            else:
                # Download single file
                # Check if the S3 path points to a specific file or needs .ipynb extension
                s3_key = prefix

                # If the key doesn't end with .ipynb, try adding it
                if not s3_key.endswith(".ipynb"):
                    test_key = f"{s3_key}.ipynb"
                    try:
                        s3_client.head_object(Bucket=bucket, Key=test_key)
                        s3_key = test_key
                        print(f"Found notebook at 's3://{bucket}/{s3_key}'")
                    except ClientError:
                        # Original key might be correct, try it
                        try:
                            s3_client.head_object(Bucket=bucket, Key=s3_key)
                        except ClientError:
                            print(
                                f"Error: File not found at 's3://{bucket}/{s3_key}' or 's3://{bucket}/{test_key}'"
                            )
                            print("No files were downloaded.")
                            return
                else:
                    # File already ends with .ipynb, check if it exists
                    try:
                        s3_client.head_object(Bucket=bucket, Key=s3_key)
                    except ClientError:
                        print(f"Error: File not found at 's3://{bucket}/{s3_key}'")
                        print("No files were downloaded.")
                        return

                # Get just the filename for local storage
                filename = os.path.basename(s3_key)
                local_file_path = os.path.join(self.notebooks_path, filename)

                # Check if file already exists locally
                if os.path.exists(local_file_path):
                    print(
                        f"File '{filename}' already exists in notebooks folder. Overwriting..."
                    )

                print(f"Downloading 's3://{bucket}/{s3_key}' to '{local_file_path}'...")
                try:
                    s3_client.download_file(bucket, s3_key, local_file_path)
                    downloaded_files.append(filename)
                except ClientError as e:
                    print(f"Error: Failed to download file: {e}")
                    print("No files were downloaded.")
                    return
                except Exception as e:
                    print(
                        f"Error: An unexpected error occurred during file download: {e}"
                    )
                    print("No files were downloaded.")
                    return

            if downloaded_files:
                print(f"\nSuccessfully downloaded {len(downloaded_files)} file(s):")
                for file_path in downloaded_files:
                    print(f"  {file_path}")
            else:
                print("No files were downloaded.")

        except NoCredentialsError:
            print(
                "Error: AWS credentials not found. Please configure your AWS credentials."
            )
        except ClientError as e:
            print(f"Error: AWS S3 operation failed: {e}")
        except Exception as e:
            print(f"Error: An unexpected error occurred during download: {e}")
