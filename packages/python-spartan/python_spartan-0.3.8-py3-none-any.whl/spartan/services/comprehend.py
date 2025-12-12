import boto3
import typer


class ComprehendService:
    def __init__(self):
        try:
            self.comprehend_client = boto3.client("comprehend")
        except Exception as e:
            typer.echo(f"Error initializing Comprehend client: {e}")
            # Potentially raise an exception or handle it as per project's error handling strategy
            raise typer.Exit(code=1)

    # Placeholder for list_models
    def list_models(self):
        try:
            response = self.comprehend_client.list_document_classifier_summaries()
            summaries = response.get("DocumentClassifierSummariesList", [])
            if not summaries:
                typer.echo("No document classifier models found.")
                return

            typer.echo("Found Comprehend Document Classifier Models:")
            for summary in summaries:
                typer.echo(f"  Name: {summary.get('DocumentClassifierName')}")
                typer.echo(f"  ARN: {summary.get('DocumentClassifierArn')}")
                typer.echo(f"  Status: {summary.get('Status')}")
                # CreationTime is a datetime object, so we should format it
                creation_time = summary.get("CreationTime")
                if creation_time:
                    typer.echo(
                        f"  Creation Time: {creation_time.strftime('%Y-%m-%d %H:%M:%S')}"
                    )
                else:
                    typer.echo("  Creation Time: Not available")
                typer.echo("---")
        except Exception as e:
            typer.echo(f"Error listing Comprehend models: {e}")
            raise typer.Exit(code=1)

    # Placeholder for get_model_details
    def get_model_details(self, model_arn: str):
        try:
            response = self.comprehend_client.describe_document_classifier(
                DocumentClassifierArn=model_arn
            )
            details = response.get("DocumentClassifierProperties")
            if not details:
                typer.echo(f"No details found for model ARN: {model_arn}")
                return

            self._display_basic_model_info(details)
            self._display_data_configuration(details)
            self._display_training_info(details)
            self._display_additional_info(details)

        except self.comprehend_client.exceptions.InvalidRequestException as e:
            typer.echo(
                f"Error: Invalid request. Is the model ARN '{model_arn}' correct? Details: {e}"
            )
            raise typer.Exit(code=1)
        except self.comprehend_client.exceptions.ResourceNotFoundException as e:
            typer.echo(
                f"Error: Resource not found. Could not find a model with ARN '{model_arn}'. Details: {e}"
            )
            raise typer.Exit(code=1)
        except Exception as e:
            typer.echo(f"Error describing Comprehend model '{model_arn}': {e}")
            raise typer.Exit(code=1)

    def _display_basic_model_info(self, details):
        """Display basic model information."""
        typer.echo(
            f"Details for Comprehend Document Classifier Model: {details.get('DocumentClassifierName')}"
        )
        typer.echo(f"  ARN: {details.get('DocumentClassifierArn')}")
        typer.echo(f"  Status: {details.get('Status')}")
        typer.echo(f"  Message: {details.get('Message')}")
        typer.echo(f"  Language Code: {details.get('LanguageCode')}")
        typer.echo(f"  Classifier Mode: {details.get('Mode')}")

    def _display_data_configuration(self, details):
        """Display input and output data configuration."""
        input_config = details.get("InputDataConfig", {})
        typer.echo("  Input Data:")
        typer.echo(f"    S3 URI: {input_config.get('S3Uri')}")
        typer.echo(f"    Input Format: {input_config.get('InputFormat')}")
        if input_config.get("LabelDelimiter"):
            typer.echo(f"    Label Delimiter: {input_config.get('LabelDelimiter')}")

        output_config = details.get("OutputDataConfig", {})
        typer.echo("  Output Data:")
        typer.echo(f"    S3 URI: {output_config.get('S3Uri')}")
        if output_config.get("KmsKeyId"):
            typer.echo(f"    KMS Key ID: {output_config.get('KmsKeyId')}")

    def _display_training_info(self, details):
        """Display training time information."""
        training_start_time = details.get("TrainingStartTime")
        if training_start_time:
            typer.echo(
                f"  Training Start Time: {training_start_time.strftime('%Y-%m-%d %H:%M:%S')}"
            )
        training_end_time = details.get("TrainingEndTime")
        if training_end_time:
            typer.echo(
                f"  Training End Time: {training_end_time.strftime('%Y-%m-%d %H:%M:%S')}"
            )

    def _display_additional_info(self, details):
        """Display additional model information."""
        typer.echo(f"  Model Version: {details.get('ModelVersion')}")
        if details.get("DocumentType"):
            typer.echo(f"  Document Type: {details.get('DocumentType')}")
        typer.echo("---")
