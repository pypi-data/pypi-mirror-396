import os

import typer
import yaml

app = typer.Typer()


class CustomDumper(yaml.Dumper):
    def increase_indent(self, flow=False, indentless=False):
        return super(CustomDumper, self).increase_indent(flow, False)


class InfrastructureService:
    def __init__(self):
        pass

    def _create_queue(self, name: str, queue_type: str, stub_filename: str, dlq: bool):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        stub_file_path = os.path.join(
            script_dir, "..", "stubs", "infrastructure", stub_filename
        )

        if not os.path.exists(stub_file_path):
            raise FileNotFoundError(f"Stub file not found: {stub_file_path}")

        with open(stub_file_path, "r") as stub_file:
            stub_content = stub_file.read()

        dlq_name = f"{name}DeadLetterQueue"
        sqs_name = f"{name}Queue"

        stub_content = stub_content.replace("{{sqs_name}}", sqs_name)
        stub_content = stub_content.replace("{{dlq_name}}", dlq_name)

        serverless_file_path = os.path.join(os.getcwd(), "serverless.yml")

        if not os.path.exists(serverless_file_path):
            raise FileNotFoundError(
                "serverless.yml not found in the current working directory"
            )

        with open(serverless_file_path, "r") as serverless_file:
            serverless_content = serverless_file.read()

        serverless_dict = yaml.safe_load(serverless_content)

        if "resources" not in serverless_dict:
            serverless_dict["resources"] = {}

        if not serverless_dict["resources"].get("Resources"):
            serverless_dict["resources"]["Resources"] = {}

        if queue_type == "sqs":
            name = sqs_name
        else:
            name = dlq_name

        if name in serverless_dict["resources"]["Resources"]:
            existing_resource = serverless_dict["resources"]["Resources"][name]
            new_resource = yaml.safe_load(stub_content)
            existing_resource.update(new_resource)
        else:
            serverless_dict["resources"]["Resources"][name] = yaml.safe_load(
                stub_content
            )

        with open("serverless.yml", "w") as serverless_file:
            yaml.dump(
                serverless_dict,
                serverless_file,
                Dumper=CustomDumper,
                default_flow_style=False,
                sort_keys=False,
            )

        return name

    def create_sqs_queue(
        self,
        queue_type: str = "sqs",
        name: str = "",
        type: str = "standard",
        dlq: bool = False,
    ):
        if queue_type == "sqs":
            if dlq:
                stub_filename = (
                    "standard_with_dlq.stub"
                    if type.lower() == "standard"
                    else "fifo_with_dlq.stub"
                )
            else:
                stub_filename = (
                    "standard_sqs.stub"
                    if type.lower() == "standard"
                    else "fifo_sqs.stub"
                )
        else:
            stub_filename = (
                "standard_dlq.stub" if type.lower() == "standard" else "fifo_dlq.stub"
            )

        name = self._create_queue(name, queue_type, stub_filename, dlq)

        return name
