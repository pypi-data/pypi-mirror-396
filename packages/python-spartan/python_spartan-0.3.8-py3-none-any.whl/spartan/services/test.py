import subprocess

import typer


class TestService:
    def __init__(self, coverage: str = None, report: str = None):
        self.coverage = coverage
        self.report = report

    def run(self):
        command = ["pytest"]

        if self.coverage is not None:
            command.extend(["--cov", self.coverage])

        if self.report is not None:
            command.extend(["--cov-report", self.report])

        result = subprocess.run(command, capture_output=True, text=True)

        if result.returncode != 0:
            typer.echo("Errors occurred:", err=True)
            typer.echo(result.stderr, err=True)
        else:
            typer.echo("Command executed successfully:")
            typer.echo(result.stdout)
