import shutil
from pathlib import Path

import typer


class DeploymentService:
    def __init__(self):
        self.current_directory = Path.cwd()

    def config(self, source: str):
        source_path = Path(source)

        if not source_path.is_file():
            typer.echo(f"Error: The specified source file '{source}' does not exist.")
            raise typer.Exit(code=1)

        destination_path = self.current_directory / source_path.name

        try:
            shutil.copy(source_path, destination_path)
            typer.echo(f"File '{source_path}' copied to '{destination_path}'")
        except Exception as e:
            typer.echo(f"Error: {e}")
            raise typer.Exit(code=1)
