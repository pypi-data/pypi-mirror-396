import os


class DebugService:
    def __init__(self):
        self.home_directory = os.path.dirname(
            os.path.dirname(os.path.abspath(__file__))
        )

    def create_launch_json(self, option: str) -> None:
        stub_mapping = {
            "Python File": "python_file.stub",
            "Python File with Arguments": "python_file_with_arguments.stub",
            "Module": "module.stub",
            "FastAPI": "fastapi.stub",
        }

        stub_file = stub_mapping.get(option)
        if not stub_file:
            print(f"Unsupported debug option: {option}")
            return

        source_stub = os.path.join(self.home_directory, "stubs", "debug", stub_file)

        destination_dir = os.path.join(os.getcwd(), ".vscode")
        os.makedirs(destination_dir, exist_ok=True)
        destination_file = os.path.join(destination_dir, "launch.json")

        if os.path.exists(destination_file):
            print("'launch.json' already exists. Skipping creation.")
            return

        try:
            with open(source_stub, "r") as f:
                content = f.read()

            with open(destination_file, "w") as f:
                f.write(content)

            print(f"File '{destination_file}' created successfully.")
        except Exception as e:
            print(f"Error creating launch.json: {e}")
